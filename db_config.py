# Database Configuration for Wisespend
import mysql.connector
from mysql.connector import Error

# ─── MySQL Connection Settings ────────────────────────────────────────────────
DB_CONFIG = {
    "host": "localhost",        # Change if using remote server
    "user": "root",             # Your MySQL username
    "password": "",             # Your MySQL password (leave empty if none)
    "database": "wisespend",
    "port": 3306,
}

# ─── Connection Pool ──────────────────────────────────────────────────────────
connection_pool = None

def init_connection_pool():
    """Initialize MySQL connection pool"""
    global connection_pool
    try:
        connection_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="wisespend_pool",
            pool_size=5,
            pool_reset_session=True,
            **DB_CONFIG
        )
        print("✓ Connection pool initialized")
        return True
    except Error as e:
        print(f"✗ Failed to initialize pool: {e}")
        return False

def get_connection():
    """Get a connection from the pool"""
    try:
        if connection_pool is None:
            init_connection_pool()
        return connection_pool.get_connection()
    except Error as e:
        print(f"✗ Connection error: {e}")
        return None

def test_connection():
    """Test database connection"""
    try:
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            conn.close()
            print("✓ Database connection successful")
            return True
    except Error as e:
        print(f"✗ Database connection failed: {e}")
    return False
