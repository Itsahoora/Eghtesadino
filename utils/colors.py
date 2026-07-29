"""Theme-aware color accessor.

Exposes ``COLORS`` as a dict-like object that returns the correct
palette (light or dark) based on the current ``theme_manager.mode``.
"""

from .theme.colors import LIGHT_COLORS, DARK_COLORS
from .theme_manager import theme_manager


class ThemeColors(dict):
    """Dict-like accessor that returns mode-appropriate colors.

    UI code calls ``COLORS.get('token')`` — this class selects the
    light or dark palette depending on ``theme_manager.mode``.
    """

    def get(self, key, default=None):
        mode = getattr(theme_manager, 'mode', 'dark')
        palette = DARK_COLORS if mode == 'dark' else LIGHT_COLORS
        return palette.get(key, default)

    def __getitem__(self, key):
        return self.get(key)


COLORS = ThemeColors()