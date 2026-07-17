"""
app/nodes/report_generator.py
=============================
Report Generator Node for the ClimateSense AI Pipeline.

This node leverages the Gemini LLM via an external service wrapper to generate
a final, comprehensive, and motivational sustainability report summarizing all
calculated metrics, strategic targets, recommendations, and active daily challenges.

Constraints:
- Reads all prior states from GraphState.
- Invokes Gemini through `app.services.gemini_client.generate_report`.
- Sets the `report_generated_at` timestamp using current UTC time.
- Gracefully handles exceptions by logging into the state's `errors` channel.
- Advances `current_step` to the ultimate step: "completed".
"""

from datetime import datetime, timezone
import logging
from typing import Any, Dict

from app.graph.state import GraphState, ReportData
from app.services.gemini_client import generate_report

logger = logging.getLogger(__name__)


def _build_report_prompt(state: GraphState) -> str:
    """
    Constructs a highly descriptive prompt incorporating all upstream context
    to ground Gemini into compiling an insightful and encouraging final report.
    """
    habits = state.get("habits")
    carbon = state.get("carbon")
    impact = state.get("impact")
    decision = state.get("decision")
    recommendations_data = state.get("recommendations")
    challenge_data = state.get("challenge")

    # Safely unpack carbon and impact details
    total_co2 = carbon.total_carbon_kg_co2 if carbon else 0.0
    emissions_breakdown = ""
    if carbon and carbon.emissions_by_category:
        emissions_breakdown = "\n".join(
            [f"- {cat}: {val:.2f} kg CO2e" for cat, val in carbon.emissions_by_category.items()]
        )

    major_contributors = ", ".join(impact.major_contributors) if impact and impact.major_contributors else "None"
    impact_narrative = impact.impact_narrative if impact else "No footprint narrative available."
    
    # Strategic directives
    priority_area = decision.priority_area if decision else "General Sustainability"
    urgency = decision.urgency if decision else "LOW"
    strategy_text = decision.strategy if decision else ""

    # Unpack lifestyle habits and interventions
    habit_summary = habits.habit_summary_text if habits else "No habit breakdown available."
    
    recs_text = ""
    if recommendations_data and recommendations_data.personalized_recommendations:
        recs_text = "\n".join(
            [f"- [{rec.category.upper()}] {rec.title}: {rec.description} (Priority {rec.priority})"
             for rec in recommendations_data.personalized_recommendations]
        )

    # Active daily challenge details
    challenge_text = "No daily challenge assigned."
    ch = challenge_data.daily_eco_challenge if challenge_data else None

    if isinstance(ch, dict):
        ch_title = ch.get("title", "Eco Action")
        ch_desc = ch.get("description", "")
        ch_diff = ch.get("difficulty", "easy")
        ch_savings = ch.get("estimated_co2_savings_kg", 0.0)
    elif ch and getattr(ch, "title", ""):
        ch_title = ch.title
        ch_desc = ch.description
        ch_diff = ch.difficulty
        ch_savings = ch.estimated_co2_savings_kg
    else:
        ch_title = ch_desc = ch_diff = None
        ch_savings = None

    if ch_title:
        challenge_text = (
            f"Title: {ch_title}\n"
            f"Description: {ch_desc}\n"
            f"Difficulty: {ch_diff}\n"
            f"Estimated Daily Savings: {ch_savings} kg CO2"
        )


    return f"""
You are the ClimateSense AI Master Sustainability Architect. Your task is to synthesize all calculated metrics and agent assessments into a comprehensive, highly personalized, and friendly Climate Action Report.

[UPSTREAM DATA CONTEXT]
- Total Footprint: {total_co2:.2f} kg CO2e
- Category Emissions Breakdown:
{emissions_breakdown}
- Highlighted Major Contributors: {major_contributors}
- Overall Quantitative Assessment: {impact_narrative}
- Strategic Focus Target: {priority_area.upper()} (Urgency: {urgency})
- Tactical Plan: {strategy_text}
- User Behavioral Overview: {habit_summary}
- Tailored Lifestyle Interventions:
{recs_text}
- Target Daily Challenge:
{challenge_text}

[REPORT GENERATION INSTRUCTIONS]

Write a concise sustainability report.

The report should be around 150–250 words.

Include exactly:

1. Brief summary of today's footprint.

2. Biggest contributor.

3. Top 3 actions the user should take.

4. Mention today's eco challenge.

5. End with one short motivational paragraph.

Use friendly and encouraging language.

Return ONLY JSON.

{{
"main_report":"",
"motivational_closing":"",
"progress_summary":""
}}

Do not use markdown.

Do not use bullet symbols unless they are inside progress_summary.

Do not include any text outside the JSON.   
"""


def report_generator_node(state: GraphState) -> Dict[str, Any]:
    """
    LangGraph Node: Report Generator.
    
    Gathers all calculated parameters and text summaries across the entire state history, 
    compiles a grounding prompt context, fetches the synthesized final analysis via 
    the Gemini client wrapper, and registers a unified ReportData summary back into state.
    """
    try:
        # 1. Capture the exact generation timestamp in UTC
        generation_time = datetime.now(timezone.utc)
        
        # 2. Build the aggregate grounding instructions context
        prompt = _build_report_prompt(state)
        
        # 3. Query Gemini using the externalized application wrapper service
        report_response = generate_report(prompt)
        
        # 4. Extract text narratives from structured return payload
        if isinstance(report_response, dict):
            main_report = report_response.get("main_report", "Your final sustainability report configuration is complete.")
            motivational_closing = report_response.get("motivational_closing", "Every step matters. Let's make an impact today!")
            progress_summary = report_response.get("progress_summary", "Report compiled successfully.")
        else:
            raise ValueError("Gemini client returned an invalid payload structure for final report.")

        # Combine the distinct narrative components into a single formatted markdown string
        full_report = (
            f"# Sustainability Report\n\n"
            f"{main_report}\n\n"
            f"---\n\n"
            f"## Progress Summary\n\n"
            f"{progress_summary}\n\n"
            f"---\n\n"
            f"## Motivation\n\n"
            f"{motivational_closing}"
        )

        # 5. Build structured diagnostic metadata mapping
        metadata_payload = {
            "model_used": "Gemini Ultra/Flash Wrapper",
            "report_version": "1.1.0",
            "generation_timestamp_iso": generation_time.isoformat()
        }

        # 6. Construct Pydantic ReportData matching actual schema constraints
        report_state = ReportData(
            sustainability_report=full_report,
            report_generated_at=generation_time,
            report_metadata=metadata_payload
        )

    except Exception as e:
        logger.error("Report Generator Node Runtime Failure: %s", str(e), exc_info=True)
        # Graceful handling: write structural fallback and capture trace into error channel without disrupting runtime graph
        return {
            "report": ReportData(),
            "errors": [f"Report Generator Node Failure: {str(e)}"],
            "current_step": "completed"
        }

    # 7. Deliver full state change payload routing out to compilation endpoint
    return {
        "report": report_state,
        "current_step": "completed"
    }
