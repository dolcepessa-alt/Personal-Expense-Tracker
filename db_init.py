# Database Schema Initialization for Wisespend
import mysql.connector
from mysql.connector import Error
from db_config import DB_CONFIG

def create_database():
    """Create the wisespend database if it doesn't exist"""
    try:
        # Connect without specifying database
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            port=DB_CONFIG["port"]
        )
        cursor = conn.cursor()
        
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        print(f"✓ Database '{DB_CONFIG['database']}' ensured")
        
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print(f"✗ Error creating database: {e}")
        return False

def create_tables():
    """Create all necessary tables"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                currency VARCHAR(50) DEFAULT 'Ghana Cedi',
                currency_symbol VARCHAR(5) DEFAULT '₵',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        print("✓ Users table created")
        
        # Transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                type ENUM('income', 'expense') NOT NULL,
                description VARCHAR(255) NOT NULL,
                amount DECIMAL(12, 2) NOT NULL,
                category VARCHAR(100),
                date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_date (user_id, date)
            )
        """)
        print("✓ Transactions table created")
        
        # Budgets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                category VARCHAR(100) NOT NULL,
                limit_amount DECIMAL(12, 2) NOT NULL,
                spent_amount DECIMAL(12, 2) DEFAULT 0,
                month_year VARCHAR(7) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_budget (user_id, category, month_year),
                INDEX idx_user_month (user_id, month_year)
            )
        """)
        print("✓ Budgets table created")
        
        # Account summary table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS account_summary (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL UNIQUE,
                balance DECIMAL(12, 2) DEFAULT 0,
                total_income DECIMAL(12, 2) DEFAULT 0,
                total_expenses DECIMAL(12, 2) DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        print("✓ Account summary table created")
        
        conn.commit()
        cursor.close()
        conn.close()
        print("\n✓ All tables created successfully!")
        return True
        
    except Error as e:
        print(f"✗ Error creating tables: {e}")
        return False

def init_database():
    """Initialize entire database"""
    print("\n--- Initializing Wisespend Database ---\n")
    if create_database():
        if create_tables():
            return True
    return False

if __name__ == "__main__":
    init_database()
