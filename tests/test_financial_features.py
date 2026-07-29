import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.financial_advisor import FinancialAdvisor

HAS_DISPLAY = bool(os.environ.get('DISPLAY'))


class FinancialFeatureTests(unittest.TestCase):
    def setUp(self):
        self.advisor = FinancialAdvisor()
        self.advisor.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_financial_data.db')
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
        user = self.advisor.login_user('student', 'strong-pass')
        self.assertIsNone(user)
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

    @unittest.skipUnless(HAS_DISPLAY, 'Requires a display server (e.g. Xvfb)')
    def test_settings_screen_can_be_created(self):
        from screens.settings_screen import SettingsScreen
        screen = SettingsScreen(self.advisor, None)
        self.assertIsNotNone(screen)


if __name__ == '__main__':
    unittest.main()
