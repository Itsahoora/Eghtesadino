import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.financial_advisor import FinancialAdvisor
from utils.resource_path import resource_path

HAS_DISPLAY = bool(os.environ.get("DISPLAY"))


class FinancialFeatureTests(unittest.TestCase):
    def setUp(self):
        self.advisor = FinancialAdvisor()
        self.advisor.db_path = resource_path("test_financial_data.db")
        self.advisor.init_database()

    def tearDown(self):
        try:
            os.remove(self.advisor.db_path)
        except FileNotFoundError:
            pass

    def test_login_returns_authenticated_user_profile(self):
        self.assertTrue(self.advisor.register_user("student", "strong-pass"))
        auth = self.advisor.login_user("student", "strong-pass")
        self.assertIsNotNone(auth)
        self.assertIn("id", auth)
        self.assertEqual(auth["username"], "student")

    def test_analysis_and_normalization_work(self):
        self.assertTrue(self.advisor.register_user("student", "strong-pass"))
        user = self.advisor.login_user("student", "strong-pass")
        self.assertIsNotNone(user)

        self.advisor.add_transaction(
            user["id"], "expense", " Food ", 250, description="  Lunch   "
        )
        self.advisor.add_transaction(
            user["id"], "income", " Salary ", 1000, description="  Allowance  "
        )

        normalized = self.advisor.normalize_transaction_data(
            "expense", " Food ", 250, "  Lunch   "
        )
        self.assertEqual(normalized["category"], "Food")
        self.assertEqual(normalized["amount"], 250.0)
        self.assertEqual(normalized["description"], "Lunch")

        insights = self.advisor.get_financial_insights(user["id"])
        self.assertIn("summary", insights)
        self.assertIn("recommendations", insights)

    def test_register_and_login_rejects_wrong_password(self):
        self.assertTrue(self.advisor.register_user("student2", "strong-pass"))
        auth = self.advisor.login_user("student2", "wrong-pass")
        self.assertIsNone(auth)

    def test_plaintext_password_not_stored(self):
        self.assertTrue(self.advisor.register_user("secure_user", "s3cret"))
        conn = self.advisor._connect()
        row = conn.execute(
            "SELECT password FROM users WHERE username = ?", ("secure_user",)
        ).fetchone()
        conn.close()
        self.assertIsNone(row[0])

    def test_transaction_cache_invalidated_on_write(self):
        self.assertTrue(self.advisor.register_user("student", "strong-pass"))
        user = self.advisor.login_user("student", "strong-pass")

        self.advisor.add_transaction(user["id"], "expense", "Food", 100)
        cached = self.advisor.get_transactions(user["id"], days=30)
        self.assertEqual(len(cached), 1)

        self.advisor.add_transaction(user["id"], "income", "Salary", 500)
        after_write = self.advisor.get_transactions(user["id"], days=30)
        self.assertEqual(len(after_write), 2, "cached rows must refresh after a write")

        self.assertIn(500.0, [t[2] for t in after_write])

    def test_allocate_to_goal_invalidates_cache(self):
        self.assertTrue(self.advisor.register_user("student", "strong-pass"))
        user = self.advisor.login_user("student", "strong-pass")
        self.advisor.add_transaction(user["id"], "income", "Salary", 1000)
        self.advisor.add_goal(user["id"], "Laptop", 800)

        before = self.advisor.get_balance(user["id"])
        self.advisor.get_spending_insights(user["id"])  # warms transaction cache

        goals = self.advisor.get_goals(user["id"])
        ok, _ = self.advisor.allocate_to_goal(user["id"], goals[0][0], 200)
        self.assertTrue(ok)
        self.assertEqual(self.advisor.get_balance(user["id"]), before - 200)
        self.assertEqual(self.advisor.get_goal_progress(user["id"])[0]["current"], 200)

    def test_encrypted_fields_round_trip_and_salt_stable(self):
        self.assertTrue(self.advisor.register_user("student", "strong-pass"))
        user = self.advisor.login_user("student", "strong-pass")
        self.advisor.add_transaction(
            user["id"], "expense", "Secret Category", 42, description="hidden note"
        )

        t = self.advisor.get_transactions(user["id"], days=30)[0]
        self.assertEqual(t[1], "Secret Category")
        self.assertEqual(t[4], "hidden note")

        stored = (
            self.advisor._connect()
            .execute(
                "SELECT category FROM transactions WHERE user_id = ?",
                (user["id"],),
            )
            .fetchone()[0]
        )
        self.assertTrue(stored.startswith("enc:"))
        self.assertNotIn("Secret Category", stored)
        self.advisor._connect().close()

        self.assertEqual(
            self.advisor._get_user_salt(user["id"]),
            self.advisor._get_user_salt(user["id"]),
        )

    def test_cache_isolated_per_user(self):
        self.assertTrue(self.advisor.register_user("alice", "pass-alice"))
        self.assertTrue(self.advisor.register_user("bob", "pass-bob"))
        alice = self.advisor.login_user("alice", "pass-alice")
        bob = self.advisor.login_user("bob", "pass-bob")

        self.advisor.add_transaction(alice["id"], "expense", "Food", 100)
        self.advisor.add_transaction(bob["id"], "expense", "Rent", 999)

        self.assertEqual(len(self.advisor.get_transactions(bob["id"], days=30)), 1)
        bob_trx = self.advisor.get_transactions(bob["id"], days=30)[0]
        self.assertEqual(bob_trx[1], "Rent")
        alice_trx = self.advisor.get_transactions(alice["id"], days=30)[0]
        self.assertEqual(alice_trx[1], "Food")


if __name__ == "__main__":
    unittest.main()
