"""
app/api/routes.py
==================
REST API routes for the ClimateSense AI Backend.

This module exposes the public-facing HTTP surface of the service. It is
intentionally thin: it validates the incoming payload, builds the initial
``GraphState``, delegates all business logic to the pre-compiled LangGraph
pipeline stored on ``request.app.state.graph``, and shapes the resulting
state into a JSON-serializable response.

Constraints adhered to in this file:
- Does not modify `app.graph.state`, `app.graph.builder`, any node, or
  `app.services.gemini_client`.
- Reuses the compiled graph attached to `app.state.graph` at startup.
- Performs no LLM calls directly; all AI/deterministic work happens inside
  the LangGraph nodes.
"""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field

from app.graph.state import create_initial_state

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

router = APIRouter(prefix="/api", tags=["ClimateSense"])


DEMO_PROFILE: Dict[str, Any] = {
    "name": "Alex Johnson",
    "email": "alex.j@example.com",
    "country": "Canada",
    "city": "Vancouver",
    "memberSince": "2025",
    "climateLevel": "Sustainability Advocate",
    "level": 12,
    "currentXP": 4500,
    "nextLevelXP": 5000,
    "streak": 30,
    "avatar": None,
}

DEMO_STATS: Dict[str, Any] = {
    "carbonScore": 85,
    "co2Saved": "245 kg",
    "challengesCompleted": 42,
    "treesSaved": 14,
    "currentRank": "#4,281",
}

DEMO_DASHBOARD: Dict[str, Any] = {
    "user": {
        "name": "Julian",
        "climateScore": 84,
        "co2Saved": "12.4",
        "streak": 12,
    },
    "chartData": [
        {"day": "Mon", "emissions": 18.2},
        {"day": "Tue", "emissions": 16.5},
        {"day": "Wed", "emissions": 14.2},
        {"day": "Thu", "emissions": 15.0},
        {"day": "Fri", "emissions": 12.8},
        {"day": "Sat", "emissions": 10.5},
        {"day": "Sun", "emissions": 9.2},
    ],
    "activities": [
        {"id": 1, "text": "Logged smart commute", "points": "+15 XP", "time": "2h ago"},
        {"id": 2, "text": "Completed Meat-free Monday", "points": "+50 XP", "time": "5h ago"},
        {"id": 3, "text": "Recycled electronics", "points": "+30 XP", "time": "1d ago"},
    ],
    "challenge": {
        "title": "Zero-Waste Lunch",
        "description": "Avoid single-use plastics today. Pack your meals using reusables.",
    },
}

DEMO_ACHIEVEMENTS: List[Dict[str, Any]] = [
    {
        "id": "a1",
        "title": "Eco Beginner",
        "description": "Calculated first footprint.",
        "icon": "seedling",
        "isUnlocked": True,
    },
    {
        "id": "a2",
        "title": "100kg Saved",
        "description": "Saved 100kg of CO2.",
        "icon": "leaf",
        "isUnlocked": True,
    },
    {
        "id": "a3",
        "title": "30-Day Streak",
        "description": "Maintained a 30-day active streak.",
        "icon": "fire",
        "isUnlocked": True,
    },
]

DEMO_GOALS: Dict[str, Any] = {
    "weekly": {"label": "Weekly CO2 Target", "current": 15, "target": 25, "unit": "kg"},
    "monthly": {"label": "Monthly Challenges", "current": 8, "target": 10, "unit": "challenges"},
    "yearly": {"label": "Yearly Trees Equivalent", "current": 14, "target": 50, "unit": "trees"},
}

DEMO_PROFILE_ACTIVITY: List[Dict[str, Any]] = [
    {"id": 1, "action": "Followed AI recommendation", "detail": "Switched to cold water laundry.", "time": "2 hours ago"},
    {"id": 2, "action": "Completed challenge", "detail": "Zero Waste Weekend.", "time": "1 day ago"},
    {"id": 3, "action": "Updated footprint", "detail": "Logged daily commute.", "time": "2 days ago"},
]

