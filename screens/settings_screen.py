import customtkinter as ctk
import tkinter.messagebox as mb
from utils.colors import COLORS
from utils.scale import sv, get_scale, set_scale
from utils.constants import ICONS, BASE_PADDING
from utils.theme_manager import theme_manager
from utils.ui_components import (
    MutedLabel,
    Card, font, animate_card_intro,
)


class SettingsScreen:
    def __init__(self, advisor, master, on_navigate=None):
        self.advisor = advisor
        self.master = master
        self.on_navigate = on_navigate
        self.user_id = None
        self._build_ui()

    def _build_ui(self):
        self.root = ctk.CTkFrame(self.master, fg_color=COLORS.get('light_bg'))

        # ── Header ──
        header = ctk.CTkFrame(self.root, fg_color='transparent')
        header.pack(fill='x', padx=sv(BASE_PADDING), pady=(sv(20), sv(8)))

        header_left = ctk.CTkFrame(header, fg_color='transparent')
        header_left.pack(side='left')

        ctk.CTkButton(
            header_left,
            text=f'{ICONS["back"]}  Back',
            command=lambda: self._nav('dashboard'),
            fg_color=COLORS.get('elevated_bg'),
            hover_color=COLORS.get('divider'),
            text_color=COLORS.get('text'),
            corner_radius=sv(8), height=sv(34),
            font=font(12),
        ).pack(side='left')

        header_right = ctk.CTkFrame(header, fg_color='transparent')
        header_right.pack(side='right')

        ctk.CTkLabel(
            header_right, text=ICONS['settings'],
            font=font(18), text_color=COLORS.get('primary'),
        ).pack(side='left', padx=(0, sv(6)))

        ctk.CTkLabel(
            header_right, text='Settings',
            font=font(20, 'bold'), text_color=COLORS.get('text'),
        ).pack(side='left')

        # ── Scrollable body ──
        scroll = ctk.CTkScrollableFrame(
            self.root, fg_color='transparent',
            scrollbar_button_color=COLORS.get('primary'),
            scrollbar_button_hover_color=COLORS.get('accent'),
        )
        scroll.pack(fill='both', expand=True, padx=sv(BASE_PADDING),
                    pady=(0, sv(BASE_PADDING)))

        # ── Theme section ──
        theme_card = Card(master=scroll, radius=sv(14))
        theme_card.pack(fill='x', pady=(0, sv(12)))
        self.root.after(100, lambda: animate_card_intro(theme_card))

        section_header = ctk.CTkFrame(theme_card, fg_color='transparent')
        section_header.pack(fill='x', padx=sv(20), pady=(sv(16), sv(8)))

        ctk.CTkLabel(
            section_header, text=ICONS['theme_dark'],
            font=font(15), text_color=COLORS.get('primary'),
        ).pack(side='left', padx=(0, sv(8)))

        ctk.CTkLabel(
            section_header, text='Appearance',
            font=font(15, 'bold'), text_color=COLORS.get('text'),
        ).pack(side='left')

        # Theme toggle row
        theme_row = ctk.CTkFrame(theme_card, fg_color='transparent')
        theme_row.pack(fill='x', padx=sv(20), pady=(sv(4), sv(16)))

        ctk.CTkLabel(
            theme_row, text='Dark mode',
            font=font(13), text_color=COLORS.get('text_secondary'),
        ).pack(side='left')

        self.theme_var = ctk.StringVar(value=theme_manager.mode.capitalize())
        self.theme_switch = ctk.CTkSwitch(
            theme_row, text='', variable=self.theme_var,
            onvalue='Dark', offvalue='Light',
            command=self._toggle_theme,
        )
        self.theme_switch.pack(side='right')

        # ── Privacy section ──
        privacy_card = Card(master=scroll, radius=sv(14))
        privacy_card.pack(fill='x', pady=(0, sv(12)))

        sec2 = ctk.CTkFrame(privacy_card, fg_color='transparent')
        sec2.pack(fill='x', padx=sv(20), pady=(sv(16), sv(8)))

        ctk.CTkLabel(
            sec2, text=ICONS['lock'],
            font=font(15), text_color=COLORS.get('warning'),
        ).pack(side='left', padx=(0, sv(8)))

        ctk.CTkLabel(
            sec2, text='Privacy',
            font=font(15, 'bold'), text_color=COLORS.get('text'),
        ).pack(side='left')

        privacy_row = ctk.CTkFrame(privacy_card, fg_color='transparent')
        privacy_row.pack(fill='x', padx=sv(20), pady=(sv(4), sv(16)))

        ctk.CTkLabel(
            privacy_row, text='Enable privacy mode',
            font=font(13), text_color=COLORS.get('text_secondary'),
        ).pack(side='left')

        self.privacy_var = ctk.StringVar(value='Off')
        ctk.CTkSwitch(
            privacy_row, text='', variable=self.privacy_var,
            onvalue='On', offvalue='Off',
            command=self._toggle_privacy,
        ).pack(side='right')

        # ── Display section ──
        display_card = Card(master=scroll, radius=sv(14))
        display_card.pack(fill='x', pady=(0, sv(12)))

        sec3 = ctk.CTkFrame(display_card, fg_color='transparent')
        sec3.pack(fill='x', padx=sv(20), pady=(sv(16), sv(8)))

        ctk.CTkLabel(
            sec3, text=ICONS['tips'],
            font=font(15), text_color=COLORS.get('accent'),
        ).pack(side='left', padx=(0, sv(8)))

        ctk.CTkLabel(
            sec3, text='Display',
            font=font(15, 'bold'), text_color=COLORS.get('text'),
        ).pack(side='left')

        # Tips toggle
        tips_row = ctk.CTkFrame(display_card, fg_color='transparent')
        tips_row.pack(fill='x', padx=sv(20), pady=(sv(4), sv(8)))

        ctk.CTkLabel(
            tips_row, text='Show learning tips',
            font=font(13), text_color=COLORS.get('text_secondary'),
        ).pack(side='left')

        self.tips_var = ctk.StringVar(value='On')
        ctk.CTkSwitch(
            tips_row, text='', variable=self.tips_var,
            onvalue='On', offvalue='Off',
            command=self._toggle_learning_tips,
        ).pack(side='right')

        # Divider
        ctk.CTkFrame(
            display_card, height=1, fg_color=COLORS.get('divider'),
        ).pack(fill='x', padx=sv(20), pady=(sv(4), sv(4)))

        # Compact toggle
        compact_row = ctk.CTkFrame(display_card, fg_color='transparent')
        compact_row.pack(fill='x', padx=sv(20), pady=(sv(4), sv(8)))

        ctk.CTkLabel(
            compact_row, text='Compact layout',
            font=font(13), text_color=COLORS.get('text_secondary'),
        ).pack(side='left')

        self.compact_var = ctk.StringVar(value='Off')
        ctk.CTkSwitch(
            compact_row, text='', variable=self.compact_var,
            onvalue='On', offvalue='Off',
            command=self._toggle_compact_mode,
        ).pack(side='right')

        # Divider
        ctk.CTkFrame(
            display_card, height=1, fg_color=COLORS.get('divider'),
        ).pack(fill='x', padx=sv(20), pady=(sv(4), sv(4)))

        # Scale selector
        scale_row = ctk.CTkFrame(display_card, fg_color='transparent')
        scale_row.pack(fill='x', padx=sv(20), pady=(sv(4), sv(16)))

        ctk.CTkLabel(
            scale_row, text='Display scale',
            font=font(13), text_color=COLORS.get('text_secondary'),
        ).pack(side='left')

        scale_options = ['80%', '90%', '100%', '110%', '125%', '150%']
        current_pct = f'{int(get_scale() * 100)}%'
        if current_pct not in scale_options:
            current_pct = '100%'

        self.scale_var = ctk.StringVar(value=current_pct)
        ctk.CTkOptionMenu(
            scale_row, values=scale_options, variable=self.scale_var,
            command=self._on_scale_change,
            width=sv(80), height=sv(32),
            fg_color=COLORS.get('input_bg'),
            dropdown_fg_color=COLORS.get('card_bg'), font=font(12),
        ).pack(side='right')

        # ── Reset section ──
        reset_card = Card(master=scroll, radius=sv(14))
        reset_card.pack(fill='x', pady=(0, sv(12)))

        ctk.CTkButton(
            reset_card,
            text=f'{ICONS["reset"]}  Reset to Defaults',
            command=self._reset_defaults,
            fg_color=COLORS.get('elevated_bg'),
            hover_color=COLORS.get('divider'),
            text_color=COLORS.get('text'),
            corner_radius=sv(10), height=sv(40),
            font=font(13),
        ).pack(padx=sv(20), pady=sv(16), anchor='w')

        # ── About section ──
        about_card = Card(master=scroll, radius=sv(14))
        about_card.pack(fill='x', pady=(0, sv(8)))

        about_inner = ctk.CTkFrame(about_card, fg_color='transparent')
        about_inner.pack(fill='x', padx=sv(20), pady=sv(16))

        ctk.CTkLabel(
            about_inner, text=f'{ICONS["info"]}  About',
            font=font(14, 'bold'), text_color=COLORS.get('text'),
        ).pack(anchor='w')

        ctk.CTkLabel(
            about_inner,
            text='Eghtesadino  v3  —  Built for students',
            font=font(11), text_color=COLORS.get('muted_text'),
        ).pack(anchor='w', pady=(sv(4), 0))

        ctk.CTkLabel(
            about_inner,
            text='Itsahoora',
            font=font(11), text_color=COLORS.get('muted_text'),
        ).pack(anchor='w')

    def _nav(self, target):
        if callable(self.on_navigate):
            self.on_navigate(target)

    def _toggle_theme(self):
        theme_manager.set_mode(
            'dark' if self.theme_var.get() == 'Dark' else 'light')
        self.theme_var.set(theme_manager.mode.capitalize())

    def _toggle_privacy(self):
        if self.user_id is not None:
            self.advisor.update_privacy_setting(
                self.user_id, self.privacy_var.get() == 'On')

    def _toggle_learning_tips(self):
        if self.user_id is not None:
            self.advisor.update_learning_tips_setting(
                self.user_id, self.tips_var.get() == 'On')

    def _toggle_compact_mode(self):
        if self.user_id is not None:
            self.advisor.update_compact_mode_setting(
                self.user_id, self.compact_var.get() == 'On')

    def _on_scale_change(self, value):
        """Apply new scale when user selects from dropdown."""
        scale_pct = int(value.replace('%', '')) / 100.0
        set_scale(scale_pct)
        mb.showinfo(
            "Scale Changed",
            "Display scale updated. Some elements may need a restart to fully adjust."
        )

    def _reset_defaults(self):
        theme_manager.reset()
        self.theme_var.set(theme_manager.mode.capitalize())
        self.privacy_var.set('Off')
        self.tips_var.set('On')
        self.compact_var.set('Off')
        set_scale(1.0)
        self.scale_var.set('100%')
        if self.user_id is not None:
            self.advisor.update_privacy_setting(self.user_id, False)
            self.advisor.update_learning_tips_setting(self.user_id, True)
            self.advisor.update_compact_mode_setting(self.user_id, False)

    def refresh_ui(self, user_id=None):
        if user_id is not None:
            self.user_id = user_id
        if self.user_id is not None:
            profile = self.advisor.get_user_profile(self.user_id)
            self.privacy_var.set(
                'On' if profile.get('privacy_enabled') else 'Off')
            self.tips_var.set(
                'On' if profile.get('show_learning_tips', True) else 'Off')
            self.compact_var.set(
                'On' if profile.get('compact_mode', False) else 'Off')
            self.theme_var.set(theme_manager.mode.capitalize())
            current_pct = f'{int(get_scale() * 100)}%'
            self.scale_var.set(current_pct)

    def pack(self, *args, **kwargs):
        return self.root.pack(*args, **kwargs)

    def pack_forget(self, *args, **kwargs):
        return self.root.pack_forget(*args, **kwargs)
