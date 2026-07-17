from app.nodes.habit_analyzer import habit_analyzer_node
from app.graph.state import create_initial_state
from app.nodes.report_generator import _build_report_prompt


def test_habit_analyzer_populates_habits():
    state = create_initial_state(
        raw_input={
            "transport": "Car - 20 km",
            "electricity": "AC - 6 hours",
            "water": "15-minute shower",
            "food": "Vegetarian",
            "waste": "1 kg plastic",
        }
    )

    update = habit_analyzer_node(state)

    assert "habits" in update
    assert update["habits"].transport.distance_km == 20
    assert update["habits"].electricity.usage_hours == 6


def test_report_prompt_handles_missing_challenge():
    state = create_initial_state(
        raw_input={
            "transport": "Bus - 12 km",
            "electricity": "Fan - 8 hours",
            "water": "10-minute shower",
            "food": "Vegetarian",
            "waste": "2 bottles",
        }
    )

    prompt = _build_report_prompt(state)

    assert "No daily challenge assigned." in prompt
