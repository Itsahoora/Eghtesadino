import json
from utils.resource_path import resource_path

_PREFS_FILE = resource_path("user_prefs.json")

# Accent colour choices: key -> base + hover tokens.
ACCENTS = {
    "teal": ("#0D9488", "#0F766E"),
    "blue": ("#2563EB", "#1D4ED8"),
    "violet": ("#7C3AED", "#6D28D9"),
    "rose": ("#E11D48", "#BE123C"),
    "amber": ("#D97706", "#B45309"),
    "green": ("#059669", "#047857"),
}

DEFAULTS = {
    "theme_mode": "system",  # light | dark | system
    "accent": "teal",  # key in ACCENTS
    "currency": "tomans",  # toman | dollar | euro
}


def _load_raw():
    try:
        with open(_PREFS_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


def _save_raw(data):
    try:
        with open(_PREFS_FILE, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
    except Exception:
        pass


def get(key):
    data = _load_raw()
    return data.get(key, DEFAULTS[key])


def set(key, value):
    if key not in DEFAULTS:
        return False
    valid = {
        "theme_mode": ("light", "dark", "system"),
        "accent": tuple(ACCENTS.keys()),
        "currency": ("tomans", "dollar", "euro"),
    }
    if key in valid and value not in valid[key]:
        return False
    data = _load_raw()
    data[key] = value
    _save_raw(data)
    return True


def resolve_mode(theme_mode=None):
    """Map a theme-mode preference to a concrete light/dark mode"""
    mode = theme_mode or get("theme_mode")
    if mode == "system":
        # Fall back to dark on unknown/headless, like the rest of the app.
        return "dark"
    return mode


def accent_tokens(accent=None):
    return ACCENTS.get(accent or get("accent"), ACCENTS["teal"])


CURRENCY_SYMBOLS = {
    "tomans": "",
    "dollar": "$",
    "euro": "€",
}


def currency_symbol(currency=None):
    return CURRENCY_SYMBOLS.get(currency or get("currency"), "")


def format_money(value, decimals=0, currency=None):
    """Format a number with the user's chosen currency symbol"""
    sym = currency_symbol(currency)
    prefix = "-" if value < 0 else ""
    amount = f"{abs(value):,.{decimals}f}"
    if sym:
        return f"{prefix}{sym}{amount}"
    return f"{prefix}{amount}"
