"""
app/nodes/decision_agent.py
===========================
Decision Agent Node for the ClimateSense AI Pipeline.

This node performs deterministic, rule-based strategic reasoning to identify the 
primary target lifestyle category (priority area) and its urgency level.
It reads from the existing carbon, habits, and impact states and populates the
newly introduced DecisionData model.

Constraints:
- Reads `state["impact"]`, `state["carbon"]`, and `state["habits"]`.
- Purely rule-based and deterministic logic (No Gemini/LLM, no carbon arithmetic).
- Returns the structural updates targeting the `decision` key.
- Handles missing or empty impact data gracefully by emitting graph errors.
"""

from typing import Any, Dict

from app.graph.state import GraphState, DecisionData


def _determine_urgency(highest_percentage: float) -> str:
    """
    Deterministically determines the strategy urgency level based on the highest 
    contributor's percentage weight.
    """
    if highest_percentage > 50.0:
        return "CRITICAL"
    elif highest_percentage > 35.0:
        return "HIGH"
    elif highest_percentage > 20.0:
        return "MEDIUM"
    return "LOW"


def decision_agent_node(state: GraphState) -> Dict[str, Any]:
    """
    LangGraph Node: Decision Agent.
    
    Performs deterministic prioritization and strategy selection. Evaluates category 
    rankings from ImpactData to build an action roadmap for downstream execution.
    """
    # 1. Retrieve prior node metrics from state safely
    impact_data = state.get("impact")
    
    if hasattr(impact_data, "ranked_contributors"):
        ranked = impact_data.ranked_contributors
    elif isinstance(impact_data, dict):
        ranked = impact_data.get("ranked_contributors", [])
    else:
        ranked = []

    # 2. ERROR HANDLING: Check if ImpactData metrics are missing or empty
    if not ranked:
        return {
            "decision": DecisionData(),
            "errors": ["Decision Agent: Impact analysis missing."],
            "current_step": "recommendation_generator",
        }

    # 3. Analyze the highest contributor to establish focus area details
    highest_contributor = ranked[0]
    primary_focus = highest_contributor.category.lower().strip()
    highest_pct = highest_contributor.percentage

    # 4. Process deterministic mapping rules
    urgency_level = _determine_urgency(highest_pct)
    reasoning = f"{primary_focus.capitalize()} contributes {highest_pct}% of today's emissions."
    strategy_plan = f"Focus recommendations on {primary_focus} before suggesting improvements in other lifestyle categories."
    
    # As this is a pure rule-based module utilizing programmatic constraints, confidence is absolute (1.0)
    strategy_confidence = 1.0

    # 5. Construct and populate the DecisionData object
    decision_data = DecisionData(
        priority_area=primary_focus,
        urgency=urgency_level,
        reason=reasoning,
        strategy=strategy_plan,
        confidence=strategy_confidence
    )

    # 6. Route structural adjustments out to the execution state
    return {
        "decision": decision_data,
        "current_step": "recommendation_generator",
    } 