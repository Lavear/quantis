from sqlalchemy import (Column, Integer, String, Float, ForeignKey,
                        DateTime, JSON, func)
from sqlalchemy.orm import relationship
from app.db.session import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    profile = relationship("FinancialProfile", back_populates="user",
                           uselist=False, cascade="all, delete-orphan")


class FinancialProfile(Base):
    __tablename__ = "financial_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    name = Column(String)
    age = Column(Integer)
    salary = Column(Float)              # annual
    monthly_expenses = Column(Float)
    savings = Column(Float)
    investments = Column(Float)
    debt = Column(Float)
    assets = Column(Float)
    financial_goal = Column(Float)
    risk_appetite = Column(String)
    user = relationship("User", back_populates="profile")
    snapshots = relationship("FinancialSnapshot", cascade="all, delete-orphan")


class FinancialSnapshot(Base):
    __tablename__ = "financial_snapshots"
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("financial_profiles.id"))
    net_worth = Column(Float)
    qfhs = Column(Float)
    months_survival = Column(Float)
    created_at = Column(DateTime, server_default=func.now())


class ScenarioResult(Base):
    __tablename__ = "scenario_results"
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("financial_profiles.id"))
    scenario = Column(String)
    result = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("financial_profiles.id"))
    months_survival = Column(Float)
    rating = Column(String)
    created_at = Column(DateTime, server_default=func.now())


class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("financial_profiles.id"))
    text = Column(String)
    priority = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())


class SimulationRun(Base):
    __tablename__ = "simulation_runs"
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("financial_profiles.id"))
    kind = Column(String)           # monte_carlo / forecast
    result = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())