DEMO_SETTINGS: Dict[str, Any] = {
    "account": {
        "fullName": "Alex Johnson",
        "email": "alex.j@example.com",
        "phone": "+1 555-0198",
        "country": "Canada",
        "language": "English",
        "timezone": "America/Toronto",
    },
    "appearance": {
        "theme": "system",
        "accentColor": "#20c997",
    },
    "notifications": {
        "email": True,
        "push": True,
        "weeklyReports": True,
        "dailyChallenge": False,
        "aiAlerts": True,
    },
    "privacy": {
        "privateProfile": False,
        "shareWeeklyReport": True,
        "communityVisibility": True,
    },
    "ai": {
        "tone": "intermediate",
        "focus": "energy",
    },
}

DEMO_CHALLENGE: Dict[str, Any] = {
    "challenge": {
        "id": "chl-99",
        "title": "Walk Instead of Driving",
        "description": "Replace all driving trips under 2 km with walking today.",
        "category": "Transport",
        "difficulty": "Easy",
        "saving": "2.5 kg CO2",
        "xp": 50,
        "time": "20 minutes",
        "status": "pending",
    },
    "progress": {
        "streak": 14,
        "weeklyProgress": 75,
        "monthlyProgress": 42,
    },
    "motivation": "Every small action creates a greener tomorrow.",
    "achievements": [
        {"id": 1, "title": "Eco Beginner"},
        {"id": 2, "title": "Green Warrior"},
        {"id": 3, "title": "100kg CO2 Saved"},
    ],
    "history": [
        {"id": "h1", "title": "Meatless Monday", "status": "completed", "date": "Yesterday", "xp": 50},
        {"id": "h2", "title": "Unplug Devices", "status": "skipped", "date": "2 days ago", "xp": 0},
    ],
}

DEMO_WEEKLY_REPORT: Dict[str, Any] = {
    "summary": {
        "carbonScore": {"value": 88, "trend": "up", "trendValue": "+4"},
        "co2Saved": {"value": "18.5", "unit": "kg", "trend": "up", "trendValue": "+2.1kg"},
        "challenges": {"value": 5, "unit": "completed", "trend": "up", "trendValue": "+1"},
        "rating": {"value": "Excellent", "trend": "neutral", "trendValue": "Maintained"},
    },
    "charts": {
        "dailyEmissions": [
            {"day": "Mon", "emissions": 12.4},
            {"day": "Tue", "emissions": 14.1},
            {"day": "Wed", "emissions": 10.2},
            {"day": "Thu", "emissions": 11.5},
            {"day": "Fri", "emissions": 9.8},
            {"day": "Sat", "emissions": 8.4},
            {"day": "Sun", "emissions": 7.2},
        ],
        "dailyChallenges": [
            {"day": "Mon", "completed": 1},
            {"day": "Tue", "completed": 0},
            {"day": "Wed", "completed": 2},
            {"day": "Thu", "completed": 1},
            {"day": "Fri", "completed": 0},
            {"day": "Sat", "completed": 1},
            {"day": "Sun", "completed": 0},
        ],
        "emissionBreakdown": [
            {"name": "Transport", "value": 45},
            {"name": "Electricity", "value": 25},
            {"name": "Food", "value": 15},
            {"name": "Water", "value": 10},
            {"name": "Waste", "value": 5},
        ],
    },
    "insights": [
        {"type": "positive", "text": "You reduced transport emissions by 18% compared to last week."},
        {"type": "negative", "text": "Electricity usage increased slightly on Tuesday and Thursday."},
        {"type": "positive", "text": "You completed 5 eco challenges, keeping your streak alive."},
    ],
    "goals": {
        "target": 100,
        "current": 73.6,
    },
}

