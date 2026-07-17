"""
app/nodes/recommendation_generator.py
=====================================
Recommendation Generator Node for the ClimateSense AI Pipeline.

This node leverages the Gemini LLM via an external service wrapper to generate
personalized, actionable, and category-focused sustainability interventions
based on prior calculations, strategic decisions, and habits.

Constraints:
- Reads `state["decision"]`, `state["impact"]`, `state["carbon"]`, and `state["habits"]`.
- Invokes Gemini through `app.services.gemini_client.generate_recommendations`.
- Gracefully handles structural exceptions by logging into the state's `errors` channel.
- Progresses the workflow control flow token onto `challenge_generator`.
"""

import logging
from typing import Any, Dict

from app.graph.state import GraphState, RecommendationsData, Recommendation
# Architectural Contract: Import client wrapper rather than SDK directly
from app.services.gemini_client import generate_recommendations

logger = logging.getLogger(__name__)

def _build_structured_prompt(state: GraphState) -> str:
    """
    Constructs a detailed prompt grounding the recommendation generator agent 
    with upstream data context and specifying the exact required output schema fields.
    
    Args:
        state (GraphState): The current state configuration of the LangGraph execution pipeline.
        
    Returns:
        str: A highly targeted string prompt ready for execution against the Gemini client.
    """
    # Unpack necessary upstream contexts from state safely
    carbon = state.get("carbon")
    decision = state.get("decision")
    habits = state.get("habits")

    total_co2 = carbon.total_carbon_kg_co2 if carbon else 0.0
    priority_area = decision.priority_area if decision else "General Sustainability"
    urgency = decision.urgency if decision else "MEDIUM"
    strategy_text = decision.strategy if decision else "Target general high-impact actions."
    habit_summary = habits.habit_summary_text if habits else "No behavioral summary available."

    return f"""
You are the ClimateSense AI Lifestyle Interventions Architect. Your objective is to translate raw user habits and quantitative carbon footprint insights into actionable, high-impact behavioral transformations.

[CORE ARCHITECTURAL FOCUS]
Based on the provided priority target area, generate targeted lifestyle adjustments that directly counteract the user's highest emission sources.

[UPSTREAM DATA CONTEXT]
- Total Evaluated Footprint: {total_co2:.2f} kg CO2e
- Highlighted Priority Target Area: {priority_area.upper()}
- Strategic Urgency: {urgency}
- Strategic Core Objective: {strategy_text}
- Granular Behavioral Narrative: {habit_summary}

[GENERATION SPECIFICATIONS]

Generate EXACTLY 5 personalized recommendations.

Each recommendation must:

- Be specific to the user's lifestyle.
- Be realistic to start today.
- Save a measurable amount of CO₂.
- Be written in simple English.
- Be no more than 2 sentences.
- Avoid generic environmental advice.
- Prioritize the user's highest emission category.

Return ONLY valid JSON.

Each recommendation must contain exactly these fields:

{{
"title":"",
"description":"",
"category":"",
"estimated_impact_kg_co2":0.0,
"priority":1
}}

Priority must range from 1 (highest impact) to 5 (lowest).

Do not include markdown.
Do not include explanations.
Do not include extra text.
"""


def recommendation_generator_node(state: GraphState) -> Dict[str, Any]:
    """
    LangGraph Node: Recommendation Generator.
    
    Compiles context from prior state execution stages, queries Gemini via the
    delegated service interface, and securely appends the results back to GraphState.
    """
    # 1. Initialize empty data structures to guarantee safe execution returns
    personalized_list = []
    
    try:
        # 2. Build the LLM grounding context prompt
        prompt = _build_structured_prompt(state)
        
        # 3. Query Gemini via the externalized wrapper service
        # Assumed interface returns a structured dictionary or list of verified recommendation records
        llm_response = generate_recommendations(prompt)
        if not llm_response:
             raise ValueError("Gemini returned an empty response.")
        
        # 4. Parse the structured output into concrete state validation components
        if isinstance(llm_response, list):
            for item in llm_response[:5]:
                personalized_list.append(
                    Recommendation(
                        title=item.get("title", "Eco Action"),
                        description=item.get("description", "Take proactive steps to reduce footprints."),
                        category=item.get("category", getattr(state.get("decision"), "priority_area", "general")),
                        estimated_impact_kg_co2=float(item.get("estimated_impact_kg_co2", 0.0)),
                        priority=int(item.get("priority", 3))
                    )
                )
        
    except Exception as e:
        logger.error(f"Gemini client recommendation generation failure: {str(e)}")
        # Graceful handling: Append the error trace to the central error channel without halting the graph
        return {
            "recommendations": RecommendationsData(),
            "errors": [f"Recommendation Generator Node Failure: {str(e)}"],
            "current_step": "challenge_generator"
        }

    # 5. Populate the final model matching the pipeline state specifications
    recommendations_state = RecommendationsData(
        candidate_interventions=[],  # Handled by separate local knowledge-base lookups if needed
        personalized_recommendations=personalized_list
    )

    # 6. Deliver the safe state update payload
    return {
        "recommendations": recommendations_state,
        "current_step": "challenge_generator"
    }