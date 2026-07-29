import customtkinter as ctk
import tkinter.messagebox as mb
from utils.colors import COLORS
from utils.scale import sv, get_scale, set_scale
from utils.constants import ICONS, BASE_PADDING
from utils.theme_manager import theme_manager
from utils.ui_components import Card, font


class SettingsScreen:
    def __init__(self, advisor, master, on_navigate=None):
        self.advisor = advisor
        self.master = master
        self.on_navigate = on_navigate
        self.user_id = None
        self._build_ui()

    def _build_ui(self):
        self.root = ctk.CTkFrame(self.master, fg_color=COLORS.get('light_bg'))

        header = ctk.CTkFrame(self.root, fg_color='transparent')
        header.pack(fill='x', padx=sv(BASE_PADDING), pady=(sv(20), sv(8)))

        header_left = ctk.CTkFrame(header, fg_color='transparent')
        header_left.pack(side='left')

        ctk.CTkButton(
            header_left,
            text='←  Back',
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

        scroll = ctk.CTkScrollableFrame(
            self.root, fg_color='transparent',
            scrollbar_button_color=COLORS.get('primary'),
            scrollbar_button_hover_color=COLORS.get('accent'),
        )
        scroll.pack(fill='both', expand=True, padx=sv(BASE_PADDING),
                    pady=(0, sv(BASE_PADDING)))

        self._build_appearance_section(scroll)
        self._build_display_section(scroll)
        self._build_reset_section(scroll)
        self._build_about_section(scroll)

    def _make_section_header(self, parent, icon, title):
        h = ctk.CTkFrame(parent, fg_color='transparent')
        h.pack(fill='x', padx=sv(20), pady=(sv(16), sv(8)))
        ctk.CTkLabel(
            h, text=icon,
            font=font(15), text_color=COLORS.get('primary'),
        ).pack(side='left', padx=(0, sv(8)))
        ctk.CTkLabel(
            h, text=title,
            font=font(15, 'bold'), text_color=COLORS.get('text'),
        ).pack(side='left')
        return h

    def _build_appearance_section(self, scroll):
        section_card = Card(master=scroll, radius=sv(14))
        section_card.pack(fill='x', pady=(0, sv(12)))

        self._make_section_header(
            section_card, ICONS['theme_dark'], 'Appearance')

        mode_row = ctk.CTkFrame(section_card, fg_color='transparent')
        mode_row.pack(fill='x', padx=sv(20), pady=(sv(4), sv(8)))

        ctk.CTkLabel(
            mode_row, text='Dark mode',
            font=font(13), text_color=COLORS.get('text_secondary'),
        ).pack(side='left')

        self.mode_var = ctk.StringVar(value=theme_manager.mode.capitalize())
        ctk.CTkSwitch(
            mode_row, text='', variable=self.mode_var,
            onvalue='Dark', offvalue='Light',
            command=self._toggle_mode,
        ).pack(side='right')

    def _build_display_section(self, scroll):
        display_card = Card(master=scroll, radius=sv(14))
        display_card.pack(fill='x', pady=(0, sv(12)))

        self._make_section_header(
            display_card, ICONS['tips'], 'Display')

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
            command=self._toggle_tips,
        ).pack(side='right')

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

    def _build_reset_section(self, scroll):
        reset_card = Card(master=scroll, radius=sv(14))
        reset_card.pack(fill='x', pady=(0, sv(12)))

        ctk.CTkButton(
            reset_card,
            text='↺  Reset to Defaults',
            command=self._reset_defaults,
            fg_color=COLORS.get('elevated_bg'),
            hover_color=COLORS.get('divider'),
            text_color=COLORS.get('text'),
            corner_radius=sv(10), height=sv(40),
            font=font(13),
        ).pack(padx=sv(20), pady=sv(16), anchor='w')

    def _build_about_section(self, scroll):
        about_card = Card(master=scroll, radius=sv(14))
        about_card.pack(fill='x', pady=(0, sv(8)))

        about_inner = ctk.CTkFrame(about_card, fg_color='transparent')
        about_inner.pack(fill='x', padx=sv(20), pady=sv(16))

        ctk.CTkLabel(
            about_inner, text='ℹ  About',
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

    def _toggle_mode(self):
        theme_manager.set_mode(
            'dark' if self.mode_var.get() == 'Dark' else 'light')
        self.mode_var.set(theme_manager.mode.capitalize())

    def _toggle_tips(self):
        if self.user_id is not None:
            self.advisor.update_learning_tips_setting(
                self.user_id, self.tips_var.get() == 'On')

    def _on_scale_change(self, value):
        scale_pct = int(value.replace('%', '')) / 100.0
        set_scale(scale_pct)
        mb.showinfo(
            'Display Scale',
            'Display scale updated. Some elements may need a restart.',
        )

    def _reset_defaults(self):
        theme_manager.set_mode('dark')
        self.mode_var.set('Dark')
        self.tips_var.set('On')
        set_scale(1.0)
        self.scale_var.set('100%')
        if self.user_id is not None:
            self.advisor.update_learning_tips_setting(self.user_id, True)
        mb.showinfo('Success', 'All settings have been reset to defaults')

    def refresh_ui(self, user_id=None):
        if user_id is not None:
            self.user_id = user_id
        if self.user_id is not None:
            profile = self.advisor.get_user_profile(self.user_id)
            self.tips_var.set(
                'On' if profile.get('show_learning_tips', True) else 'Off')
        self.mode_var.set(theme_manager.mode.capitalize())

    def pack(self, *args, **kwargs):
        return self.root.pack(*args, **kwargs)

    def pack_forget(self, *args, **kwargs):
        return self.root.pack_forget(*args, **kwargs)