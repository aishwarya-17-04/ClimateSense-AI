""" app/graph/state.py =================== Central state schema for the ClimateSense AI LangGraph pipeline. This module is the executable version of Section 4 ("State Design") of the approved ClimateSense AI architecture document. Every field that exists from START to END lives here, grouped by the node that owns it. Design notes ------------ * Each logical group (meta, input, habits, carbon, impact, recommendations, challenge, report) is modeled as a Pydantic ``BaseModel``. This gives real runtime validation (e.g. ``distance_km >= 0``) and means the same classes can be reused later as Gemini structured-output schemas for the agent nodes — one schema, two jobs. * The top-level ``GraphState`` itself is a ``TypedDict``, not a Pydantic model. This is the more idiomatic LangGraph choice, and it is what makes the ``Annotated[..., reducer]`` fields below behave predictably. * LangGraph rule this file is built around: if more than one node can write to the same top-level state key *in the same step*, that key needs a reducer, or the graph raises ``InvalidUpdateError``. In this graph, the Recommendation Generator and Challenge Generator nodes run in parallel (see Section 6, "Graph Design"), and both may append to the execution log, append an error, or bump a retry counter in the same step. That is why ``node_execution_log``, ``errors``, and ``retry_count`` carry explicit reducers below. Every other key is owned by exactly one node and uses LangGraph's default last-write-wins behavior. * ``current_step`` is a plain, non-reduced field. It is meant to be written only by the sequential nodes (Input Validator, Habit Analyzer, Carbon Calculator, Impact Analyzer, Report Generator). Do NOT write to it from inside the parallel Recommendation/Challenge stage — with no reducer, a concurrent write from both branches will raise ``InvalidUpdateError``. Use ``node_execution_log`` to observe progress during that stage instead. """

import operator
import uuid
from datetime import datetime, timezone
from typing import Annotated, Any, Literal, TypedDict

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Reducers
# ---------------------------------------------------------------------------


def merge_dicts(current: dict[str, int], new: dict[str, int]) -> dict[str, int]:
    """Reducer for ``retry_count``. Merges per-node retry counters instead of overwriting the whole dict, so the two nodes in the parallel stage (Recommendation Generator, Challenge Generator) can each update their own counter in the same graph step without clobbering the other's update. """
    merged = dict(current)
    merged.update(new)
    return merged


# ---------------------------------------------------------------------------
# meta — set once, at graph invocation
# ---------------------------------------------------------------------------


class MetaInfo(BaseModel):
    """Request/session metadata."""

    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str | None = None
    requested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    region: str = "global"  # selects the emission-factor / benchmark dataset


# ---------------------------------------------------------------------------
# input — populated by the Input Validator node
# ---------------------------------------------------------------------------


class InputData(BaseModel):
    """Raw payload plus the results of validation/normalization."""

    raw_input: dict[str, Any] = Field(default_factory=dict)
    is_valid_input: bool = False
    validation_errors: list[str] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)
    applied_defaults: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# habits — populated by the Habit Analyzer node
# ---------------------------------------------------------------------------


class TransportHabit(BaseModel):
    mode: str = ""  # e.g. "car", "bus", "bike", "flight"
    distance_km: float = Field(default=0.0, ge=0)
    fuel_type: str | None = None  # e.g. "petrol", "diesel", "electric"
    passengers: int = Field(default=1, ge=1)


class ElectricityHabit(BaseModel):
    appliance: str = ""  # e.g. "AC", "heater", "washing machine"
    usage_hours: float = Field(default=0.0, ge=0, le=24)
    estimated_wattage: float | None = Field(default=None, ge=0)


class WaterHabit(BaseModel):
    activity: str = ""  # e.g. "shower", "bath", "dishwashing"
    duration_minutes: float = Field(default=0.0, ge=0)
    flow_rate_lpm: float | None = Field(default=None, ge=0)


class FoodHabit(BaseModel):
    diet_type: str = ""  # e.g. "vegetarian", "non_vegetarian", "vegan"
    meals_estimate: int | None = Field(default=None, ge=0)


class WasteHabit(BaseModel):
    waste_type: str = ""  # e.g. "plastic_bottle", "food_waste"
    quantity: float = Field(default=0.0, ge=0)
    unit: str = "items"


class HabitsData(BaseModel):
    """Structured + semantically enriched lifestyle data."""

    transport: TransportHabit = Field(default_factory=TransportHabit)
    electricity: ElectricityHabit = Field(default_factory=ElectricityHabit)
    water: WaterHabit = Field(default_factory=WaterHabit)
    food: FoodHabit = Field(default_factory=FoodHabit)
    waste: WasteHabit = Field(default_factory=WasteHabit)
    behavioral_flags: list[str] = Field(default_factory=list)
    habit_summary_text: str = ""


# ---------------------------------------------------------------------------
# carbon — populated by the Carbon Calculator node (deterministic, no LLM)
# ---------------------------------------------------------------------------


