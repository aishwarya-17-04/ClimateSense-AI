"""
app/services/carbon_math.py
=============================================================================
ClimateSense AI - Deterministic Carbon Calculation Engine
=============================================================================

WHAT THIS MODULE IS
--------------------
This is the "Domain / Services Layer" component behind the Carbon
Calculator node described in the ClimateSense AI architecture document.
It contains ONLY pure, deterministic Python functions:

    * No LangGraph.
    * No FastAPI.
    * No Gemini / LLM calls of any kind.
    * No file I/O, no network calls, no randomness, no hidden state.

Given the same inputs, every function here ALWAYS returns the exact same
output. That predictability is the entire point: the project's headline
"your footprint is X kg CO2e" number must be something a reviewer can
verify by hand against a transparent formula. An LLM must never be the
source of truth for a number like this - Gemini's job elsewhere in the
system is language and reasoning, not arithmetic.

This module is designed to be imported later by the Carbon Calculator
node inside the LangGraph pipeline, and called with the already-structured
data the Habit Analyzer node produces, e.g.:

    structured_transport   = {"mode": "car", "distance_km": 20}
    structured_electricity = {"appliance": "ac", "usage_hours": 6}
    structured_water       = {"activity": "shower", "duration_minutes": 15}
    structured_food        = {"diet_type": "non_vegetarian"}
    structured_waste       = {"waste_type": "plastic_bottle", "quantity": 3}

WHAT THIS MODULE CALCULATES
----------------------------
Five independent emission categories, each expressed in kilograms of CO2
equivalent (kg CO2e):

    1. Transportation -> distance_km x mode emission factor
    2. Electricity     -> usage_hours x appliance power (kW) x grid factor
    3. Water            -> duration_minutes x activity flow rate (L/min)
                            x water treatment factor
    4. Food             -> diet_type mapped to a daily average figure
    5. Waste            -> quantity x per-item/per-kg material factor

A NOTE ON DOUBLE-COUNTING (WATER vs. ELECTRICITY)
---------------------------------------------------
`calculate_water_emissions()` deliberately covers ONLY the water supply,
treatment, and pumping footprint of an activity (e.g., a shower). It does
NOT include the energy used to HEAT that water. Heating water is
electrical work - if a user's electricity habits also include a
"water_heater" appliance entry, that energy is already counted once by
`calculate_electricity_emissions()`. Counting it again under "water"
would double-count the same emissions across two categories. This is a
deliberate methodological choice (the "recommended default" from the
architecture doc), not an oversight - see the docstring of
`calculate_water_emissions()` below for the full explanation.

DESIGN PRINCIPLES (SOLID, applied to a functional module)
------------------------------------------------------------
    * Single Responsibility - each public function calculates exactly ONE
      category of emissions. `calculate_total_emissions()` has exactly one
      job too: composing the other five results.
    * Open/Closed            - every emission factor and usage-rate lives in
      a module-level dictionary. Adding a new transport mode, appliance,
      diet type, or waste type never requires touching a function body -
      only the data tables in Section 1 below.
    * Liskov Substitution    - in spirit (this principle technically
      describes class hierarchies, but the same idea applies here): all
      five category functions share the same shape,
      (identifying string(s), quantity) -> float kg CO2e, so any one of
      them can be swapped, mocked, or looped over uniformly.
    * Interface Segregation  - each function only asks for the parameters
      it actually needs (e.g., `calculate_food_emissions` doesn't need a
      distance or a wattage), instead of one bloated shared "activity"
      object every function would have to unpack.
    * Dependency Inversion   - this module depends on nothing but the
      Python standard library. The future LangGraph node will depend on
      THIS module's plain function signatures, not the other way around -
      nothing in this file knows, or needs to know, that LangGraph exists.

USAGE
------
See the `if __name__ == "__main__":` block at the bottom of this file for
a complete worked example.
"""

from typing import Any, Dict

__all__ = [
    "TRANSPORT_FACTORS",
    "APPLIANCE_POWER_KW",
    "ELECTRICITY_GRID_FACTORS",
    "WATER_FLOW_RATES_LPM",
    "WATER_TREATMENT_FACTORS",
    "FOOD_FACTORS",
    "WASTE_FACTORS",
    "calculate_transport_emissions",
    "calculate_electricity_emissions",
    "calculate_water_emissions",
    "calculate_food_emissions",
    "calculate_waste_emissions",
    "calculate_total_emissions",
]


