"""
app/nodes/habit_analyzer.py
===========================
Habit Analyzer Node for the ClimateSense AI Pipeline.

This module reads the validated raw input from the graph state, normalizes
the loosely-structured text fields into fully structured Pydantic models
(TransportHabit, ElectricityHabit, etc.), and generates a deterministic
qualitative summary and behavioral flags.

Constraints adhered to in this file:
- Reads from `GraphState`.
- Returns updated `GraphState` (returning the `habits` dictionary key).
- No carbon calculations (delegated to Carbon Calculator).
- No Gemini/LLM calls (enforced deterministic extraction).
- Follows SOLID principles and LangGraph best practices.
"""

import re
from typing import Any, Dict, List

from app.graph.state import (
    GraphState,
    HabitsData,
    TransportHabit,
    ElectricityHabit,
    WaterHabit,
    FoodHabit,
    WasteHabit,
)


def _extract_number(text: str, default: float = 0.0) -> float:
    """Helper to extract the first positive number from a string."""
    match = re.search(r'\d+(\.\d+)?', text)
    return float(match.group()) if match else default


def _parse_transport(raw_val: str) -> TransportHabit:
    """
    Parses transport strings like "Car - 20 km" into a TransportHabit.
    Assumes format: "<mode> - <distance> <unit>".
    """
    mode = "car"  # safe default
    distance = 0.0

    if "-" in raw_val:
         parts = raw_val.split("-", 1)
         mode = parts[0].strip().lower().replace(" ", "_")
         distance = _extract_number(parts[1])
    else:
             mode = raw_val.strip().lower().replace(" ", "_")
             distance = _extract_number(raw_val)

    # Normalize transport aliases
    TRANSPORT_ALIASES = {
    "bike": "bike",
    "bicycle": "bike",
    "cycle": "bike",
    "cycling": "bike",

    "car": "car",
    "auto": "car",
    "taxi": "car",
    "cab": "car",

    "bus": "bus",

    "train": "train",
    "metro": "train",

    "motorbike": "motorbike",
    "motorcycle": "motorbike",
    "scooter": "motorbike",

    "walk": "walk",
    "walking": "walk",
    "public_transport": "public_transport",
    "other": "other",}

    mode = TRANSPORT_ALIASES.get(mode, mode)

    return TransportHabit(mode=mode, distance_km=distance)


def _parse_electricity(raw_val: str) -> ElectricityHabit:
    """
    Supports:
    - AC - 6 hours
    - Fan 8 hours/day
    - 180 kWh/month
    - 250 units/month
    """

    text = raw_val.lower()

    appliance = "general"

    if "ac" in text:
        appliance = "ac"
    elif "fan" in text:
        appliance = "fan"
    elif "fridge" in text:
        appliance = "fridge"
    elif "tv" in text:
        appliance = "tv"
    elif "washing" in text:
        appliance = "washing_machine"

    number = _extract_number(text)

    # If user entered monthly electricity consumption,
    # convert it to an estimated daily usage hours.
    if "kwh" in text or "unit" in text or "units" in text:
        usage_hours = min(number / 30, 24)

    else:
        usage_hours = min(number, 24)

    return ElectricityHabit(
        appliance=appliance,
        usage_hours=usage_hours,
    )


def _parse_water(raw_val: str) -> WaterHabit:
    """
    Parses water strings like "15-minute shower" into a WaterHabit.
    """
    activity = "shower"  # default assumption
    duration = _extract_number(raw_val)

    lower_val = raw_val.lower()
    if "bath" in lower_val:
        activity = "bath"
    elif "dish" in lower_val:
        activity = "dishwashing"
    elif "laundry" in lower_val:
        activity = "laundry"
    elif "hand" in lower_val or "brush" in lower_val:
        activity = "handwashing"

    return WaterHabit(activity=activity, duration_minutes=duration)


def _parse_food(raw_val: str) -> FoodHabit:
    """
    Parses food strings like "Non Vegetarian" into a FoodHabit.
    """
    diet_type = raw_val.strip().lower().replace(" ", "_").replace("-", "_")
    return FoodHabit(diet_type=diet_type)


