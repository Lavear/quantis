from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import current_user
from app.core.security import hash_password, verify_password, create_access_token
from app.models.models import (User, FinancialProfile, ScenarioResult,
                               SimulationRun)
from app.schemas.schemas import (UserCreate, Token, ProfileIn, ProfileOut,
                                 ScenarioIn, MonteCarloIn, ForecastIn)
from app.services.finance import (Profile, qfhs, simulate_scenario, SCENARIOS,
                                  monte_carlo, forecast_compound, risk_resilience)
from app.services.explain import recommendations, explain

router = APIRouter()


def _profile_obj(fp: FinancialProfile) -> Profile:
    return Profile(age=fp.age, salary=fp.salary,
                   monthly_expenses=fp.monthly_expenses, savings=fp.savings,
                   investments=fp.investments, debt=fp.debt, assets=fp.assets)


def _get_fp(user: User, db: Session) -> FinancialProfile:
    fp = db.query(FinancialProfile).filter_by(user_id=user.id).first()
    if not fp:
        raise HTTPException(404, "No financial profile. POST /profile first.")
    return fp


@router.post("/register", response_model=Token)
def register(body: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(400, "Email already registered")
    user = User(email=body.email, hashed_password=hash_password(body.password))
    db.add(user); db.commit()
    return Token(access_token=create_access_token(user.email))


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Bad credentials")
    return Token(access_token=create_access_token(user.email))


@router.post("/profile", response_model=ProfileOut)
def upsert_profile(body: ProfileIn, user: User = Depends(current_user),
                   db: Session = Depends(get_db)):
    fp = db.query(FinancialProfile).filter_by(user_id=user.id).first()
    if fp:
        for k, v in body.model_dump().items():
            setattr(fp, k, v)
    else:
        fp = FinancialProfile(user_id=user.id, **body.model_dump())
        db.add(fp)
    db.commit(); db.refresh(fp)
    return fp


@router.get("/dashboard")
def dashboard(user: User = Depends(current_user), db: Session = Depends(get_db)):
    fp = _get_fp(user, db)
    p = _profile_obj(fp)
    h = qfhs(p)
    net_worth = fp.savings + fp.investments + fp.assets - fp.debt
    return {
        "name": fp.name,
        "net_worth": round(net_worth, 2),
        "savings": fp.savings,
        "investments": fp.investments,
        "debt": fp.debt,
        "qfhs": h,
        "months_survival": round(risk_resilience(p), 1),
    }


@router.post("/calculate-qfhs")
def calc_qfhs(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return qfhs(_profile_obj(_get_fp(user, db)))


@router.post("/simulate-scenario")
def scenario(body: ScenarioIn, user: User = Depends(current_user),
             db: Session = Depends(get_db)):
    fp = _get_fp(user, db)
    p = _profile_obj(fp)
    if body.scenario == "all":
        return {"results": [simulate_scenario(p, s) for s in SCENARIOS]}
    if body.scenario not in SCENARIOS:
        raise HTTPException(400, f"Unknown scenario. Options: {SCENARIOS + ['all']}")
    res = simulate_scenario(p, body.scenario)
    db.add(ScenarioResult(profile_id=fp.id, scenario=body.scenario, result=res))
    db.commit()
    return res


@router.post("/monte-carlo")
def mc(body: MonteCarloIn, user: User = Depends(current_user),
       db: Session = Depends(get_db)):
    fp = _get_fp(user, db)
    res = monte_carlo(_profile_obj(fp), years=body.years, runs=body.runs,
                      target_wealth=body.target_wealth or fp.financial_goal or None)
    db.add(SimulationRun(profile_id=fp.id, kind="monte_carlo", result=res))
    db.commit()
    return res


@router.post("/forecast")
def forecast(body: ForecastIn, user: User = Depends(current_user),
             db: Session = Depends(get_db)):
    fp = _get_fp(user, db)
    p = _profile_obj(fp)
    res = forecast_compound(p, growth=body.growth)
    try:
        from app.services.ml_forecast import forecast_rf
        rf = forecast_rf(p)
    except Exception:
        rf = None
    db.add(SimulationRun(profile_id=fp.id, kind="forecast", result=res))
    db.commit()
    return {"forecast": res, "random_forest": rf}


@router.get("/recommendations")
def recs(user: User = Depends(current_user), db: Session = Depends(get_db)):
    p = _profile_obj(_get_fp(user, db))
    return {"recommendations": recommendations(p), "explainability": explain(p)}
