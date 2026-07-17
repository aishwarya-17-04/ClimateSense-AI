"""
app/nodes/climate_impact_analyzer.py
====================================
Climate Impact Analyzer Node for the ClimateSense AI Pipeline.

This module reads the pre-calculated carbon emissions from the graph state
and performs a deterministic analysis. It ranks categories, calculates 
percentage contributions, determines an overall impact severity, and 
generates a purely rule-based impact summary.

Constraints adhered to in this file:
- Reads `emissions_by_category` and `total_carbon_kg_co2` from `state["carbon"]`.
- No Gemini/LLM calls.
- No carbon footprint math (only statistical percentage/ranking math).
- Populates the existing `ImpactData` model.
- Updates state and routes to the next node.
"""

from typing import Any, Dict, List

from app.graph.state import (
    GraphState,
    ImpactData,
    RankedContributor,
)


def _determine_impact_level(total_kg_co2: float) -> str:
    """
    Deterministically assigns an overall impact level based on total 
    daily estimated carbon emissions (kg CO2e).
    """
    if total_kg_co2 < 10.0:
        return "LOW"
    elif total_kg_co2 < 25.0:
        return "MEDIUM"
    elif total_kg_co2 < 40.0:
        return "HIGH"
    else:
        return "VERY_HIGH"


def _generate_impact_summary(
    ranked_list: List[RankedContributor], 
    impact_level: str, 
    total_kg_co2: float
) -> str:
    """
    Generates a clear, deterministic summary of the user's carbon footprint.
    """
    if not ranked_list or total_kg_co2 <= 0:
        return "No measurable carbon emissions were found. The overall impact level is LOW."

    highest = ranked_list[0]
    lowest = ranked_list[-1]

    # Handle edge case where all emissions are zero
    if highest.kg_co2 == 0:
        return "All categories reflect zero emissions. The overall impact level is LOW."

    return (
        f"{highest.category.capitalize()} contributes the most to the user's daily "
        f"emissions at {highest.percentage}%, while {lowest.category.capitalize()} "
        f"contributes the least at {lowest.percentage}%. "
        f"The overall carbon impact level is {impact_level}."
    )


def climate_impact_analyzer_node(state: GraphState) -> Dict[str, Any]:
    """
    LangGraph Node: Climate Impact Analyzer.
    
    Reads calculated carbon data, ranks the highest and lowest contributors,
    calculates their percentages, assigns a deterministic impact level, 
    and writes the results to the ImpactData state.
    """
    # 1. Retrieve the carbon calculations safely
    carbon_data = state.get("carbon")
    
    if hasattr(carbon_data, "emissions_by_category"):
        emissions = carbon_data.emissions_by_category
        total_carbon = carbon_data.total_carbon_kg_co2
    elif isinstance(carbon_data, dict):
        emissions = carbon_data.get("emissions_by_category", {})
        total_carbon = carbon_data.get("total_carbon_kg_co2", 0.0)
    else:
        emissions = {}
        total_carbon = 0.0

    # IMPROVED ERROR HANDLING: Halt and report if data is missing
    # Because `errors` is defined with a reducer in state.py (operator.add),
    # returning it this way appends the error safely without clobbering existing errors.
    if not emissions:
        return {
            "impact": ImpactData(),
            "errors": [
                "Climate Impact Analyzer failed: Carbon data is missing or emissions are empty."
         ],
             "current_step": "decision_agent",
    }

    ranked_list: List[RankedContributor] = []
    major_contributors: List[str] = []

    # 2. Rank every category and calculate percentage contribution
    if emissions:
        # Sort items descending based on kg_co2 value
        sorted_emissions = sorted(emissions.items(), key=lambda x: x[1], reverse=True)
        
        for category, kg_co2 in sorted_emissions:
            percentage = (kg_co2 / total_carbon * 100) if total_carbon > 0 else 0.0
            
            ranked_list.append(
                RankedContributor(
                    category=category,
                    kg_co2=round(kg_co2, 2),
                    percentage=round(percentage, 1)
                )
            )
            
            # Identify major contributors (threshold > 25% contribution as per architecture)
            if percentage > 25.0:
                major_contributors.append(category)

    # 3. Determine Overall Impact Level
    impact_level = _determine_impact_level(total_carbon)

    # 4. Generate Deterministic Summary
    summary = _generate_impact_summary(ranked_list, impact_level, total_carbon)

    # 5. Populate ImpactData model
    impact_state = ImpactData(
        ranked_contributors=ranked_list,
        major_contributors=major_contributors,
        impact_narrative=summary
    )

    # 6. Return state update
    return {
        "impact": impact_state,
        "current_step": "decision_agent",
    }