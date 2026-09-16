import customtkinter as ctk
import tkinter.messagebox as mb
from utils.colors import COLORS
from utils.scale import sv
from utils.constants import ICONS, BASE_PADDING, MEDIUM_PADDING
from utils.ui_components import ScreenHeader, BaseScreen, font


class AddGoalScreen(BaseScreen):
    def __init__(self, advisor, master, on_navigate=None):
        self.advisor = advisor
        self.master = master
        self.on_navigate = on_navigate
        self.user_id = None
        self._build_ui()

    def _build_ui(self):
        self.root = ctk.CTkFrame(self.master, fg_color=COLORS.get("app_bg"))

        pad = sv(BASE_PADDING)
        med = sv(MEDIUM_PADDING)

        ScreenHeader(
            self.root,
            ICONS["goal"],
            "New Goal",
            on_back=lambda: self._nav("dashboard"),
        ).pack(fill="x", padx=pad, pady=(sv(20), sv(12)))

        body = ctk.CTkFrame(
            self.root,
            fg_color=COLORS.get("card_bg"),
            corner_radius=sv(16),
            border_width=1,
            border_color=COLORS.get("divider"),
        )
        body.pack(fill="both", expand=True, padx=pad, pady=(0, pad))

        form = ctk.CTkFrame(body, fg_color="transparent")
        form.pack(pady=med * 2, padx=med * 2)

        ctk.CTkLabel(
            form,
            text=f'{ICONS["goal"]}  Goal Name',
            font=font(13, "bold"),
            text_color=COLORS.get("text"),
        ).pack(anchor="w", pady=(0, sv(8)))

        self.name_entry = ctk.CTkEntry(
            form,
            width=sv(360),
            height=sv(40),
            corner_radius=sv(10),
            placeholder_text="e.g., New Laptop, Vacation, Emergency Fund",
            font=font(13),
            border_width=1,
            border_color=COLORS.get("divider"),
        )
        self.name_entry.pack(pady=(0, med))

        ctk.CTkLabel(
            form,
            text=f'{ICONS["amount"]}  Target Amount',
            font=font(13, "bold"),
            text_color=COLORS.get("text"),
        ).pack(anchor="w", pady=(0, sv(8)))

        self.target_entry = ctk.CTkEntry(
            form,
            width=sv(360),
            height=sv(40),
            corner_radius=sv(10),
            placeholder_text="e.g., 10,000,000",
            font=font(13),
            border_width=1,
            border_color=COLORS.get("divider"),
        )
        self.target_entry.pack(pady=(0, med * 2))

        ctk.CTkButton(
            form,
            text="+  Create Goal",
            command=self._do_add,
            fg_color=COLORS.get("accent"),
            hover_color=COLORS.get("primary"),
            corner_radius=sv(10),
            width=sv(220),
            height=sv(42),
            font=font(14, "bold"),
        ).pack()

        self._mark_built()

    def _do_add(self):
        name = self.name_entry.get().strip()
        if not name:
            mb.showwarning("Missing", "Please enter a goal name")
            return

        try:
            target = float(self.target_entry.get())
        except (TypeError, ValueError):
            mb.showwarning("Invalid amount", "Please enter a valid target amount")
            return

        if target <= 0:
            mb.showwarning("Invalid amount", "Target amount must be greater than zero")
            return

        if getattr(self, "user_id", None) is not None:
            self.advisor.add_goal(self.user_id, name, target)
            self.name_entry.delete(0, "end")
            self.target_entry.delete(0, "end")
            self._nav("dashboard")

    def refresh_ui(self, user_id=None):
        if user_id is not None:
            self.user_id = user_id
