""" app/nodes/carbon_calculator.py ================================================================================ ClimateSense AI - Carbon Calculator Node (2nd node in the LangGraph pipeline) START -> Habit Analyzer -> **Carbon Calculator** -> Climate Impact Analyzer -> Decision Agent -> Recommendation Generator -> Challenge Generator -> Report Generator -> END WHAT THIS NODE DOES -------------------- Reads the five structured habit sub-objects the Habit Analyzer node already wrote into `state["habits"]`, runs each one through the matching deterministic function in `app/services/carbon_math.py`, and writes the result into `state["carbon"]` as a `CarbonData` object. This node contains NO emission-calculation formulas of its own. Every kg CO2e number produced here comes from a function that already exists in `carbon_math.py`. This file's only job is orchestration: read state in, call the right functions with the right arguments, handle anything that goes wrong without crashing the graph, write state out. (Single Responsibility Principle: "calculate emissions" belongs to carbon_math.py; "wire that calculation into the graph" belongs to this file - the two are deliberately kept apart.) WHY THIS NODE DOES NOT CALL GEMINI ------------------------------------ The Carbon Calculator is the one node in the whole pipeline with a hard "no LLM" rule. Carbon math has to be reproducible and auditable - the same habits must always produce the same kg CO2e number, and that number needs to be checkable by hand against a transparent formula. An LLM is non-deterministic and is not a reliable calculator, so it has no role here. Gemini's job starts later in the pipeline (Recommendation Generator onward), where the task shifts from "compute a number" to "write personalized language about a number that has already been computed." ERROR-HANDLING PHILOSOPHY --------------------------- `carbon_math.py` deliberately raises `ValueError` for bad input (e.g. an unrecognized appliance name) instead of silently guessing - correct behavior for a pure function library that fails loudly during testing. But a LangGraph node is not a unit test: one unrecognized appliance name should not take down the whole graph run. This node is where that translation happens - the one place in the system whose job is to convert a raised exception from the deterministic layer into a logged, non-fatal entry in `state["errors"]`, so the graph keeps moving. Each of the five categories is calculated independently, in its own try/except (see `_calculate_category`). If, say, the electricity appliance name is unrecognized, only that category falls back to 0.0 kg CO2e with a clear message in `errors` - transport, water, food, and waste are still calculated normally. A single bad field never blocks the other four. A second, outer try/except wraps the whole node as a last-resort safety net against anything genuinely unforeseen (e.g. a missing `state["habits"]` entirely) - see `carbon_calculator_node`'s body. A NOTE ON `habit_analyzer.py` -------------------------------- The uploaded `habit_analyzer.py` came through as an empty (0-byte) file, so its actual node-function name and return-shape conventions could not be read. This file follows the standard LangGraph convention instead: a plain function that takes the whole `GraphState` and returns a partial-update dict, matching the convention `graph/state.py` is written around throughout. If the real `habit_analyzer.py` uses a different function name or a different return shape, that is a small, localized fix here - it would not change anything about how this node talks to carbon_math.py. """

from collections.abc import Callable
from datetime import datetime, timezone
from time import perf_counter
from typing import Any

from app.graph.state import CarbonData, GraphState, HabitsData, NodeExecutionRecord
from app.services.carbon_math import (
    APPLIANCE_POWER_KW,
    ELECTRICITY_GRID_FACTORS,
    FOOD_FACTORS,
    TRANSPORT_FACTORS,
    WASTE_FACTORS,
    WATER_FLOW_RATES_LPM,
    WATER_TREATMENT_FACTORS,
    calculate_electricity_emissions,
    calculate_food_emissions,
    calculate_transport_emissions,
    calculate_waste_emissions,
    calculate_water_emissions,
)

# Used both as the "who logged this" field in NodeExecutionRecord and inside
# every error message this node appends, so every log line this node
# produces is traceable back to it at a glance.
NODE_NAME = "carbon_calculator"

# The categories this node is responsible for, in the fixed order they are
# always reported in. Defined once, here, so nothing below has to repeat
# this list as a "magic" set of five strings.
CATEGORIES: tuple[str, ...] = ("transport", "electricity", "water", "food", "waste")