# =============================================================================
# 1. EMISSION FACTOR & REFERENCE DATA TABLES
# =============================================================================
# Every number the calculations below depend on lives here, and ONLY here.
# Nothing past this section contains a "magic number." To add a new
# transport mode, appliance, diet type, etc., add a dictionary entry here -
# never edit a function body.
#
# All factors are reasonable, illustrative averages appropriate for a
# college-level project. They are NOT audited scientific figures and
# should not be used for regulatory or scientific carbon accounting.

# --- Transportation ---------------------------------------------------------
# kg CO2e emitted per kilometer traveled, by mode of transport.
TRANSPORT_FACTORS: Dict[str, float] = {
    "car": 0.192,         # average petrol/diesel car
    "motorbike": 0.103,   # average motorbike
    "bus": 0.105,         # per passenger, average occupancy
    "train": 0.041,       # average electric/diesel rail, per passenger
    "bike": 0.0,          # human-powered, no direct emissions
    "walk": 0.0,          # human-powered, no direct emissions
}

# --- Electricity -------------------------------------------------------------
# Typical power draw (in kilowatts, kW) of common household appliances.
# This is a USAGE-RATE table, not an emission factor by itself - it's the
# "how much energy does this appliance use per hour" half of the formula.
APPLIANCE_POWER_KW: Dict[str, float] = {
    "ac": 1.50,               # split/window air conditioner
    "fan": 0.075,
    "refrigerator": 0.15,
    "washing_machine": 0.50,
    "water_heater": 2.00,     # electric geyser/immersion heater
    "television": 0.10,
    "laptop": 0.05,
    "lighting": 0.06,         # LED bulb(s), typical room
}

# kg CO2e emitted per kWh of electricity drawn from the grid. Stored as a
# dictionary (even with one entry) so a region-specific grid factor can be
# added later without changing any function signature - this is the
# Open/Closed extension point mentioned in the architecture doc's
# "region-configurable emission factors" suggestion.
ELECTRICITY_GRID_FACTORS: Dict[str, float] = {
    "grid_average": 0.475,
}

# --- Water ---------------------------------------------------------------
# Typical flow rate (in liters per minute, L/min) of common water
# activities. Like appliance power above, this is a USAGE-RATE table, not
# an emission factor - it's the "how much water does this activity use per
# minute" half of the formula.
WATER_FLOW_RATES_LPM: Dict[str, float] = {
    "shower": 9.0,
    "handwashing": 6.0,
    "dishwashing": 8.0,
    "brushing_teeth": 6.0,
    "laundry": 10.0,
}

# kg CO2e emitted per liter of water for supply, treatment, and pumping
# ONLY. Water-heating energy is intentionally excluded here - see the
# "NOTE ON DOUBLE-COUNTING" section in the module docstring above.
WATER_TREATMENT_FACTORS: Dict[str, float] = {
    "standard_supply": 0.0003,
}

# --- Food ------------------------------------------------------------------
# kg CO2e per day, by overall diet type. These are literature-style
# average figures covering production, processing, and transport of a
# full day's food for one person - not a per-meal or per-ingredient
# breakdown.
FOOD_FACTORS: Dict[str, float] = {
    "vegan": 2.9,
    "vegetarian": 3.8,
    "pescatarian": 3.9,
    "non_vegetarian": 7.2,
}

# --- Waste -------------------------------------------------------------
# kg CO2e per unit of waste generated, by material/type. For discrete
# items (bottles, bags, cans) "quantity" means item COUNT. For the two
# bulk categories ("food_waste", "general_waste") "quantity" means
# KILOGRAMS instead. This distinction is documented here because it isn't
# visible from the dictionary values alone.
WASTE_FACTORS: Dict[str, float] = {
    "plastic_bottle": 0.08,   # kg CO2e per item
    "plastic_bag": 0.04,      # kg CO2e per item
    "paper": 0.01,            # kg CO2e per sheet/item
    "glass_bottle": 0.20,     # kg CO2e per item
    "aluminum_can": 0.17,     # kg CO2e per item
    "food_waste": 0.25,       # kg CO2e per KILOGRAM
    "general_waste": 0.10,    # kg CO2e per KILOGRAM (landfill mix)
}


