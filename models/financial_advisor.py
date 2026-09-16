import re
import sqlite3
from datetime import datetime, timedelta
from utils.resource_path import resource_path


class FinancialAdvisor:
    """Facade that owns every database operation the app needs"""

    def __init__(self):
        self.db_path = resource_path("financial_data.db")
        self.init_database()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_database(self):
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password TEXT,
                display_name TEXT,
                privacy_enabled INTEGER DEFAULT 0,
                show_learning_tips INTEGER DEFAULT 1
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                type TEXT,
                category TEXT,
                amount REAL,
                date TEXT,
                description TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                goal_name TEXT,
                target_amount REAL,
                current_amount REAL,
                deadline TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)

        self._ensure_user_columns(conn)
        conn.commit()
        conn.close()

    def _ensure_user_columns(self, conn):
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(users)")
        columns = {row[1] for row in cursor.fetchall()}

        migrations = {
            "display_name": "ALTER TABLE users ADD COLUMN display_name TEXT",
            "privacy_enabled": "ALTER TABLE users ADD COLUMN privacy_enabled INTEGER DEFAULT 0",
            "show_learning_tips": "ALTER TABLE users ADD COLUMN show_learning_tips INTEGER DEFAULT 1",
        }
        for col, ddl in migrations.items():
            if col not in columns:
                cursor.execute(ddl)

    # ── Input normalization ───────────────────────────────

    def normalize_transaction_data(self, ttype, category, amount, description=""):
        normalized_type = (ttype or "").strip().lower()
        if normalized_type not in {"income", "expense"}:
            normalized_type = "expense"

        normalized_category = (
            re.sub(r"\s+", " ", (category or "").strip()).title() or "Other"
        )
        try:
            amount_value = abs(float(amount))
        except (TypeError, ValueError):
            amount_value = 0.0

        normalized_description = (
            re.sub(r"\s+", " ", (description or "").strip()) or "No description"
        )
        return {
            "type": normalized_type,
            "category": normalized_category,
            "amount": round(amount_value, 2),
            "description": normalized_description,
        }

    # ── Account management ────────────────────────────────

    def register_user(self, username, password):
        if not username or not password:
            return False
        try:
            conn = self._connect()
            conn.execute(
                "INSERT INTO users (username, password, display_name) "
                "VALUES (?, ?, ?)",
                (username, password, username),
            )
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    def login_user(self, username, password):
        conn = self._connect()
        row = conn.execute(
            "SELECT id, username, password FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        conn.close()
        if row is None:
            return None
        user_id, stored_username, _ = row
        if row[2] != password:
            return None
        profile = self.get_user_profile(user_id)
        return {
            "id": user_id,
            "username": stored_username,
            "display_name": profile.get("display_name") or stored_username,
            "privacy_enabled": profile.get("privacy_enabled", False),
        }

    def get_user_profile(self, user_id):
        conn = self._connect()
        row = conn.execute(
            "SELECT id, username, display_name, privacy_enabled, "
            "show_learning_tips FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        conn.close()
        if not row:
            return {}
        return {
            "id": row[0],
            "username": row[1],
            "display_name": row[2] or row[1],
            "privacy_enabled": bool(row[3]),
            "show_learning_tips": bool(row[4]),
        }

    def update_user_setting(self, user_id, key, value):
        if not user_id or key not in {"privacy_enabled", "show_learning_tips"}:
            return False
        try:
            conn = self._connect()
            conn.execute(
                f"UPDATE users SET {key} = ? WHERE id = ?", (1 if value else 0, user_id)
            )
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    def update_learning_tips_setting(self, user_id, enabled):
        return self.update_user_setting(user_id, "show_learning_tips", enabled)

    def update_display_name(self, user_id, display_name):
        if not user_id or not display_name or not display_name.strip():
            return False
        try:
            conn = self._connect()
            conn.execute(
                "UPDATE users SET display_name = ? WHERE id = ?",
                (display_name.strip(), user_id),
            )
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    def change_username(self, user_id, new_username):
        """Change a user's username. Returns (ok, message)."""
        username = (new_username or "").strip()
        if not username:
            return False, "Username cannot be empty."
        if self.user_with_username(username):
            return False, "That username is already taken. Choose another."
        try:
            conn = self._connect()
            conn.execute(
                "UPDATE users SET username = ? WHERE id = ?",
                (username, user_id),
            )
            conn.commit()
            conn.close()
            return True, "Username updated."
        except Exception:
            return False, "Could not update username. Please try again."

    def user_with_username(self, username):
        conn = self._connect()
        row = conn.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()
        conn.close()
        return row is not None

    def change_password(self, user_id, current_password, new_password):
        """Change the user's password after verifying the current one."""
        if not new_password:
            return False, "New password cannot be empty."
        if len(new_password) < 6:
            return False, "New password must be at least 6 characters."
        conn = self._connect()
        row = conn.execute(
            "SELECT password FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        conn.close()
        if row is None or row[0] != current_password:
            return False, "Current password is incorrect."
        try:
            conn = self._connect()
            conn.execute(
                "UPDATE users SET password = ? WHERE id = ?",
                (new_password, user_id),
            )
            conn.commit()
            conn.close()
            return True, "Password updated."
        except Exception:
            return False, "Could not update password. Please try again."

    def delete_account(self, user_id):
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM goals WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False
        finally:
            conn.close()

    # ── Transactions ──────────────────────────────────────

    def add_transaction(self, user_id, ttype, category, amount, description=""):
        normalized = self.normalize_transaction_data(
            ttype, category, amount, description
        )
        conn = self._connect()
        try:
            conn.execute(
                "INSERT INTO transactions (user_id, type, category, amount, date, description) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    user_id,
                    normalized["type"],
                    normalized["category"],
                    normalized["amount"],
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    normalized["description"],
                ),
            )
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_transactions(self, user_id, days=30):
        conn = self._connect()
        date_limit = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        rows = conn.execute(
            "SELECT type, category, amount, date, description "
            "FROM transactions WHERE user_id = ? AND date >= ? ORDER BY date DESC",
            (user_id, date_limit),
        ).fetchall()
        conn.close()
        return [tuple(row) for row in rows]

    def get_balance(self, user_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT type, SUM(amount) FROM transactions WHERE user_id = ? GROUP BY type",
            (user_id,),
        )
        data = {t: amt for t, amt in cursor.fetchall()}
        conn.close()
        return data.get("income", 0) - data.get("expense", 0)

    # ── Goals ─────────────────────────────────────────────

    def add_goal(self, user_id, goal_name, target_amount, deadline=None):
        conn = self._connect()
        try:
            conn.execute(
                "INSERT INTO goals (user_id, goal_name, target_amount, current_amount, deadline) "
                "VALUES (?, ?, ?, ?, ?)",
                (user_id, goal_name, target_amount, 0.0, deadline),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_goals(self, user_id):
        conn = self._connect()
        rows = conn.execute(
            "SELECT id, goal_name, target_amount, current_amount, deadline "
            "FROM goals WHERE user_id = ?",
            (user_id,),
        ).fetchall()
        conn.close()
        return rows

    def delete_goal(self, user_id, goal_id):
        conn = self._connect()
        try:
            conn.execute(
                "DELETE FROM goals WHERE id = ? AND user_id = ?", (goal_id, user_id)
            )
            conn.commit()
            return True
        except Exception:
            conn.rollback()
            return False
        finally:
            conn.close()

    def allocate_to_goal(self, user_id, goal_id, amount):
        if amount <= 0:
            return False, "Amount must be positive"

        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT target_amount, current_amount FROM goals WHERE id = ? AND user_id = ?",
            (goal_id, user_id),
        )
        goal = cursor.fetchone()
        if not goal:
            conn.close()
            return False, "Goal not found"

        target_amount, current_amount = goal
        remaining_needed = target_amount - current_amount
        if remaining_needed <= 0:
            conn.close()
            return False, f"Goal already reached! Target: {target_amount}"

        current_balance = self.get_balance(user_id)
        if current_balance < amount:
            conn.close()
            return False, f"Insufficient balance. Current: {current_balance:,.0f}"

        actual_allocate = min(amount, remaining_needed)

        try:
            conn.execute(
                "INSERT INTO transactions (user_id, type, category, amount, date, description) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    user_id,
                    "expense",
                    "Goal Allocation",
                    actual_allocate,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    f"Allocated to goal ID {goal_id}",
                ),
            )
            conn.execute(
                "UPDATE goals SET current_amount = current_amount + ? WHERE id = ? AND user_id = ?",
                (actual_allocate, goal_id, user_id),
            )
            conn.commit()
            if actual_allocate < amount:
                return True, (
                    f"Allocated {actual_allocate:,.0f} (goal reached!). "
                    f"Remaining {amount - actual_allocate:,.0f} stayed in balance."
                )
            return True, "Allocation successful"
        except Exception:
            conn.rollback()
            return False, "An unexpected error occurred. Please try again."
        finally:
            conn.close()

    # ── Analytics ──────────────────────────────────────────

    def _month_totals(self, user_id, start, end):
        conn = self._connect()
        rows = conn.execute(
            "SELECT type, SUM(amount) FROM transactions "
            "WHERE user_id = ? AND date >= ? AND date <= ? GROUP BY type",
            (user_id, start, end + " 23:59:59"),
        ).fetchall()
        conn.close()
        return {t: amt for t, amt in rows}

    @staticmethod
    def _pct_change(new, old):
        # No meaningful percentage when the previous value is zero.
        if old == 0:
            return None
        change = new - old
        if old < 0:
            return round((change / abs(old)) * 100, 1)
        return round((change / old) * 100, 1)

    def get_financial_insights(self, user_id):
        transactions = self.get_transactions(user_id, days=30)
        income_total = sum(
            amount for ttype, _, amount, _, _ in transactions if ttype == "income"
        )
        expense_total = sum(
            amount for ttype, _, amount, _, _ in transactions if ttype == "expense"
        )
        balance = income_total - expense_total
        expense_ratio = (expense_total / income_total) if income_total else 0.0
        savings_rate = max(0.0, 1 - expense_ratio)

        recommendations = []
        if balance < 0:
            recommendations.append(
                "Your balance is negative. Ease back by trimming one non-essential for now."
            )
            recommendations.append(
                "Focus on covering essentials first; then rebuild your savings buffer."
            )
        else:
            if savings_rate < 0.25:
                recommendations.append(
                    "Try a 20% save-first rule for your weekly allowance or income."
                )
            if expense_total > 0 and expense_total > income_total * 0.7:
                recommendations.append(
                    "Your spending is heavy; focus on needs before wants for the next month."
                )
            recommendations.append(
                "You are on a healthy track—keep a small emergency buffer in your goals."
            )

        return {
            "summary": {
                "balance": round(balance, 2),
                "income": round(income_total, 2),
                "expenses": round(expense_total, 2),
                "savings_rate": round(savings_rate * 100, 1),
                "expense_ratio": round(expense_ratio * 100, 1),
                "deficit": round(balance, 2) < 0,
            },
            "recommendations": recommendations,
        }

    def get_coach_advice(self, user_id):
        transactions = self.get_transactions(user_id, days=30)
        if not transactions:
            return None

        insights = self.get_spending_insights(user_id, days=30)
        balance = self.get_balance(user_id)
        income = insights["total_income"]
        expenses = insights["total_expense"]
        savings_rate = insights["savings_rate"]
        top_cat = insights["top_categories"][0] if insights["top_categories"] else None
        velocity = insights["velocity_direction"]
        velocity_pct = insights["velocity_pct"]
        goal_progress = self.get_goal_progress(user_id)
        recurring = self.get_recurring_expenses(user_id, days=60)
        recurring_total = sum(r["average_amount"] for r in recurring)

        # Largest single expense (for a spike mention). Need enough history to
        # distinguish a genuine spike from a thin dataset — a single big line in
        # a 2–3 item budget is just the whole month, not an anomaly.
        biggest = insights.get("biggest_expense")
        recent_spike = None
        if (
            biggest
            and expenses > 0
            and insights["transaction_count"] >= 4
            and (biggest["amount"] / max(expenses, 1)) > 0.5
        ):
            recent_spike = biggest

        # Goal needing attention: not completed, some progress, slow pace.
        slow_goal = None
        for g in goal_progress:
            if (
                g["status"] not in ("completed",)
                and g.get("months_left", 0) is not None
                and g["months_left"] > 4
            ):
                slow_goal = g
                break
        if slow_goal is None:
            for g in goal_progress:
                if g["status"] != "completed" and g["current"] > 0:
                    slow_goal = g
                    break

        advice = None  # main text
        reason = None  # why
        action = None  # next step

        # Priority 1: negative balance.
        if balance < 0:
            advice = (
                f"Your balance is at {balance:,.0f}, so spending is running "
                "ahead of your money right now."
            )
            reason = (
                f"This month you brought in {income:,.0f} but spent {expenses:,.0f} "
                f"across your categories."
            )
            action = (
                "Try trimming one flexible category — like entertainment or snacks — "
                "for the next week to ease back toward zero."
            )

        # Priority 2: a category taking a large share.
        elif top_cat and income > 0 and top_cat[1] / income > 0.35:
            cat = top_cat[0]
            cat_pct = top_cat[1] / income * 100
            advice = (
                f"{cat} is taking a big share of your income — about {cat_pct:.0f}%."
            )
            reason = (
                f"You've spent {top_cat[1]:,.0f} on {cat.lower()} in the last 30 days, "
                f"more than a third of your {income:,.0f} income."
            )
            action = (
                f"See if there's one repeat purchase within {cat.lower()} you could "
                "set a modest cap on this month."
            )

        # Priority 3: a goal falling behind.
        elif slow_goal is not None:
            g = slow_goal
            shortfall = g["remaining"]
            gap_pct = g["percentage"]
            advice = (
                f"Your goal “{g['name']}” is at {gap_pct:.0f}% with "
                f"{shortfall:,.0f} still to go."
            )
            if g["months_left"] is not None:
                reason = (
                    f"At your current savings pace, that would take roughly "
                    f"{g['months_left']:.1f} more months."
                )
            else:
                reason = "It hasn't been getting contributions recently."
            action = (
                f"A one-time top-up of about {max(shortfall * 0.2, 1):,.0f} now "
                "would move it noticeably closer."
            )

        # Priority 4: unusual recent spend spike.
        elif recent_spike is not None:
            advice = (
                f"There was a large {recent_spike['category'].lower()} charge of "
                f"{recent_spike['amount']:,.0f} recently."
            )
            reason = (
                f"It made up more than half of your total spending in the period, "
                "which stands out as unusual."
            )
            action = (
                "If it was a one-off, you're probably fine — otherwise it's worth "
                "reviewing that category for next month."
            )

        # Priority 5: recurring costs running high.
        elif recurring and income > 0 and recurring_total / income > 0.5:
            advice = (
                f"Recurring costs like {recurring[0]['category'].lower()} take a "
                "constant slice of your income."
            )
            reason = (
                f"In an average month, recurring items add up to about "
                f"{recurring_total:,.0f}."
            )
            action = (
                "Listing them out — subscriptions, transport, rent — makes it easy "
                "to spot one to pause or swap."
            )

        # Priority 6: rising spending trend (needs enough history to mean anything).
        elif velocity == "increasing" and insights["transaction_count"] >= 4:
            advice = (
                f"Your spending has been creeping up — about {velocity_pct:.0f}% "
                "higher in the second half of the month."
            )
            reason = (
                "Earlier spending was lighter, so the trend is heading the wrong way."
            )
            action = (
                "Catch it early: pick one day next week to log expenses the moment "
                "they happen."
            )

        # Priority 7: strong savings.
        elif savings_rate >= 25:
            advice = (
                f"You're keeping {savings_rate:.0f}% of your income — that's a "
                "solid savings habit."
            )
            reason = (
                f"In the last 30 days you earned {income:,.0f} and spent {expenses:,.0f}, "
                "which is a healthy gap."
            )
            action = (
                "Consider moving part of that surplus into a goal so it has a clear "
                "job to do."
            )

        # Fallback: stable, modest situation.
        else:
            advice = (
                f"Your money is fairly balanced this month — {income:,.0f} in, "
                f"{expenses:,.0f} out."
            )
            if top_cat:
                reason = (
                    f"Your top spending category is {top_cat[0].lower()}, around "
                    f"{top_cat[1]:,.0f}."
                )
            else:
                reason = "Spending is spread reasonably across categories."
            action = (
                "Keep the pattern steady, and let a small buffer grow into a goal "
                "when you can."
            )

        return {
            "insight": advice,
            "reason": reason,
            "action": action,
            "context": {
                "balance": round(balance, 2),
                "income": round(income, 2),
                "expenses": round(expenses, 2),
                "savings_rate": round(savings_rate, 1),
                "deficit": balance < 0,
            },
        }

    def get_spending_insights(self, user_id, days=30):
        transactions = self.get_transactions(user_id, days=days)
        expenses = [
            (cat, amt, date)
            for ttype, cat, amt, date, _ in transactions
            if ttype == "expense"
        ]
        total_expense = sum(amt for _, amt, _ in expenses)
        total_income = sum(
            amt for ttype, _, amt, _, _ in transactions if ttype == "income"
        )

        active_days = len({date.split(" ")[0] for _, _, date in expenses}) or 1
        daily_avg = total_expense / max(active_days, 1)

        cat_totals = {}
        for cat, amt, _ in expenses:
            cat_totals[cat] = cat_totals.get(cat, 0) + amt
        top_categories = sorted(cat_totals.items(), key=lambda x: x[1], reverse=True)

        biggest = max(expenses, key=lambda x: x[1]) if expenses else None

        mid = days // 2
        cutoff = (datetime.now() - timedelta(days=mid)).strftime("%Y-%m-%d")
        early = sum(amt for _, amt, date in expenses if date[:10] < cutoff)
        late = sum(amt for _, amt, date in expenses if date[:10] >= cutoff)
        if early > 0:
            velocity_pct = ((late - early) / early) * 100
        elif late > 0:
            velocity_pct = 100.0
        else:
            velocity_pct = 0.0

        projected_monthly = (total_expense / max(days, 1)) * 30
        savings_rate = (
            ((total_income - total_expense) / total_income * 100)
            if total_income > 0
            else 0
        )

        return {
            "total_expense": round(total_expense, 2),
            "total_income": round(total_income, 2),
            "daily_average": round(daily_avg, 2),
            "active_days": active_days,
            "transaction_count": len(transactions),
            "top_categories": [(cat, round(amt, 2)) for cat, amt in top_categories[:5]],
            "biggest_expense": (
                {"category": biggest[0], "amount": biggest[1], "date": biggest[2]}
                if biggest
                else None
            ),
            "velocity_pct": round(velocity_pct, 1),
            "velocity_direction": (
                "increasing"
                if velocity_pct > 5
                else ("decreasing" if velocity_pct < -5 else "stable")
            ),
            "projected_monthly": round(projected_monthly, 2),
            "savings_rate": round(savings_rate, 1),
        }

    def get_monthly_comparison(self, user_id):
        now = datetime.now()
        current_start = now.replace(day=1).strftime("%Y-%m-%d")
        prev_month_end = now.replace(day=1) - timedelta(days=1)
        prev_start = prev_month_end.replace(day=1).strftime("%Y-%m-%d")
        prev_end = prev_month_end.strftime("%Y-%m-%d")

        curr = self._month_totals(user_id, current_start, now.strftime("%Y-%m-%d"))
        prev = self._month_totals(user_id, prev_start, prev_end)

        curr_income = curr.get("income", 0)
        curr_expense = curr.get("expense", 0)
        prev_income = prev.get("income", 0)
        prev_expense = prev.get("expense", 0)

        return {
            "current": {
                "income": round(curr_income, 2),
                "expense": round(curr_expense, 2),
                "balance": round(curr_income - curr_expense, 2),
            },
            "previous": {
                "income": round(prev_income, 2),
                "expense": round(prev_expense, 2),
                "balance": round(prev_income - prev_expense, 2),
            },
            "changes": {
                "income_pct": self._pct_change(curr_income, prev_income),
                "expense_pct": self._pct_change(curr_expense, prev_expense),
                "balance_pct": self._pct_change(
                    curr_income - curr_expense, prev_income - prev_expense
                ),
            },
        }

    def get_category_breakdown(self, user_id, days=30, ttype="expense"):
        transactions = self.get_transactions(user_id, days=days)
        cat_totals = {}
        for typ, cat, amt, _, _ in transactions:
            if typ == ttype:
                cat_totals[cat] = cat_totals.get(cat, 0) + amt

        total = sum(cat_totals.values())
        breakdown = []
        for cat, amt in sorted(cat_totals.items(), key=lambda x: x[1], reverse=True):
            pct = (amt / total * 100) if total > 0 else 0
            bar_len = int(pct / 100 * 30)
            breakdown.append(
                {
                    "category": cat,
                    "amount": round(amt, 2),
                    "percentage": round(pct, 1),
                    "bar": "█" * bar_len + "░" * (30 - bar_len),
                }
            )
        return breakdown

    def get_monthly_trend(self, user_id, months=6):
        now = datetime.now()
        trend = []
        conn = self._connect()
        try:
            for i in range(months - 1, -1, -1):
                month_date = now - timedelta(days=i * 30)
                start = month_date.replace(day=1).strftime("%Y-%m-%d")
                if month_date.month == 12:
                    end = month_date.replace(
                        year=month_date.year + 1, month=1, day=1
                    ) - timedelta(days=1)
                else:
                    end = month_date.replace(
                        month=month_date.month + 1, day=1
                    ) - timedelta(days=1)

                rows = conn.execute(
                    "SELECT type, SUM(amount) FROM transactions "
                    "WHERE user_id = ? AND date >= ? AND date <= ? GROUP BY type",
                    (user_id, start, end.strftime("%Y-%m-%d") + " 23:59:59"),
                ).fetchall()

                data = {t: amt for t, amt in rows}
                income = round(data.get("income", 0), 2)
                expense = round(data.get("expense", 0), 2)
                trend.append(
                    {
                        "month": month_date.strftime("%b %Y"),
                        "income": income,
                        "expense": expense,
                        "balance": round(income - expense, 2),
                    }
                )
        finally:
            conn.close()
        return trend

    def get_recurring_expenses(self, user_id, days=90):
        transactions = self.get_transactions(user_id, days=days)

        cat_months = {}
        for ttype, cat, amt, date, _ in transactions:
            if ttype != "expense":
                continue
            try:
                month_key = datetime.strptime(date[:10], "%Y-%m-%d").strftime("%Y-%m")
            except Exception:
                continue
            cat_months.setdefault(cat, {})
            cat_months[cat][month_key] = cat_months[cat].get(month_key, 0) + amt

        recurring = []
        for cat, months_data in cat_months.items():
            if len(months_data) >= 2:
                amounts = list(months_data.values())
                recurring.append(
                    {
                        "category": cat,
                        "months_active": len(months_data),
                        "average_amount": round(sum(amounts) / len(amounts), 2),
                        "total": round(sum(amounts), 2),
                    }
                )
        recurring.sort(key=lambda x: x["total"], reverse=True)
        return recurring

    def get_budget_alerts(self, user_id, days=30):
        insights = self.get_spending_insights(user_id, days=days)
        comparison = self.get_monthly_comparison(user_id)
        alerts = []

        if (
            insights["transaction_count"] > 0
            and insights["total_income"] > 0
            and insights["savings_rate"] < 10
        ):
            alerts.append(
                {
                    "level": "danger",
                    "title": "Spending Alert",
                    "message": f"Your savings rate is only {insights['savings_rate']:.1f}%. Consider reducing expenses.",
                }
            )

        if insights["velocity_direction"] == "increasing":
            alerts.append(
                {
                    "level": "warning",
                    "title": "Spending Increasing",
                    "message": f"Your spending is {insights['velocity_pct']:+.1f}% higher in the second half of the period.",
                }
            )

        expense_pct = comparison["changes"]["expense_pct"]
        if expense_pct is not None and expense_pct > 20:
            alerts.append(
                {
                    "level": "warning",
                    "title": "Month Over Budget",
                    "message": f"Expenses increased {expense_pct:+.1f}% vs last month.",
                }
            )

        for goal_id, name, target, current, deadline in self.get_goals(user_id):
            if target > 0:
                pct = (current / target) * 100
                if 80 <= pct < 100:
                    alerts.append(
                        {
                            "level": "info",
                            "title": f"Goal Nearing: {name}",
                            "message": f"{pct:.0f}% reached — {target - current:,.0f} remaining.",
                        }
                    )
                elif pct >= 100:
                    alerts.append(
                        {
                            "level": "success",
                            "title": f"Goal Reached: {name}",
                            "message": f"You've reached your target of {target:,.0f}!",
                        }
                    )

        if not alerts:
            alerts.append(
                {
                    "level": "success",
                    "title": "All Good",
                    "message": "Your finances are on track. Keep it up!",
                }
            )

        return alerts

    def get_goal_progress(self, user_id):
        goals = self.get_goals(user_id)
        insights = self.get_spending_insights(user_id, days=30)
        monthly_savings = max(insights["total_income"] - insights["total_expense"], 0)

        result = []
        for goal_id, name, target, current, deadline in goals:
            remaining = max(target - current, 0)
            pct = (current / target * 100) if target > 0 else 100

            if monthly_savings > 0 and remaining > 0:
                months_left = remaining / monthly_savings
                est_date = (datetime.now() + timedelta(days=months_left * 30)).strftime(
                    "%b %Y"
                )
            else:
                months_left = None
                est_date = "N/A"

            if pct >= 100:
                status = "completed"
            elif pct >= 80:
                status = "almost"
            else:
                status = "on_track"

            result.append(
                {
                    "id": goal_id,
                    "name": name,
                    "target": target,
                    "current": round(current, 2),
                    "remaining": round(remaining, 2),
                    "percentage": round(pct, 1),
                    "status": status,
                    "estimated_date": est_date,
                    "months_left": round(months_left, 1) if months_left else None,
                }
            )
        return result