# =============================================================================
# INTERNAL HELPERS
# =============================================================================
# Each helper has exactly one small job, so `carbon_calculator_node` at the
# bottom of this file reads as a short, linear list of steps instead of one
# long function doing everything (Single Responsibility, applied within a
# single node rather than across the whole module).


def _normalize_for_lookup(raw: str) -> str:
    """ Normalize a category string the same way `carbon_math.py` normalizes its own lookups internally, so a factor-table read here resolves to the exact same key a successful `calculate_*_emissions()` call already resolved to. Used only to build the human-readable `emission_factors_used` report below - never to calculate an emissions value. All five actual emissions figures still come exclusively from carbon_math.py's public functions; this is a read of carbon_math.py's public data tables, not a re-implementation of any calculation. Args: raw: The raw category string, e.g. "Non Vegetarian". Returns: The normalized key, e.g. "non_vegetarian". """
    return raw.strip().lower().replace(" ", "_").replace("-", "_")


def _calculate_category( category: str, compute: Callable[[], float], errors: list[str], ) -> tuple[float, bool]:
    """ Run one category's carbon_math.py function and gracefully absorb any failure instead of letting it crash this node (and, in turn, the graph). Args: category: Human-readable category name, used in the error message if `compute` fails (e.g. "transport"). compute: A zero-argument callable that performs the actual calculation - a small lambda that closes over the real carbon_math.py function and its arguments, e.g. ``lambda: calculate_transport_emissions(mode, distance_km)``. errors: The list to append a message to if `compute` raises. The caller merges this list into `state["errors"]` on return. Returns: A ``(value, succeeded)`` tuple: - On success: the real computed kg CO2e value, and True. - On failure: 0.0 (a placeholder, not a claim the true value is zero) and False, with a message already appended to `errors` explaining what went wrong and why the category is being treated as 0.0 for now. """
    try:
        return compute(), True
    except (ValueError, TypeError) as exc:
        errors.append(
            f"{NODE_NAME}: could not calculate {category} emissions ({exc}). "
            f"Treated as 0.0 kg CO2e - the true value is unknown, not zero."
        )
        return 0.0, False


def _build_emission_factors_used( habits: HabitsData, successful_categories: set[str], ) -> dict[str, float]:
    """ Build a transparency report of which emission factor was applied to each successful category - useful later for the Sustainability Report ("your car trip was calculated at 0.192 kg CO2e/km"). This performs table LOOKUPS only, against dictionaries carbon_math.py already exports publicly (`TRANSPORT_FACTORS`, `APPLIANCE_POWER_KW`, etc.) - it never repeats any of the arithmetic that produces an emissions figure. Electricity and water are each reported as a single combined rate (their two underlying numbers multiplied together), since `CarbonData.emission_factors_used` stores one float per category, not a nested structure. Args: habits: `state["habits"]`. successful_categories: Names of categories that calculated without error. A category NOT in this set is simply left out of the returned dict - `state["errors"]` is the one place that explains why, rather than this function fabricating a misleading 0.0 "factor" for a category that never actually resolved to one. Returns: A dict mapping category name to the kg CO2e factor applied, for whichever categories succeeded. """
    factors: dict[str, float] = {}

    if "transport" in successful_categories:
        key = _normalize_for_lookup(habits.transport.mode)
        factors["transport"] = TRANSPORT_FACTORS[key]

    if "electricity" in successful_categories:
        key = _normalize_for_lookup(habits.electricity.appliance)
        power_kw = APPLIANCE_POWER_KW[key]
        grid_factor = ELECTRICITY_GRID_FACTORS["grid_average"]
        factors["electricity"] = round(power_kw * grid_factor, 4)

    if "water" in successful_categories:
        key = _normalize_for_lookup(habits.water.activity)
        flow_rate_lpm = WATER_FLOW_RATES_LPM[key]
        treatment_factor = WATER_TREATMENT_FACTORS["standard_supply"]
        factors["water"] = round(flow_rate_lpm * treatment_factor, 4)

    if "food" in successful_categories:
        key = _normalize_for_lookup(habits.food.diet_type)
        factors["food"] = FOOD_FACTORS[key]

    if "waste" in successful_categories:
        key = _normalize_for_lookup(habits.waste.waste_type)
        factors["waste"] = WASTE_FACTORS[key]

    return factors