# =============================================================================
# 2. INTERNAL HELPER FUNCTIONS
# =============================================================================
# Private (leading-underscore) utilities used by the public calculator
# functions in Section 3. Beginners: a leading underscore is a Python
# convention meaning "internal use only - not part of this module's public
# API." Centralizing validation here (instead of copy-pasting the same
# checks into every calculate_*() function) is what keeps this module DRY
# (Don't Repeat Yourself) and easy to unit test in isolation.

def _validate_non_negative(value: float, field_name: str) -> None:
    """
    Raise a clear error if a numeric input is negative.

    Args:
        value: The number to check (e.g., a distance, duration, or
            quantity - anything that physically cannot be negative).
        field_name: A human-readable name for the value, used in the
            error message so the caller immediately knows which argument
            was invalid.

    Raises:
        ValueError: If `value` is negative.
    """
    if value < 0:
        raise ValueError(f"'{field_name}' cannot be negative. Received: {value}")


def _lookup_factor(key: str, factor_table: Dict[str, float], field_name: str) -> float:
    """
    Normalize a user-supplied string and look up its value in a reference
    dictionary (an emission-factor table or a usage-rate table), raising a
    helpful error if it isn't found.

    Normalization lowercases the string, trims surrounding whitespace, and
    converts spaces/hyphens to underscores, so "Car", " car ", and "car"
    all match the same dictionary key.

    Args:
        key: The raw string to look up (e.g., "Car", "AC", "Non Vegetarian").
        factor_table: The dictionary to search, e.g. TRANSPORT_FACTORS.
        field_name: A human-readable name for what `key` represents, used
            to build a clear error message (e.g., "transport mode").

    Returns:
        The numeric value stored in `factor_table` for the normalized key.

    Raises:
        ValueError: If the normalized key is not present in `factor_table`.
            The error message lists every valid option, which is exactly
            the kind of error a developer wiring up the LangGraph node
            will want to see immediately, instead of a silent KeyError.
    """
    normalized_key = key.strip().lower().replace(" ", "_").replace("-", "_")
    if normalized_key not in factor_table:
        valid_options = ", ".join(sorted(factor_table.keys()))
        raise ValueError(
            f"Unknown {field_name} '{key}'. Valid options are: {valid_options}"
        )
    return factor_table[normalized_key]


# =============================================================================
# 3. PUBLIC CALCULATION FUNCTIONS
# =============================================================================

def calculate_transport_emissions(mode: str, distance_km: float) -> float:
    """
    Calculate emissions from a single transportation activity.

    Formula: distance_km x mode_emission_factor

    Args:
        mode: The mode of transport. Must be a key in TRANSPORT_FACTORS
            (currently: "car", "motorbike", "bus", "train", "bike",
            "walk"). Matching is case-insensitive.
        distance_km: Distance traveled, in kilometers. Must be >= 0.

    Returns:
        Estimated emissions in kg CO2e for this trip.

    Raises:
        ValueError: If `distance_km` is negative, or `mode` is not a
            recognized transport mode.

    Example:
        >>> round(calculate_transport_emissions("car", 20), 4)
        3.84
    """
    _validate_non_negative(distance_km, "distance_km")
    factor = _lookup_factor(mode, TRANSPORT_FACTORS, "transport mode")
    return distance_km * factor


def calculate_electricity_emissions(appliance: str, usage_hours: float) -> float:
    """
    Calculate emissions from running a household appliance.

    Formula: usage_hours x appliance_power_kW x grid_emission_factor

    Args:
        appliance: The appliance used. Must be a key in
            APPLIANCE_POWER_KW (currently: "ac", "fan", "refrigerator",
            "washing_machine", "water_heater", "television", "laptop",
            "lighting"). Matching is case-insensitive.
        usage_hours: How long the appliance ran, in hours. Must be >= 0.

    Returns:
        Estimated emissions in kg CO2e for this usage.

    Raises:
        ValueError: If `usage_hours` is negative, or `appliance` is not
            recognized.

    Example:
        >>> round(calculate_electricity_emissions("ac", 6), 4)
        4.275
    """
    _validate_non_negative(usage_hours, "usage_hours")
    power_kw = _lookup_factor(appliance, APPLIANCE_POWER_KW, "appliance")
    grid_factor = ELECTRICITY_GRID_FACTORS["grid_average"]
    kwh_used = usage_hours * power_kw
    return kwh_used * grid_factor


