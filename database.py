import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "employee_db",
    "user": "postgres",
    "password": "PostGREsql",   
}


def get_connection():
    """Open and return a new database connection."""
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)


def init_db():
    """Create the employees table if it does not exist."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    id          SERIAL PRIMARY KEY,
                    name        VARCHAR(100) NOT NULL,
                    age         INTEGER NOT NULL,
                    department  VARCHAR(100) NOT NULL,
                    salary      INTEGER      NOT NULL
                );
            """)
        conn.commit()
    finally:
        conn.close()
