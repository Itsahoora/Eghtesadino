"""Reports screen — monthly comparison, trends, category breakdown, and insights."""

import customtkinter as ctk
from utils.colors import COLORS
from utils.scale import sv
from utils.constants import ICONS, FONT_FAMILY, BASE_PADDING, MEDIUM_PADDING
from utils.ui_components import Card, MutedLabel, font, animate_card_intro


class ReportsScreen:
    def __init__(self, advisor, master, on_navigate=None):
        self.advisor = advisor
        self.master = master
        self.on_navigate = on_navigate
        self.user_id = None
        self._build_ui()

    # ── UI construction ───────────────────────────────────────────

    def _build_ui(self):
        pad = sv(BASE_PADDING)
        self.root = ctk.CTkScrollableFrame(
            self.master,
            fg_color=COLORS.get("light_bg"),
            scrollbar_button_color=COLORS.get("primary"),
            scrollbar_button_hover_color=COLORS.get("accent"),
        )

        self.content = ctk.CTkFrame(self.root, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=pad)

        # Header
        header = ctk.CTkFrame(self.content, fg_color="transparent")
        header.pack(fill="x", pady=(sv(20), MEDIUM_PADDING))

        header_left = ctk.CTkFrame(header, fg_color="transparent")
        header_left.pack(side="left")

        ctk.CTkButton(
            header_left,
            text=f'{ICONS["back"]}  Back',
            command=lambda: self._nav("dashboard"),
            fg_color=COLORS.get("elevated_bg"),
            hover_color=COLORS.get("divider"),
            text_color=COLORS.get("text"),
            corner_radius=sv(8), height=sv(34), font=font(12),
        ).pack(side="left", padx=(0, sv(12)))

        header_right = ctk.CTkFrame(header, fg_color="transparent")
        header_right.pack(side="right")

        ctk.CTkLabel(
            header_right, text=ICONS["reports"],
            font=font(18), text_color=COLORS.get("primary"),
        ).pack(side="left", padx=(0, sv(6)))

        ctk.CTkLabel(
            header_right, text="Reports",
            font=font(20, "bold"), text_color=COLORS.get("text"),
        ).pack(side="left")

        # Five card sections
        self.comparison_card = self._make_card(self.content)
        self.trend_card = self._make_card(self.content)
        self.category_card = self._make_card(self.content)
        self.recurring_card = self._make_card(self.content)
        self.insights_card = self._make_card(self.content)

    def _make_card(self, parent):
        card = Card(master=parent, radius=sv(16))
        card.pack(fill="x", pady=(0, MEDIUM_PADDING))
        animate_card_intro(card)
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=sv(20), pady=sv(16))
        card._body = body  # attach body reference for easy access
        return card

    # ── Shared rendering helpers ──────────────────────────────────

    def _section_title(self, parent, icon, text):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, sv(10)))
        ctk.CTkLabel(
            row, text=icon, font=font(15), text_color=COLORS.get("primary"),
        ).pack(side="left", padx=(0, sv(6)))
        ctk.CTkLabel(
            row, text=text, font=font(15, "bold"), text_color=COLORS.get("text"),
        ).pack(side="left")

    def _kpi_row(self, parent, left_label, left_val, right_label, right_val,
                 left_color=None, right_color=None):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=sv(4))
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=1)

        muted = COLORS.get("muted_text")
        default = COLORS.get("text")

        ctk.CTkLabel(row, text=left_label, font=font(11),
                     text_color=muted).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(row, text=left_val, font=font(13, "bold"),
                     text_color=left_color or default).grid(
            row=1, column=0, sticky="w", pady=(sv(2), 0))

        ctk.CTkLabel(row, text=right_label, font=font(11),
                     text_color=muted).grid(
            row=0, column=1, sticky="w", padx=(sv(16), 0))
        ctk.CTkLabel(row, text=right_val, font=font(13, "bold"),
                     text_color=right_color or default).grid(
            row=1, column=1, sticky="w", padx=(sv(16), 0), pady=(sv(2), 0))

    def _change_chip(self, parent, label, value, positive_good=True):
        """Small label showing a +/- percentage change."""
        color = COLORS.get("success") if (value >= 0) == positive_good else COLORS.get("danger")
        prefix = "+" if value > 0 else ""
        return ctk.CTkLabel(
            parent, text=f"{prefix}{value:.1f}% {label}",
            font=font(10, "bold"), text_color=color,
            fg_color=COLORS.get("input_bg"),
            corner_radius=sv(6), padx=sv(8), pady=sv(3),
        )

    def _text_bar(self, parent, label, value, max_value):
        """Render a row with a Unicode horizontal bar chart."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=sv(2))

        ctk.CTkLabel(
            row, text=label, font=font(11),
            text_color=COLORS.get("text"), width=sv(120),
        ).pack(side="left")

        pct = (value / max_value * 100) if max_value > 0 else 0
        filled = max(1, int(pct / 5))
        bar_text = "█" * filled + "░" * (20 - filled)

        ctk.CTkLabel(
            row, text=bar_text, font=(FONT_FAMILY, sv(10)),
            text_color=COLORS.get("primary"), width=sv(180),
        ).pack(side="left", padx=(sv(8), 0))

        ctk.CTkLabel(
            row, text=f"{value:,.0f}", font=font(11, "bold"),
            text_color=COLORS.get("text"), width=sv(80),
        ).pack(side="left", padx=(sv(8), 0))

        ctk.CTkLabel(
            row, text=f"{pct:.1f}%", font=font(10),
            text_color=COLORS.get("muted_text"), width=sv(50),
        ).pack(side="left")

    def _clear(self, widget):
        for w in widget.winfo_children():
            w.destroy()

    def _nav(self, target):
        if callable(self.on_navigate):
            self.on_navigate(target)

    def _empty_state(self, parent, text):
        MutedLabel(parent, text=text, size=12).pack(pady=sv(10))

    # ── Refresh ───────────────────────────────────────────────────

    def refresh_ui(self, user_id=None):
        if user_id is not None:
            self.user_id = user_id
        if getattr(self, "user_id", None) is None:
            return

        text_col = COLORS.get("text")
        muted_col = COLORS.get("muted_text")
        success_col = COLORS.get("success")
        danger_col = COLORS.get("danger")
        input_bg = COLORS.get("input_bg")

        # ── Monthly Comparison ──
        body = self.comparison_card._body
        self._clear(body)
        self._section_title(body, ICONS["reports"], "Monthly Comparison")

        try:
            comp = self.advisor.get_monthly_comparison(self.user_id)
            curr = comp["current"]
            prev = comp["previous"]

            self._kpi_row(body,
                          "Current Month Income", f'{curr["income"]:,.2f}',
                          "Previous Month Income", f'{prev["income"]:,.2f}',
                          left_color=success_col, right_color=success_col)
            self._kpi_row(body,
                          "Current Month Expense", f'{curr["expense"]:,.2f}',
                          "Previous Month Expense", f'{prev["expense"]:,.2f}',
                          left_color=danger_col, right_color=danger_col)
            self._kpi_row(body,
                          "Current Month Balance", f'{curr["balance"]:,.2f}',
                          "Previous Month Balance", f'{prev["balance"]:,.2f}')

            chg_row = ctk.CTkFrame(body, fg_color="transparent")
            chg_row.pack(fill="x", pady=(sv(8), 0))
            ctk.CTkLabel(chg_row, text="Change:", font=font(11, "bold"),
                         text_color=muted_col).pack(side="left", padx=(0, sv(8)))

            for key, label in [("income_pct", "Income"), ("expense_pct", "Expense"),
                               ("balance_pct", "Balance")]:
                chip = self._change_chip(
                    chg_row, label, comp["changes"][key],
                    positive_good=(key != "expense_pct"),
                )
                chip.pack(side="left", padx=sv(4))
        except Exception:
            self._empty_state(body, "No data yet")

        # ── Monthly Trend ──
        body = self.trend_card._body
        self._clear(body)
        self._section_title(body, ICONS["forward"], "Monthly Trend (Last 6 Months)")

        try:
            trend = self.advisor.get_monthly_trend(self.user_id)
            if not trend:
                self._empty_state(body, "Not enough data")
            else:
                header_row = ctk.CTkFrame(body, fg_color="transparent")
                header_row.pack(fill="x", pady=(0, sv(6)))
                for lbl, w in [("Month", 120), ("Income", 90),
                               ("Expense", 90), ("Balance", 90)]:
                    ctk.CTkLabel(header_row, text=lbl, font=font(10, "bold"),
                                 text_color=muted_col, width=sv(w)).pack(
                        side="left", padx=sv(4))

                for m in trend:
                    row = ctk.CTkFrame(body, fg_color=input_bg,
                                       corner_radius=sv(6))
                    row.pack(fill="x", pady=sv(2))
                    income_str = f"+{m['income']:,.0f}" if m["income"] >= 0 else f"{m['income']:,.0f}"
                    expense_str = f"-{m['expense']:,.0f}" if m["expense"] > 0 else "0"
                    balance_str = f"{m['balance']:+,.0f}"
                    for val, w, color in [
                        (m["month"], 120, text_col),
                        (income_str, 90, success_col),
                        (expense_str, 90, danger_col),
                        (balance_str, 90, success_col if m["balance"] >= 0 else danger_col),
                    ]:
                        ctk.CTkLabel(row, text=val, font=font(11),
                                     text_color=color, width=sv(w)).pack(
                            side="left", padx=sv(4), pady=sv(4))
        except Exception:
            self._empty_state(body, "No trend data")

        # ── Category Breakdown ──
        body = self.category_card._body
        self._clear(body)
        self._section_title(body, ICONS["category"], "Expense Breakdown (30 Days)")

        try:
            cats = self.advisor.get_category_breakdown(self.user_id)
            if not cats:
                self._empty_state(body, "No expenses yet")
            else:
                max_val = cats[0]["amount"]
                for cat in cats[:8]:
                    self._text_bar(body, f'{ICONS["expense"]} {cat["category"]}',
                                   cat["amount"], max_val)
        except Exception:
            self._empty_state(body, "No data")

        # ── Recurring Expenses ──
        body = self.recurring_card._body
        self._clear(body)
        self._section_title(body, ICONS["repeat"], "Recurring Expenses (2+ Months)")

        try:
            recurring = self.advisor.get_recurring_expenses(self.user_id)
            if not recurring:
                self._empty_state(body, "No recurring expenses detected")
            else:
                for r in recurring:
                    row = ctk.CTkFrame(body, fg_color=input_bg,
                                       corner_radius=sv(8))
                    row.pack(fill="x", pady=sv(3))
                    inner = ctk.CTkFrame(row, fg_color="transparent")
                    inner.pack(fill="x", padx=sv(12), pady=sv(8))

                    ctk.CTkLabel(
                        inner, text=f'{ICONS["repeat"]}  {r["category"]}',
                        font=font(12, "bold"), text_color=text_col,
                    ).pack(side="left")

                    detail = f'  avg {r["average_amount"]:,.0f}/mo  |  {r["months_active"]} months'
                    ctk.CTkLabel(inner, text=detail, font=font(11),
                                 text_color=muted_col).pack(side="left")
        except Exception:
            self._empty_state(body, "No data")

        # ── Spending Insights ──
        body = self.insights_card._body
        self._clear(body)
        self._section_title(body, ICONS["tips"], "Spending Insights (30 Days)")

        try:
            si = self.advisor.get_spending_insights(self.user_id)
            if not si or si["total_expense"] == 0:
                self._empty_state(body, "Add some expenses to see insights")
            else:
                self._kpi_row(
                    body,
                    "Daily Average", f'{si["daily_average"]:,.0f}',
                    "Projected Month End", f'{si["projected_monthly"]:,.0f}',
                    left_color=COLORS.get("primary"),
                )
                self._kpi_row(
                    body,
                    "Savings Rate", f'{si["savings_rate"]:.1f}%',
                    "Transactions", str(si["transaction_count"]),
                    left_color=success_col if si["savings_rate"] >= 20 else danger_col,
                )

                # Velocity indicator
                vel = si["velocity_direction"]
                vel_color = (
                    COLORS.get("warning") if vel == "increasing"
                    else (success_col if vel == "decreasing" else text_col)
                )
                vel_frame = ctk.CTkFrame(body, fg_color=input_bg,
                                         corner_radius=sv(8))
                vel_frame.pack(fill="x", pady=(sv(8), 0))
                vel_inner = ctk.CTkFrame(vel_frame, fg_color="transparent")
                vel_inner.pack(fill="x", padx=sv(12), pady=sv(10))

                vel_icon = (
                    ICONS["warning"] if vel == "increasing"
                    else (ICONS["success"] if vel == "decreasing" else ICONS["info"])
                )
                ctk.CTkLabel(
                    vel_inner, text=f"{vel_icon}  Spending Velocity: ",
                    font=font(12, "bold"), text_color=muted_col,
                ).pack(side="left")
                ctk.CTkLabel(
                    vel_inner, text=vel.title(),
                    font=font(12, "bold"), text_color=vel_color,
                ).pack(side="left")

                if si["top_categories"]:
                    ctk.CTkLabel(
                        body, text=f'\n{ICONS["category"]}  Top Categories:',
                        font=font(11, "bold"), text_color=muted_col,
                    ).pack(anchor="w", pady=(sv(8), sv(4)))
                    for cat_name, cat_amt in si["top_categories"][:3]:
                        cat_pct = (cat_amt / si["total_expense"] * 100) if si["total_expense"] > 0 else 0
                        ctk.CTkLabel(
                            body,
                            text=f"    {cat_name:16}  {cat_amt:>10,.0f}  ({cat_pct:.1f}%)",
                            font=(FONT_FAMILY, sv(11)), text_color=text_col,
                        ).pack(anchor="w")
        except Exception:
            self._empty_state(body, "No insights yet")

    def pack(self, *args, **kwargs):
        return self.root.pack(*args, **kwargs)

    def pack_forget(self, *args, **kwargs):
        return self.root.pack_forget(*args, **kwargs)