def calculate_water_emissions(activity: str, duration_minutes: float) -> float:
    """
    Calculate emissions from water supply, treatment, and pumping for a
    timed water activity.

    Formula: duration_minutes x activity_flow_rate_Lpm x water_treatment_factor

    IMPORTANT - scope of this function: this covers water SUPPLY and
    TREATMENT only. It deliberately excludes the energy used to HEAT the
    water. If the same user's electricity habits also include a
    "water_heater" appliance (see `calculate_electricity_emissions`), that
    already accounts for the heating energy - counting it again here would
    double-count the same emissions under two categories. See the module
    docstring's "NOTE ON DOUBLE-COUNTING" section for the full reasoning.

    Args:
        activity: The water activity performed. Must be a key in
            WATER_FLOW_RATES_LPM (currently: "shower", "handwashing",
            "dishwashing", "brushing_teeth", "laundry"). Matching is
            case-insensitive.
        duration_minutes: How long the activity lasted, in minutes.
            Must be >= 0.

    Returns:
        Estimated emissions in kg CO2e for this activity.

    Raises:
        ValueError: If `duration_minutes` is negative, or `activity` is
            not recognized.

    Example:
        >>> round(calculate_water_emissions("shower", 15), 4)
        0.0405
    """
    _validate_non_negative(duration_minutes, "duration_minutes")
    flow_rate_lpm = _lookup_factor(activity, WATER_FLOW_RATES_LPM, "water activity")
    treatment_factor = WATER_TREATMENT_FACTORS["standard_supply"]
    liters_used = duration_minutes * flow_rate_lpm
    return liters_used * treatment_factor


def calculate_food_emissions(diet_type: str, days: float = 1.0) -> float:
    """
    Calculate emissions from a user's diet.

    Formula: diet_daily_average_kg_co2e x days

    Args:
        diet_type: The user's overall diet pattern. Must be a key in
            FOOD_FACTORS (currently: "vegan", "vegetarian", "pescatarian",
            "non_vegetarian"). Matching is case-insensitive.
        days: Number of days this diet pattern covers. Defaults to 1.0
            (a single day), matching the single-field `structured_food`
            shape produced by the Habit Analyzer node. Pass a larger
            value (e.g. 7 for a week) to scale the estimate. Must be >= 0.

    Returns:
        Estimated emissions in kg CO2e for the given number of days.

    Raises:
        ValueError: If `days` is negative, or `diet_type` is not
            recognized.

    Example:
        >>> round(calculate_food_emissions("non_vegetarian"), 4)
        7.2
    """
    _validate_non_negative(days, "days")
    daily_factor = _lookup_factor(diet_type, FOOD_FACTORS, "diet type")
    return daily_factor * days


def calculate_waste_emissions(waste_type: str, quantity: float) -> float:
    """
    Calculate emissions from waste generation.

    Formula: quantity x per_unit_material_factor

    Args:
        waste_type: The type of waste generated. Must be a key in
            WASTE_FACTORS (currently: "plastic_bottle", "plastic_bag",
            "paper", "glass_bottle", "aluminum_can", "food_waste",
            "general_waste"). Matching is case-insensitive. For discrete
            items this is a per-item factor; for "food_waste" and
            "general_waste" it is a per-kilogram factor (see the comment
            above WASTE_FACTORS in Section 1).
        quantity: The number of items (for discrete waste types) or
            kilograms (for the two bulk waste types). Must be >= 0.

    Returns:
        Estimated emissions in kg CO2e for this waste.

    Raises:
        ValueError: If `quantity` is negative, or `waste_type` is not
            recognized.

    Example:
        >>> round(calculate_waste_emissions("plastic_bottle", 3), 4)
        0.24
    """
    _validate_non_negative(quantity, "quantity")
    factor = _lookup_factor(waste_type, WASTE_FACTORS, "waste type")
    return quantity * factor


