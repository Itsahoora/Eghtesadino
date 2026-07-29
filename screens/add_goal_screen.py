import customtkinter as ctk
from utils.colors import COLORS
from utils.scale import sv
from utils.constants import ICONS, BASE_PADDING, MEDIUM_PADDING
from utils.ui_components import Card, TitleLabel, font, animate_card_intro


class AddGoalScreen:
    def __init__(self, advisor, master, on_navigate=None):
        self.advisor = advisor
        self.master = master
        self.on_navigate = on_navigate
        self.user_id = None
        self._build_ui()

    def _build_ui(self):
        self.root = ctk.CTkFrame(self.master, fg_color=COLORS.get('light_bg'))

        pad = sv(BASE_PADDING)
        med = sv(MEDIUM_PADDING)

        # ── Header ──
        header = ctk.CTkFrame(self.root, fg_color='transparent')
        header.pack(fill='x', padx=pad, pady=(sv(20), sv(12)))

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
            header_right, text=ICONS['goal'],
            font=font(18), text_color=COLORS.get('accent'),
        ).pack(side='left', padx=(0, sv(6)))

        ctk.CTkLabel(
            header_right, text='New Goal',
            font=font(20, 'bold'), text_color=COLORS.get('text'),
        ).pack(side='left')

        # ── Card ──
        body = ctk.CTkFrame(
            self.root, fg_color=COLORS.get('card_bg'),
            corner_radius=sv(16),
        )
        body.pack(fill='both', expand=True, padx=pad, pady=(0, pad))
        self.root.after(100, lambda: animate_card_intro(body))

        # ── Form ──
        form = ctk.CTkFrame(body, fg_color='transparent')
        form.pack(pady=med * 2, padx=med * 2)

        # Goal name
        ctk.CTkLabel(
            form, text=f'{ICONS["goal"]}  Goal Name',
            font=font(13, 'bold'), text_color=COLORS.get('text'),
        ).pack(anchor='w', pady=(0, sv(8)))

        self.name_entry = ctk.CTkEntry(
            form, width=sv(360), height=sv(44),
            corner_radius=sv(10),
            placeholder_text='e.g., New Laptop, Vacation, Emergency Fund',
            font=font(13),
            border_width=1, border_color=COLORS.get('divider'),
        )
        self.name_entry.pack(pady=(0, med))

        # Target amount
        ctk.CTkLabel(
            form, text=f'{ICONS["amount"]}  Target Amount',
            font=font(13, 'bold'), text_color=COLORS.get('text'),
        ).pack(anchor='w', pady=(0, sv(8)))

        self.target_entry = ctk.CTkEntry(
            form, width=sv(360), height=sv(44),
            corner_radius=sv(10),
            placeholder_text='e.g., 10,000,000',
            font=font(13),
            border_width=1, border_color=COLORS.get('divider'),
        )
        self.target_entry.pack(pady=(0, med * 2))

        # Create button
        ctk.CTkButton(
            form, text=f'{ICONS["add"]}  Create Goal',
            command=self._do_add,
            fg_color=COLORS.get('accent'),
            hover_color=COLORS.get('primary'),
            corner_radius=sv(10), width=sv(220), height=sv(46),
            font=font(14, 'bold'),
        ).pack()

    def _nav(self, target):
        if callable(self.on_navigate):
            self.on_navigate(target)

    def _do_add(self):
        name = self.name_entry.get().strip()
        try:
            target = float(self.target_entry.get())
        except Exception:
            target = 0.0

        if name and getattr(self, 'user_id', None) is not None:
            self.advisor.add_goal(self.user_id, name, target)
            self.name_entry.delete(0, 'end')
            self.target_entry.delete(0, 'end')
            self._nav('dashboard')

    def refresh_ui(self, user_id=None):
        if user_id is not None:
            self.user_id = user_id

    def pack(self, *args, **kwargs):
        return self.root.pack(*args, **kwargs)

    def pack_forget(self, *args, **kwargs):
        return self.root.pack_forget(*args, **kwargs)
