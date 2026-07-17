"""
app/graph/builder.py
====================
Graph construction module for the ClimateSense AI Pipeline.

This module is responsible for orchestrating the execution flow of the AI pipeline
using LangGraph. It registers all processing nodes, defines the sequential execution
edges, and compiles the final state graph.
"""

import logging
from langgraph.graph import StateGraph, END
from typing import Any

# Import the centralized State definition
from app.graph.state import GraphState

# Import every node individually
from app.nodes.habit_analyzer import habit_analyzer_node
from app.nodes.carbon_calculator import carbon_calculator_node
from app.nodes.climate_impact_analyzer import climate_impact_analyzer_node
from app.nodes.decision_agent import decision_agent_node
from app.nodes.recommendation_generator import recommendation_generator_node
from app.nodes.challenge_generator import challenge_generator_node
from app.nodes.report_generator import report_generator_node

# Configure module-level logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def build_graph() -> Any:
    """
    Constructs, configures, and compiles the LangGraph state machine.

    Responsibilities:
    - Initializes the StateGraph with the central GraphState schema.
    - Registers every AI/processing node.
    - Defines the strictly sequential execution path from entry point to END.
    - Compiles the graph into an executable format.

    Returns:
        Any: The compiled and runnable LangGraph object.

    Raises:
        RuntimeError: If graph creation, node registration, edge mapping, 
                      or compilation fails.
    """
    try:
        logger.info("Graph creation started.")
        
        # 1. Initialize StateGraph
        builder: StateGraph = StateGraph(GraphState)

        # Register all nodes
        builder.add_node("habit_analyzer", habit_analyzer_node)
        builder.add_node("carbon_calculator", carbon_calculator_node)
        builder.add_node("climate_impact_analyzer", climate_impact_analyzer_node)
        builder.add_node("decision_agent", decision_agent_node)
        builder.add_node("recommendation_generator", recommendation_generator_node)
        builder.add_node("challenge_generator", challenge_generator_node)
        builder.add_node("report_generator", report_generator_node)
        logger.info("Node registration completed.")

        # 3. Register all edges (Strict Sequential Flow)
        builder.set_entry_point("habit_analyzer")
        builder.add_edge("habit_analyzer", "carbon_calculator")
        builder.add_edge("carbon_calculator", "climate_impact_analyzer")
        builder.add_edge("climate_impact_analyzer", "decision_agent")
        builder.add_edge("decision_agent", "recommendation_generator")
        builder.add_edge("recommendation_generator", "challenge_generator")
        builder.add_edge("challenge_generator", "report_generator")
        builder.add_edge("report_generator", END)
        
        logger.info("Edge registration completed.")

        # 4. Compile the graph
        compiled_graph = builder.compile()
        
        logger.info("Graph compilation successful.")
        
        return compiled_graph

    except Exception as e:
        logger.error(f"Failed to build the LangGraph workflow: {e}", exc_info=True)
        raise RuntimeError(f"Graph construction failed: {e}") from e