def _parse_waste(raw_val: str) -> WasteHabit:
    """
    Parses waste strings like "3 Plastic Bottles" into a WasteHabit.
    """
    quantity = _extract_number(raw_val)
    waste_type = "general_waste"  # default fallback

    lower_val = raw_val.lower()
    if "plastic bottle" in lower_val:
        waste_type = "plastic_bottle"
    elif "plastic bag" in lower_val:
        waste_type = "plastic_bag"
    elif "paper" in lower_val:
        waste_type = "paper"
    elif "glass" in lower_val:
        waste_type = "glass_bottle"
    elif "can" in lower_val or "aluminum" in lower_val:
        waste_type = "aluminum_can"
    elif "food" in lower_val:
        waste_type = "food_waste"

    return WasteHabit(waste_type=waste_type, quantity=quantity)


def _generate_behavioral_flags(habits: HabitsData) -> List[str]:
    """
    Deterministically generates behavioral flags based on parsed habits.
    """
    flags = []
    
    if habits.electricity.usage_hours > 5.0:
        flags.append("high_electricity_use")
    if habits.transport.distance_km > 30.0 and habits.transport.mode not in ["bike", "walk", "train"]:
        flags.append("heavy_commuter")
    if habits.food.diet_type == "non_vegetarian":
        flags.append("meat_heavy_diet")
    if habits.water.duration_minutes > 15.0:
        flags.append("high_water_consumption")
    if habits.waste.quantity > 5.0 and "plastic" in habits.waste.waste_type:
        flags.append("high_plastic_waste")
        
    return flags


def _generate_habit_summary(habits: HabitsData) -> str:
    """
    Deterministically composes a plain-text summary of the user's habits.
    """
    return (
        f"The user commutes {habits.transport.distance_km}km by {habits.transport.mode}, "
        f"runs a {habits.electricity.appliance} for {habits.electricity.usage_hours} hours, "
        f"spends {habits.water.duration_minutes} minutes on {habits.water.activity}, "
        f"follows a {habits.food.diet_type.replace('_', ' ')} diet, "
        f"and disposes of {habits.waste.quantity} units of {habits.waste.waste_type.replace('_', ' ')}."
    )


def habit_analyzer_node(state: GraphState) -> Dict[str, Any]:
    """
    LangGraph Node: Habit Analyzer.
    
    Extracts the raw user payload, normalizes it using deterministic rules,
    enriches the parsed data with flags/summaries, and updates the state.
    """
    # 1. Retrieve the raw input dictionary safely.
    input_data = state.get("input")
    if hasattr(input_data, "raw_input"):
        raw_dict = input_data.raw_input
    elif isinstance(input_data, dict):
        raw_dict = input_data.get("raw_input", {})
    else:
        raw_dict = {}

    # 2. Extract and parse individual fields
    raw_transport = str(raw_dict.get("transport", ""))
    raw_electricity = str(raw_dict.get("electricity", ""))
    raw_water = str(raw_dict.get("water", ""))
    raw_food = str(raw_dict.get("food", ""))
    raw_waste = str(raw_dict.get("waste", ""))

    structured_transport = _parse_transport(raw_transport)
    structured_electricity = _parse_electricity(raw_electricity)
    structured_water = _parse_water(raw_water)
    structured_food = _parse_food(raw_food)
    structured_waste = _parse_waste(raw_waste)

    # 3. Assemble the base HabitsData model
    habits = HabitsData(
        transport=structured_transport,
        electricity=structured_electricity,
        water=structured_water,
        food=structured_food,
        waste=structured_waste,
    )

    # 4. Generate deterministic qualitative enrichments
    habits.behavioral_flags = _generate_behavioral_flags(habits)
    habits.habit_summary_text = _generate_habit_summary(habits)

    # 5. Return the state update dictionary for LangGraph to apply
    return {
        "habits": habits,
        "current_step": "carbon_calculator",
    }