# Authentication screens: login, registration, and currency selection.
# setup(ctx) attaches show_login / show_register onto the shared ctx.
import flet as ft
import json
import os
from theme import *
from db_operations import get_user, create_user, get_user_data

REMEMBER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             ".remember_me")


def _load_remembered_email():
    try:
        if os.path.exists(REMEMBER_FILE):
            with open(REMEMBER_FILE) as f:
                return json.load(f).get("email", "")
    except Exception:
        pass
    return ""


def _save_remembered_email(email):
    try:
        with open(REMEMBER_FILE, "w") as f:
            json.dump({"email": email}, f)
    except Exception:
        pass


def _clear_remembered_email():
    try:
        if os.path.exists(REMEMBER_FILE):
            os.remove(REMEMBER_FILE)
    except Exception:
        pass


def setup(ctx):
    page            = ctx.page
    user            = ctx.user
    current_user_id = ctx.current_user_id
    is_returning    = ctx.is_returning
    income_dlg      = ctx.income_dlg
    expense_dlg     = ctx.expense_dlg
    dashboard_view  = ctx.dashboard_view

    def show_snack(text, color=RED):
        page.open(ft.SnackBar(
            content=ft.Text(text, color=WHITE), bgcolor=color))

    def auth_card(controls, spacing=20):
        # Centered white card scaffold shared by login / register / currency
        cw = min(460, page.width - 48) if page.width > 0 else 460
        return ft.Container(
            expand=True, alignment=ft.alignment.center,
            content=ft.Container(
                width=cw, bgcolor=WHITE, border_radius=30, padding=40,
                border=ft.border.all(1, BORDER),
                shadow=ft.BoxShadow(blur_radius=25, color="#DCE3F0",
                                    offset=ft.Offset(0, 6)),
                content=ft.Column(
                    spacing=spacing,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=controls,
                ),
            ),
        )

    def show_login(e=None):
        income_dlg.open  = False
        expense_dlg.open = False
        page.overlay.clear()
        page.clean()

        remembered = _load_remembered_email()
        em = tf(
            border_radius=18, hint_text="Email Address",
            prefix_icon=ft.Icons.EMAIL_OUTLINED, value=remembered,
        )
        pw = tf(
            border_radius=18, hint_text="Password",
            password=True, can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
        )
        remember_me = ft.Checkbox(
            label="Remember me", value=bool(remembered), active_color=PRIMARY,
        )

        def login(e):
            if not em.value.strip() or not pw.value.strip():
                show_snack("Please enter email and password.")
                return

            # Check database for user
            db_user = get_user(em.value.strip())
            if db_user and db_user["password"] == pw.value.strip():
                if remember_me.value:
                    _save_remembered_email(em.value.strip())
                else:
                    _clear_remembered_email()
                # Load user data from database
                current_user_id[0] = db_user["id"]
                user_data = get_user_data(db_user["id"])
                if user_data:
                    user.update(user_data)
                    is_returning[0] = True
                    page.clean()
                    page.add(dashboard_view())
                    page.update()
                    show_snack(f"Welcome, {user['name']}!", GREEN)
                else:
                    show_snack("Error loading user data.")
            else:
                show_snack("Invalid email or password.")

        card_width = min(460, page.width - 48) if page.width > 0 else 460
        page.add(auth_card(spacing=22, controls=[
            logo(),
            ft.Text("SpendWise", size=36,
                    weight=ft.FontWeight.BOLD, color=PRIMARY),
            btxt("TRACK SMART • SPEND WISE • SAVE MORE", 13),
            em, pw,
            ft.Row(
                alignment=ft.MainAxisAlignment.START,
                controls=[remember_me],
            ),
            ft.ElevatedButton(
                "Sign In", width=card_width - 80, height=55,
                bgcolor=GREEN, color=WHITE,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=18)),
                on_click=login,
            ),
            ft.TextButton("Create Account", on_click=show_register),
        ]))
        page.update()

    def show_register(e=None):
        page.overlay.clear()
        page.clean()

        rf = tf(border_radius=18, hint_text="First Name", prefix_icon=ft.Icons.PERSON_OUTLINE, expand=True)
        rl = tf(border_radius=18, hint_text="Last Name", expand=True)
        re = tf(border_radius=18, hint_text="Email Address", prefix_icon=ft.Icons.EMAIL_OUTLINED)
        rp = tf(border_radius=18, hint_text="Password", password=True, can_reveal_password=True, prefix_icon=ft.Icons.LOCK_OUTLINE)
        rc = tf(border_radius=18, hint_text="Confirm Password", password=True, can_reveal_password=True, prefix_icon=ft.Icons.LOCK_OUTLINE)

        strength_bars = [
            ft.Container(height=5, border_radius=4, bgcolor=BORDER, expand=True)
            for _ in range(4)
        ]
        strength_label = ft.Text("", size=12, color=TEXT_LIGHT)
        strength_row = ft.Column(
            visible=False, spacing=4,
            controls=[ft.Row(spacing=4, controls=strength_bars), strength_label],
        )

        def on_password_change(e):
            pw_val = rp.value or ""
            if not pw_val:
                strength_row.visible = False
            else:
                strength_row.visible = True
                level, color, filled = get_password_strength(pw_val)
                for i, bar in enumerate(strength_bars):
                    bar.bgcolor = color if i < filled else BORDER
                strength_label.value = level
                strength_label.color = color
            page.update()

        rp.on_change = on_password_change

        def save_currency(cname, csymbol):
            user_id = create_user(
                user["name"], user["email"], user["password"],
                cname, csymbol
            )
            if user_id:
                # Account created -> always redirect to the login page
                show_login()
                show_snack("Account created! Please sign in.", GREEN)
            else:
                show_login()
                show_snack("Email already registered or account creation failed.", RED)

        def cur_tile(flag, cname, csymbol):
            return ft.Container(
                padding=15, border_radius=18, bgcolor="#F8FAFC",
                border=ft.border.all(1, BORDER), ink=True,
                on_click=lambda e: save_currency(cname, csymbol),
                content=ft.Row(spacing=15, controls=[
                    ft.Text(flag, size=28),
                    ft.Column(spacing=2, controls=[
                        ft.Text(cname, size=15,
                                weight=ft.FontWeight.BOLD, color=TEXT),
                        btxt(f"Symbol: {csymbol}"),
                    ]),
                ]),
            )

        def show_currency():
            # Full-page currency picker (no modal -> no stuck scrim)
            page.overlay.clear()
            page.clean()
            page.add(auth_card(spacing=14, controls=[
                ttxt("Choose Your Currency", 26, PRIMARY),
                btxt("This will be used across your account."),
                cur_tile("🇬🇭", "Ghana Cedi",         "₵"),
                cur_tile("🇺🇸", "US Dollar",          "$"),
                cur_tile("🇬🇧", "British Pound",      "£"),
                cur_tile("🇪🇺", "Euro",               "€"),
                cur_tile("🇳🇬", "Nigerian Naira",     "₦"),
                cur_tile("🇿🇦", "South African Rand", "R"),
                ft.TextButton("← Back", on_click=show_register),
            ]))
            page.update()

        def create_account(e):
            first = rf.value.strip(); last = rl.value.strip()
            name  = f"{first} {last}".strip()
            email = re.value.strip()
            pw_   = rp.value.strip(); conf = rc.value.strip()
            if not first or not last or not email or not pw_ or not conf:
                show_snack("Please fill all fields."); return
            # Email must contain '@' and a '.' in the domain part
            at = email.find("@")
            if (at < 1 or " " in email
                    or "." not in email[at + 1:]
                    or email.endswith(".")):
                show_snack("Enter a valid email (must contain '@' and '.').")
                return
            if pw_ != conf:
                show_snack("Passwords do not match."); return
            if len(pw_) < 6:
                show_snack("Password must be at least 6 characters."); return
            # Reject duplicate email up front (email is UNIQUE in the database)
            if get_user(email):
                show_snack("Email already registered. Please sign in.")
                return
            user["name"]     = name
            user["email"]    = email
            user["password"] = pw_
            show_currency()

        card_width = min(460, page.width - 48) if page.width > 0 else 460
        page.add(auth_card(spacing=20, controls=[
            logo(),
            ttxt("Create Account", 34, PRIMARY),
            btxt("Secure your financial future today."),
            ft.Row(spacing=12, controls=[rf, rl]),
            re, rp, strength_row, rc,
            ft.ElevatedButton(
                "Create Account", width=card_width - 80, height=55,
                bgcolor=PRIMARY, color=WHITE,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=18)),
                on_click=create_account,
            ),
            ft.TextButton(
                "Already have an account? Sign In",
                on_click=show_login,
            ),
        ]))
        page.update()

    ctx.show_login    = show_login
    ctx.show_register = show_register
