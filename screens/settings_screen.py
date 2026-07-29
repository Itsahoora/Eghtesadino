import customtkinter as ctk
import tkinter.messagebox as mb
from tkinter import colorchooser
from utils.colors import COLORS
from utils.scale import sv, get_scale, set_scale
from utils.constants import ICONS, BASE_PADDING
from utils.theme_manager import theme_manager
from utils.ui_components import Card, font, animate_card_intro
from utils.localization import tr, get_available_languages, _get_lang
from utils.theme.colors import PRESETS


class SettingsScreen:
    def __init__(self, advisor, master, on_navigate=None):
        self.advisor = advisor
        self.master = master
        self.on_navigate = on_navigate
        self.user_id = None
        self._color_buttons = {}
        self._build_ui()

    def _build_ui(self):
        self.root = ctk.CTkFrame(self.master, fg_color=COLORS.get('light_bg'))

        header = ctk.CTkFrame(self.root, fg_color='transparent')
        header.pack(fill='x', padx=sv(BASE_PADDING), pady=(sv(20), sv(8)))

        header_left = ctk.CTkFrame(header, fg_color='transparent')
        header_left.pack(side='left')

        ctk.CTkButton(
            header_left,
            text=f'{ICONS["back"]}  {tr("back")}',
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
            header_right, text=tr('settings'),
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
        self._build_language_section(scroll)
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
        self.root.after(100, lambda: animate_card_intro(section_card))

        self._make_section_header(
            section_card, ICONS['theme_dark'], tr('appearance'))

        # Mode toggle
        mode_row = ctk.CTkFrame(section_card, fg_color='transparent')
        mode_row.pack(fill='x', padx=sv(20), pady=(sv(4), sv(8)))

        ctk.CTkLabel(
            mode_row, text=tr('theme_dark'),
            font=font(13), text_color=COLORS.get('text_secondary'),
        ).pack(side='left')

        self.mode_var = ctk.StringVar(value=theme_manager.mode.capitalize())
        ctk.CTkSwitch(
            mode_row, text='', variable=self.mode_var,
            onvalue='Dark', offvalue='Light',
            command=self._toggle_mode,
        ).pack(side='right')

        # Presets row
        presets_row = ctk.CTkFrame(section_card, fg_color='transparent')
        presets_row.pack(fill='x', padx=sv(20), pady=(sv(4), sv(8)))

        ctk.CTkLabel(
            presets_row, text=tr('themes'),
            font=font(13), text_color=COLORS.get('text_secondary'),
        ).pack(anchor='w', pady=(0, sv(6)))

        presets_frame = ctk.CTkFrame(presets_row, fg_color='transparent')
        presets_frame.pack(fill='x')

        current_preset = theme_manager.get_preset_name()
        self._preset_buttons = {}
        for name, label in [('default', tr('default')), ('blue', tr('blue')),
                            ('green', tr('green')), ('purple', tr('purple')),
                            ('orange', tr('orange'))]:
            is_active = current_preset == name
            btn = ctk.CTkButton(
                presets_frame, text=label,
                command=lambda n=name: self._apply_preset(n),
                fg_color=COLORS.get('primary') if is_active else COLORS.get('elevated_bg'),
                hover_color=COLORS.get('primary_hover') if is_active else COLORS.get('divider'),
                text_color=COLORS.get('text_on_primary') if is_active else COLORS.get('text'),
                corner_radius=sv(8), height=sv(32),
                font=font(11, 'bold'),
            )
            btn.pack(side='left', padx=(0, sv(6)), expand=True, fill='x')
            self._preset_buttons[name] = btn

        # Custom colors
        color_card = Card(master=scroll, radius=sv(14))
        color_card.pack(fill='x', pady=(0, sv(12)))

        self._make_section_header(
            color_card, ICONS['palette'], tr('custom_colors'))

        color_tokens = [
            ('primary', tr('primary_color')),
            ('accent', tr('accent_color')),
            ('dark_bg', tr('bg_color')),
            ('card_bg', tr('card_color')),
            ('elevated_bg', tr('sidebar_color')),
            ('text', tr('text_color')),
        ]

        self._color_vars = {}
        for token, label in color_tokens:
            row = ctk.CTkFrame(color_card, fg_color='transparent')
            row.pack(fill='x', padx=sv(20), pady=(sv(4), sv(4)))

            ctk.CTkLabel(
                row, text=label,
                font=font(13), text_color=COLORS.get('text_secondary'),
            ).pack(side='left')

            current_val = theme_manager.get_color(token)
            var = ctk.StringVar(value=current_val)
            self._color_vars[token] = (var, None)

            btn = ctk.CTkButton(
                row, text='  \u25CF',
                command=lambda t=token, v=var: self._pick_color(t, v),
                fg_color=current_val,
                hover_color='#555555',
                text_color=COLORS.get('text_on_primary'),
                corner_radius=sv(6), height=sv(28), width=sv(40),
                font=font(10),
            )
            btn.pack(side='right')
            self._color_vars[token] = (var, btn)

        apply_btn = ctk.CTkButton(
            color_card, text=tr('apply'),
            command=self._apply_custom_colors,
            fg_color=COLORS.get('accent'),
            hover_color=COLORS.get('primary'),
            corner_radius=sv(8), height=sv(36),
            font=font(12, 'bold'),
        )
        apply_btn.pack(padx=sv(20), pady=sv(12), anchor='e')

    def _build_display_section(self, scroll):
        display_card = Card(master=scroll, radius=sv(14))
        display_card.pack(fill='x', pady=(0, sv(12)))

        self._make_section_header(
            display_card, ICONS['tips'], tr('display'))

        tips_row = ctk.CTkFrame(display_card, fg_color='transparent')
        tips_row.pack(fill='x', padx=sv(20), pady=(sv(4), sv(8)))

        ctk.CTkLabel(
            tips_row, text=tr('show_learning_tips'),
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
            scale_row, text=tr('display_scale'),
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

    def _build_language_section(self, scroll):
        lang_card = Card(master=scroll, radius=sv(14))
        lang_card.pack(fill='x', pady=(0, sv(12)))

        self._make_section_header(
            lang_card, ICONS['language'], tr('language'))

        self.lang_var = ctk.StringVar(value=_get_lang())
        lang_list = ctk.CTkFrame(lang_card, fg_color='transparent')
        lang_list.pack(fill='x', padx=sv(20), pady=(sv(4), sv(16)))

        for code, name in get_available_languages():
            is_active = code == _get_lang()
            btn = ctk.CTkButton(
                lang_list, text=name,
                command=lambda c=code: self._set_language(c),
                fg_color=COLORS.get('primary') if is_active else COLORS.get('elevated_bg'),
                hover_color=COLORS.get('primary_hover') if is_active else COLORS.get('divider'),
                text_color=COLORS.get('text_on_primary') if is_active else COLORS.get('text'),
                corner_radius=sv(8), height=sv(32),
                font=font(12),
            )
            btn.pack(side='left', padx=sv(4))
            btn.bind('<Button-1>', lambda e, b=btn: self._highlight_lang(b))

    def _highlight_lang(self, btn):
        for child in btn.master.winfo_children():
            try:
                child.configure(
                    fg_color=COLORS.get('elevated_bg'),
                    hover_color=COLORS.get('divider'),
                    text_color=COLORS.get('text'),
                )
            except Exception:
                pass
        btn.configure(
            fg_color=COLORS.get('primary'),
            hover_color=COLORS.get('primary_hover'),
            text_color=COLORS.get('text_on_primary'),
        )

    def _build_reset_section(self, scroll):
        reset_card = Card(master=scroll, radius=sv(14))
        reset_card.pack(fill='x', pady=(0, sv(12)))

        ctk.CTkButton(
            reset_card,
            text=f'{ICONS["reset"]}  {tr("reset_defaults")}',
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
            about_inner, text=f'{ICONS["info"]}  {tr("about")}',
            font=font(14, 'bold'), text_color=COLORS.get('text'),
        ).pack(anchor='w')

        ctk.CTkLabel(
            about_inner,
            text=tr('app_version'),
            font=font(11), text_color=COLORS.get('muted_text'),
        ).pack(anchor='w', pady=(sv(4), 0))

        ctk.CTkLabel(
            about_inner,
            text=tr('by'),
            font=font(11), text_color=COLORS.get('muted_text'),
        ).pack(anchor='w')

    def _nav(self, target):
        if callable(self.on_navigate):
            self.on_navigate(target)

    def _toggle_mode(self):
        theme_manager.set_mode(
            'dark' if self.mode_var.get() == 'Dark' else 'light')
        self.mode_var.set(theme_manager.mode.capitalize())

    def _apply_preset(self, name):
        theme_manager.apply_preset(name)
        self.mode_var.set(theme_manager.mode.capitalize())
        self._update_preset_buttons()

    def _update_preset_buttons(self):
        current = theme_manager.get_preset_name()
        for name, btn in self._preset_buttons.items():
            is_active = name == current
            try:
                btn.configure(
                    fg_color=COLORS.get('primary') if is_active else COLORS.get('elevated_bg'),
                    hover_color=COLORS.get('primary_hover') if is_active else COLORS.get('divider'),
                    text_color=COLORS.get('text_on_primary') if is_active else COLORS.get('text'),
                )
            except Exception:
                pass

    def _pick_color(self, token, var):
        current = var.get()
        result = colorchooser.askcolor(
            title=tr('custom_colors'), initialcolor=current,
        )
        if result and result[1]:
            var.set(result[1])
            _, btn = self._color_vars.get(token, (None, None))
            if btn is not None:
                try:
                    btn.configure(fg_color=result[1])
                except Exception:
                    pass

    def _apply_custom_colors(self):
        for token, (var, btn) in self._color_vars.items():
            value = var.get()
            if value:
                theme_manager.set_color(token, value)
        self._update_preset_buttons()
        mb.showinfo(tr('success'), tr('colors_applied'))

    def _toggle_tips(self):
        if self.user_id is not None:
            self.advisor.update_learning_tips_setting(
                self.user_id, self.tips_var.get() == 'On')

    def _on_scale_change(self, value):
        scale_pct = int(value.replace('%', '')) / 100.0
        set_scale(scale_pct)
        mb.showinfo(
            tr('display_scale'),
            tr('scale_changed'),
        )

    def _set_language(self, lang):
        if lang == _get_lang():
            return
        from utils.localization import set_language
        set_language(lang)
        self.lang_var.set(lang)
        mb.showinfo(
            tr('language'),
            tr('language_changed'),
        )

    def _reset_defaults(self):
        theme_manager.clear_overrides()
        theme_manager.set_mode('dark')
        self.mode_var.set('Dark')
        self.tips_var.set('On')
        set_scale(1.0)
        self.scale_var.set('100%')
        if self.user_id is not None:
            self.advisor.update_learning_tips_setting(self.user_id, True)
        self._update_preset_buttons()
        mb.showinfo(tr('success'), tr('reset_complete'))

    def refresh_ui(self, user_id=None):
        if user_id is not None:
            self.user_id = user_id
        if self.user_id is not None:
            profile = self.advisor.get_user_profile(self.user_id)
            self.tips_var.set(
                'On' if profile.get('show_learning_tips', True) else 'Off')
        self.mode_var.set(theme_manager.mode.capitalize())
        self.lang_var.set(_get_lang())
        self._update_preset_buttons()

    def pack(self, *args, **kwargs):
        return self.root.pack(*args, **kwargs)

    def pack_forget(self, *args, **kwargs):
        return self.root.pack_forget(*args, **kwargs)