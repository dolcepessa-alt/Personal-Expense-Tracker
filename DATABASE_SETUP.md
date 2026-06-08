# Wisespend - Database Setup Guide

## MySQL Installation & Configuration

### Step 1: Install MySQL Server

#### Windows:
1. Download MySQL Community Server from https://dev.mysql.com/downloads/mysql/
2. Run the installer and follow the setup wizard
3. Choose "Server only" during installation
4. Configure MySQL as a Windows Service (recommended)
5. Remember the root password you set

#### macOS:
```bash
brew install mysql
brew services start mysql
mysql_secure_installation
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get install mysql-server
sudo mysql_secure_installation
```

### Step 2: Update Database Configuration

Edit `db_config.py` with your MySQL credentials:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",              # Your MySQL username
    "password": "your_password", # Your MySQL password
    "database": "wisespend",
    "port": 3306,
}
```

### Step 3: Initialize the Database

Run the initialization script:

```bash
python db_init.py
```

You should see:
```
--- Initializing Wisespend Database ---

✓ Database 'wisespend' ensured
✓ Users table created
✓ Transactions table created
✓ Budgets table created
✓ Account summary table created

✓ All tables created successfully!
```

### Step 4: Verify Connection

```bash
python -c "from db_config import init_connection_pool, test_connection; init_connection_pool(); test_connection()"
```

Should output: `✓ Database connection successful`

## Database Schema

### users
- Stores user account information
- Fields: id, name, email, password, currency, currency_symbol, created_at, updated_at

### transactions
- Stores all income and expense transactions
- Fields: id, user_id, type, description, amount, category, date, created_at
- Indexed by user_id and date for performance

### budgets
- Stores budget limits and spent amounts
- Fields: id, user_id, category, limit_amount, spent_amount, month_year, created_at
- Unique constraint on (user_id, category, month_year)

### account_summary
- Summary statistics for each user
- Fields: id, user_id, balance, total_income, total_expenses, updated_at

## Using Database Functions in wisespend.py

The app now uses these functions instead of in-memory storage:

```python
# Import at top of wisespend.py
from db_config import init_connection_pool, test_connection
from db_operations import *

# Initialize pool on startup
def main(page):
    init_connection_pool()
    if not test_connection():
        show_snack("Database connection failed!", RED)
        return
    
    # Use functions like:
    user_id = create_user(name, email, password)
    user = get_user_by_id(user_id)
    add_transaction(user_id, "income", description, amount, category, date)
    transactions = get_transactions(user_id)
```

## Troubleshooting

### Connection refused
- Make sure MySQL is running: `mysql -u root -p`
- Check port 3306 is available

### Access denied
- Verify username and password in db_config.py
- Reset MySQL password if forgotten

### Database doesn't exist
- Run `python db_init.py` again

### Performance Issues
- The connection pool defaults to 5 connections
- Adjust pool_size in db_config.py if needed
- Indexes are automatically created for common queries
