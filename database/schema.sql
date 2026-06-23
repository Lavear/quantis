-- Quantis PostgreSQL schema
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS financial_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR,
    age INTEGER,
    salary FLOAT,
    monthly_expenses FLOAT,
    savings FLOAT,
    investments FLOAT,
    debt FLOAT,
    assets FLOAT,
    financial_goal FLOAT,
    risk_appetite VARCHAR
);

CREATE TABLE IF NOT EXISTS financial_snapshots (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER REFERENCES financial_profiles(id) ON DELETE CASCADE,
    net_worth FLOAT, qfhs FLOAT, months_survival FLOAT,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS scenario_results (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER REFERENCES financial_profiles(id) ON DELETE CASCADE,
    scenario VARCHAR, result JSONB, created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS risk_assessments (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER REFERENCES financial_profiles(id) ON DELETE CASCADE,
    months_survival FLOAT, rating VARCHAR, created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER REFERENCES financial_profiles(id) ON DELETE CASCADE,
    text VARCHAR, priority INTEGER, created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS simulation_runs (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER REFERENCES financial_profiles(id) ON DELETE CASCADE,
    kind VARCHAR, result JSONB, created_at TIMESTAMP DEFAULT now()
);
