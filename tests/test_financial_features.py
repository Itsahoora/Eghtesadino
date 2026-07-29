import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.financial_advisor import FinancialAdvisor
from utils.resource_path import resource_path

HAS_DISPLAY = bool(os.environ.get('DISPLAY'))


class FinancialFeatureTests(unittest.TestCase):
    def setUp(self):
        self.advisor = FinancialAdvisor()
        self.advisor.db_path = resource_path('test_financial_data.db')
        self.advisor.init_database()

    def tearDown(self):
        try:
            os.remove(self.advisor.db_path)
        except FileNotFoundError:
            pass

    def test_login_returns_authenticated_user_profile(self):
        self.assertTrue(self.advisor.register_user('student', 'strong-pass'))
        auth = self.advisor.login_user('student', 'strong-pass')
        self.assertIsNotNone(auth)
        self.assertIn('id', auth)
        self.assertEqual(auth['username'], 'student')

    def test_analysis_and_normalization_work(self):
        self.assertTrue(self.advisor.register_user('student', 'strong-pass'))
        user = self.advisor.login_user('student', 'strong-pass')
        self.assertIsNotNone(user)

        self.advisor.add_transaction(user['id'], 'expense', ' Food ', 250, description='  Lunch   ')
        self.advisor.add_transaction(user['id'], 'income', ' Salary ', 1000, description='  Allowance  ')

        normalized = self.advisor.normalize_transaction_data('expense', ' Food ', 250, '  Lunch   ')
        self.assertEqual(normalized['category'], 'Food')
        self.assertEqual(normalized['amount'], 250.0)
        self.assertEqual(normalized['description'], 'Lunch')

        insights = self.advisor.get_financial_insights(user['id'])
        self.assertIn('summary', insights)
        self.assertIn('recommendations', insights)

    def test_register_and_login_rejects_wrong_password(self):
        self.assertTrue(self.advisor.register_user('student2', 'strong-pass'))
        auth = self.advisor.login_user('student2', 'wrong-pass')
        self.assertIsNone(auth)

    def test_plaintext_password_not_stored(self):
        self.assertTrue(self.advisor.register_user('secure_user', 's3cret'))
        conn = self.advisor._connect()
        row = conn.execute("SELECT password FROM users WHERE username = ?", ('secure_user',)).fetchone()
        conn.close()
        self.assertIsNone(row[0])


if __name__ == '__main__':
    unittest.main()
