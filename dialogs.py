# Add-Income and Add-Expense dialogs.
# setup(ctx) builds both dialogs and attaches them (plus their open handlers)
# onto the shared ctx so the dashboard and auth screens can use them.
import flet as ft
from datetime import datetime
from theme import *
from db_operations import add_transaction, update_account_summary

EXP_CATS = ["🍔 Food", "🚗 Transport", "🏠 Rent", "💊 Health",
            "🎮 Entertainment", "🛍️ Shopping", "📚 Education",
            "💡 Utilities", "Other"]


def setup(ctx):
    page            = ctx.page
    user            = ctx.user
    current_user_id = ctx.current_user_id
    current_tab     = ctx.current_tab

    def show_snack(text, color=RED):
        page.open(ft.SnackBar(
            content=ft.Text(text, color=WHITE), bgcolor=color))

    def make_tx_dialog(kind):
        # kind == "income" or "expense" — both dialogs share one builder
        inc   = kind == "income"
        accent = GREEN if inc else RED
        amount = tf(label="Amount", keyboard_type=ft.KeyboardType.NUMBER,
                    prefix_icon=ft.Icons.ATTACH_MONEY)
        desc   = tf(label="Description (e.g. Monthly Salary)" if inc
                    else "Description (e.g. Groceries)",
                    prefix_icon=ft.Icons.NOTES)
        cat_dd = None if inc else ft.Dropdown(
            label="Category", border_radius=16, bgcolor=CARD_SOFT,
            border_color=BORDER, color=TEXT, value="Other",
            options=[ft.dropdown.Option(c) for c in EXP_CATS],
        )

        def close():
            dlg.open = False
            amount.value = ""
            desc.value = ""
            if cat_dd is not None:
                cat_dd.value = "Other"
            page.update()

        def confirm(e):
            sym = user["currency_symbol"]
            try:
                amt = float(amount.value.strip())
                if amt <= 0:
                    raise ValueError
            except (ValueError, AttributeError):
                show_snack("Enter a valid positive amount.")
                return
            d   = desc.value.strip() or ("Income" if inc else "Expense")
            cat = "Income" if inc else (cat_dd.value or "Other")
            today = datetime.now()

            tx_id = add_transaction(
                current_user_id[0], kind, d, amt, cat,
                today.strftime("%Y-%m-%d")
            )
            if tx_id:
                user["transactions"].insert(0, {
                    "id": tx_id, "type": kind,
                    "desc": d, "amount": amt,
                    "category": cat,
                    "date": today.strftime("%d %b %Y"),
                })

            # Update balance
            if inc:
                user["balance"] += amt
                user["total_income"] += amt
            else:
                user["balance"] -= amt
                user["total_expenses"] += amt
            update_account_summary(
                current_user_id[0],
                user["balance"], user["total_income"], user["total_expenses"]
            )

            close()
            show_snack(f"Income of {sym}{amt:.2f} added!", GREEN) if inc else \
                show_snack(f"Expense of {sym}{amt:.2f} recorded!", ORANGE)
            ctx.load_tab(current_tab[0])

        dlg = ft.AlertDialog(
            modal=True, bgcolor=WHITE,
            title=ttxt("Add Income" if inc else "Add Expense", 22, accent),
            content=ft.Container(
                width=380,
                content=ft.Column(spacing=16 if inc else 14, tight=True,
                                   controls=[
                    btxt("Enter the income details below." if inc
                         else "Enter the expense details below.", 14),
                    amount, desc, *([] if cat_dd is None else [cat_dd]),
                ]),
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: close()),
                ft.ElevatedButton(
                    "Add Income" if inc else "Add Expense",
                    bgcolor=accent, color=WHITE, on_click=confirm,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        def open_dlg(e):
            dlg.open = True
            page.update()

        return dlg, open_dlg

    income_dlg,  open_income  = make_tx_dialog("income")
    expense_dlg, open_expense = make_tx_dialog("expense")

    ctx.income_dlg   = income_dlg
    ctx.expense_dlg  = expense_dlg
    ctx.open_income  = open_income
    ctx.open_expense = open_expense
