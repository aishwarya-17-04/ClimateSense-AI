import pytest
from pydantic import ValidationError

from app.api.routes import AnalyzeRequest, _derive_impact_level
from app.main import create_app


def test_app_registers_core_routes():
    app = create_app()
    paths = {route.path for route in app.routes}

    assert "/api/analyze" in paths
    assert "/api/profile" in paths
    assert "/api/profile/goals" in paths
    assert "/api/profile/activity" in paths
    assert "/api/settings" in paths
    assert "/api/challenge/today" in paths
    assert "/api/community/stats" in paths
    assert "/api/community/badges" in paths
    assert "/api/community/leaderboard" in paths
    assert "/api/report/weekly" in paths
    assert "/api/dashboard" in paths
    assert "/api/users/me" in paths
    assert "/api/users/me/settings" in paths
    assert "/api/carbon/challenge/today" in paths
    assert "/api/carbon/challenge/complete/{challenge_id}" in paths


def test_analyze_request_accepts_expected_payload():
    payload = AnalyzeRequest(
        transport="Car - 20 km",
        electricity="AC - 6 hours",
        water="15-minute shower",
        food="Vegetarian",
        waste="1 kg plastic",
    )

    assert payload.transport == "Car - 20 km"
    assert payload.food == "Vegetarian"


def test_analyze_request_rejects_empty_fields():
    with pytest.raises(ValidationError):
        AnalyzeRequest(
            transport="",
            electricity="AC - 6 hours",
            water="15-minute shower",
            food="Vegetarian",
            waste="1 kg plastic",
        )


def test_impact_level_thresholds():
    assert _derive_impact_level(5.0) == "LOW"
    assert _derive_impact_level(10.0) == "MEDIUM"
    assert _derive_impact_level(25.0) == "HIGH"
    assert _derive_impact_level(40.0) == "VERY_HIGH"


def test_frontend_connection_routes_return_expected_shapes():
    app = create_app()
    routes = {route.path: route for route in app.routes}

    assert routes["/api/profile"].endpoint is not None
    assert routes["/api/settings"].endpoint is not None
    assert routes["/api/report/weekly"].endpoint is not None
    assert routes["/api/dashboard"].endpoint is not None
    assert routes["/api/community/stats"].endpoint is not None
