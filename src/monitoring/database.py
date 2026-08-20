import sys
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

def delete_all_rows():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """        DELETE FROM usage_logs        """
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
            operation,

            status

        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            usage.operation,

            usage.status,
        ),
    )

    connection.commit()

    connection.close()


# ============================================================
# ALTER TABLE TO ADD COLUMN DYNAMICALLY
# ============================================================

def add_column_dynamically(column_name, data_type):
    """Adds any column name and type to the table dynamically."""
    # Safety Check: Clean inputs to remove spaces or bad characters
    clean_column = "".join(c for c in column_name if c.isalnum() or c == "_")
    clean_type = "".join(c for c in data_type if c.isalnum())

    # Map common terms to valid SQLite types
    type_mapping = {
        "string": "TEXT",
        "text": "TEXT",
        "number": "INTEGER",
        "int": "INTEGER",
        "float": "REAL",
        "boolean": "INTEGER"  # SQLite uses 0 or 1 for booleans
    }

    # Convert user type to uppercase SQLite type (defaults to TEXT if unknown)
    sql_type = type_mapping.get(clean_type.lower(), "TEXT")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Build the query string dynamically
        # Replace 'tickets' with your actual table name
        query = f"ALTER TABLE usage_logs ADD COLUMN {clean_column} {sql_type}"
        
        cursor.execute(query)
        conn.commit()
        print(f"Success: Added column '{clean_column}' with type '{sql_type}'.")
    except sqlite3.OperationalError as e:
        print(f"Error: Could not add column. {e}")
    finally:
        conn.close()



# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    initialize_database()

    print("SupportPilot database initialized successfully.")

    print(f"Database location: {DB_PATH}")


# The safety guard checks the terminal command
if __name__ == "__main__":

    # Check if the user typed an extra word in the terminal
    if len(sys.argv) > 1:
        command = sys.argv[1]        
        # If they typed 'delete', run the delete function
        if command == "delete":
            delete_all_rows()
        elif command == "createdb":            
            initialize_database()
        elif command == "addcolumn":              
            if len(sys.argv) == 4:
                col_name = sys.argv[2]
                col_type = sys.argv[3]
                add_column_dynamically(col_name, col_type)
            else:
                print("Missing arguments! Format: python database.py alter_dynamic [name] [type]")            
        else:
            print(f"Unknown command: '{command}'. Try 'delete' or 'createdb'.")
    else:
        print("Please provide a command. Example: python database.py delete")