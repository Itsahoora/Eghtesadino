import customtkinter as ctk
import tkinter.messagebox as mb
from utils.colors import COLORS
from utils.scale import sv
from utils.constants import ICONS
from utils.ui_components import TitleLabel, BodyLabel, MutedLabel, BaseScreen, font


class LoginScreen(BaseScreen):
    def __init__(self, advisor, master, on_success=None):
        self.advisor = advisor
        self.master = master
        self.on_success = on_success
        self._build_ui()

    def _build_ui(self):
        self.root = ctk.CTkFrame(self.master, fg_color=COLORS.get("app_bg"))

        container = ctk.CTkFrame(
            self.root,
            fg_color=COLORS.get("card_bg"),
            corner_radius=sv(22),
            border_width=1,
            border_color=COLORS.get("divider"),
        )
        container.place(relx=0.5, rely=0.5, anchor="center")

        inner = ctk.CTkFrame(container, fg_color="transparent")
        inner.pack(padx=sv(40), pady=sv(36))

        ctk.CTkLabel(
            inner,
            text=ICONS["balance"],
            font=font(36),
            text_color=COLORS.get("primary"),
        ).pack(pady=(0, sv(4)))

        TitleLabel(
            master=inner,
            text="Eghtesadino",
            size=26,
            text_color=COLORS.get("text"),
        ).pack(pady=(0, sv(4)))

        MutedLabel(
            master=inner,
            text="Smart budgeting & personalized advice",
            size=12,
        ).pack(pady=(0, sv(28)))

        BodyLabel(
            master=inner,
            text="Username",
            size=12,
            text_color=COLORS.get("text_secondary"),
        ).pack(anchor="w", padx=sv(4))

        self.username_input = ctk.CTkEntry(
            inner,
            width=sv(320),
            height=sv(42),
            corner_radius=sv(10),
            placeholder_text=f'{ICONS["user"]}  Enter your username',
            font=font(13),
            border_width=1,
            border_color=COLORS.get("divider"),
        )
        self.username_input.pack(pady=(sv(6), sv(16)))

        BodyLabel(
            master=inner,
            text="Password",
            size=12,
            text_color=COLORS.get("text_secondary"),
        ).pack(anchor="w", padx=sv(4))

        pwd_frame = ctk.CTkFrame(inner, fg_color="transparent")
        pwd_frame.pack(pady=(sv(6), sv(24)))

        self.password_input = ctk.CTkEntry(
            pwd_frame,
            width=sv(260),
            height=sv(42),
            corner_radius=sv(10),
            placeholder_text=f'{ICONS["lock"]}  Enter your password',
            show="*",
            font=font(13),
            border_width=1,
            border_color=COLORS.get("divider"),
        )
        self.password_input.pack(side="left")

        self._show_pwd = False
        self.pwd_toggle_button = ctk.CTkButton(
            pwd_frame,
            text=ICONS["show"],
            width=sv(44),
            height=sv(42),
            command=self._toggle_password,
            corner_radius=sv(10),
            fg_color=COLORS.get("elevated_bg"),
            hover_color=COLORS.get("divider"),
            text_color=COLORS.get("text_secondary"),
            font=font(14),
        )
        self.pwd_toggle_button.pack(side="left", padx=(sv(8), 0))

        ctk.CTkButton(
            inner,
            text=f'{ICONS["forward"]}  Sign In',
            width=sv(320),
            height=sv(44),
            corner_radius=sv(10),
            fg_color=COLORS.get("primary"),
            hover_color=COLORS.get("primary_hover"),
            font=font(14, "bold"),
            command=self._on_login,
        ).pack(pady=(0, sv(16)))

        register_lbl = ctk.CTkLabel(
            inner,
            text="Don't have an account?  Create one",
            text_color=COLORS.get("primary"),
            cursor="hand2",
            font=font(12),
        )
        register_lbl.pack(pady=(0, sv(4)))
        register_lbl.bind("<Button-1>", lambda e: self._on_register())

        # Bind Return on the entries (not the toplevel) so the binding lives
        # only while the login screen exists and doesn't leak to other screens.
        for entry in (self.username_input, self.password_input):
            entry.bind("<Return>", lambda e: self._on_login())

        self._mark_built()

    def _toggle_password(self):
        self._show_pwd = not self._show_pwd
        self.password_input.configure(show="" if self._show_pwd else "*")
        icon = ICONS["hide"] if self._show_pwd else ICONS["show"]
        try:
            self.pwd_toggle_button.configure(text=icon)
        except Exception:
            pass

    def _on_login(self):
        username = self.username_input.get().strip()
        password = self.password_input.get().strip()
        if not username or not password:
            mb.showwarning("Missing", "Please enter both username and password")
            return

        user = self.advisor.login_user(username, password)
        if user:
            mb.showinfo(
                "Welcome", f'Welcome back, {user.get("display_name", username)}!'
            )
            if callable(self.on_success):
                try:
                    self.on_success(user["id"])
                except Exception:
                    pass
        else:
            mb.showerror("Login failed", "Invalid username or password")

    def _on_register(self):
        username = self.username_input.get().strip()
        password = self.password_input.get().strip()
        if not username or not password:
            mb.showwarning("Missing", "Enter a username and password to register")
            return
        ok = self.advisor.register_user(username, password)
        if ok:
            mb.showinfo("Registered", "Account created — you can now sign in")
            self.username_input.delete(0, "end")
            self.password_input.delete(0, "end")
        else:
            mb.showerror("Error", "Registration failed (username may be taken)")

    def reset(self):
        """Clear the form so another user can log in cleanly"""
        self.username_input.delete(0, "end")
        self.password_input.delete(0, "end")
        if self._show_pwd:
            self._toggle_password()
