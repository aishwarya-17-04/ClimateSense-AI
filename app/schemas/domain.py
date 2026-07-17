from typing import List

from pydantic import BaseModel, ConfigDict, EmailStr, Field

class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=120)

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    is_active: bool

class CarbonInput(BaseModel):
    transport_miles: float = Field(..., ge=0)
    electricity_kwh: float = Field(..., ge=0)
    meat_meals_per_week: int = Field(..., ge=0)

class AIRecommendation(BaseModel):
    category: str
    advice: str
    impact: str

class CarbonAnalysisResponse(BaseModel):
    total_emissions_kg: float
    recommendations: List[AIRecommendation]
    daily_challenge: str
    report_summary: str