class CarbonData(BaseModel):
    emissions_by_category: dict[str, float] = Field(default_factory=dict)
    total_carbon_kg_co2: float = Field(default=0.0, ge=0)
    emission_factors_used: dict[str, float] = Field(default_factory=dict)
    calculation_metadata: dict[str, Any] = Field(default_factory=dict)  # {source, version, region}


# ---------------------------------------------------------------------------
# impact — populated by the Impact Analyzer node
# ---------------------------------------------------------------------------


class RankedContributor(BaseModel):
    category: str
    kg_co2: float = Field(ge=0)
    percentage: float = Field(ge=0, le=100)


class BenchmarkComparison(BaseModel):
    regional_avg_kg_co2: float | None = None
    global_avg_kg_co2: float | None = None
    vs_regional_pct: float | None = None
    vs_global_pct: float | None = None


class ImpactData(BaseModel):
    ranked_contributors: list[RankedContributor] = Field(default_factory=list)
    major_contributors: list[str] = Field(default_factory=list)
    benchmark_comparison: BenchmarkComparison = Field(default_factory=BenchmarkComparison)
    impact_equivalencies: list[str] = Field(default_factory=list)
    impact_narrative: str = ""


# ---------------------------------------------------------------------------
# recommendations — populated by the Recommendation Generator node
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# decision — populated by the Decision Agent node
# ---------------------------------------------------------------------------


class DecisionData(BaseModel):
    """Structured strategy and prioritization output from the Decision Agent."""

    priority_area: str = ""  # e.g. "transport", "electricity", "water", "food", "waste"
    urgency: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = "LOW"
    reason: str = ""
    strategy: str = ""
    confidence: float = Field(default=1.0, ge=0, le=1)


class InterventionCandidate(BaseModel):
    """One entry retrieved deterministically from the intervention knowledge base, before Gemini personalizes/prioritizes among the candidates."""

    action: str
    category: str
    estimated_co2_savings_kg: float = Field(ge=0)
    difficulty: Literal["easy", "medium", "hard"] = "easy"


class Recommendation(BaseModel):
    title: str
    description: str
    category: str
    estimated_impact_kg_co2: float = Field(ge=0)
    priority: int = Field(ge=1)


class RecommendationsData(BaseModel):
    candidate_interventions: list[InterventionCandidate] = Field(default_factory=list)
    personalized_recommendations: list[Recommendation] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# challenge — populated by the Challenge Generator node
# ---------------------------------------------------------------------------


class EcoChallenge(BaseModel):
    title: str = ""
    description: str = ""
    category: str = ""
    difficulty: Literal["easy", "medium", "hard"] = "easy"
    estimated_co2_savings_kg: float = Field(default=0.0, ge=0)


class ChallengeData(BaseModel):
    challenge_target_category: str = ""
    daily_eco_challenge: EcoChallenge = Field(default_factory=EcoChallenge)


# ---------------------------------------------------------------------------
# report — populated by the Report Generator node
# ---------------------------------------------------------------------------


class ReportData(BaseModel):
    sustainability_report: str = ""
    report_generated_at: datetime | None = None
    report_metadata: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# observability — cross-cutting, written by every node
# ---------------------------------------------------------------------------


class NodeExecutionRecord(BaseModel):
    node: str
    status: Literal["success", "error", "skipped"]
    duration_ms: float = Field(ge=0)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# Top-level graph state
# ---------------------------------------------------------------------------


class GraphState(TypedDict):
    """The single state object threaded through every node in the graph. Field ownership (which node writes each key) is documented in the architecture design doc, Section 4. Only ``node_execution_log``, ``errors``, and ``retry_count`` are written by more than one node — everything else has exactly one writer and needs no reducer. """

    meta: MetaInfo
    input: InputData
    habits: HabitsData
    carbon: CarbonData
    impact: ImpactData
    decision: DecisionData
    recommendations: RecommendationsData
    challenge: ChallengeData
    report: ReportData

    # Cross-cutting / observability — see reducer note in the module docstring.
    node_execution_log: Annotated[list[NodeExecutionRecord], operator.add]
    errors: Annotated[list[str], operator.add]
    retry_count: Annotated[dict[str, int], merge_dicts]

    # Sequential-only progress marker — do not write from the parallel stage.
    current_step: str


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def create_initial_state( raw_input: dict[str, Any], region: str = "global", user_id: str | None = None, ) -> GraphState:
    """Builds a fully-formed initial ``GraphState`` from the raw request payload. Every field is present with a sensible default, so no node needs to guard against missing keys on its first read. """

    return GraphState(
        meta=MetaInfo(region=region, user_id=user_id),
        input=InputData(raw_input=raw_input),
        habits=HabitsData(),
        carbon=CarbonData(),
        impact=ImpactData(),
        decision=DecisionData(),
        recommendations=RecommendationsData(),
        challenge=ChallengeData(),
        report=ReportData(),
        node_execution_log=[],
        errors=[],
        retry_count={},
        current_step="input_validator",
    )