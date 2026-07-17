from app.graph.builder import build_graph
from app.graph.state import create_initial_state


def test_create_initial_state_contains_required_sections():
    state = create_initial_state(
        raw_input={
            "transport": "Bus - 12 km",
            "electricity": "Fan - 8 hours",
            "water": "10-minute shower",
            "food": "Vegetarian",
            "waste": "2 bottles",
        }
    )

    assert state["input"].raw_input["transport"] == "Bus - 12 km"
    assert state["carbon"].total_carbon_kg_co2 == 0.0
    assert state["current_step"] == "input_validator"


def test_graph_compiles():
    graph = build_graph()

    assert graph is not None
