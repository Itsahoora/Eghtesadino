"""DPI-aware scaling utilities.

Caches the scale factor in memory so ``sv()`` never hits disk after
initial load.  Call ``init_scaling(app)`` once at startup.

Users can override the automatic scale via ``set_scale()``, which
persists the choice to ``user_scale.json``.
"""

import os
import json
import customtkinter as ctk

_SCALE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'user_scale.json')

_cached_scale: float | None = None


def _read_scale() -> float:
    """Read saved scale from disk. Returns 1.0 if no file or on error."""
    try:
        with open(_SCALE_FILE, 'r') as f:
            return float(json.load(f).get('scale', 1.0))
    except Exception:
        return 1.0


def _write_scale(value: float) -> None:
    """Persist scale value to disk."""
    try:
        with open(_SCALE_FILE, 'w') as f:
            json.dump({'scale': value}, f)
    except Exception:
        pass


def _apply_scale(scale: float) -> None:
    """Apply scale to CustomTkinter widget and window scaling."""
    for setter in (ctk.set_widget_scaling, ctk.set_window_scaling):
        try:
            setter(scale)
        except Exception:
            pass


def init_scaling(app) -> None:
    """Calculate and apply the optimal scale factor for the current display.

    Respects a previously saved user preference from ``user_scale.json``.
    If no preference exists, auto-calculates based on screen resolution.
    """
    global _cached_scale

    saved = _read_scale()
    if saved != 1.0:
        _cached_scale = saved
    else:
        try:
            root = app.winfo_toplevel()
            screen_w = root.winfo_screenwidth()
            screen_h = root.winfo_screenheight()
        except Exception:
            screen_w, screen_h = 1366, 768

        _cached_scale = min(screen_w / 1366, screen_h / 768)
        _cached_scale = max(0.7, min(1.4, _cached_scale))
        _write_scale(_cached_scale)

    _apply_scale(_cached_scale)


def set_scale(value: float) -> None:
    """Change scale at runtime and apply immediately.

    The new value is persisted so it survives app restarts.
    """
    global _cached_scale
    value = max(0.5, min(2.0, value))
    _cached_scale = value
    _write_scale(value)
    _apply_scale(value)


def get_scale() -> float:
    """Return the current scale factor."""
    global _cached_scale
    if _cached_scale is None:
        _cached_scale = _read_scale()
    return _cached_scale


def sv(value: float) -> int:
    """Scale a pixel value by the current DPI scale factor."""
    global _cached_scale
    if _cached_scale is None:
        _cached_scale = _read_scale()
    return int(value * _cached_scale)
