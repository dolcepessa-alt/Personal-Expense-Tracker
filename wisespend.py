# SpendWise — application entry point.
# Wires the screen modules together through a shared context (ctx) object
# and starts on the login screen.
import flet as ft
from types import SimpleNamespace

from theme import BG, RED
from db_config import init_connection_pool, test_connection
import dialogs
import dashboard
import auth


def main(page: ft.Page):
    page.title              = "SpendWise"
    page.bgcolor            = BG
    page.theme_mode         = ft.ThemeMode.LIGHT
    page.padding            = 0
    page.window_min_width   = 900
    page.window_min_height  = 600
    page.window_width       = 1200
    page.window_height      = 820

    # ─── Initialize Database ──────────────────────────────────────────────────
    init_connection_pool()
    if not test_connection():
        page.add(ft.Container(
            expand=True, alignment=ft.alignment.center,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
                controls=[
                    ft.Text("❌ Database Connection Failed", size=24,
                            weight=ft.FontWeight.BOLD, color=RED),
                    ft.Text(
                        "Please ensure MySQL is running and configured correctly.\n"
                        "See DATABASE_SETUP.md for instructions.",
                        size=14, text_align=ft.TextAlign.CENTER),
                ],
            ),
        ))
        return

    # ── Shared application state ─────────────────────────────────────────────
    ctx = SimpleNamespace(
        page=page,
        current_user_id=[None],          # mutable list to track logged-in user
        user={
            "id": None, "name": "", "email": "", "password": "",
            "currency": "Ghana Cedi", "currency_symbol": "₵",
            "balance": 0.00, "total_income": 0.00, "total_expenses": 0.00,
            "transactions": [],
            "budgets": {},
        },
        current_tab=["home"],            # mutable list so closures can write to it
        is_returning=[False],            # True on login, False on first signup
        dashboard_content=ft.Container(expand=True),
        sidebar_column=ft.Column(spacing=6, expand=True),
    )

    # ── Wire the modules (order matters: dialogs -> dashboard -> auth) ────────
    dialogs.setup(ctx)      # provides ctx.income_dlg / expense_dlg / open_*
    dashboard.setup(ctx)    # provides ctx.dashboard_view / load_tab
    auth.setup(ctx)         # provides ctx.show_login / show_register

    # START
    ctx.show_login()


ft.app(target=main)
