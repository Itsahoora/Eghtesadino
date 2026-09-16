"""Application-wide constants: categories, window size, spacing, icons, fonts"""

# ── Transaction categories ────────────────────────────────────────
INCOME_CATEGORIES = ["Salary", "Investment", "Work", "Other"]

EXPENSE_CATEGORIES = [
    "Food",
    "Transportation",
    "Education",
    "Entertainment",
    "Utilities",
    "Rent",
    "Other",
]

# ── Window (raw values — scaled via sv() at runtime) ──────────────
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 780

# ── Spacing tokens (raw values — apply sv() when used) ───────────
BASE_PADDING = 24
SMALL_PADDING = 12
MEDIUM_PADDING = 18

# ── Glyph icon map (Segoe UI-safe, no emoji, no new font) ───────
ICONS = {
    "forward": "→",
    "settings": "⚙",
    "reports": "◫",
    "dashboard": "⌂",
    "add": "+",
    "delete": "⌫",
    "balance": "◒",
    "income": "↗",
    "expense": "↘",
    "goal": "◎",
    "category": "▤",
    "amount": "¤",
    "repeat": "↻",
    "success": "✓",
    "warning": "!",
    "info": "i",
    "lock": "⚿",
    "tips": "✦",
    "theme_dark": "☾",
    "user": "●",
    "show": "◉",
    "hide": "○",
}

# ── Font families ─────────────────────────────────────────────────
FONT_FAMILY = "Segoe UI"
