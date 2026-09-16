import customtkinter as ctk
from models.financial_advisor import FinancialAdvisor
from screens.login_screen import LoginScreen
from screens.add_goal_screen import AddGoalScreen
from screens.dashboard_screen import DashboardScreen
from screens.reports_screen import ReportsScreen
from screens.settings_screen import SettingsScreen
from utils.constants import WINDOW_WIDTH, WINDOW_HEIGHT
from utils.scale import init_scaling
from utils.theme_manager import theme_manager
from utils.preferences import resolve_mode


class FinancialApp:

    def __init__(self):
        self.app = ctk.CTk()
        self.app.title("Eghtesadino")
        self.app.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.app.minsize(720, 560)

        init_scaling(self.app)

        self.advisor = FinancialAdvisor()
        self.container = ctk.CTkFrame(self.app, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.screens = {
            "login": LoginScreen(
                self.advisor, self.container, on_success=self._on_login_success
            ),
            "dashboard": DashboardScreen(
                self.advisor, self.container, on_navigate=self.show_screen
            ),
            "reports": ReportsScreen(
                self.advisor, self.container, on_navigate=self.show_screen
            ),
            "add_goal": AddGoalScreen(
                self.advisor, self.container, on_navigate=self.show_screen
            ),
            "settings": SettingsScreen(
                self.advisor,
                self.container,
                on_navigate=self.show_screen,
                on_logout=self._logout,
            ),
        }

        self.current_user = None
        self._current_screen_name = None
        theme_manager.register_listener(self._on_theme_change)

        # Apply persisted preferences before showing the start screen
        self._apply_startup_preferences()

        self.show_screen("login")

    def _apply_startup_preferences(self):
        mode = resolve_mode()
        theme_manager.set_mode(mode)

    def _on_login_success(self, user_id):
        self.current_user = user_id
        self.show_screen("dashboard")

    def _logout(self):
        self.current_user = None
        # Clear the login form and drop each screen's user so the next user starts from a clean state
        self.screens["login"].reset()
        for name in ("dashboard", "reports", "settings", "add_goal"):
            self.screens[name].user_id = None
        self.show_screen("login")

    def show_screen(self, name, animate=True):
        self._current_screen_name = name
        for screen in self.screens.values():
            screen.pack_forget()

        screen = self.screens.get(name)
        if screen is None:
            return

        # A hidden screen built under the previous theme is stale rebuild it
        if screen.is_stale():
            screen.rebuild()
        else:
            screen.pack(fill="both", expand=True)

        if hasattr(screen, "refresh_ui"):
            screen.refresh_ui(self.current_user)

    def run(self):
        self.app.mainloop()

    def _on_theme_change(self):
        """Reapply theme colors to the visible screen by rebuilding its UI."""
        screen = self.screens.get(self._current_screen_name)
        if screen is not None:
            screen.rebuild()


if __name__ == "__main__":
    app = FinancialApp()
    app.run()