def calculate_total_emissions(
    transport_mode: str,
    transport_distance_km: float,
    electricity_appliance: str,
    electricity_usage_hours: float,
    water_activity: str,
    water_duration_minutes: float,
    diet_type: str,
    waste_type: str,
    waste_quantity: float,
    *,
    food_days: float = 1.0,
) -> Dict[str, Any]:
    """
    Calculate a full daily carbon footprint by combining all five
    categories: transportation, electricity, water, food, and waste.

    This function does no math of its own beyond addition - it simply
    composes the five single-category functions above and packages their
    results. (Single Responsibility: this function's one job is
    composition, not calculation.)

    Args:
        transport_mode: See `calculate_transport_emissions`.
        transport_distance_km: See `calculate_transport_emissions`.
        electricity_appliance: See `calculate_electricity_emissions`.
        electricity_usage_hours: See `calculate_electricity_emissions`.
        water_activity: See `calculate_water_emissions`.
        water_duration_minutes: See `calculate_water_emissions`.
        diet_type: See `calculate_food_emissions`.
        waste_type: See `calculate_waste_emissions`.
        waste_quantity: See `calculate_waste_emissions`.
        food_days: See `calculate_food_emissions`. Keyword-only (after the
            `*`) so it can never be mixed up positionally with one of the
            nine required arguments above. Defaults to 1.0.

    Returns:
        A dictionary shaped to slot directly into the ClimateSense AI
        GraphState `carbon` group::

            {
                "emissions_by_category": {
                    "transport": <float, kg CO2e>,
                    "electricity": <float, kg CO2e>,
                    "water": <float, kg CO2e>,
                    "food": <float, kg CO2e>,
                    "waste": <float, kg CO2e>,
                },
                "total_carbon_kg_co2": <float, kg CO2e>,
            }

        Every number is rounded to 2 decimal places for readability. Each
        category is rounded before summing, so the displayed breakdown
        always adds up exactly to the displayed total - avoiding a
        confusing "the numbers don't quite add up" moment for the user.

    Raises:
        ValueError: If any individual category calculation raises one
            (see each function above for specifics). This function does
            not catch or suppress those errors - a bad input should fail
            loudly and immediately, not silently produce a wrong total.

    Example:
        >>> result = calculate_total_emissions(
        ...     transport_mode="car",
        ...     transport_distance_km=20,
        ...     electricity_appliance="ac",
        ...     electricity_usage_hours=6,
        ...     water_activity="shower",
        ...     water_duration_minutes=15,
        ...     diet_type="non_vegetarian",
        ...     waste_type="plastic_bottle",
        ...     waste_quantity=3,
        ... )
        >>> result["total_carbon_kg_co2"]
        15.6
    """
    transport = calculate_transport_emissions(transport_mode, transport_distance_km)
    electricity = calculate_electricity_emissions(electricity_appliance, electricity_usage_hours)
    water = calculate_water_emissions(water_activity, water_duration_minutes)
    food = calculate_food_emissions(diet_type, food_days)
    waste = calculate_waste_emissions(waste_type, waste_quantity)

    emissions_by_category: Dict[str, float] = {
        "transport": round(transport, 2),
        "electricity": round(electricity, 2),
        "water": round(water, 2),
        "food": round(food, 2),
        "waste": round(waste, 2),
    }
    total = round(sum(emissions_by_category.values()), 2)

    return {
        "emissions_by_category": emissions_by_category,
        "total_carbon_kg_co2": total,
    }


# =============================================================================
# 4. EXAMPLE USAGE
# =============================================================================
# This block only executes when the file is run directly, e.g.:
#     python app/services/carbon_math.py
# It will NOT run when this module is imported elsewhere (such as by the
# future LangGraph Carbon Calculator node) - that is what the
# `if __name__ == "__main__":` guard is for.

if __name__ == "__main__":
    # This mirrors the example walkthrough in the architecture document:
    # transport: "Car - 20 km", electricity: "AC - 6 hours",
    # water: "15-minute shower", food: "Non Vegetarian",
    # waste: "3 Plastic Bottles"
    result = calculate_total_emissions(
        transport_mode="car",
        transport_distance_km=20,
        electricity_appliance="ac",
        electricity_usage_hours=6,
        water_activity="shower",
        water_duration_minutes=15,
        diet_type="non_vegetarian",
        waste_type="plastic_bottle",
        waste_quantity=3,
    )
    print(result)

    # ------------------------------------------------------------------
    # Bonus: the same result, printed as a readable breakdown. Optional -
    # the plain `print(result)` above already shows you everything - but
    # a formatted view is easier to scan at a glance.
    # ------------------------------------------------------------------
    print("\nClimateSense AI - Daily Carbon Footprint")
    print("=" * 42)
    for category, value in result["emissions_by_category"].items():
        print(f"  {category.capitalize():<14}{value:>8} kg CO2e")
    print("-" * 42)
    print(f"  {'TOTAL':<14}{result['total_carbon_kg_co2']:>8} kg CO2e")