DEMO_LEADERBOARD: List[Dict[str, Any]] = [
    {"id": 1, "rank": 1, "name": "Elena R.", "score": 15420, "streak": 182, "badge": "Climate Hero", "avatar": None},
    {"id": 2, "rank": 2, "name": "David K.", "score": 14900, "streak": 145, "badge": "Challenge Master", "avatar": None},
    {"id": 3, "rank": 3, "name": "Sarah M.", "score": 14250, "streak": 90, "badge": "Green Influencer", "avatar": None},
    {"id": 4, "rank": 4, "name": "You (Alex)", "score": 13800, "streak": 65, "badge": "100kg Saved", "avatar": None},
]

DEMO_COMMUNITY_STATS: Dict[str, Any] = {
    "globalRank": "4,281",
    "friendsRank": "3",
    "co2SavedTogether": "12,450 kg",
    "challengesCompleted": "142",
}

DEMO_COMMUNITY_BADGES: List[Dict[str, Any]] = [
    {"id": "b1", "title": "Eco Beginner", "desc": "Completed first challenge.", "icon": "seedling", "isUnlocked": True},
    {"id": "b2", "title": "100kg Saved", "desc": "Saved 100kg of CO2.", "icon": "leaf", "isUnlocked": True},
    {"id": "b3", "title": "Challenge Master", "desc": "Complete 50 challenges.", "icon": "trophy", "isUnlocked": False},
    {"id": "b4", "title": "Green Influencer", "desc": "Invite 5 friends.", "icon": "users", "isUnlocked": False},
    {"id": "b5", "title": "Climate Hero", "desc": "Top 1% Global Rank.", "icon": "globe", "isUnlocked": False},
]

DEMO_COMMUNITY_CHALLENGES: List[Dict[str, Any]] = [
    {
        "id": 101,
        "title": "Bike to Work Week",
        "description": "Replace car commutes with cycling for 5 days.",
        "participants": 8432,
        "daysRemaining": 3,
        "reward": "500 Pts + Badge",
    },
    {
        "id": 102,
        "title": "Plastic Free Weekend",
        "description": "Avoid all single-use plastics from Friday to Sunday.",
        "participants": 12050,
        "daysRemaining": 1,
        "reward": "300 Pts",
    },
]

DEMO_COMMUNITY_ACTIVITY: List[Dict[str, Any]] = [
    {"id": 1, "user": "Alice", "action": "completed", "target": "Zero Waste Challenge", "time": "2 hours ago"},
    {"id": 2, "user": "John", "action": "reached", "target": "a 30-day streak", "time": "4 hours ago"},
]

# ---------------------------------------------------------------------------
# Impact-level thresholds
# ---------------------------------------------------------------------------
# Mirrors the deterministic bands used inside the Climate Impact Analyzer
# node (see `app/nodes/climate_impact_analyzer.py::_determine_impact_level`).
# `ImpactData` does not persist a standalone `impact_level` field on the
# graph state, so it is re-derived here from `total_carbon_kg_co2` for the
# purposes of shaping the API response only. No node or state file is
# modified to accommodate this.


def _derive_impact_level(total_kg_co2: float) -> str:
    """Derive a human-readable impact level from total daily emissions.

    Args:
        total_kg_co2: Total estimated daily carbon footprint in kg CO2e.

    Returns:
        str: One of "LOW", "MEDIUM", "HIGH", or "VERY_HIGH".
    """
    if total_kg_co2 < 10.0:
        return "LOW"
    elif total_kg_co2 < 25.0:
        return "MEDIUM"
    elif total_kg_co2 < 40.0:
        return "HIGH"
    return "VERY_HIGH"


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class AnalyzeRequest(BaseModel):
    """Incoming payload describing a user's daily lifestyle habits.

    Attributes:
        transport: Free-text description of transport habits, e.g. "Car - 20 km".
        electricity: Free-text description of electricity usage, e.g. "AC - 6 hours".
        water: Free-text description of water usage, e.g. "15-minute shower".
        food: Free-text description of diet type, e.g. "Non Vegetarian".
        waste: Free-text description of waste generation, e.g. "3 Plastic Bottles".
    """

    transport: str = Field(
        ...,
        min_length=1,
        max_length=300,
        description="Transport habit description.",
    )
    electricity: str = Field(
        ...,
        min_length=1,
        max_length=300,
        description="Electricity usage description.",
    )
    water: str = Field(
        ...,
        min_length=1,
        max_length=300,
        description="Water usage description.",
    )
    food: str = Field(
        ...,
        min_length=1,
        max_length=300,
        description="Diet/food habit description.",
    )
    waste: str = Field(
        ...,
        min_length=1,
        max_length=300,
        description="Waste generation description.",
    )