# =============================================================================
# THE NODE
# =============================================================================


def carbon_calculator_node(state: GraphState) -> dict[str, Any]:
    """ LangGraph node: calculate the user's carbon footprint from their already-structured habits. Reads `state["habits"]` (populated earlier by the Habit Analyzer node) and `state["meta"]` (read-only, for region metadata), computes kg CO2e for transport, electricity, water, food, and waste using the functions in `app/services/carbon_math.py`, and returns a partial state update containing the populated `carbon` field. This node never calls Gemini, never generates recommendations, a report, or an eco challenge, never parses raw user input, and never modifies `state["habits"]` - it only reads habits and writes carbon data. Args: state: The current `GraphState`. Returns: A partial `GraphState` update (LangGraph convention: a node returns only the keys it is changing, not the whole state): - "carbon": the populated `CarbonData`. - "errors": any per-category failure messages from this run (merged into the graph's existing errors via the `errors` reducer defined in `graph/state.py` - safe even though a later node in this same graph may also append to `errors`). - "node_execution_log": one `NodeExecutionRecord` describing this run (merged via the `node_execution_log` reducer). - "current_step": always advanced to "climate_impact_analyzer", whether this run succeeded, partially failed, or hit the outer safety net - the graph must never get stuck here. """
    started_at = perf_counter()
    errors: list[str] = []

    try:
        habits = state["habits"]

        # --- Step 1: calculate each category independently -------------
        # A failure in any one of these five never prevents the other
        # four from being calculated - see `_calculate_category`.
        transport_kg, transport_ok = _calculate_category(
            "transport",
            lambda: calculate_transport_emissions(
                mode=habits.transport.mode,
                distance_km=habits.transport.distance_km,
            ),
            errors,
        )
        electricity_kg, electricity_ok = _calculate_category(
            "electricity",
            lambda: calculate_electricity_emissions(
                appliance=habits.electricity.appliance,
                usage_hours=habits.electricity.usage_hours,
            ),
            errors,
        )
        water_kg, water_ok = _calculate_category(
            "water",
            lambda: calculate_water_emissions(
                activity=habits.water.activity,
                duration_minutes=habits.water.duration_minutes,
            ),
            errors,
        )
        food_kg, food_ok = _calculate_category(
            "food",
            # `days` is left at carbon_math.py's default (1.0) - this
            # node estimates a single day's footprint, matching the
            # single-day shape of `structured_food` from Habit Analyzer.
            lambda: calculate_food_emissions(diet_type=habits.food.diet_type),
            errors,
        )
        waste_kg, waste_ok = _calculate_category(
            "waste",
            lambda: calculate_waste_emissions(
                waste_type=habits.waste.waste_type,
                quantity=habits.waste.quantity,
            ),
            errors,
        )

        # --- Step 2: assemble the category breakdown --------------------
        # Rounded the same way carbon_math.py's own calculate_total_
        # emissions() rounds (2 decimal places, *before* summing), so the
        # displayed breakdown always adds up exactly to the displayed
        # total - whether this node or carbon_math.py's composed function
        # produced the numbers, the result is identical.
        emissions_by_category: dict[str, float] = {
            "transport": round(transport_kg, 2),
            "electricity": round(electricity_kg, 2),
            "water": round(water_kg, 2),
            "food": round(food_kg, 2),
            "waste": round(waste_kg, 2),
        }
        total_carbon_kg_co2 = round(sum(emissions_by_category.values()), 2)

        # --- Step 3: build the transparency + metadata reports ----------
        successful_categories = {
            category
            for category, ok in zip(
                CATEGORIES,
                (transport_ok, electricity_ok, water_ok, food_ok, waste_ok),
            )
            if ok
        }
        emission_factors_used = _build_emission_factors_used(habits, successful_categories)

        calculation_metadata: dict[str, Any] = {
            "source": "app.services.carbon_math",
            "grid_emission_factor_kg_per_kwh": ELECTRICITY_GRID_FACTORS["grid_average"],
            "water_treatment_factor_kg_per_liter": WATER_TREATMENT_FACTORS["standard_supply"],
            "region": state["meta"].region,
            "categories_with_errors": sorted(set(CATEGORIES) - successful_categories),
            "calculated_at": datetime.now(timezone.utc).isoformat(),
        }

        carbon_data = CarbonData(
            emissions_by_category=emissions_by_category,
            total_carbon_kg_co2=total_carbon_kg_co2,
            emission_factors_used=emission_factors_used,
            calculation_metadata=calculation_metadata,
        )
        status = "error" if errors else "success"

    except Exception as exc:
        # Last-resort safety net. Everything above already handles the
        # *expected* failure mode (an unrecognized category string) at
        # the per-category level. This catches anything genuinely
        # unforeseen - e.g. `state["habits"]` missing entirely - so that
        # even a bug produces a logged error and a valid (empty) carbon
        # state, never a crashed graph.
        errors.append(
            f"{NODE_NAME}: unexpected failure ({exc}). Carbon data could not be calculated."
        )
        carbon_data = CarbonData()  # all-zero CarbonData - still a valid object downstream nodes can read
        status = "error"

    duration_ms = (perf_counter() - started_at) * 1000

    return {
        "carbon": carbon_data,
        "errors": errors,
        "node_execution_log": [
            NodeExecutionRecord(node=NODE_NAME, status=status, duration_ms=duration_ms)
        ],
        "current_step": "climate_impact_analyzer",
    }


