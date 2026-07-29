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
            "login": LoginScreen(self.advisor, self.container, on_success=self._on_login_success),
            "dashboard": DashboardScreen(self.advisor, self.container, on_navigate=self.show_screen),
            "reports": ReportsScreen(self.advisor, self.container, on_navigate=self.show_screen),
            "add_goal": AddGoalScreen(self.advisor, self.container, on_navigate=self.show_screen),
            "settings": SettingsScreen(self.advisor, self.container, on_navigate=self.show_screen),
        }

        self.current_user = None
        theme_manager.register_listener(self._on_theme_change)

        self.show_screen("login")

    def _on_login_success(self, user_id):
        self.current_user = user_id
        self.show_screen("dashboard")

    def show_screen(self, name):
        for screen in self.screens.values():
            try:
                screen.pack_forget()
            except Exception:
                pass

        screen = self.screens.get(name)
        if screen is None:
            return

        screen.pack(fill="both", expand=True)
        if hasattr(screen, "refresh_ui"):
            try:
                screen.refresh_ui(self.current_user)
            except Exception:
                pass

    def run(self):
        self.app.mainloop()

    def _on_theme_change(self):
        for screen in self.screens.values():
            if hasattr(screen, "refresh_ui"):
                try:
                    screen.refresh_ui(self.current_user)
                except Exception:
                    pass


if __name__ == "__main__":
    app = FinancialApp()
    app.run()
