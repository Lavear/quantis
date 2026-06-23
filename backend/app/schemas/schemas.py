from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProfileIn(BaseModel):
    name: str
    age: int
    salary: float
    monthly_expenses: float
    savings: float
    investments: float
    debt: float
    assets: float
    financial_goal: float = 0
    risk_appetite: str = "moderate"


class ProfileOut(ProfileIn):
    id: int

    class Config:
        from_attributes = True


class ScenarioIn(BaseModel):
    scenario: str


class MonteCarloIn(BaseModel):
    years: int = 5
    runs: int = 1000
    target_wealth: Optional[float] = None


class ForecastIn(BaseModel):
    growth: float = 0.08
