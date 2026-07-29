import base64
import hashlib
import os
import re
import secrets
import sqlite3
from datetime import datetime, timedelta


class FinancialAdvisor:
    """Facade that owns every database operation the app needs."""

    def __init__(self):
        self.db_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "financial_data.db"
        )
        self.pepper = os.environ.get(
            "EGHTESADINO_PEPPER", "eghtesadino-student-finance-v3"
        )
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
                password_hash TEXT,
                password_salt TEXT,
                display_name TEXT,
                privacy_enabled INTEGER DEFAULT 0
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
            "password_hash": "ALTER TABLE users ADD COLUMN password_hash TEXT",
            "password_salt": "ALTER TABLE users ADD COLUMN password_salt TEXT",
            "display_name": "ALTER TABLE users ADD COLUMN display_name TEXT",
            "privacy_enabled": "ALTER TABLE users ADD COLUMN privacy_enabled INTEGER DEFAULT 0",
            "show_learning_tips": "ALTER TABLE users ADD COLUMN show_learning_tips INTEGER DEFAULT 1",
            "compact_mode": "ALTER TABLE users ADD COLUMN compact_mode INTEGER DEFAULT 0",
            "profile_pic": "ALTER TABLE users ADD COLUMN profile_pic TEXT",
        }
        for col, ddl in migrations.items():
            if col not in columns:
                cursor.execute(ddl)

    # ── Password / encryption helpers ─────────────────────

    def _hash_password(self, password, salt):
        return hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 200_000
        ).hex()

    def _verify_password(self, password, password_hash, salt):
        return self._hash_password(password, salt) == password_hash

    def _derive_key(self, user_id, salt):
        seed = f"{self.pepper}:{user_id}:{salt}".encode("utf-8")
        return hashlib.pbkdf2_hmac("sha256", seed, b"eghtesadino", 120_000)

    def _protect_text(self, text, user_id, salt):
        if text is None:
            text = ""
        key = self._derive_key(user_id, salt)
        payload = text.encode("utf-8")
        masked = bytearray(b ^ key[i % len(key)] for i, b in enumerate(payload))
        return "enc:" + base64.b64encode(masked).decode("ascii")

    def _unprotect_text(self, text, user_id, salt):
        if not text or not isinstance(text, str) or not text.startswith("enc:"):
            return text or ""
        key = self._derive_key(user_id, salt)
        data = base64.b64decode(text[4:].encode("ascii"))
        decoded = bytearray(b ^ key[i % len(key)] for i, b in enumerate(data))
        return decoded.decode("utf-8")

    def _get_user_salt(self, user_id):
        profile = self.get_user_profile(user_id)
        return profile.get("password_salt") or "default"

    # ── Input normalization ───────────────────────────────

    def normalize_transaction_data(self, ttype, category, amount, description=""):
        normalized_type = (ttype or "").strip().lower()
        if normalized_type not in {"income", "expense"}:
            normalized_type = "expense"

        normalized_category = re.sub(r"\s+", " ", (category or "").strip()).title() or "Other"
        try:
            amount_value = abs(float(amount))
        except (TypeError, ValueError):
            amount_value = 0.0

        normalized_description = re.sub(r"\s+", " ", (description or "").strip()) or "No description"
        return {
            "type": normalized_type,
            "category": normalized_category,
            "amount": round(amount_value, 2),
            "description": normalized_description,
        }

    # ── User management ──────────────────────────────────

    def register_user(self, username, password):
        if not username or not password:
            return False
        try:
            salt = secrets.token_hex(16)
            password_hash = self._hash_password(password, salt)
            conn = self._connect()
            conn.execute(
                "INSERT INTO users (username, password_hash, password_salt, display_name, profile_pic) "
                "VALUES (?, ?, ?, ?, ?)",
                (username, password_hash, salt, username, None),
            )
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    def login_user(self, username, password):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, password_hash, password_salt, "
            "display_name, privacy_enabled, profile_pic "
            "FROM users WHERE username = ?",
            (username,),
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        user_id = row[0]
        stored_username = row[1]
        password_hash = row[2]
        salt = row[3]
        display_name = row[4]
        privacy_enabled = row[5]
        profile_pic = row[6] if len(row) > 6 else None

        if not password_hash or not salt or not self._verify_password(password, password_hash, salt):
            return None

        result = {
            "id": user_id,
            "username": stored_username,
            "display_name": display_name or stored_username,
            "privacy_enabled": bool(privacy_enabled),
        }
        if profile_pic:
            result["profile_pic"] = profile_pic
        return result

    def get_user_profile(self, user_id):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, display_name, password_salt, privacy_enabled, "
            "show_learning_tips, compact_mode, profile_pic FROM users WHERE id = ?",
            (user_id,),
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return {}
        return {
            "id": row[0],
            "username": row[1],
            "display_name": row[2] or row[1],
            "password_salt": row[3],
            "privacy_enabled": bool(row[4]),
            "show_learning_tips": bool(row[5]) if len(row) > 5 else True,
            "compact_mode": bool(row[6]) if len(row) > 6 else False,
            "profile_pic": row[7] if len(row) > 7 else None,
        }

    def update_user_setting(self, user_id, key, value):
        if not user_id or key not in {"privacy_enabled", "show_learning_tips", "compact_mode"}:
            return False
        try:
            conn = self._connect()
            conn.execute(f"UPDATE users SET {key} = ? WHERE id = ?", (1 if value else 0, user_id))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    def update_privacy_setting(self, user_id, enabled):
        return self.update_user_setting(user_id, "privacy_enabled", enabled)

    def update_learning_tips_setting(self, user_id, enabled):
        return self.update_user_setting(user_id, "show_learning_tips", enabled)

    def update_compact_mode_setting(self, user_id, enabled):
        return self.update_user_setting(user_id, "compact_mode", enabled)

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

    def update_profile_pic(self, user_id, pic_path):
        if not user_id:
            return False
        try:
            conn = self._connect()
            conn.execute(
                "UPDATE users SET profile_pic = ? WHERE id = ?",
                (pic_path, user_id),
            )
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    def delete_account(self, user_id):
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM goals WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    # ── Transactions ──────────────────────────────────────

    def add_transaction(self, user_id, ttype, category, amount, description=""):
        normalized = self.normalize_transaction_data(ttype, category, amount, description)
        salt = self._get_user_salt(user_id)

        conn = self._connect()
        try:
            conn.execute(
                "INSERT INTO transactions (user_id, type, category, amount, date, description) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    user_id,
                    normalized["type"],
                    self._protect_text(normalized["category"], user_id, salt),
                    normalized["amount"],
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    self._protect_text(normalized["description"], user_id, salt),
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

        salt = self._get_user_salt(user_id)
        return [
            (
                row[0],
                self._unprotect_text(row[1], user_id, salt),
                row[2],
                row[3],
                self._unprotect_text(row[4], user_id, salt),
            )
            for row in rows
        ]

    def get_all_transactions(self, user_id):
        return self.get_transactions(user_id, days=99999)

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
        conn.execute(
            "INSERT INTO goals (user_id, goal_name, target_amount, current_amount, deadline) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, goal_name, target_amount, 0.0, deadline),
        )
        conn.commit()
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
        try:
            conn = self._connect()
            conn.execute("DELETE FROM goals WHERE id = ? AND user_id = ?", (goal_id, user_id))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

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
        salt = self._get_user_salt(user_id)

        try:
            conn.execute(
                "INSERT INTO transactions (user_id, type, category, amount, date, description) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    user_id,
                    "expense",
                    self._protect_text("Goal Allocation", user_id, salt),
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
        except Exception as e:
            conn.rollback()
            return False, str(e)
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
        if old == 0:
            return 100.0 if new > 0 else 0.0
        return round(((new - old) / old) * 100, 1)

    def get_statistics(self, user_id):
        expenses = {}
        for ttype, category, amount, _, _ in self.get_transactions(user_id, days=30):
            if ttype == "expense":
                expenses[category] = expenses.get(category, 0) + amount
        return expenses

    def get_financial_insights(self, user_id):
        transactions = self.get_transactions(user_id, days=30)
        income_total = sum(amount for ttype, _, amount, _, _ in transactions if ttype == "income")
        expense_total = sum(amount for ttype, _, amount, _, _ in transactions if ttype == "expense")
        balance = income_total - expense_total
        expense_ratio = (expense_total / income_total) if income_total else 0.0
        savings_rate = max(0.0, 1 - expense_ratio)

        recommendations = []
        if savings_rate < 0.25:
            recommendations.append("Try a 20% save-first rule for your weekly allowance or income.")
        if expense_total > 0 and expense_total > income_total * 0.7:
            recommendations.append("Your spending is heavy; focus on needs before wants for the next month.")
        if balance >= 0:
            recommendations.append("You are on a healthy track—keep a small emergency buffer in your goals.")
        else:
            recommendations.append("A short spending review will restore balance quickly.")

        return {
            "summary": {
                "balance": round(balance, 2),
                "income": round(income_total, 2),
                "expenses": round(expense_total, 2),
                "savings_rate": round(savings_rate * 100, 1),
                "expense_ratio": round(expense_ratio * 100, 1),
            },
            "recommendations": recommendations,
        }

    def get_education_topics(self):
        return [
            {
                "title": "Needs vs Wants",
                "level": "Beginner",
                "tip": "Separate essentials from fun spending to build better habits.",
            },
            {
                "title": "Saving with Goals",
                "level": "Intermediate",
                "tip": "A small weekly target helps you stay consistent and motivated.",
            },
            {
                "title": "Budgeting for School",
                "level": "Student",
                "tip": "Plan your monthly budget around study costs, meals, and transport.",
            },
        ]

    def get_trend_data(self, user_id, days=30):
        conn = self._connect()
        start_date = datetime.now() - timedelta(days=days)
        rows = conn.execute(
            "SELECT date, type, amount FROM transactions "
            "WHERE user_id = ? AND date >= ? ORDER BY date ASC",
            (user_id, start_date.strftime("%Y-%m-%d %H:%M:%S")),
        ).fetchall()
        conn.close()

        income_by_day = {}
        expense_by_day = {}
        for date_str, ttype, amount in rows:
            key = date_str.split(" ")[0]
            if ttype == "income":
                income_by_day[key] = income_by_day.get(key, 0) + amount
            else:
                expense_by_day[key] = expense_by_day.get(key, 0) + amount

        income_list, expense_list = [], []
        for i in range(days):
            d_str = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            income_list.append(income_by_day.get(d_str, 0))
            expense_list.append(expense_by_day.get(d_str, 0))
        return income_list, expense_list

    def get_spending_insights(self, user_id, days=30):
        transactions = self.get_transactions(user_id, days=days)
        expenses = [(cat, amt, date) for ttype, cat, amt, date, _ in transactions if ttype == "expense"]
        total_expense = sum(amt for _, amt, _ in expenses)
        total_income = sum(amt for ttype, _, amt, _, _ in transactions if ttype == "income")

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
        savings_rate = ((total_income - total_expense) / total_income * 100) if total_income > 0 else 0

        return {
            "total_expense": round(total_expense, 2),
            "total_income": round(total_income, 2),
            "daily_average": round(daily_avg, 2),
            "active_days": active_days,
            "transaction_count": len(transactions),
            "top_categories": [(cat, round(amt, 2)) for cat, amt in top_categories[:5]],
            "biggest_expense": {"category": biggest[0], "amount": biggest[1], "date": biggest[2]} if biggest else None,
            "velocity_pct": round(velocity_pct, 1),
            "velocity_direction": (
                "increasing" if velocity_pct > 5
                else ("decreasing" if velocity_pct < -5 else "stable")
            ),
            "projected_monthly": round(projected_monthly, 2),
            "savings_rate": round(savings_rate, 1),
        }

    def get_monthly_comparison(self, user_id):
        now = datetime.now()
        current_start = now.replace(day=1).strftime("%Y-%m-%d")
        prev_month_end = (now.replace(day=1) - timedelta(days=1))
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
            breakdown.append({
                "category": cat,
                "amount": round(amt, 2),
                "percentage": round(pct, 1),
                "bar": "█" * bar_len + "░" * (30 - bar_len),
            })
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
                    end = month_date.replace(year=month_date.year + 1, month=1, day=1) - timedelta(days=1)
                else:
                    end = month_date.replace(month=month_date.month + 1, day=1) - timedelta(days=1)

                rows = conn.execute(
                    "SELECT type, SUM(amount) FROM transactions "
                    "WHERE user_id = ? AND date >= ? AND date <= ? GROUP BY type",
                    (user_id, start, end.strftime("%Y-%m-%d") + " 23:59:59"),
                ).fetchall()

                data = {t: amt for t, amt in rows}
                income = round(data.get("income", 0), 2)
                expense = round(data.get("expense", 0), 2)
                trend.append({
                    "month": month_date.strftime("%b %Y"),
                    "income": income,
                    "expense": expense,
                    "balance": round(income - expense, 2),
                })
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
                recurring.append({
                    "category": cat,
                    "months_active": len(months_data),
                    "average_amount": round(sum(amounts) / len(amounts), 2),
                    "total": round(sum(amounts), 2),
                })
        recurring.sort(key=lambda x: x["total"], reverse=True)
        return recurring

    def get_budget_alerts(self, user_id, days=30):
        insights = self.get_spending_insights(user_id, days=days)
        comparison = self.get_monthly_comparison(user_id)
        alerts = []

        if insights["savings_rate"] < 10:
            alerts.append({
                "level": "danger",
                "title": "Spending Alert",
                "message": f"Your savings rate is only {insights['savings_rate']:.1f}%. Consider reducing expenses.",
            })

        if insights["velocity_direction"] == "increasing":
            alerts.append({
                "level": "warning",
                "title": "Spending Increasing",
                "message": f"Your spending is {insights['velocity_pct']:+.1f}% higher in the second half of the period.",
            })

        if comparison["changes"]["expense_pct"] > 20:
            alerts.append({
                "level": "warning",
                "title": "Month Over Budget",
                "message": f"Expenses increased {comparison['changes']['expense_pct']:+.1f}% vs last month.",
            })

        for goal_id, name, target, current, deadline in self.get_goals(user_id):
            if target > 0:
                pct = (current / target) * 100
                if 80 <= pct < 100:
                    alerts.append({
                        "level": "info",
                        "title": f"Goal Nearing: {name}",
                        "message": f"{pct:.0f}% reached — {target - current:,.0f} remaining.",
                    })
                elif pct >= 100:
                    alerts.append({
                        "level": "success",
                        "title": f"Goal Reached: {name}",
                        "message": f"You've reached your target of {target:,.0f}!",
                    })

        if not alerts:
            alerts.append({
                "level": "success",
                "title": "All Good",
                "message": "Your finances are on track. Keep it up!",
            })

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
                est_date = (datetime.now() + timedelta(days=months_left * 30)).strftime("%b %Y")
            else:
                months_left = None
                est_date = "N/A"

            if pct >= 100:
                status = "completed"
            elif pct >= 80:
                status = "almost"
            else:
                status = "on_track"

            result.append({
                "id": goal_id,
                "name": name,
                "target": target,
                "current": round(current, 2),
                "remaining": round(remaining, 2),
                "percentage": round(pct, 1),
                "status": status,
                "estimated_date": est_date,
                "months_left": round(months_left, 1) if months_left else None,
            })
        return result
