# Database Operations for Wisespend
import mysql.connector
from mysql.connector import Error
from db_config import get_connection
from datetime import datetime

# ─── USER OPERATIONS ──────────────────────────────────────────────────────────

def create_user(name, email, password, currency="Ghana Cedi", currency_symbol="₵"):
    """Create a new user"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO users (name, email, password, currency, currency_symbol)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, email, password, currency, currency_symbol))
        
        user_id = cursor.lastrowid
        conn.commit()
        
        # Create account summary record
        cursor.execute("""
            INSERT INTO account_summary (user_id, balance, total_income, total_expenses)
            VALUES (%s, 0, 0, 0)
        """, (user_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        return user_id
    except Error as e:
        print(f"✗ Error creating user: {e}")
        return None

def get_user(email):
    """Get user by email"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT * FROM users WHERE email = %s
        """, (email,))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    except Error as e:
        print(f"✗ Error fetching user: {e}")
        return None

def get_user_by_id(user_id):
    """Get user by ID"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT * FROM users WHERE id = %s
        """, (user_id,))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    except Error as e:
        print(f"✗ Error fetching user: {e}")
        return None

# ─── ACCOUNT SUMMARY OPERATIONS ────────────────────────────────────────────────

def get_account_summary(user_id):
    """Get account summary"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT balance, total_income, total_expenses FROM account_summary
            WHERE user_id = %s
        """, (user_id,))
        
        summary = cursor.fetchone()
        cursor.close()
        conn.close()
        return summary
    except Error as e:
        print(f"✗ Error fetching account summary: {e}")
        return None

def update_account_summary(user_id, balance, total_income, total_expenses):
    """Update account summary"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE account_summary
            SET balance = %s, total_income = %s, total_expenses = %s
            WHERE user_id = %s
        """, (balance, total_income, total_expenses, user_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print(f"✗ Error updating account summary: {e}")
        return False

# ─── TRANSACTION OPERATIONS ───────────────────────────────────────────────────

def add_transaction(user_id, tx_type, description, amount, category, date):
    """Add a new transaction"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO transactions (user_id, type, description, amount, category, date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, tx_type, description, amount, category, date))
        
        tx_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        return tx_id
    except Error as e:
        print(f"✗ Error adding transaction: {e}")
        return None

def get_transactions(user_id, limit=50):
    """Get user transactions (most recent first)"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, type, description, amount, category, date
            FROM transactions
            WHERE user_id = %s
            ORDER BY date DESC, created_at DESC
            LIMIT %s
        """, (user_id, limit))
        
        transactions = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Convert to format compatible with app
        result = []
        for tx in transactions:
            result.append({
                "id": tx["id"],
                "type": tx["type"],
                "desc": tx["description"],
                "amount": float(tx["amount"]),
                "category": tx["category"],
                "date": tx["date"].strftime("%d %b %Y"),
            })
        return result
    except Error as e:
        print(f"✗ Error fetching transactions: {e}")
        return []

def delete_transaction(transaction_id):
    """Delete a transaction"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM transactions WHERE id = %s
        """, (transaction_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print(f"✗ Error deleting transaction: {e}")
        return False

def get_transactions_by_category(user_id, month_year):
    """Get transactions grouped by category for a specific month"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT category, SUM(amount) as total, COUNT(*) as count, type
            FROM transactions
            WHERE user_id = %s AND DATE_FORMAT(date, '%Y-%m') = %s
            GROUP BY category, type
        """, (user_id, month_year))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Error as e:
        print(f"✗ Error fetching transactions by category: {e}")
        return []

# ─── BUDGET OPERATIONS ─────────────────────────────────────────────────────────

def set_budget(user_id, category, limit_amount, month_year):
    """Set or update a budget"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO budgets (user_id, category, limit_amount, month_year)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE limit_amount = %s
        """, (user_id, category, limit_amount, month_year, limit_amount))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print(f"✗ Error setting budget: {e}")
        return False

def get_budgets(user_id, month_year):
    """Get budgets for a specific month"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT category, limit_amount, spent_amount
            FROM budgets
            WHERE user_id = %s AND month_year = %s
        """, (user_id, month_year))
        
        budgets = cursor.fetchall()
        cursor.close()
        conn.close()
        return budgets
    except Error as e:
        print(f"✗ Error fetching budgets: {e}")
        return []

def update_budget_spent(user_id, category, month_year, spent_amount):
    """Update spent amount for a budget"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE budgets
            SET spent_amount = %s
            WHERE user_id = %s AND category = %s AND month_year = %s
        """, (spent_amount, user_id, category, month_year))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print(f"✗ Error updating budget: {e}")
        return False

# ─── UTILITY FUNCTIONS ────────────────────────────────────────────────────────

def calculate_totals(user_id):
    """Calculate total income and expenses for a user"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN type='income' THEN amount ELSE 0 END) as total_income,
                SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) as total_expenses
            FROM transactions
            WHERE user_id = %s
        """, (user_id,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return {
            "total_income": float(result["total_income"] or 0),
            "total_expenses": float(result["total_expenses"] or 0),
        }
    except Error as e:
        print(f"✗ Error calculating totals: {e}")
        return {"total_income": 0, "total_expenses": 0}

def get_user_data(user_id):
    """Load complete user data (for session start)"""
    try:
        user = get_user_by_id(user_id)
        summary = get_account_summary(user_id)
        transactions = get_transactions(user_id)
        month_key = datetime.now().strftime("%Y-%m")
        budget_rows = get_budgets(user_id, month_key)
        budgets = {b["category"]: float(b["limit_amount"]) for b in budget_rows}

        if user and summary:
            return {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "currency": user["currency"],
                "currency_symbol": user["currency_symbol"],
                "balance": float(summary["balance"]),
                "total_income": float(summary["total_income"]),
                "total_expenses": float(summary["total_expenses"]),
                "transactions": transactions,
                "budgets": budgets,
            }
        return None
    except Exception as e:
        print(f"✗ Error loading user data: {e}")
        return None
