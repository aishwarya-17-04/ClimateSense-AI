"""
app/nodes/challenge_generator.py
================================
Challenge Generator Node for the ClimateSense AI Pipeline.

This node leverages the Gemini LLM via an external service wrapper to generate
exactly ONE personalized, actionable, daily eco-challenge based on the strategic 
decisions, user habits, and high-priority recommendations discovered upstream.

Constraints:
- Reads `state["decision"]`, `state["recommendations"]`, and `state["habits"]`.
- Invokes Gemini through `app.services.gemini_client.generate_daily_challenge`.
- Gracefully handles exceptions by logging into the state's `errors` channel.
- Progresses the workflow control flow token onto `report_generator`.
"""

import logging
from typing import Any, Dict

from app.graph.state import GraphState, ChallengeData, EcoChallenge
from app.services.gemini_client import generate_daily_challenge

logger = logging.getLogger(__name__)


def _build_challenge_prompt(state: GraphState) -> str:
    """
    Constructs a highly structured instruction prompt using context from prior 
    nodes to ensure Gemini creates an achievable daily challenge matching the 
    user's target focus.
    """
    habits = state.get("habits")
    decision = state.get("decision")
    recommendations_data = state.get("recommendations")

    # Extract priority context from upstream nodes
    priority_area = decision.priority_area if decision else "transport"
    urgency = decision.urgency if decision else "LOW"
    habit_summary = habits.habit_summary_text if habits else "No habit breakdown available."

    # Identify the highest priority recommendation to ground the challenge
    top_rec_title = "General Carbon Reduction Action"
    top_rec_desc = "Adopt sustainable practices in daily activities."
    
    if recommendations_data and recommendations_data.personalized_recommendations:
        # Sort recommendations to find priority 1 or highest rank
        sorted_recs = sorted(
            recommendations_data.personalized_recommendations, 
            key=lambda x: x.priority
        )
        if sorted_recs:
            top_rec_title = sorted_recs[0].title
            top_rec_desc = sorted_recs[0].description

    return f"""
You are the ClimateSense AI Behavioral Modification Coach. Your task is to generate exactly ONE highly personalized, realistic, motivating, and gamified daily eco-challenge that the user can fully complete within the next 24 hours.

[USER CONTEXT]
- Strategic Priority Area: {priority_area.upper()} (The challenge MUST target this vertical)
- Strategic Urgency Level: {urgency}
- User Habits Grounding: {habit_summary}
- Target Seed Recommendation: "{top_rec_title}" - {top_rec_desc}

[CHALLENGE REQUIREMENTS]

Generate ONE fun daily eco challenge.

The challenge should:

- Take less than one day.
- Be achievable by a college student.
- Match the user's highest carbon emission category.
- Have a motivating title.
- Explain WHY it matters.
- Estimate realistic CO₂ savings.

Return ONLY JSON.

{{
"title":"",
"description":"",
"category":"",
"difficulty":"easy",
"estimated_co2_savings_kg":0.0
}}

No markdown.
No explanations.
No extra text.
"""


def challenge_generator_node(state: GraphState) -> Dict[str, Any]:
    """
    LangGraph Node: Challenge Generator.
    
    Gathers context from prior execution steps, fetches a daily tailored challenge 
    via the Gemini service provider wrapper, and commits it into ChallengeData.
    """
    try:
        # 1. Compile the grounding prompt context
        prompt = _build_challenge_prompt(state)
        
        # 2. Invoke the designated Gemini helper client function
        challenge_response = generate_daily_challenge(prompt)
        
        # 3. Parse and structure the response dictionary into Pydantic models
        if isinstance(challenge_response, dict):
            # Construct a formal EcoChallenge Pydantic instance directly
            eco_challenge = EcoChallenge(
                title=challenge_response.get("title", "Eco Step Today"),
                description=challenge_response.get("description", "Take a proactive climate action step today."),
                category=challenge_response.get("category", getattr(state.get("decision"), "priority_area", "general")),
                difficulty=challenge_response.get("difficulty", "easy"),
                estimated_co2_savings_kg=float(challenge_response.get("estimated_co2_savings_kg", 0.0))
            )
            
            # Populate ChallengeData with the concrete Pydantic object
            challenge_state = ChallengeData(
                challenge_target_category=eco_challenge.category,
                daily_eco_challenge=eco_challenge
            )
        else:
            raise ValueError("Gemini client returned an invalid data format for daily challenge.")

    except Exception as e:
        logger.error(f"Challenge Generator Node Failure: {str(e)}")
        # Safe structural fallback: register error trace to state without crashing execution path
        return {
            "challenge": ChallengeData(),
            "errors": [f"Challenge Generator Node Failure: {str(e)}"],
            "current_step": "report_generator"
        }

    # 4. Return target dictionary update state
    return {
        "challenge": challenge_state,
        "current_step": "report_generator"
    }
