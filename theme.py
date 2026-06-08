# Shared theme: colour palette + reusable UI widget helpers.
# These helpers are pure (they only build controls from their arguments),
# so every screen module can import them with `from theme import *`.
import flet as ft

# ─── COLORS ───────────────────────────────────────────────────────────────────
BG            = "#F5F7FB"
CARD          = "#FFFFFF"
CARD_SOFT     = "#F8FAFC"
PRIMARY       = "#061A6E"
PRIMARY_LIGHT = "#1736A3"
GREEN         = "#19C14B"
RED           = "#EF4444"
ORANGE        = "#F59E0B"
TEXT          = "#0F172A"
TEXT_LIGHT    = "#64748B"
BORDER        = "#E2E8F0"
WHITE         = "#FFFFFF"


def get_password_strength(password):
    score = 0
    if len(password) >= 8:  score += 1
    if len(password) >= 12: score += 1
    if any(c.isupper() for c in password): score += 1
    if any(c.islower() for c in password): score += 1
    if any(c.isdigit() for c in password): score += 1
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password): score += 1
    if score <= 1: return "Weak",   RED,       1
    if score <= 2: return "Fair",   ORANGE,    2
    if score <= 4: return "Good",   "#EAB308", 3
    return                "Strong", GREEN,     4


def ttxt(text, size=28, color=TEXT):
    return ft.Text(text, size=size, weight=ft.FontWeight.BOLD, color=color)


def btxt(text, size=13, color=TEXT_LIGHT):
    return ft.Text(text, size=size, color=color)


def tf(border_radius=16, **kw):
    # Shared TextField styling (CARD_SOFT == "#F8FAFC")
    return ft.TextField(border_radius=border_radius, bgcolor=CARD_SOFT,
                        border_color=BORDER, color=TEXT, **kw)


def chip_col(*chip_args):
    return ft.Column(col={"xs": 12, "sm": 4},
                     controls=[stat_chip(*chip_args)])


def mk_card(content, padding=20):
    return ft.Container(
        bgcolor=CARD, border_radius=24, padding=padding,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=20, color="#DCE3F0",
                            offset=ft.Offset(0, 4)),
        content=content,
    )


def stat_chip(label, value, icon, color, bg):
    return ft.Container(
        expand=True, bgcolor=bg, border_radius=20, padding=20,
        content=ft.Column(spacing=8, controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Container(
                        width=40, height=40, border_radius=12,
                        bgcolor=color + "22",
                        alignment=ft.alignment.center,
                        content=ft.Text(icon, size=18),
                    ),
                    ft.Text(label, size=12, color=TEXT_LIGHT,
                            weight=ft.FontWeight.W_600),
                ]
            ),
            ft.Text(value, size=22, weight=ft.FontWeight.BOLD, color=color),
        ]),
    )


def tx_row(icon, name, amount, color, date="Today"):
    return ft.Container(
        padding=14, border_radius=18, bgcolor=CARD_SOFT,
        border=ft.border.all(1, BORDER),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(spacing=12, controls=[
                    ft.Container(
                        width=46, height=46, border_radius=14,
                        bgcolor="#E8EEFF", alignment=ft.alignment.center,
                        content=ft.Text(icon, size=20),
                    ),
                    ft.Column(spacing=2, controls=[
                        ft.Text(name, color=TEXT,
                                weight=ft.FontWeight.BOLD, size=14),
                        btxt(date),
                    ]),
                ]),
                ft.Text(amount, color=color,
                        weight=ft.FontWeight.BOLD, size=15),
            ],
        ),
    )


def progress_bar(pct, color, track=BORDER):
    # Filled bar (BORDER == "#E2E8F0")
    return ft.Container(
        height=10, border_radius=6, bgcolor=track,
        content=ft.Row(spacing=0, tight=True, controls=[
            ft.Container(expand=max(1, int(pct * 100)),
                         height=10, border_radius=6, bgcolor=color),
            ft.Container(expand=max(1, 100 - int(pct * 100))),
        ]),
    )


def empty_state(text, padding=20):
    return ft.Container(padding=padding, alignment=ft.alignment.center,
                        content=btxt(text, 14))


def logo(size=100):
    return ft.Image(src="logo.png", width=size, height=size,
                    fit=ft.ImageFit.CONTAIN)
