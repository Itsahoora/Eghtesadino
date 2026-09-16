import customtkinter as ctk
import tkinter.messagebox as mb
from utils.colors import COLORS
from utils.scale import sv, get_scale, set_scale
from utils.constants import ICONS, BASE_PADDING
from utils.preferences import (
    ACCENTS,
    get as get_pref,
    set as set_pref,
    resolve_mode,
)
from utils.theme_manager import theme_manager
from utils.ui_components import Card, ScreenHeader, BaseScreen, SectionTitle, font

__version__ = "1.0.0"


class SettingsScreen(BaseScreen):
    def __init__(self, advisor, master, on_navigate=None, on_logout=None):
        self.advisor = advisor
        self.master = master
        self.on_navigate = on_navigate
        self.on_logout = on_logout
        self.user_id = None
        self._build_ui()

    def _build_ui(self):
        self.root = ctk.CTkFrame(self.master, fg_color=COLORS.get("app_bg"))

        ScreenHeader(
            self.root,
            ICONS["settings"],
            "Settings",
            on_back=lambda: self._nav("dashboard"),
        ).pack(fill="x", padx=sv(BASE_PADDING), pady=(sv(20), sv(8)))

        scroll = ctk.CTkScrollableFrame(
            self.root,
            fg_color="transparent",
            scrollbar_button_color=COLORS.get("primary"),
            scrollbar_button_hover_color=COLORS.get("accent"),
        )
        scroll.pack(
            fill="both", expand=True, padx=sv(BASE_PADDING), pady=(0, sv(BASE_PADDING))
        )

        self._build_account_section(scroll)
        self._build_appearance_section(scroll)
        self._build_financial_section(scroll)
        self._build_display_section(scroll)
        self._build_about_section(scroll)
        self._mark_built()

    def _make_section_header(self, parent, icon, title):
        h = ctk.CTkFrame(parent, fg_color="transparent")
        h.pack(fill="x", padx=sv(20), pady=(sv(16), sv(8)))
        SectionTitle(h, icon, title).pack(side="left")
        return h

    def _build_account_section(self, scroll):
        account_card = Card(master=scroll, radius=sv(14))
        account_card.pack(fill="x", pady=(0, sv(12)))

        self._make_section_header(account_card, ICONS["user"], "Account")

        # Identity line — shows the current display name + username
        self.identity_label = ctk.CTkLabel(
            account_card,
            text="",
            font=font(12, "bold"),
            text_color=COLORS.get("text"),
        )
        self.identity_label.pack(anchor="w", padx=sv(20), pady=(sv(2), sv(10)))

        # Display name edit.
        name_row = ctk.CTkFrame(account_card, fg_color="transparent")
        name_row.pack(fill="x", padx=sv(20), pady=(sv(4), sv(10)))

        ctk.CTkLabel(
            name_row,
            text="Display name",
            font=font(13),
            text_color=COLORS.get("text_secondary"),
        ).pack(side="left")

        self.name_var = ctk.StringVar(value="")
        ctk.CTkEntry(
            name_row,
            textvariable=self.name_var,
            width=sv(160),
            height=sv(30),
            corner_radius=sv(8),
            fg_color=COLORS.get("input_bg"),
            font=font(12),
        ).pack(side="left", padx=(sv(8), sv(4)))

        ctk.CTkButton(
            name_row,
            text="Save",
            command=self._save_name,
            fg_color=COLORS.get("primary"),
            hover_color=COLORS.get("primary_hover"),
            corner_radius=sv(8),
            height=sv(30),
            width=sv(52),
            font=font(12, "bold"),
        ).pack(side="left")

        # Account actions.
        actions_row = ctk.CTkFrame(account_card, fg_color="transparent")
        actions_row.pack(fill="x", padx=sv(20), pady=(sv(2), sv(16)))

        ctk.CTkButton(
            actions_row,
            text="Change username",
            command=self._change_username_dialog,
            fg_color=COLORS.get("elevated_bg"),
            hover_color=COLORS.get("divider"),
            text_color=COLORS.get("text"),
            corner_radius=sv(8),
            height=sv(32),
            font=font(12),
        ).pack(side="left", padx=(0, sv(8)))

        ctk.CTkButton(
            actions_row,
            text="Change password",
            command=self._change_password_dialog,
            fg_color=COLORS.get("elevated_bg"),
            hover_color=COLORS.get("divider"),
            text_color=COLORS.get("text"),
            corner_radius=sv(8),
            height=sv(32),
            font=font(12),
        ).pack(side="left", padx=(0, sv(8)))

        ctk.CTkButton(
            actions_row,
            text="Log out",
            command=self._logout,
            fg_color=COLORS.get("primary"),
            hover_color=COLORS.get("primary_hover"),
            text_color=COLORS.get("text_on_primary"),
            corner_radius=sv(8),
            height=sv(32),
            width=sv(88),
            font=font(12, "bold"),
        ).pack(side="left")

        # Delete account — visually distinct, separated, requires confirmation
        delete_card = Card(master=scroll, radius=sv(14), bg_color="input_bg")
        delete_card.pack(fill="x", pady=(0, sv(12)))

        del_inner = ctk.CTkFrame(delete_card, fg_color="transparent")
        del_inner.pack(fill="x", padx=sv(20), pady=sv(14))

        ctk.CTkButton(
            del_inner,
            text="Delete account and all data",
            command=self._delete_account,
            fg_color=COLORS.get("danger"),
            hover_color=COLORS.get("warning"),
            text_color="#FFFFFF",
            corner_radius=sv(8),
            height=sv(34),
            width=sv(220),
            font=font(12, "bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            del_inner,
            text="This permanently removes your account and all transactions/goals. Cannot be undone.",
            font=font(10),
            text_color=COLORS.get("muted_text"),
        ).pack(anchor="w", pady=(sv(6), 0))

    def _save_name(self):
        value = self.name_var.get().strip()
        if not value or self.user_id is None:
            return
        if self.advisor.update_display_name(self.user_id, value):
            mb.showinfo("Success", "Display name updated")
            self._refresh_identity()
        else:
            mb.showerror("Error", "Could not update display name")

    def _refresh_identity(self):
        if self.user_id is None:
            return
        profile = self.advisor.get_user_profile(self.user_id)
        display = profile.get("display_name") or profile.get("username", "")
        username = profile.get("username", "")
        try:
            self.identity_label.configure(
                text=f"{ICONS['user']}  {display}  ·  @{username}"
            )
        except Exception:
            pass

    def _change_username_dialog(self):
        if self.user_id is None:
            return
        dlg = ctk.CTkToplevel(self.root)
        dlg.title("Change username")
        dlg.geometry(f"{sv(380)}x{sv(180)}")
        dlg.transient(self.root)
        dlg.grab_set()

        ctk.CTkLabel(dlg, text="New username", font=font(13)).pack(pady=(sv(16), sv(6)))
        entry = ctk.CTkEntry(
            dlg, width=sv(280), height=sv(34), font=font(13), corner_radius=sv(8)
        )
        entry.pack(pady=(0, sv(10)))
        entry.focus_set()

        def submit():
            val = entry.get().strip()
            ok, msg = self.advisor.change_username(self.user_id, val)
            if ok:
                dlg.destroy()
                mb.showinfo("Success", msg)
                self._refresh_identity()
            else:
                mb.showerror("Change username", msg)

        ctk.CTkButton(
            dlg,
            text="Update",
            command=submit,
            fg_color=COLORS.get("primary"),
            hover_color=COLORS.get("primary_hover"),
            corner_radius=sv(8),
            height=sv(32),
            font=font(12, "bold"),
        ).pack(pady=(sv(4), sv(8)))
        entry.bind("<Return>", lambda _e: submit())

    def _change_password_dialog(self):
        if self.user_id is None:
            return
        dlg = ctk.CTkToplevel(self.root)
        dlg.title("Change password")
        dlg.geometry(f"{sv(420)}x{sv(260)}")
        dlg.transient(self.root)
        dlg.grab_set()

        show_msg = ctk.CTkLabel(
            dlg, text="", font=font(10), text_color=COLORS.get("danger")
        )
        show_msg.pack(pady=(sv(6), 0))

        def row(label):
            ctk.CTkLabel(
                dlg, text=label, font=font(12), text_color=COLORS.get("text_secondary")
            ).pack()
            e = ctk.CTkEntry(
                dlg,
                width=sv(300),
                height=sv(32),
                show="*",
                font=font(12),
                corner_radius=sv(8),
            )
            e.pack(pady=(sv(4), sv(8)))
            return e

        current = row("Current password")
        new = row("New password")
        confirm = row("Confirm new password")

        def submit():
            cur = current.get()
            n = new.get()
            c = confirm.get()
            if n != c:
                show_msg.configure(text="New passwords do not match.")
                return
            ok, msg = self.advisor.change_password(self.user_id, cur, n)
            if ok:
                dlg.destroy()
                mb.showinfo("Success", msg)
            else:
                show_msg.configure(text=msg)

        ctk.CTkButton(
            dlg,
            text="Update password",
            command=submit,
            fg_color=COLORS.get("primary"),
            hover_color=COLORS.get("primary_hover"),
            corner_radius=sv(8),
            height=sv(34),
            font=font(12, "bold"),
        ).pack(pady=(sv(4), sv(8)))
        confirm.bind("<Return>", lambda _e: submit())

    def _logout(self):
        if self.user_id is None:
            return
        if callable(self.on_logout):
            self.on_logout()

    def _delete_account(self):
        if self.user_id is None:
            return
        confirm = mb.askyesno(
            "Delete account",
            "This will permanently delete your account and ALL your data "
            "(transactions and goals). This cannot be undone.\n\n"
            "Are you sure you want to continue?",
            icon="warning",
        )
        if not confirm:
            return
        ok = self.advisor.delete_account(self.user_id)
        if not ok:
            mb.showerror(
                "Delete account", "Could not delete your account. Please try again."
            )
            return
        if callable(self.on_logout):
            self.on_logout()

    def _build_appearance_section(self, scroll):
        section_card = Card(master=scroll, radius=sv(14))
        section_card.pack(fill="x", pady=(0, sv(12)))

        self._make_section_header(section_card, ICONS["theme_dark"], "Appearance")

        # Theme mode: Light / Dark / System
        mode_row = ctk.CTkFrame(section_card, fg_color="transparent")
        mode_row.pack(fill="x", padx=sv(20), pady=(sv(4), sv(8)))

        ctk.CTkLabel(
            mode_row,
            text="Theme",
            font=font(13),
            text_color=COLORS.get("text_secondary"),
        ).pack(side="left")

        theme_choices = ["Light", "Dark", "System"]
        current = get_pref("theme_mode")
        label = "System" if current == "system" else current.capitalize()
        if label not in theme_choices:
            label = "System"
        self.theme_var = ctk.StringVar(value=label)
        self.theme_menu = ctk.CTkOptionMenu(
            mode_row,
            values=theme_choices,
            variable=self.theme_var,
            command=self._on_theme_mode_change,
            width=sv(100),
            height=sv(30),
            fg_color=COLORS.get("input_bg"),
            dropdown_fg_color=COLORS.get("card_bg"),
            font=font(12),
        )
        self.theme_menu.pack(side="right")

        # Accent colour
        accent_row = ctk.CTkFrame(section_card, fg_color="transparent")
        accent_row.pack(fill="x", padx=sv(20), pady=(sv(4), sv(14)))

        ctk.CTkLabel(
            accent_row,
            text="Accent colour",
            font=font(13),
            text_color=COLORS.get("text_secondary"),
        ).pack(side="left")

        accent_choices = [name.capitalize() for name in ACCENTS.keys()]
        self.accent_var = ctk.StringVar(value=get_pref("accent").capitalize())
        ctk.CTkOptionMenu(
            accent_row,
            values=accent_choices,
            variable=self.accent_var,
            command=self._on_accent_change,
            width=sv(100),
            height=sv(30),
            fg_color=COLORS.get("input_bg"),
            dropdown_fg_color=COLORS.get("card_bg"),
            font=font(12),
        ).pack(side="right")

    def _on_theme_mode_change(self, value):
        key = value.lower()
        set_pref("theme_mode", key)
        concrete = resolve_mode(key)
        theme_manager.set_mode(concrete)

    def _on_accent_change(self, value):
        set_pref("accent", value.lower())
        # Rebuild the visible screen so all COLORS.get('primary') re-resolve
        if hasattr(self, "rebuild"):
            try:
                self.rebuild()
            except Exception:
                pass

    def _build_financial_section(self, scroll):
        section_card = Card(master=scroll, radius=sv(14))
        section_card.pack(fill="x", pady=(0, sv(12)))

        self._make_section_header(section_card, ICONS["amount"], "Financial")

        currency_row = ctk.CTkFrame(section_card, fg_color="transparent")
        currency_row.pack(fill="x", padx=sv(20), pady=(sv(4), sv(14)))

        ctk.CTkLabel(
            currency_row,
            text="Currency",
            font=font(13),
            text_color=COLORS.get("text_secondary"),
        ).pack(side="left")

        currency_choices = ["Tomans", "Dollar", "Euro"]
        current_currency = get_pref("currency")
        self.currency_var = ctk.StringVar(value=current_currency.capitalize())
        ctk.CTkOptionMenu(
            currency_row,
            values=currency_choices,
            variable=self.currency_var,
            command=self._on_currency_change,
            width=sv(100),
            height=sv(30),
            fg_color=COLORS.get("input_bg"),
            dropdown_fg_color=COLORS.get("card_bg"),
            font=font(12),
        ).pack(side="right")

    def _on_currency_change(self, value):
        set_pref("currency", value.lower())

    def _build_display_section(self, scroll):
        display_card = Card(master=scroll, radius=sv(14))
        display_card.pack(fill="x", pady=(0, sv(12)))

        self._make_section_header(display_card, ICONS["tips"], "Display")

        tips_row = ctk.CTkFrame(display_card, fg_color="transparent")
        tips_row.pack(fill="x", padx=sv(20), pady=(sv(4), sv(8)))

        ctk.CTkLabel(
            tips_row,
            text="Show learning tips",
            font=font(13),
            text_color=COLORS.get("text_secondary"),
        ).pack(side="left")

        self.tips_var = ctk.StringVar(value="On")
        ctk.CTkSwitch(
            tips_row,
            text="",
            variable=self.tips_var,
            onvalue="On",
            offvalue="Off",
            command=self._toggle_tips,
        ).pack(side="right")

        scale_row = ctk.CTkFrame(display_card, fg_color="transparent")
        scale_row.pack(fill="x", padx=sv(20), pady=(sv(4), sv(16)))

        ctk.CTkLabel(
            scale_row,
            text="Display scale",
            font=font(13),
            text_color=COLORS.get("text_secondary"),
        ).pack(side="left")

        scale_options = ["80%", "90%", "100%", "110%", "125%", "150%"]
        current_pct = f"{int(get_scale() * 100)}%"
        if current_pct not in scale_options:
            current_pct = "100%"

        self.scale_var = ctk.StringVar(value=current_pct)
        ctk.CTkOptionMenu(
            scale_row,
            values=scale_options,
            variable=self.scale_var,
            command=self._on_scale_change,
            width=sv(80),
            height=sv(32),
            fg_color=COLORS.get("input_bg"),
            dropdown_fg_color=COLORS.get("card_bg"),
            font=font(12),
        ).pack(side="right")

    def _build_about_section(self, scroll):
        about_card = Card(master=scroll, radius=sv(14))
        about_card.pack(fill="x", pady=(0, sv(8)))

        about_inner = ctk.CTkFrame(about_card, fg_color="transparent")
        about_inner.pack(fill="x", padx=sv(20), pady=sv(16))

        ctk.CTkLabel(
            about_inner,
            text="ℹ  About",
            font=font(14, "bold"),
            text_color=COLORS.get("text"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            about_inner,
            text=f"Eghtesadino  v{__version__}  —  Built for students",
            font=font(11),
            text_color=COLORS.get("muted_text"),
        ).pack(anchor="w", pady=(sv(4), 0))

        ctk.CTkLabel(
            about_inner,
            text="Itsahoora",
            font=font(11),
            text_color=COLORS.get("muted_text"),
        ).pack(anchor="w")

    def _toggle_tips(self):
        if self.user_id is not None:
            self.advisor.update_learning_tips_setting(
                self.user_id, self.tips_var.get() == "On"
            )

    def _on_scale_change(self, value):
        scale_pct = int(value.replace("%", "")) / 100.0
        set_scale(scale_pct)
        mb.showinfo(
            "Display Scale",
            "Display scale updated. Some elements may need a restart.",
        )

    def refresh_ui(self, user_id=None):
        if user_id is not None:
            self.user_id = user_id
        if self.user_id is not None:
            profile = self.advisor.get_user_profile(self.user_id)
            self.tips_var.set(
                "On" if profile.get("show_learning_tips", True) else "Off"
            )
            if hasattr(self, "name_var"):
                self.name_var.set(profile.get("display_name", ""))
            self._refresh_identity()
