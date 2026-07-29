import os
import json
import customtkinter as ctk
from .theme.colors import DARK_COLORS, PRESETS


class ThemeManager:
    THEME_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'user_theme.json')

    def __init__(self):
        self.mode = 'dark'
        self._overrides = {}
        self._listeners = []
        self._load()
        try:
            ctk.set_appearance_mode(self.mode.capitalize())
        except Exception:
            pass

    def _load(self):
        try:
            with open(self.THEME_FILE, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
                self.mode = data.get('mode', self.mode)
                self._overrides = data.get('overrides', {})
        except Exception:
            pass

    def _save(self):
        try:
            with open(self.THEME_FILE, 'w', encoding='utf-8') as fh:
                json.dump({
                    'mode': self.mode,
                    'overrides': self._overrides,
                }, fh, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def toggle_mode(self):
        self.mode = 'light' if self.mode == 'dark' else 'dark'
        self._apply_mode()
        self._save()

    def set_mode(self, mode):
        if mode not in {'light', 'dark'}:
            return False
        self.mode = mode
        self._apply_mode()
        self._save()
        return True

    def reset(self):
        self.mode = 'dark'
        self._overrides = {}
        self._apply_mode()
        self._save()
        return True

    def _apply_mode(self):
        try:
            ctk.set_appearance_mode(self.mode.capitalize())
        except Exception:
            pass
        for cb in list(self._listeners):
            try:
                cb()
            except Exception:
                pass

    def get_color(self, token, default=None):
        if token in self._overrides:
            return self._overrides[token]
        from .theme.colors import LIGHT_COLORS, DARK_COLORS
        palette = DARK_COLORS if self.mode == 'dark' else LIGHT_COLORS
        return palette.get(token, default)

    def set_color(self, token, value):
        self._overrides[token] = value
        self._save()
        for cb in list(self._listeners):
            try:
                cb()
            except Exception:
                pass

    def clear_overrides(self):
        self._overrides = {}
        self._save()
        for cb in list(self._listeners):
            try:
                cb()
            except Exception:
                pass

    def register_listener(self, cb):
        if cb not in self._listeners:
            self._listeners.append(cb)

    def unregister_listener(self, cb):
        try:
            self._listeners.remove(cb)
        except Exception:
            pass

    def apply_preset(self, name):
        preset = PRESETS.get(name)
        if preset is None:
            return False
        self._overrides = dict(preset.get(self.mode, {}))
        try:
            ctk.set_appearance_mode(self.mode.capitalize())
        except Exception:
            pass
        self._save()
        for cb in list(self._listeners):
            try:
                cb()
            except Exception:
                pass
        return True

    def export_theme(self):
        return {'mode': self.mode, 'overrides': self._overrides}

    def import_theme(self, data):
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except Exception:
                return False
        if not isinstance(data, dict):
            return False
        self.mode = data.get('mode', self.mode)
        self._overrides = data.get('overrides', self._overrides)
        try:
            ctk.set_appearance_mode(self.mode.capitalize())
        except Exception:
            pass
        self._save()
        return True

    def get_preset_name(self):
        for name, preset in PRESETS.items():
            if preset.get(self.mode) == self._overrides:
                return name
        if not self._overrides:
            return 'default'
        return 'custom'


theme_manager = ThemeManager()