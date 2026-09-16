"""Reports screen — monthly comparison, trends, category breakdown, and insights"""

import customtkinter as ctk
from utils.colors import COLORS
from utils.scale import sv
from utils.constants import ICONS, FONT_FAMILY, BASE_PADDING, MEDIUM_PADDING
from utils.ui_components import (
    Card, MutedLabel, ScreenHeader, ProgressBar, BaseScreen, SectionTitle, font,
)


class ReportsScreen(BaseScreen):
    def __init__(self, advisor, master, on_navigate=None):
        self.advisor = advisor
        self.master = master
        self.on_navigate = on_navigate
        self.user_id = None
        self._build_ui()

    def _build_ui(self):
        pad = sv(BASE_PADDING)
        self.root = ctk.CTkScrollableFrame(
            self.master,
            fg_color=COLORS.get("app_bg"),
            scrollbar_button_color=COLORS.get("primary"),
            scrollbar_button_hover_color=COLORS.get("accent"),
        )

        self.content = ctk.CTkFrame(self.root, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=pad)

        ScreenHeader(
            self.content, ICONS["reports"], "Reports",
            on_back=lambda: self._nav("dashboard"),
        ).pack(fill="x", pady=(sv(20), sv(MEDIUM_PADDING)))

        self.comparison_card = self._make_card(self.content)
        self.trend_card = self._make_card(self.content)
        self.category_card = self._make_card(self.content)
        self.recurring_card = self._make_card(self.content)
        self.insights_card = self._make_card(self.content)
        self._mark_built()

    def _make_card(self, parent):
        card = Card(master=parent, radius=sv(16))
        card.pack(fill="x", pady=(0, sv(MEDIUM_PADDING)))
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=sv(20), pady=sv(16))
        card._body = body
        return card

    def _section_title(self, parent, icon, text):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, sv(10)))
        SectionTitle(row, icon, text).pack(side="left")

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
        if value is None:
            return ctk.CTkLabel(
                parent, text=f"— {label}",
                font=font(10, "bold"), text_color=COLORS.get("muted_text"),
                fg_color=COLORS.get("input_bg"),
                corner_radius=sv(6), padx=sv(8), pady=sv(3),
            )
        color = COLORS.get("success") if (value >= 0) == positive_good else COLORS.get("danger")
        prefix = "+" if value > 0 else ""
        return ctk.CTkLabel(
            parent, text=f"{prefix}{value:.1f}% {label}",
            font=font(10, "bold"), text_color=color,
            fg_color=COLORS.get("input_bg"),
            corner_radius=sv(6), padx=sv(8), pady=sv(3),
        )

    def _trend_chart(self, parent, trend):
        """Render a 6-month income/expense grouped bar chart on canvas"""
        width = max(sv(520), parent.winfo_width() or sv(520))
        height = sv(200)
        pad_l, pad_r, pad_t, pad_b = sv(8), sv(8), sv(10), sv(30)
        plot_w = width - pad_l - pad_r
        plot_h = height - pad_t - pad_b

        canvas = ctk.CTkCanvas(
            parent, width=width, height=height,
            bg=COLORS.get("card_bg"), highlightthickness=0,
        )
        canvas.pack(fill="x", pady=(0, sv(6)))

        values = [max(m["income"], m["expense"], 1) for m in trend]
        vmax = max(values) or 1

        n = len(trend)
        group_w = plot_w / max(n, 1)
        bar_w = min(sv(26), group_w / 3)

        income_col = COLORS.get("success")
        expense_col = COLORS.get("danger")
        muted = COLORS.get("muted_text")

        for i, m in enumerate(trend):
            cx = pad_l + group_w * i + group_w / 2
            for j, (val, color) in enumerate([
                (m["income"], income_col),
                (m["expense"], expense_col),
            ]):
                bh = (val / vmax) * plot_h
                x0 = cx - bar_w + j * (bar_w + sv(2))
                y0 = pad_t + plot_h - bh
                canvas.create_rectangle(x0, y0, x0 + bar_w, pad_t + plot_h,
                                        fill=color, outline="", width=0)

            lbl = m["month"].split()[0]  # e.g. "Sep"
            canvas.create_text(cx, pad_t + plot_h + sv(14), text=lbl,
                               fill=muted, font=(FONT_FAMILY, sv(9)))

        canvas.create_line(pad_l, pad_t + plot_h, width - pad_r, pad_t + plot_h,
                           fill=COLORS.get("divider"))

        # Legend
        legend_y = sv(6)
        canvas.create_rectangle(sv(110), legend_y, sv(122), legend_y + sv(8),
                                fill=income_col, outline="")
        canvas.create_text(sv(126), legend_y + sv(4), text="Income",
                           fill=muted, anchor="w", font=(FONT_FAMILY, sv(9)))
        canvas.create_rectangle(sv(180), legend_y, sv(192), legend_y + sv(8),
                                fill=expense_col, outline="")
        canvas.create_text(sv(196), legend_y + sv(4), text="Expense",
                           fill=muted, anchor="w", font=(FONT_FAMILY, sv(9)))

    def _category_bars(self, parent, cats):
        """Bars scaled to the top category, with amount + % labels"""
        if not cats:
            return
        max_val = cats[0]["amount"] or 1
        for cat in cats[:8]:
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", pady=sv(4))
            ctk.CTkLabel(
                row, text=f'{ICONS["expense"]} {cat["category"]}',
                font=font(11), text_color=COLORS.get("text"),
                width=sv(140), anchor="w",
            ).pack(side="left")
            bar = ProgressBar(row, height=sv(8), width=sv(120),
                              progress_color="info")
            bar.pack(side="left", padx=(sv(8), 0))
            pct = (cat["amount"] / max_val) if max_val > 0 else 0
            bar.set(pct)
            ctk.CTkLabel(
                row, text=f'{cat["amount"]:,.0f}', font=font(11, "bold"),
                text_color=COLORS.get("text"), width=sv(90),
            ).pack(side="left", padx=(sv(8), 0))
            ctk.CTkLabel(
                row, text=f'{cat["percentage"]:.1f}%', font=font(10),
                text_color=COLORS.get("muted_text"), width=sv(50),
            ).pack(side="left")

    def _clear(self, widget):
        for w in widget.winfo_children():
            w.destroy()

    def _empty_state(self, parent, text):
        MutedLabel(parent, text=text, size=12).pack(pady=sv(10))

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

        body = self.trend_card._body
        self._clear(body)
        self._section_title(body, ICONS["forward"], "Monthly Trend (Last 6 Months)")

        try:
            trend = self.advisor.get_monthly_trend(self.user_id)
            if not trend:
                self._empty_state(body, "Not enough data")
            else:
                self._trend_chart(body, trend)
        except Exception:
            self._empty_state(body, "No trend data")

        body = self.category_card._body
        self._clear(body)
        self._section_title(body, ICONS["category"], "Expense Breakdown (30 Days)")

        try:
            cats = self.advisor.get_category_breakdown(self.user_id)
            if not cats:
                self._empty_state(body, "No expenses yet")
            else:
                self._category_bars(body, cats)
        except Exception:
            self._empty_state(body, "No data")

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

        body = self.insights_card._body
        self._clear(body)
        self._section_title(body, ICONS["tips"], "Spending Insights (30 Days)")

        try:
            si = self.advisor.get_spending_insights(self.user_id)
            if not si or si["total_expense"] == 0:
                self._empty_state(body, "Add some expenses to see insights")
            else:
                bal = si["total_income"] - si["total_expense"]
                self._kpi_row(
                    body,
                    "Daily Average", f'{si["daily_average"]:,.0f}',
                    "Projected Month End", f'{si["projected_monthly"]:,.0f}',
                    left_color=COLORS.get("primary"),
                )
                # With a deficit, savings rate is meaningless — surface the deficit
                warning_col = COLORS.get("warning")
                if bal < 0:
                    self._kpi_row(
                        body,
                        "Net Position", f"{-bal:,.0f} over",
                        "Status", "Spending exceeds income",
                        left_color=warning_col,
                        right_color=warning_col,
                    )
                else:
                    self._kpi_row(
                        body,
                        "Savings Rate", f'{si["savings_rate"]:.1f}%',
                        "Transactions", str(si["transaction_count"]),
                        left_color=success_col if si["savings_rate"] >= 20 else danger_col,
                    )

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