# =============================================================================
# STANDALONE DEMO
# =============================================================================
# Not part of the graph - this only runs when this file is executed
# directly (`python app/nodes/carbon_calculator.py`), so importing this
# module from elsewhere (e.g. the real graph builder) never prints
# anything. Included so this node can be sanity-checked on its own,
# without needing the rest of the graph wired up yet.

if __name__ == "__main__":
    from app.graph.state import create_initial_state

    # Build a minimal state as if the Habit Analyzer node had already run,
    # using the project's standard worked example.
    demo_state = create_initial_state(
        raw_input={
            "transport": "Car - 20 km",
            "electricity": "AC - 6 hours",
            "water": "15-minute shower",
            "food": "Non Vegetarian",
            "waste": "3 Plastic Bottles",
        }
    )
    demo_state["habits"] = HabitsData(
        transport={"mode": "car", "distance_km": 20},
        electricity={"appliance": "ac", "usage_hours": 6},
        water={"activity": "shower", "duration_minutes": 15},
        food={"diet_type": "non_vegetarian"},
        waste={"waste_type": "plastic_bottle", "quantity": 3},
    )

    update = carbon_calculator_node(demo_state)

    print("ClimateSense AI - Carbon Calculator Node (standalone run)")
    print("=" * 58)
    print("carbon.emissions_by_category:", update["carbon"].emissions_by_category)
    print("carbon.total_carbon_kg_co2 :", update["carbon"].total_carbon_kg_co2)
    print("carbon.emission_factors_used:", update["carbon"].emission_factors_used)
    print("carbon.calculation_metadata :", update["carbon"].calculation_metadata)
    print("errors :", update["errors"])
    print("node_execution_log :", update["node_execution_log"])
    print("current_step :", update["current_step"])

    # Second run, deliberately with an unrecognized transport mode and
    # appliance, to demonstrate the graceful-degradation path.
    print("\n--- second run: unrecognized mode + appliance -----------------")
    demo_state["habits"] = HabitsData(
        transport={"mode": "hoverboard", "distance_km": 5},
        electricity={"appliance": "server_rack", "usage_hours": 2},
        water={"activity": "shower", "duration_minutes": 10},
        food={"diet_type": "vegan"},
        waste={"waste_type": "aluminum_can", "quantity": 2},
    )
    update_2 = carbon_calculator_node(demo_state)
    print("carbon.emissions_by_category:", update_2["carbon"].emissions_by_category)
    print("carbon.total_carbon_kg_co2 :", update_2["carbon"].total_carbon_kg_co2)
    print("errors :", update_2["errors"])