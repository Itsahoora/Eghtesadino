import customtkinter as ctk
import tkinter.messagebox as mb
from utils.colors import COLORS
from utils.scale import sv
from utils.constants import (
    INCOME_CATEGORIES, EXPENSE_CATEGORIES,
    BASE_PADDING, MEDIUM_PADDING,
    ICONS, FONT_FAMILY,
)
from utils.ui_components import (
    MutedLabel, Card, ProgressBar, BaseScreen, SectionTitle, Donut, font,
)
from utils.preferences import format_money


class DashboardScreen(BaseScreen):
    def __init__(self, advisor, master, on_navigate=None):
        self.advisor = advisor
        self.master = master
        self.on_navigate = on_navigate
        self.user_id = None
        self.show_learning_tips = True
        self._build_ui()

    def _build_ui(self):
        pad = sv(BASE_PADDING)
        med = sv(MEDIUM_PADDING)

        self.root = ctk.CTkScrollableFrame(
            self.master,
            fg_color=COLORS.get('app_bg'),
            scrollbar_button_color=COLORS.get('primary'),
            scrollbar_button_hover_color=COLORS.get('accent'),
        )

        self.content = ctk.CTkFrame(self.root, fg_color='transparent')
        self.content.pack(fill='both', expand=True, padx=pad)

        self.welcome_label = ctk.CTkLabel(
            self.content, text='', font=font(13),
            text_color=COLORS.get('muted_text'),
        )
        self.welcome_label.pack(fill='x', pady=(sv(16), 0))

        self._build_header(med)
        self.alerts_frame = ctk.CTkFrame(self.content, fg_color='transparent')
        self.alerts_frame.pack(fill='x', pady=(0, med))
        self._build_balance_card(med)
        self._build_stats_row(med)
        self._build_goals_card(med)
        self._build_transactions_card(med)
        self._build_form_card(med)
        self._build_learning_card()
        self._mark_built()

    def _build_header(self, med):
        header = ctk.CTkFrame(self.content, fg_color='transparent')
        header.pack(fill='x', pady=(sv(20), med))

        header_left = ctk.CTkFrame(header, fg_color='transparent')
        header_left.pack(side='left')

        ctk.CTkLabel(
            header_left, text=ICONS['dashboard'],
            font=font(20), text_color=COLORS.get('primary'),
        ).pack(side='left', padx=(0, sv(8)))

        ctk.CTkLabel(
            header_left, text='Dashboard',
            font=font(20, 'bold'), text_color=COLORS.get('text'),
        ).pack(side='left')

        header_right = ctk.CTkFrame(header, fg_color='transparent')
        header_right.pack(side='right')

        ctk.CTkButton(
            header_right, text='Reports',
            command=lambda: self._nav('reports'),
            fg_color=COLORS.get('primary'),
            hover_color=COLORS.get('primary_hover'),
            corner_radius=sv(20), height=sv(36), width=sv(80),
            font=font(12),
        ).pack(side='left', padx=(0, sv(6)))

        ctk.CTkButton(
            header_right, text='Settings',
            command=lambda: self._nav('settings'),
            fg_color=COLORS.get('elevated_bg'),
            hover_color=COLORS.get('divider'),
            text_color=COLORS.get('text'),
            corner_radius=sv(20), height=sv(36), width=sv(80),
            font=font(12),
        ).pack(side='left')

    def _build_balance_card(self, med):
        """Balance hero: brand-tinted panel with a savings-rate donut"""
        self.balance_card = Card(master=self.content, radius=sv(16),
                                  bg_color='hero_bg')
        self.balance_card.pack(fill='x', pady=(0, med))

        card_fill = COLORS.get('hero_bg')
        try:
            self.balance_card.configure(fg_color=card_fill,
                                        border_color=COLORS.get('divider'))
        except Exception:
            pass

        bal_inner = ctk.CTkFrame(self.balance_card, fg_color='transparent')
        bal_inner.pack(fill='x', padx=sv(24), pady=sv(20))

        left = ctk.CTkFrame(bal_inner, fg_color='transparent')
        left.pack(side='left', fill='x', expand=True)

        ctk.CTkLabel(
            left, text="CURRENT BALANCE",
            font=font(10, 'bold'), text_color=COLORS.get('muted_text'),
        ).pack(anchor='w')

        self.balance_label = ctk.CTkLabel(
            left, text='--',
            font=(FONT_FAMILY, sv(26), 'bold'), text_color=COLORS.get('text'),
        )
        self.balance_label.pack(anchor='w', pady=(sv(2), sv(6)))

        sub_row = ctk.CTkFrame(left, fg_color='transparent')
        sub_row.pack(anchor='w')

        self.income_label = ctk.CTkLabel(
            sub_row, text=f"{ICONS['income']} Income  --",
            font=font(11, 'bold'), text_color=COLORS.get('success'),
        )
        self.income_label.pack(side='left', padx=(0, sv(14)))

        self.expense_label = ctk.CTkLabel(
            sub_row, text=f"{ICONS['expense']} Expense  --",
            font=font(11, 'bold'), text_color=COLORS.get('danger'),
        )
        self.expense_label.pack(side='left')

        ring = ctk.CTkFrame(bal_inner, fg_color='transparent')
        ring.pack(side='right', padx=(sv(8), 0))

        self.savings_donut = Donut(
            ring, size=68, progress_color='success', track_color='divider',
        )
        self.savings_donut.pack()

        self.savings_label = ctk.CTkLabel(
            ring, text='--', font=font(11, 'bold'),
            text_color=COLORS.get('success'),
        )
        self.savings_label.pack(pady=(sv(2), 0))

        ctk.CTkLabel(
            ring, text='saved', font=font(9),
            text_color=COLORS.get('muted_text'),
        ).pack()

    def _build_stats_row(self, med):
        self.stats_frame = ctk.CTkFrame(self.content, fg_color='transparent')
        self.stats_frame.pack(fill='x', pady=(0, med))

        self.stat_daily = self._make_stat_card(self.stats_frame, ICONS['expense'], 'Daily avg', '--')
        self.stat_daily.pack(side='left', fill='x', expand=True, padx=(0, sv(6)))

        self.stat_savings = self._make_stat_card(self.stats_frame, ICONS['tips'], 'Savings rate', '--')
        self.stat_savings.pack(side='left', fill='x', expand=True, padx=sv(3))

        self.stat_velocity = self._make_stat_card(self.stats_frame, ICONS['forward'], 'Spending trend', '--')
        self.stat_velocity.pack(side='left', fill='x', expand=True, padx=(sv(6), 0))

    def _make_stat_card(self, parent, icon, label, value):
        card = ctk.CTkFrame(
            parent, fg_color=COLORS.get('card_bg'),
            corner_radius=sv(12), border_width=1,
            border_color=COLORS.get('divider'),
        )
        inner = ctk.CTkFrame(card, fg_color='transparent')
        inner.pack(fill='both', expand=True, padx=sv(14), pady=sv(12))

        top = ctk.CTkFrame(inner, fg_color='transparent')
        top.pack(fill='x')

        ctk.CTkLabel(
            top, text=icon, font=font(12),
            text_color=COLORS.get('primary'),
        ).pack(side='left', padx=(0, sv(4)))

        ctk.CTkLabel(
            top, text=label, font=font(9, 'bold'),
            text_color=COLORS.get('muted_text'),
        ).pack(side='left')

        value_lbl = ctk.CTkLabel(
            inner, text=value, font=font(16, 'bold'),
            text_color=COLORS.get('text'),
        )
        value_lbl.pack(anchor='w', pady=(sv(2), 0))
        card._value_label = value_lbl
        return card

    def _set_stat(self, card, value, color=None):
        try:
            card._value_label.configure(
                text=value,
                text_color=color or COLORS.get('text'),
            )
        except Exception:
            pass

    def _build_goals_card(self, med):
        self.goals_card = Card(master=self.content, radius=sv(16))
        self.goals_card.pack(fill='x', pady=(0, med))

        goals_header = ctk.CTkFrame(self.goals_card, fg_color='transparent')
        goals_header.pack(fill='x', padx=sv(20), pady=(sv(16), 0))

        SectionTitle(
            goals_header, ICONS['goal'], 'Goals', icon_color=COLORS.get('accent'),
        ).pack(side='left')

        ctk.CTkButton(
            goals_header, text='+  Add Goal',
            command=lambda: self._nav('add_goal'),
            fg_color=COLORS.get('primary'),
            hover_color=COLORS.get('primary_hover'),
            corner_radius=sv(8), height=sv(32), font=font(12, 'bold'),
        ).pack(side='right')

        alloc_frame = ctk.CTkFrame(
            self.goals_card, fg_color=COLORS.get('input_bg'),
            corner_radius=sv(10),
        )
        alloc_frame.pack(fill='x', padx=sv(20), pady=sv(12))

        ctk.CTkLabel(
            alloc_frame, text='Allocate:',
            font=font(11), text_color=COLORS.get('muted_text'),
        ).pack(side='left', padx=(sv(10), sv(6)))

        self.goal_var = ctk.StringVar()
        self.goal_menu = ctk.CTkOptionMenu(
            alloc_frame, values=[], variable=self.goal_var,
            width=sv(130), height=sv(32),
            dropdown_fg_color=COLORS.get('card_bg'),
            fg_color=COLORS.get('card_bg'), font=font(12),
        )
        self.goal_menu.pack(side='left', padx=sv(12))

        self.alloc_amount_entry = ctk.CTkEntry(
            alloc_frame, placeholder_text='Amount',
            width=sv(80), height=sv(32), font=font(12),
        )
        self.alloc_amount_entry.pack(side='left', padx=sv(12))

        ctk.CTkButton(
            alloc_frame, text=ICONS['add'],
            command=self._do_allocate,
            fg_color=COLORS.get('success'),
            hover_color=COLORS.get('accent'),
            corner_radius=sv(8), width=sv(40), height=sv(32),
            font=font(13, 'bold'),
        ).pack(side='left', padx=(0, sv(10)))

        self.goals_list_frame = ctk.CTkFrame(
            self.goals_card, fg_color='transparent')
        self.goals_list_frame.pack(
            fill='both', expand=True, padx=sv(20), pady=(0, sv(16)))

    def _build_transactions_card(self, med):
        self.trx_card = Card(master=self.content, radius=sv(16))
        self.trx_card.pack(fill='both', expand=True, padx=0, pady=(0, med))

        trx_header = ctk.CTkFrame(self.trx_card, fg_color='transparent')
        trx_header.pack(fill='x', padx=sv(20), pady=(sv(16), sv(4)))

        trx_left = ctk.CTkFrame(trx_header, fg_color='transparent')
        trx_left.pack(side='left')

        SectionTitle(
            trx_left, ICONS['reports'], 'Recent Transactions',
        ).pack(side='left')

        self.trx_list = ctk.CTkTextbox(
            self.trx_card, state='disabled',
            corner_radius=sv(10),
            fg_color=COLORS.get('input_bg'),
            text_color=COLORS.get('text'),
            font=(FONT_FAMILY, sv(12)), border_width=0,
        )
        self.trx_list.pack(
            fill='both', expand=True, padx=sv(20), pady=(0, sv(16)))

    def _build_form_card(self, med):
        self.form_card = Card(master=self.content, radius=sv(16))
        self.form_card.pack(fill='x', padx=0, pady=(0, med))

        form_header = ctk.CTkFrame(self.form_card, fg_color='transparent')
        form_header.pack(fill='x', padx=sv(20), pady=(sv(14), sv(6)))

        SectionTitle(
            form_header, ICONS['add'], 'Add Transaction',
            icon_color=COLORS.get('accent'),
        ).pack(side='left')

        form = ctk.CTkFrame(self.form_card, fg_color='transparent')
        form.pack(fill='x', padx=sv(20), pady=(0, sv(14)))

        for col in range(5):
            form.grid_columnconfigure(col, weight=0)
        form.grid_columnconfigure(2, weight=1)

        self.type_var = ctk.StringVar(value='expense')
        ctk.CTkOptionMenu(
            form, values=['income', 'expense'], variable=self.type_var,
            width=sv(90), height=sv(34),
            fg_color=COLORS.get('input_bg'),
            dropdown_fg_color=COLORS.get('card_bg'), font=font(12),
        ).grid(row=0, column=0, padx=sv(4), pady=sv(4), sticky='ew')

        self.category_var = ctk.StringVar(value=EXPENSE_CATEGORIES[0])
        self.cat_menu = ctk.CTkOptionMenu(
            form, values=EXPENSE_CATEGORIES, variable=self.category_var,
            width=sv(120), height=sv(34),
            fg_color=COLORS.get('input_bg'),
            dropdown_fg_color=COLORS.get('card_bg'), font=font(12),
        )
        self.cat_menu.grid(row=0, column=1, padx=sv(4), pady=sv(4), sticky='ew')

        self.desc_entry = ctk.CTkEntry(
            form, placeholder_text='Description',
            height=sv(34), font=font(12),
        )
        self.desc_entry.grid(row=0, column=2, padx=sv(4), pady=sv(4), sticky='ew')

        self.amount_entry = ctk.CTkEntry(
            form, placeholder_text='Amount',
            width=sv(80), height=sv(34), font=font(12),
        )
        self.amount_entry.grid(row=0, column=3, padx=sv(4), pady=sv(4), sticky='ew')

        ctk.CTkButton(
            form, text=ICONS['add'],
            command=self._add_transaction,
            fg_color=COLORS.get('primary'),
            hover_color=COLORS.get('primary_hover'),
            corner_radius=sv(8), width=sv(50), height=sv(34),
            font=font(14, 'bold'),
        ).grid(row=0, column=4, padx=sv(4), pady=sv(4), sticky='ew')

        self.type_var.trace_add('write', self._on_type_change)

    def _build_learning_card(self):
        """Financial Coach card — looks & reads like a local AI assistant"""
        self.learning_card = Card(master=self.content, radius=sv(16))
        self.learning_card.pack(fill='x', pady=(0, sv(10)))

        learn_header = ctk.CTkFrame(self.learning_card, fg_color='transparent')
        learn_header.pack(fill='x', padx=sv(20), pady=(sv(14), sv(6)))

        ctk.CTkLabel(
            learn_header, text='✦',
            font=font(15), text_color=COLORS.get('accent'),
        ).pack(side='left', padx=(0, sv(6)))
        ctk.CTkLabel(
            learn_header, text='Financial Coach',
            font=font(15, 'bold'), text_color=COLORS.get('text'),
        ).pack(side='left')

        self.coach_body = ctk.CTkFrame(
            self.learning_card, fg_color=COLORS.get('input_bg'),
            corner_radius=sv(10),
        )
        self.coach_body.pack(fill='x', padx=sv(20), pady=(0, sv(14)))

    def _on_type_change(self, *_):
        if self.type_var.get() == 'income':
            self.cat_menu.configure(values=INCOME_CATEGORIES)
            self.category_var.set(INCOME_CATEGORIES[0])
        else:
            self.cat_menu.configure(values=EXPENSE_CATEGORIES)
            self.category_var.set(EXPENSE_CATEGORIES[0])

    def _add_transaction(self):
        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            mb.showwarning('Warning', 'Amount is invalid')
            return

        if amount <= 0:
            mb.showwarning('Warning', 'Amount must be greater than zero')
            return

        ttype = self.type_var.get()
        cat = self.category_var.get()
        desc = self.desc_entry.get().strip()

        if self.user_id is None:
            return

        self.advisor.add_transaction(
            self.user_id, ttype, cat, amount, description=desc)
        self.desc_entry.delete(0, 'end')
        self.amount_entry.delete(0, 'end')
        self.refresh_ui()

    def _do_allocate(self):
        try:
            amount = float(self.alloc_amount_entry.get())
        except ValueError:
            mb.showwarning('Warning', 'Amount is invalid')
            return

        goal_name = self.goal_var.get()
        if not goal_name or goal_name == 'No goals yet. Add one to start!':
            mb.showwarning('Warning', 'Please select a goal')
            return

        goals = self.advisor.get_goals(self.user_id)
        goal_id = None
        for g in goals:
            if g[1] == goal_name:
                goal_id = g[0]
                break

        if goal_id is None:
            return

        success, msg = self.advisor.allocate_to_goal(
            self.user_id, goal_id, amount)
        if success:
            mb.showinfo('Success', msg)
            self.alloc_amount_entry.delete(0, 'end')
            self.refresh_ui()
        else:
            mb.showerror('Error', msg)

    def _delete_goal(self, goal_id, goal_name):
        confirm = mb.askyesno('Delete Goal', f"Delete '{goal_name}'?")
        if confirm:
            if self.advisor.delete_goal(self.user_id, goal_id):
                mb.showinfo('Success', 'Goal deleted')
                self.refresh_ui()
            else:
                mb.showerror('Error', 'Failed to delete goal')

    def _render_alerts(self):
        for w in self.alerts_frame.winfo_children():
            w.destroy()

        try:
            alerts = self.advisor.get_budget_alerts(self.user_id)
        except Exception:
            return

        level_colors = {
            'danger': COLORS.get('danger'),
            'warning': COLORS.get('warning'),
            'info': COLORS.get('primary'),
            'success': COLORS.get('success'),
        }
        level_bg = {
            'danger': COLORS.get('alert_danger_bg'),
            'warning': COLORS.get('alert_warning_bg'),
            'info': COLORS.get('alert_info_bg'),
            'success': COLORS.get('alert_success_bg'),
        }

        for alert in alerts[:2]:
            lvl = alert.get('level', 'info')
            row = ctk.CTkFrame(
                self.alerts_frame,
                fg_color=level_bg.get(lvl, COLORS.get('card_bg')),
                corner_radius=sv(10),
            )
            row.pack(fill='x', pady=sv(3))

            inner = ctk.CTkFrame(row, fg_color='transparent')
            inner.pack(fill='x', padx=sv(14), pady=sv(10))

            ctk.CTkLabel(
                inner, text=alert.get('title', ''),
                font=font(12, 'bold'),
                text_color=level_colors.get(lvl, COLORS.get('text')),
            ).pack(anchor='w')

            ctk.CTkLabel(
                inner, text=alert.get('message', ''),
                font=font(11),
                text_color=COLORS.get('muted_text'),
            ).pack(anchor='w', pady=(sv(2), 0))

    def _render_goals(self):
        for widget in self.goals_list_frame.winfo_children():
            widget.destroy()

        goal_progress = self.advisor.get_goal_progress(self.user_id)
        goal_names = [g['name'] for g in goal_progress]

        if goal_names:
            self.goal_menu.configure(values=goal_names)
            if not self.goal_var.get() or self.goal_var.get() == 'No goals yet. Add one to start!':
                self.goal_var.set(goal_names[0])
        else:
            self.goal_menu.configure(values=['No goals yet. Add one to start!'])
            self.goal_var.set('No goals yet. Add one to start!')

        if not goal_progress:
            MutedLabel(
                self.goals_list_frame,
                text=f"{ICONS['info']}  No goals yet. Add one to start!",
                size=12,
            ).pack(pady=sv(12))
            return

        text_color = COLORS.get('text')
        muted_color = COLORS.get('muted_text')
        input_bg = COLORS.get('input_bg')

        for g in goal_progress:
            item_frame = Card(
                master=self.goals_list_frame, radius=sv(10),
                bg_color='input_bg', hover=True,
            )
            item_frame.pack(fill='x', pady=sv(4))

            info_frame = ctk.CTkFrame(item_frame, fg_color='transparent')
            info_frame.pack(fill='x', padx=sv(14), pady=sv(10))

            name_frame = ctk.CTkFrame(info_frame, fg_color='transparent')
            name_frame.pack(side='left', fill='x', expand=True)

            status_icon = ICONS['success'] if g['status'] == 'completed' else (
                ICONS['warning'] if g['status'] == 'almost' else ICONS['goal'])

            ctk.CTkLabel(
                name_frame, text=f"{status_icon}  {g['name']}",
                font=font(12, 'bold'), text_color=text_color,
            ).pack(anchor='w')

            detail = f'{g["current"]:,.0f} / {g["target"]:,.0f}  ({g["percentage"]:.1f}%)'
            if g['estimated_date'] and g['status'] != 'completed':
                detail += f'  — est. {g["estimated_date"]}'
            ctk.CTkLabel(
                name_frame, text=detail,
                font=font(11), text_color=muted_color,
            ).pack(anchor='w', pady=(sv(2), 0))

            ctk.CTkButton(
                info_frame, text=ICONS['delete'],
                command=lambda gid=g['id'], gn=g['name']: self._delete_goal(gid, gn),
                width=sv(32), height=sv(28),
                fg_color='transparent', hover_color=COLORS.get('danger'),
                text_color=COLORS.get('danger'),
                corner_radius=sv(6), font=font(13),
            ).pack(side='right', padx=sv(4))

            bar_color = COLORS.get('success') if g['status'] == 'completed' else (
                COLORS.get('warning') if g['status'] == 'almost' else COLORS.get('accent'))
            pbar = ProgressBar(
                item_frame, height=sv(6),
                progress_color=bar_color,
            )
            pbar.pack(fill='x', padx=sv(14), pady=(0, sv(8)))
            pbar.set(min(g['percentage'] / 100, 1.0))

    def refresh_ui(self, user_id=None):
        if user_id is not None:
            self.user_id = user_id

        if getattr(self, 'user_id', None) is None:
            return

        profile = self.advisor.get_user_profile(self.user_id)
        self.show_learning_tips = profile.get('show_learning_tips', True)

        display_name = profile.get('display_name') or profile.get('username', '')
        try:
            self.welcome_label.configure(
                text=f"{ICONS['user']}  Welcome back, {display_name}")
        except Exception:
            pass

        bal = self.advisor.get_balance(self.user_id)
        try:
            # Negative balance is a valid state — show it clearly, not clamped
            if bal < 0:
                bal_color = COLORS.get('warning')
            elif bal > 0:
                bal_color = COLORS.get('success')
            else:
                bal_color = COLORS.get('text')
            self.balance_label.configure(
                text=format_money(bal, decimals=2), text_color=bal_color)
        except Exception:
            pass

        try:
            insights = self.advisor.get_spending_insights(self.user_id)
            self.income_label.configure(
                text=f"{ICONS['income']} Income  {insights['total_income']:,.2f}")
            self.expense_label.configure(
                text=f"{ICONS['expense']} Expense  {insights['total_expense']:,.2f}")

            rate = insights['savings_rate']
            self._set_stat(self.stat_daily, f'{insights["daily_average"]:,.0f}')

            if bal < 0:
                self._set_stat(self.stat_savings, 'Deficit',
                               COLORS.get('warning'))
                if hasattr(self, 'savings_donut'):
                    try:
                        self.savings_donut.set_color('warning')
                        self.savings_donut.set(0.25)
                        self.savings_label.configure(
                            text='over', text_color=COLORS.get('warning'))
                    except Exception:
                        pass
            else:
                self._set_stat(self.stat_savings, f'{rate:.1f}%',
                               COLORS.get('success') if rate >= 20 else COLORS.get('warning'))
                try:
                    self.savings_donut.set_color('success')
                    self.savings_donut.set(rate / 100)
                    self.savings_label.configure(
                        text=f'{rate:.1f}%', text_color=COLORS.get('success'))
                except Exception:
                    pass

            vel = insights['velocity_direction']
            vel_icon = ICONS['warning'] if vel == 'increasing' else (
                ICONS['success'] if vel == 'decreasing' else ICONS['info'])
            self._set_stat(
                self.stat_velocity,
                f'{vel_icon} {vel.title()}',
                COLORS.get('warning') if vel == 'increasing' else (
                    COLORS.get('success') if vel == 'decreasing' else COLORS.get('text')),
            )
        except Exception:
            pass

        self._render_alerts()

        trxs = self.advisor.get_transactions(self.user_id)
        try:
            self.trx_list.configure(state='normal')
            self.trx_list.delete('0.0', 'end')
            for t in trxs[:15]:
                typ, cat, amt, date, desc = t
                desc_text = (desc or '').strip()
                icon = ICONS['income'] if typ == 'income' else ICONS['expense']
                signed = amt if typ == 'income' else -amt
                line = f'{icon}  {date[:10]}   {cat:14}   {signed:>+12,.2f}'
                if desc_text:
                    line += f'   {desc_text}'
                self.trx_list.insert('end', f'{line}\n')
            if not trxs:
                self.trx_list.insert(
                    'end', f'\n  {ICONS["info"]}  No transactions yet.\n')
            self.trx_list.configure(state='disabled')
        except Exception:
            pass

        self._render_goals()
        self._render_learning_tips()

    def _render_learning_tips(self):
        if not getattr(self, 'show_learning_tips', True):
            try:
                self.learning_card.pack_forget()
            except Exception:
                pass
            return
        try:
            self.learning_card.pack(fill='x', pady=(0, sv(10)))
            for w in self.coach_body.winfo_children():
                w.destroy()

            advice = self.advisor.get_coach_advice(self.user_id)
            if advice is None:
                MutedLabel(
                    self.coach_body,
                    text=(f"{ICONS['info']}  Start by adding an income and an "
                          "expense — your coach will then read your numbers."),
                    size=12,
                ).pack(anchor='w', padx=sv(14), pady=sv(14))
            else:
                inner = ctk.CTkFrame(self.coach_body, fg_color='transparent')
                inner.pack(fill='x', padx=sv(14), pady=sv(12))

                ctk.CTkLabel(
                    inner, text=advice['insight'],
                    font=font(13, 'bold'),
                    text_color=COLORS.get('text'),
                    wraplength=sv(560), justify='left',
                ).pack(anchor='w')

                if advice.get('reason'):
                    ctk.CTkLabel(
                        inner, text=advice['reason'],
                        font=font(11),
                        text_color=COLORS.get('text_secondary'),
                        wraplength=sv(560), justify='left',
                    ).pack(anchor='w', pady=(sv(6), 0))

                if advice.get('action'):
                    ctk.CTkLabel(
                        inner, text=f"→  {advice['action']}",
                        font=font(11), text_color=COLORS.get('primary'),
                        wraplength=sv(560), justify='left',
                    ).pack(anchor='w', pady=(sv(8), 0))

                self._fade_in_card(inner)
        except Exception:
            pass

    def _fade_in_card(self, widget):
        """Subtle one-shot slide-up when coach advice refreshes"""
        try:
            from utils.ui_components import _motion_ok
            if not _motion_ok():
                return
        except Exception:
            return
        steps = 5
        for i in range(steps, 0, -1):
            widget.after(
                (steps - i) * 12,
                lambda p=i: widget.pack_configure(pady=(p, 0)),
            )
        widget.after(steps * 12, lambda: widget.pack_configure(pady=(12, 0)))