class AnalyzeResponse(BaseModel):
    """Final shaped response returned to API consumers.

    Attributes:
        total_carbon_kg_co2: Total estimated daily carbon footprint in kg CO2e.
        impact_level: Deterministic severity band for the footprint.
        recommendations: Personalized sustainability recommendations.
        daily_challenge: The single generated daily eco-challenge.
        report: The full generated sustainability report (markdown text).
    """

    total_carbon_kg_co2: float
    impact_level: str
    emissions_by_category: Dict[str, float]
    carbon_score: int
    recommendations: List[Dict[str, Any]]
    daily_challenge: Dict[str, Any]
    report: str


class SettingsUpdateRequest(BaseModel):
    category: str = Field(..., min_length=1, max_length=80)
    key: str = Field(..., min_length=1, max_length=80)
    value: Any


class ChallengeActionRequest(BaseModel):
    id: str | int = Field(..., description="Challenge identifier.")


class CommunityJoinRequest(BaseModel):
    challengeId: str | int = Field(..., description="Community challenge identifier.")


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.get("/profile")
async def get_profile() -> Dict[str, Any]:
    return DEMO_PROFILE


@router.get("/dashboard")
async def get_dashboard() -> Dict[str, Any]:
    return DEMO_DASHBOARD


@router.get("/profile/stats")
async def get_profile_stats() -> Dict[str, Any]:
    return DEMO_STATS


@router.get("/profile/achievements")
async def get_profile_achievements() -> List[Dict[str, Any]]:
    return DEMO_ACHIEVEMENTS


@router.get("/profile/goals")
async def get_profile_goals() -> Dict[str, Any]:
    return DEMO_GOALS


@router.get("/profile/activity")
async def get_profile_activity() -> List[Dict[str, Any]]:
    return DEMO_PROFILE_ACTIVITY


@router.get("/settings")
async def get_settings() -> Dict[str, Any]:
    return DEMO_SETTINGS


@router.put("/settings/update")
async def update_settings(payload: SettingsUpdateRequest) -> Dict[str, Any]:
    return {
        "message": "Setting updated.",
        "category": payload.category,
        "key": payload.key,
        "value": payload.value,
    }


@router.post("/settings/export")
async def export_settings() -> Dict[str, str]:
    return {"message": "Data export initiated."}


@router.delete("/account")
async def delete_account() -> Dict[str, str]:
    return {"message": "Account deletion simulated."}


@router.get("/challenge/today")
async def get_today_challenge() -> Dict[str, Any]:
    return DEMO_CHALLENGE


@router.post("/challenge/{action}")
async def update_challenge_status(
    action: str,
    payload: ChallengeActionRequest,
) -> Dict[str, Any]:
    allowed_actions = {"accept", "complete", "skip"}
    if action not in allowed_actions:
        raise HTTPException(status_code=400, detail="Unsupported challenge action.")

    return {
        "message": f"Challenge {action} recorded.",
        "challenge_id": payload.id,
        "status": action,
    }


@router.get("/community/leaderboard")
async def get_community_leaderboard() -> List[Dict[str, Any]]:
    return DEMO_LEADERBOARD


@router.get("/community/stats")
async def get_community_stats() -> Dict[str, Any]:
    return DEMO_COMMUNITY_STATS


