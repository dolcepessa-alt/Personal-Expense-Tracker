# Dashboard: the four tab pages (Home, Transactions, Stats, Budget),
# the sidebar, navigation, and the logged-in dashboard layout.
# setup(ctx) wires everything onto the shared ctx.
import flet as ft
from datetime import datetime
from theme import *
from db_operations import get_budgets, set_budget


def setup(ctx):
    page              = ctx.page
    user              = ctx.user
    current_user_id   = ctx.current_user_id
    current_tab       = ctx.current_tab
    is_returning      = ctx.is_returning
    dashboard_content = ctx.dashboard_content
    sidebar_column    = ctx.sidebar_column
    income_dlg        = ctx.income_dlg
    expense_dlg       = ctx.expense_dlg
    open_income       = ctx.open_income
    open_expense      = ctx.open_expense

    def show_snack(text, color=RED):
        page.open(ft.SnackBar(
            content=ft.Text(text, color=WHITE), bgcolor=color))

    # ── Button row (only for Home & Transactions) ──────────────────────────────
    def btn_row():
        return ft.Row(
            spacing=16,
            controls=[
                ft.ElevatedButton(
                    "＋  Add Income",
                    bgcolor=GREEN, color=WHITE, expand=True, height=52,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=16)),
                    on_click=open_income,
                ),
                ft.ElevatedButton(
                    "－  Add Expense",
                    bgcolor=RED, color=WHITE, expand=True, height=52,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=16)),
                    on_click=open_expense,
                ),
            ],
        )

    # ── HOME ──────────────────────────────────────────────────────────────────
    def build_home():
        sym = user["currency_symbol"]
        txs = user["transactions"][:5]

        if txs:
            rows = [
                tx_row(
                    "💰" if t["type"] == "income" else "💸",
                    t["desc"],
                    ("+" if t["type"] == "income" else "−") +
                    f"{sym}{t['amount']:.2f}",
                    GREEN if t["type"] == "income" else RED,
                    t.get("date", "Today"),
                )
                for t in txs
            ]
        else:
            rows = [empty_state(
                "No transactions yet — add income or an expense to begin.")]

        return ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
            controls=[
                # Balance card
                ft.Container(
                    padding=30, border_radius=28,
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.top_left,
                        end=ft.alignment.bottom_right,
                        colors=[PRIMARY, PRIMARY_LIGHT],
                    ),
                    content=ft.Column(spacing=16, controls=[
                        *([ft.Text(
                            f"Welcome, {user['name'].split()[0]} 👋",
                            size=15, color="#D6E2FF",
                            weight=ft.FontWeight.W_500,
                        )] if is_returning[0] else []),
                        btxt("Total Balance", 14, "#D6E2FF"),
                        ft.Text(
                            f"{sym}{user['balance']:.2f}",
                            size=40, weight=ft.FontWeight.BOLD, color=WHITE,
                        ),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Column(spacing=3, controls=[
                                    btxt("INCOME", 11, "#D6E2FF"),
                                    ttxt(f"{sym}{user['total_income']:.2f}",
                                         20, WHITE),
                                ]),
                                ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.END,
                                    spacing=3,
                                    controls=[
                                        btxt("EXPENSES", 11, "#D6E2FF"),
                                        ttxt(f"{sym}{user['total_expenses']:.2f}",
                                             20, WHITE),
                                    ],
                                ),
                            ],
                        ),
                    ]),
                ),

                # ← buttons live HERE, right under the balance card
                btn_row(),

                # Stat chips
                ft.ResponsiveRow(spacing=16, controls=[
                    chip_col(
                        "Net Savings",
                        f"{sym}{max(0, user['balance']):.2f}",
                        "💎", GREEN, "#ECFDF5",
                    ),
                    chip_col(
                        "Transactions",
                        str(len(user["transactions"])),
                        "🔄", PRIMARY, "#EFF2FF",
                    ),
                    chip_col(
                        "Expense Ratio",
                        (
                            f"{user['total_expenses'] / user['total_income'] * 100:.0f}%"
                            if user["total_income"] > 0 else "—"
                        ),
                        "📉", RED, "#FFF5F5",
                    ),
                ]),

                # Recent transactions
                mk_card(ft.Column(spacing=14, controls=[
                    ttxt("Recent Transactions", 18),
                    *rows,
                ])),
            ],
        )

    # ── TRANSACTIONS ──────────────────────────────────────────────────────────
    def build_transactions():
        sym = user["currency_symbol"]
        txs = user["transactions"]
        filt = ["All"]

        tx_list_col = ft.Column(spacing=10)

        def render(fv):
            data = (txs if fv == "All"
                    else [t for t in txs if t["type"] == fv.lower()])
            if not data:
                return [empty_state("No transactions found.", 30)]
            out = []
            for t in data:
                icon  = "💰" if t["type"] == "income" else "💸"
                color = GREEN if t["type"] == "income" else RED
                sign  = "+" if t["type"] == "income" else "−"
                cat   = t.get("category", "")
                label = t["desc"] + (f"  · {cat}" if cat else "")
                out.append(tx_row(icon, label,
                                  f"{sign}{sym}{t['amount']:.2f}",
                                  color, t.get("date", "")))
            return out

        tx_list_col.controls = render("All")

        chip_refs = {}

        def make_chip(label):
            def clicked(e):
                filt[0] = label
                tx_list_col.controls = render(label)
                for lbl, c in chip_refs.items():
                    c.bgcolor = PRIMARY if lbl == label else CARD_SOFT
                    for txt in c.content.controls:
                        txt.color = WHITE if lbl == label else TEXT
                page.update()

            chip = ft.Container(
                padding=ft.padding.symmetric(horizontal=18, vertical=8),
                border_radius=12,
                bgcolor=PRIMARY if filt[0] == label else CARD_SOFT,
                border=ft.border.all(1, BORDER),
                ink=True,
                on_click=clicked,
                content=ft.Row(controls=[
                    ft.Text(label,
                            color=WHITE if filt[0] == label else TEXT,
                            size=13, weight=ft.FontWeight.W_600),
                ]),
            )
            chip_refs[label] = chip
            return chip

        summary = (
            f"{len(txs)} total · "
            f"{sum(1 for t in txs if t['type']=='income')} income · "
            f"{sum(1 for t in txs if t['type']=='expense')} expenses"
        )

        return ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
            controls=[
                # buttons at the top of this tab too
                btn_row(),

                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ttxt("All Transactions", 22),
                        btxt(summary, 13),
                    ],
                ),

                ft.Row(spacing=10, controls=[
                    make_chip("All"),
                    make_chip("Income"),
                    make_chip("Expense"),
                ]),

                mk_card(tx_list_col),
            ],
        )

    # ── STATS ─────────────────────────────────────────────────────────────────
    def build_stats():
        sym = user["currency_symbol"]
        txs = user["transactions"]

        cat_totals: dict[str, float] = {}
        for t in txs:
            if t["type"] == "expense":
                c = t.get("category", "Other")
                cat_totals[c] = cat_totals.get(c, 0) + t["amount"]

        total_exp = user["total_expenses"] or 1

        cat_bars = []
        for cat, amt in sorted(cat_totals.items(),
                                key=lambda x: x[1], reverse=True):
            pct   = amt / total_exp
            color = PRIMARY if pct > 0.5 else (ORANGE if pct > 0.25 else GREEN)
            cat_bars.append(ft.Column(spacing=6, controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        btxt(cat, 13, TEXT),
                        btxt(f"{sym}{amt:.2f}  ({pct*100:.0f}%)", 13),
                    ],
                ),
                progress_bar(pct, color),
            ]))

        # bar chart of last 10
        chart_bars = []
        last10 = list(reversed(txs[-10:]))
        if last10:
            max_val = max(t["amount"] for t in last10) or 1
            for t in last10:
                h     = max(6, int(t["amount"] / max_val * 90))
                color = GREEN if t["type"] == "income" else RED
                chart_bars.append(ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4,
                    controls=[
                        ft.Container(
                            width=30, height=h, border_radius=6,
                            bgcolor=color,
                            tooltip=f"{t['desc']}: {sym}{t['amount']:.2f}",
                        ),
                        btxt(t["desc"][:4], 9, color),
                    ],
                ))

        monthly: dict[str, dict] = {}
        for t in txs:
            mo = t.get("date", "")[-8:]
            if mo not in monthly:
                monthly[mo] = {"income": 0.0, "expense": 0.0}
            monthly[mo][t["type"]] += t["amount"]

        month_rows = [
            ft.Container(
                padding=14, border_radius=16, bgcolor=CARD_SOFT,
                border=ft.border.all(1, BORDER),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        btxt(mo or "—", 14, TEXT),
                        ft.Row(spacing=20, controls=[
                            ft.Text(f"+{sym}{v['income']:.2f}",
                                    color=GREEN, weight=ft.FontWeight.BOLD),
                            ft.Text(f"−{sym}{v['expense']:.2f}",
                                    color=RED, weight=ft.FontWeight.BOLD),
                        ]),
                    ],
                ),
            )
            for mo, v in list(monthly.items())[:6]
        ]

        controls = [
            ttxt("Statistics", 22),
            ft.ResponsiveRow(spacing=16, controls=[
                chip_col("Total Income", f"{sym}{user['total_income']:.2f}",
                         "💰", GREEN, "#ECFDF5"),
                chip_col("Total Expenses", f"{sym}{user['total_expenses']:.2f}",
                         "💸", RED, "#FFF5F5"),
                chip_col("Net Balance", f"{sym}{user['balance']:.2f}",
                         "📊", PRIMARY, "#EFF2FF"),
            ]),
            mk_card(ft.Column(spacing=16, controls=[
                ttxt("Recent Activity", 18),
                ft.Container(
                    height=120,
                    content=ft.Row(
                        spacing=8,
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.END,
                        controls=chart_bars or [btxt("No data yet.", 14)],
                    ),
                ),
                ft.Row(spacing=16, controls=[
                    ft.Row(spacing=6, controls=[
                        ft.Container(width=12, height=12, border_radius=3,
                                     bgcolor=GREEN),
                        btxt("Income", 12),
                    ]),
                    ft.Row(spacing=6, controls=[
                        ft.Container(width=12, height=12, border_radius=3,
                                     bgcolor=RED),
                        btxt("Expense", 12),
                    ]),
                ]),
            ])),
            mk_card(ft.Column(spacing=14, controls=[
                ttxt("Spending by Category", 18),
                *(cat_bars if cat_bars else
                  [btxt("No expenses recorded yet.", 14)]),
            ])),
        ]
        if month_rows:
            controls.append(mk_card(ft.Column(spacing=14, controls=[
                ttxt("Monthly Breakdown", 18),
                *month_rows,
            ])))

        return ft.Column(scroll=ft.ScrollMode.AUTO, spacing=20,
                         controls=controls)

    # ── BUDGET ────────────────────────────────────────────────────────────────
    def build_budget():
        sym = user["currency_symbol"]

        # Always load the latest saved budgets from DB
        month_key  = datetime.now().strftime("%Y-%m")
        db_budgets = get_budgets(current_user_id[0], month_key)
        for b in db_budgets:
            user["budgets"][b["category"]] = float(b["limit_amount"])

        budgets = user["budgets"]
        txs     = user["transactions"]

        CATS = ["🍔 Food", "🚗 Transport", "🏠 Rent", "💊 Health",
                "🎮 Entertainment", "🛍️ Shopping", "📚 Education",
                "💡 Utilities", "Other"]

        this_month = datetime.now().strftime("%b %Y")
        spent: dict[str, float] = {}
        for t in txs:
            if t["type"] == "expense" and this_month in t.get("date", ""):
                c = t.get("category", "Other")
                spent[c] = spent.get(c, 0) + t["amount"]

        budget_cards = []
        for cat in CATS:
            limit = budgets.get(cat)
            if not limit:
                continue
            use   = spent.get(cat, 0)
            pct   = min(use / limit, 1)
            color = RED if pct >= 0.9 else (ORANGE if pct >= 0.6 else GREEN)
            status = "OVER BUDGET 🚨" if use > limit else \
                     f"{sym}{limit - use:.2f} remaining"
            budget_cards.append(ft.Container(
                padding=16, border_radius=18, bgcolor=CARD_SOFT,
                border=ft.border.all(1, BORDER),
                content=ft.Column(spacing=8, controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            btxt(cat, 14, TEXT),
                            btxt(f"{sym}{use:.2f} / {sym}{limit:.2f}", 13),
                        ],
                    ),
                    progress_bar(pct, color),
                    btxt(status, 12, RED if use > limit else GREEN),
                ]),
            ))

        cat_dd = ft.Dropdown(
            label="Category", border_radius=14,
            bgcolor=CARD_SOFT, border_color=BORDER, color=TEXT,
            options=[ft.dropdown.Option(c) for c in CATS],
        )
        limit_field = tf(
            border_radius=14, label=f"Monthly limit ({sym})",
            keyboard_type=ft.KeyboardType.NUMBER,
            prefix_icon=ft.Icons.SAVINGS,
        )

        def save_budget(e):
            cat = cat_dd.value
            if not cat:
                show_snack("Please select a category.")
                return
            try:
                lim = float(limit_field.value.strip())
                if lim <= 0:
                    raise ValueError
            except (ValueError, AttributeError):
                show_snack("Please enter a valid limit.")
                return
            ok = set_budget(current_user_id[0], cat, lim,
                            datetime.now().strftime("%Y-%m"))
            if not ok:
                show_snack("Error saving budget.")
                return
            budgets[cat] = lim
            user["budgets"][cat] = lim
            show_snack(f"Budget for {cat} set to {sym}{lim:.2f}!", GREEN)
            load_tab("budget")

        body_controls = [
            ttxt("Budget Planner", 22),
            btxt(f"Set monthly spending limits — tracked for {this_month}", 14),
            mk_card(ft.Column(spacing=14, controls=[
                ttxt("Set a Budget", 18),
                cat_dd,
                limit_field,
                ft.ElevatedButton(
                    "Save Budget",
                    bgcolor=PRIMARY, color=WHITE, height=48,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=14)),
                    on_click=save_budget,
                ),
            ])),
        ]

        if budget_cards:
            body_controls.append(mk_card(ft.Column(spacing=14, controls=[
                ttxt("Your Budgets", 18),
                *budget_cards,
            ])))
        else:
            body_controls.append(
                empty_state("No budgets set yet. Add one above!", 24))

        return ft.Column(scroll=ft.ScrollMode.AUTO, spacing=20,
                         controls=body_controls)

    # ── LOAD TAB ───────────────────────────────────────────────────────────────
    def load_tab(tab):
        current_tab[0] = tab
        builders = {
            "home":         build_home,
            "transactions": build_transactions,
            "stats":        build_stats,
            "budget":       build_budget,
        }
        dashboard_content.content = builders[tab]()
        refresh_sidebar()
        page.update()

    # ── SIDEBAR ────────────────────────────────────────────────────────────────
    def nav_btn(icon, label, tab):
        active = current_tab[0] == tab

        def clicked(e):
            load_tab(tab)

        return ft.Container(
            border_radius=16, ink=True, on_click=clicked,
            padding=ft.padding.symmetric(horizontal=16, vertical=13),
            bgcolor=PRIMARY if active else None,
            content=ft.Row(spacing=12, controls=[
                ft.Text(icon, size=20),
                ft.Text(label, size=15, weight=ft.FontWeight.W_600,
                        color=WHITE if active else TEXT),
            ]),
        )

    def do_logout(e):
        current_user_id[0] = None
        user.update({"id": None, "balance": 0.0, "total_income": 0.0,
                     "total_expenses": 0.0, "transactions": [],
                     "budgets": {}})
        ctx.show_login()
        show_snack("Logged out successfully.", GREEN)

    def refresh_sidebar():
        sym  = user["currency_symbol"]
        name = user["name"]
        sidebar_column.controls = [
            ft.Column(
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    logo(70),
                    ft.Text("SpendWise", size=26,
                            weight=ft.FontWeight.BOLD, color=PRIMARY),
                    btxt("TRACK SMART • SPEND WISE"),
                ],
            ),
            ft.Container(height=8),
            ft.Container(
                padding=14, border_radius=16,
                bgcolor=CARD_SOFT, border=ft.border.all(1, BORDER),
                content=ft.Row(spacing=10, controls=[
                    ft.Container(
                        width=38, height=38, border_radius=12,
                        bgcolor=PRIMARY, alignment=ft.alignment.center,
                        content=ft.Text(
                            name[0].upper() if name else "?",
                            size=18, color=WHITE, weight=ft.FontWeight.BOLD),
                    ),
                    ft.Column(spacing=2, controls=[
                        ft.Text(name or "User", size=14,
                                weight=ft.FontWeight.BOLD, color=TEXT),
                        btxt(f"{sym}{user['balance']:.2f}", 12),
                    ]),
                ]),
            ),
            ft.Container(height=8),
            nav_btn("🏠", "Home",          "home"),
            nav_btn("🧾", "Transactions",  "transactions"),
            nav_btn("📊", "Stats",         "stats"),
            nav_btn("💰", "Budget",        "budget"),
            ft.Container(expand=True),
            ft.Divider(color=BORDER),
            ft.Container(
                border_radius=16, padding=14, bgcolor="#FFF1F2",
                ink=True, on_click=do_logout,
                content=ft.Row(controls=[
                    ft.Text("🚪"),
                    ft.Text("Logout", color=RED,
                            weight=ft.FontWeight.BOLD, size=15),
                ]),
            ),
        ]

    # ── DASHBOARD LAYOUT ───────────────────────────────────────────────────────
    def dashboard_view():
        # Always reset dialog state before (re-)adding to overlay
        income_dlg.open  = False
        expense_dlg.open = False
        if income_dlg not in page.overlay:
            page.overlay.append(income_dlg)
        if expense_dlg not in page.overlay:
            page.overlay.append(expense_dlg)

        current_tab[0] = "home"
        dashboard_content.content = build_home()
        refresh_sidebar()

        return ft.Row(
            expand=True,
            controls=[
                ft.Container(
                    width=270, bgcolor=WHITE,
                    padding=ft.padding.symmetric(horizontal=20, vertical=24),
                    border=ft.border.only(right=ft.BorderSide(1, BORDER)),
                    content=sidebar_column,
                ),
                ft.Container(
                    expand=True, padding=30,
                    content=dashboard_content,
                ),
            ],
        )

    ctx.dashboard_view  = dashboard_view
    ctx.load_tab        = load_tab
    ctx.refresh_sidebar = refresh_sidebar
