-- AI Start Map - Database Schema
-- SQLite

CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT,
    email TEXT,
    business_type TEXT,
    ai_experience_level TEXT,
    input_mode TEXT DEFAULT 'text',
    status TEXT DEFAULT 'in_progress',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    question_key TEXT,
    question_text TEXT,
    answer_text TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE TABLE IF NOT EXISTS analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    summary TEXT,
    extracted_facts_json TEXT,
    top_3_json TEXT,
    full_result_json TEXT,
    model_used_extraction TEXT,
    model_used_recommendation TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE TABLE IF NOT EXISTS workflow_catalog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    category TEXT,
    problem TEXT,
    benefits TEXT,
    when_it_fits TEXT,
    expected_output TEXT,
    effort_level TEXT,
    value_level TEXT,
    is_quick_win BOOLEAN DEFAULT 0,
    description TEXT
);