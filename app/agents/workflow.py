from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.core.config import settings

# 1. Define the State
class CarbonState(TypedDict):
    input_data: dict
    total_emissions: float
    analysis_context: str
    recommendations: List[dict]
    challenge: str
    report: str

llm = ChatGoogleGenerativeAI(
    model=settings.GEMINI_MODEL,
    google_api_key=settings.GOOGLE_API_KEY,
    temperature=0.2,
)

# 2. Nodes
def analyze_carbon(state: CarbonState) -> dict:
    """Calculates basic emissions based on standardized formulas."""
    data = state["input_data"]
    transport = data.get("transport_miles", 0) * 0.404 # kg CO2 per mile
    energy = data.get("electricity_kwh", 0) * 0.385 # kg CO2 per kWh
    food = data.get("meat_meals_per_week", 0) * 3.3 # kg CO2 per meal
    
    total = transport + energy + food
    context = f"Transport: {transport}kg, Energy: {energy}kg, Food: {food}kg."
    
    return {"total_emissions": total, "analysis_context": context}

def generate_recommendations(state: CarbonState) -> dict:
    prompt = PromptTemplate.from_template(
        "Based on these emissions: {context}. Total: {total}. "
        "Provide 3 personalized, actionable sustainability recommendations. "
        "Format as strict JSON: [{{'category': 'string', 'advice': 'string', 'impact': 'High/Medium/Low'}}]"
    )
    chain = prompt | llm | JsonOutputParser()
    res = chain.invoke({"context": state["analysis_context"], "total": state["total_emissions"]})
    return {"recommendations": res}

def create_challenge(state: CarbonState) -> dict:
    prompt = PromptTemplate.from_template(
        "Based on the recommendations: {recs}. Create ONE simple, achievable daily eco-challenge for the user today. "
        "Return just the string description of the challenge."
    )
    chain = prompt | llm 
    res = chain.invoke({"recs": state["recommendations"]})
    return {"challenge": res.content}

def generate_report(state: CarbonState) -> dict:
    prompt = PromptTemplate.from_template(
        "Summarize the user's carbon footprint ({total} kg) and today's challenge ({challenge}) into a brief, encouraging 2-sentence report."
    )
    chain = prompt | llm
    res = chain.invoke({"total": state["total_emissions"], "challenge": state["challenge"]})
    return {"report": res.content}

# 3. Build Graph
workflow = StateGraph(CarbonState)
workflow.add_node("analyze", analyze_carbon)
workflow.add_node("recommend", generate_recommendations)
workflow.add_node("create_challenge", create_challenge)
workflow.add_node("generate_report", generate_report)

workflow.set_entry_point("analyze")
workflow.add_edge("analyze", "recommend")
workflow.add_edge("recommend", "create_challenge")
workflow.add_edge("create_challenge", "generate_report")
workflow.add_edge("generate_report", END)

carbon_app = workflow.compile()
