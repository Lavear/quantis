"""Generate 10,000 synthetic users for Quantis. Outputs dataset/users.csv"""
import numpy as np, pandas as pd
from faker import Faker

N = 10_000
fake = Faker("en_IN")
rng = np.random.default_rng(42)


def main(n=N, out="users.csv"):
    age = rng.integers(22, 60, n)
    # salary correlated with age (INR annual)
    salary = np.round((300000 + (age - 22) * 35000) *
                      rng.lognormal(0, 0.35, n), -3)
    monthly_expenses = np.round(salary / 12 * rng.uniform(0.35, 0.85, n), -2)
    savings = np.round(salary * rng.uniform(0.05, 1.5, n), -3)
    investments = np.round(salary * rng.uniform(0.0, 3.0, n), -3)
    debt = np.round(salary * rng.uniform(0.0, 1.2, n), -3)
    assets = np.round(salary * rng.uniform(0.0, 5.0, n), -3)
    goal = np.round((savings + investments) * rng.uniform(1.5, 4.0, n), -3)
    risk = rng.choice(["conservative", "moderate", "aggressive"], n,
                      p=[0.3, 0.5, 0.2])

    df = pd.DataFrame({
        "name": [fake.name() for _ in range(n)],
        "age": age, "salary": salary, "monthly_expenses": monthly_expenses,
        "savings": savings, "investments": investments, "debt": debt,
        "assets": assets, "financial_goal": goal, "risk_appetite": risk,
    })
    df.to_csv(out, index=False)
    print(f"Wrote {len(df)} rows -> {out}")
    return df


if __name__ == "__main__":
    main()
