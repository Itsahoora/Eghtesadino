from .theme.colors import LIGHT_COLORS, DARK_COLORS
from .theme_manager import theme_manager
from .preferences import accent_tokens


class ThemeColors(dict):

    def _palette(self):
        mode = getattr(theme_manager, "mode", "dark")
        base = DARK_COLORS if mode == "dark" else LIGHT_COLORS
        # Apply the user's chosen accent to the shared brand tokens.
        try:
            primary, primary_hover = accent_tokens()
            return dict(base, primary=primary, primary_hover=primary_hover)
        except Exception:
            return base

    def get(self, key, default=None):
        return self._palette().get(key, default)

    def __getitem__(self, key):
        return self.get(key)

    def __contains__(self, key):
        return key in self._palette()

    def __iter__(self):
        return iter(self._palette())

    def __len__(self):
        return len(self._palette())


COLORS = ThemeColors()
