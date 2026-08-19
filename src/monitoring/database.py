import sqlite3
from pathlib import Path

from src.monitoring.usage import LLMUsage


# ============================================================
# DATABASE PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DB_DIR = BASE_DIR / "data"

DB_PATH = DB_DIR / "supportpilot.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    DB_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)

    return connection


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS usage_logs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            request_id TEXT,
            timestamp TEXT,

            user_id TEXT,
            session_id TEXT,

            provider TEXT,
            model TEXT,

            input_tokens INTEGER DEFAULT 0,
            output_tokens INTEGER DEFAULT 0,
            total_tokens INTEGER DEFAULT 0,

            input_cost REAL DEFAULT 0,
            output_cost REAL DEFAULT 0,
            total_cost REAL DEFAULT 0,

            latency_ms REAL,

            status TEXT,
            error_type TEXT,

            retrieval_score REAL,
            handoff INTEGER DEFAULT 0
        )
        """
    )

    connection.commit()

    connection.close()


# ============================================================
# SAVE LLM USAGE
# ============================================================

def save_usage_record(usage: LLMUsage):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO usage_logs (

            request_id,
            timestamp,

            provider,
            model,

            input_tokens,
            output_tokens,
            total_tokens,

            input_cost,
            output_cost,
            total_cost,

            latency_ms,

            status

        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            usage.request_id,
            usage.timestamp.isoformat(),

            usage.provider,
            usage.model,

            usage.input_tokens,
            usage.output_tokens,
            usage.total_tokens,

            usage.input_cost,
            usage.output_cost,
            usage.total_cost,

            usage.latency_ms,

            usage.status,
        ),
    )

    connection.commit()

    connection.close()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    initialize_database()

    print("SupportPilot database initialized successfully.")

    print(f"Database location: {DB_PATH}")