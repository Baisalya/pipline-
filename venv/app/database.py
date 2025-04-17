import pyodbc
from .config import DB_CONFIG

def get_db_connection():
    try:
        conn_str = (
            f"DRIVER={{{DB_CONFIG['driver']}}};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"UID={DB_CONFIG['username']};"
            f"PWD={DB_CONFIG['password']}"
        )
        conn = pyodbc.connect(conn_str)
        print("✅ Database Connected Successfully!")
        return conn
    except Exception as e:
        raise Exception(f"❌ Database Connection Failed: {str(e)}")
