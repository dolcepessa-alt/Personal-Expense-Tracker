# SpendWise 💰

**Track Smart • Spend Wise • Save More**

A desktop personal-finance tracker built with [Flet](https://flet.dev/) (Python) and a MySQL backend. Create an account, record income and expenses, set monthly budgets, and view spending statistics.

## Features
- User accounts with secure sign-up / sign-in
- Multi-currency support (Ghana Cedi, US Dollar, Pound, Euro, Naira, Rand)
- Income & expense tracking with categories
- Monthly budget planner with progress tracking
- Statistics: spending by category, recent activity, monthly breakdown

## Tech stack
- **Frontend:** Flet (Flutter-powered Python UI)
- **Backend:** MySQL (via `mysql-connector-python`)

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure & create the database**
   - Make sure MySQL is running.
   - Update your credentials in `db_config.py` if needed.
   - Initialize the database and tables:
     ```bash
     python setup_database.py
     ```
   - See [DATABASE_SETUP.md](DATABASE_SETUP.md) for full details.

3. **Run the app**
   ```bash
   python wisespend.py
   ```

## Project structure
| File | Responsibility |
|------|----------------|
| `wisespend.py` | App entry point — wires the modules together and starts |
| `theme.py` | Colour palette and reusable UI widget helpers |
| `auth.py` | Login, registration, and currency-selection screens |
| `dialogs.py` | Add-Income / Add-Expense dialogs |
| `dashboard.py` | Home, Transactions, Stats, Budget tabs + sidebar |
| `db_config.py` | MySQL connection settings & pool |
| `db_init.py` | Database & table schema creation |
| `db_operations.py` | CRUD operations (users, transactions, budgets) |
| `setup_database.py` | One-command database initialization |

The screen modules share state through a small `ctx` object created in
`wisespend.py`, so each module stays self-contained.

## Team
This project was built by three contributors:
- **[Name 1]** — Database & backend (`db_*.py`, `setup_database.py`)
- **[Name 2]** — Dashboard & tabs (`dashboard.py`)
- **[Name 3]** — Auth, theme & app shell (`auth.py`, `theme.py`, `dialogs.py`, `wisespend.py`)