@router.get("/community/badges")
async def get_community_badges() -> List[Dict[str, Any]]:
    return DEMO_COMMUNITY_BADGES


@router.get("/community/challenges")
async def get_community_challenges() -> List[Dict[str, Any]]:
    return DEMO_COMMUNITY_CHALLENGES


@router.get("/community/activity")
async def get_community_activity() -> List[Dict[str, Any]]:
    return DEMO_COMMUNITY_ACTIVITY


@router.post("/community/join")
async def join_community_challenge(payload: CommunityJoinRequest) -> Dict[str, Any]:
    return {
        "message": "Successfully joined the challenge.",
        "challenge_id": payload.challengeId,
    }


@router.get("/report/weekly")
async def get_weekly_report() -> Dict[str, Any]:
    return DEMO_WEEKLY_REPORT


@router.get("/report/download")
async def download_weekly_report() -> Response:
    content = "ClimateSense AI weekly report\n\nYour sustainability report is ready."
    return Response(
        content=content,
        media_type="text/plain",
        headers={"Content-Disposition": "attachment; filename=weekly-report.txt"},
    )


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(payload: AnalyzeRequest, request: Request) -> AnalyzeResponse:
    """Run the full ClimateSense AI pipeline for a single user submission.

    Builds the initial LangGraph state from the request payload, invokes the
    compiled graph stored on ``request.app.state.graph``, and extracts the
    carbon footprint, impact level, recommendations, daily challenge, and
    final report from the resulting state.

    Args:
        payload: The validated incoming lifestyle habit payload.
        request: The current FastAPI request, used to access the compiled
            LangGraph pipeline attached to `app.state.graph` at startup.

    Returns:
        AnalyzeResponse: The shaped analysis result for the client.

    Raises:
        HTTPException: With status code 500 if graph execution fails for
            any reason.
    """
    logger.info("Incoming /analyze request.")

    raw_input: Dict[str, Any] = {
        "transport": payload.transport,
        "electricity": payload.electricity,
        "water": payload.water,
        "food": payload.food,
        "waste": payload.waste,
    }

    initial_state = create_initial_state(raw_input=raw_input)

    try:
        logger.info("Graph execution started.")
        final_state = await request.app.state.graph.ainvoke(initial_state)
        logger.info("Graph execution finished.")
    except Exception as exc:
        logger.error("Graph execution failed: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="ClimateSense AI pipeline execution failed. Please try again.",
        ) from exc

    try:
        carbon = final_state.get("carbon")
        recommendations_data = final_state.get("recommendations")
        challenge_data = final_state.get("challenge")
        report_data = final_state.get("report")

        total_carbon_kg_co2 = carbon.total_carbon_kg_co2 if carbon else 0.0
        emissions_by_category = carbon.emissions_by_category if carbon else {}
        impact_level = _derive_impact_level(total_carbon_kg_co2)
        carbon_score = max(0, min(100, round(100 - total_carbon_kg_co2 * 2)))

        recommendations: List[Dict[str, Any]] = []
        if recommendations_data and recommendations_data.personalized_recommendations:
            recommendations = [
                rec.model_dump()
                for rec in recommendations_data.personalized_recommendations
            ]

        daily_challenge: Dict[str, Any] = {}
        if challenge_data and challenge_data.daily_eco_challenge:
            daily_challenge = challenge_data.daily_eco_challenge.model_dump()

        report_text = report_data.sustainability_report if report_data else ""

    except Exception as exc:
        logger.error(
            "Failed to extract pipeline results from graph state: %s",
            exc,
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to parse ClimateSense AI pipeline results.",
        ) from exc

    return AnalyzeResponse(
        total_carbon_kg_co2=total_carbon_kg_co2,
        impact_level=impact_level,
        emissions_by_category=emissions_by_category,
        carbon_score=carbon_score,
        recommendations=recommendations,
        daily_challenge=daily_challenge,
        report=report_text,
    )
