import json
import customtkinter as ctk
from utils.resource_path import resource_path


class ThemeManager:
    THEME_FILE = resource_path('user_theme.json')

    def __init__(self):
        self.mode = 'dark'
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
        except Exception:
            pass

    def _save(self):
        try:
            with open(self.THEME_FILE, 'w', encoding='utf-8') as fh:
                json.dump({'mode': self.mode}, fh, ensure_ascii=False, indent=2)
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

    def register_listener(self, cb):
        if cb not in self._listeners:
            self._listeners.append(cb)

    def unregister_listener(self, cb):
        try:
            self._listeners.remove(cb)
        except Exception:
            pass


theme_manager = ThemeManager()