"""Recommendation engine + SHAP-based explainability."""
from __future__ import annotations
import numpy as np
from app.services.finance import (Profile, qfhs, WEIGHTS, savings_score,
                                   liquidity_score, debt_score,
                                   investment_score, resilience_score)


def recommendations(p: Profile) -> list[dict]:
    h = qfhs(p)
    c = h["components"]
    recs = []
    if c["L"] < 60:
        recs.append((1, "Build your emergency fund toward 6 months of expenses to improve liquidity."))
    if c["D"] < 60:
        recs.append((1, "Reduce outstanding debt; your debt-to-income ratio is dragging the score."))
    if c["S"] < 60:
        recs.append((2, "Raise your monthly savings rate toward 20% of income."))
    if c["I"] < 60:
        recs.append((2, "Increase investment allocation (e.g. SIP contributions) to grow long-term wealth."))
    if c["R"] < 60:
        recs.append((1, "Strengthen risk resilience by holding more liquid reserves."))
    if not recs:
        recs.append((3, "Finances are well balanced. Consider rebalancing investments annually."))
    recs.sort(key=lambda x: x[0])
    return [{"priority": pr, "text": t} for pr, t in recs]


_FN = {"S": savings_score, "L": liquidity_score, "D": debt_score,
       "I": investment_score, "R": resilience_score}


def explain(p: Profile) -> dict:
    """Exact SHAP values via additive decomposition of the linear QFHS.

    QFHS is a weighted sum of 5 component scores, so the Shapley value of
    each component equals weight_i * (component_i - baseline_i), where the
    baseline is the population-neutral score of 50.
    """
    baseline_component = 50.0
    contribs = {}
    for k, w in WEIGHTS.items():
        comp = _FN[k](p)
        contribs[k] = round(w * (comp - baseline_component), 2)
    base_value = sum(WEIGHTS[k] * baseline_component for k in WEIGHTS)
    drivers = sorted(contribs.items(), key=lambda x: x[1])
    names = {"S": "savings rate", "L": "liquidity", "D": "debt management",
             "I": "investment efficiency", "R": "risk resilience"}
    msgs = []
    for k, v in drivers:
        direction = "lowered" if v < 0 else "raised"
        msgs.append(f"{names[k].capitalize()} {direction} your score by {abs(v):.1f} points.")
    return {
        "base_value": round(base_value, 2),
        "shap_values": contribs,
        "explanations": msgs,
    }
