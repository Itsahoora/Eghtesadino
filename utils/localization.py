"""Centralized localization system for Eghtesadino.

All visible UI strings are defined here, keyed by language code.
The active language is loaded from ``user_theme.json`` under the key
``language`` and falls back to English.
"""

import os
import json

LOCALES_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets', 'locales')
LANGUAGE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'user_theme.json')


def _load_language():
    try:
        with open(LANGUAGE_FILE, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        return data.get('language', 'en')
    except Exception:
        return 'en'


def _save_language(lang):
    try:
        with open(LANGUAGE_FILE, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
    except Exception:
        data = {}
    data['language'] = lang
    try:
        with open(LANGUAGE_FILE, 'w', encoding='utf-8') as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
    except Exception:
        pass


LOCALES = {
    'en': {
        'app_name': 'Eghtesadino',
        'dashboard': 'Dashboard',
        'reports': 'Reports',
        'settings': 'Settings',
        'profile': 'Profile',
        'logout': 'Logout',
        'delete_account': 'Delete Account',
        'back': 'Back',
        'theme_dark': 'Dark mode',
        'theme_light': 'Light mode',
        'appearance': 'Appearance',
        'themes': 'Themes',
        'default': 'Default',
        'blue': 'Blue',
        'green': 'Green',
        'purple': 'Purple',
        'orange': 'Orange',
        'custom': 'Custom',
        'custom_colors': 'Custom Colors',
        'primary_color': 'Primary Color',
        'accent_color': 'Accent Color',
        'bg_color': 'Background Color',
        'card_color': 'Card Color',
        'sidebar_color': 'Sidebar Color',
        'text_color': 'Text Color',
        'reset_defaults': 'Reset to Defaults',
        'language': 'Language',
        'preview': 'Preview',
        'remove_photo': 'Remove Photo',
        'save_profile': 'Save Profile',
        'display_name': 'Display Name',
        'profile_picture': 'Profile Picture',
        'upload_photo': 'Upload Photo',
        'choose_file': 'Choose File',
        'personal_account': 'Personal Account',
        'show_learning_tips': 'Show learning tips',
        'display_scale': 'Display scale',
        'delete_confirm': 'Delete Account',
        'delete_message': 'Are you sure? This will permanently delete all your data.',
        'delete_double': 'Confirm Delete',
        'delete_double_msg': 'This action cannot be undone. Continue?',
        'logout_confirm': 'Logout',
        'logout_msg': 'Are you sure you want to logout?',
        'success': 'Success',
        'error': 'Error',
        'warning': 'Warning',
        'profile_saved': 'Profile saved successfully',
        'image_error': 'Please select a valid image file (PNG, JPG, JPEG, GIF)',
        'image_too_large': 'Image is too large. Maximum size is 5 MB.',
        'no_selection': 'No file selected',
        'about': 'About',
        'app_version': 'Eghtesadino  v3  —  Built for students',
        'by': 'Itsahoora',
        'monthly_comparison': 'Monthly Comparison',
        'monthly_trend': 'Monthly Trend (Last 6 Months)',
        'expense_breakdown': 'Expense Breakdown (30 Days)',
        'recurring_expenses': 'Recurring Expenses (2+ Months)',
        'spending_insights': 'Spending Insights (30 Days)',
        'add_transaction': 'Add Transaction',
        'add_goal': 'Add Goal',
        'goals': 'Goals',
        'balance': 'Balance',
        'income': 'Income',
        'expense': 'Expense',
        'daily_avg': 'Daily Avg',
        'savings_rate': 'Savings Rate',
        'spending': 'Spending',
        'learning_corner': 'Learning Corner',
        'no_transactions': 'No transactions yet.',
        'no_goals': 'No goals yet. Add one to start!',
        'no_data': 'No data yet',
        'all_good': 'All Good',
        'finances_on_track': 'Your finances are on track. Keep it up!',
        'sign_in': 'Sign In',
        'register': "Don't have an account?  Create one",
        'password': 'Password',
        'username': 'Username',
        'welcome': 'Welcome back,',
        'login_failed': 'Login failed',
        'invalid_credentials': 'Invalid username or password',
        'registered': 'Account created',
        'register_failed': 'Registration failed',
        'scale_changed': 'Display scale updated. Some elements may need a restart.',
        'insufficient_balance': 'Insufficient balance',
        'goal_reached': 'Goal already reached',
        'allocation_success': 'Allocation successful',
        'recent_transactions': 'Recent Transactions',
        'allocate': 'Allocate',
        'financial_insights': 'Financial Insights',
        'suggestions': 'Suggestions',
        'student_lessons': 'Student-friendly lessons',
        'goal_required': 'Please select a goal',
        'goal_deleted': 'Goal deleted',
        'no_transactions': 'No transactions yet.',
        'insufficient_balance': 'Insufficient balance',
        'invalid': 'Invalid input',
        'required': 'is required',
        'profile_save_failed': 'Failed to save profile',
        'display': 'Display',
        'apply': 'Apply',
        'colors_applied': 'Custom colors applied successfully',
        'reset_complete': 'All settings have been reset to defaults',
        'language_changed': 'Language changed. Please restart the application for full effect.',
        'amount': 'Amount',
        'description': 'Description',
    },
    'fa': {
        'app_name': 'اگتسبادینو',
        'dashboard': 'داشبورد',
        'reports': 'گزارشات',
        'settings': 'تنظیمات',
        'profile': 'پروفایل',
        'logout': 'خروج',
        'delete_account': 'حذف حساب',
        'back': 'بازگشت',
        'theme_dark': 'حالت تاریک',
        'theme_light': 'حالت روشن',
        'appearance': 'ظاهر',
        'themes': 'تم‌ها',
        'default': 'پیش‌فرض',
        'blue': 'آبی',
        'green': 'سبز',
        'purple': 'بنفش',
        'orange': 'نارنجی',
        'custom': 'سفارشی',
        'custom_colors': 'رنگ‌های سفارشی',
        'primary_color': 'رنگ اصلی',
        'accent_color': 'رنگ accent',
        'bg_color': 'رنگ پس‌زمینه',
        'card_color': 'رنگ کارت',
        'sidebar_color': 'رنگ نوار کناری',
        'text_color': 'رنگ متن',
        'reset_defaults': 'بازنشانی',
        'language': 'زبان',
        'preview': 'پیش‌نمایش',
        'remove_photo': 'حذف عکس',
        'save_profile': 'ذخیره پروفایل',
        'display_name': 'نام نمایشی',
        'profile_picture': 'تصویر پروفایل',
        'upload_photo': 'آپلود عکس',
        'choose_file': 'انتخاب فایل',
        'personal_account': 'حساب شخصی',
        'show_learning_tips': 'نمایش نکات یادگیری',
        'display_scale': 'مقیاس نمایش',
        'delete_confirm': 'حذف حساب',
        'delete_message': 'آیا مطمئن هستید؟ تمام داده‌ها به طور دائمی حذف می‌شوند.',
        'delete_double': 'تأیید حذف',
        'delete_double_msg': 'این عمل قابل بازگشت نیست. ادامه دهید؟',
        'logout_confirm': 'خروج از حساب',
        'logout_msg': 'آیا می‌خواهید از حساب خارج شوید؟',
        'success': 'موفق',
        'error': 'خطا',
        'warning': 'هشدار',
        'profile_saved': 'پروفایل با موفقیت ذخیره شد',
        'image_error': 'لطفاً یک فایل تصویر معتبر انتخاب کنید (PNG, JPG, JPEG, GIF)',
        'image_too_large': 'تصویر بزرگ است. حداکثر اندازه ۵ مگابایت.',
        'no_selection': 'فایلی انتخاب نشد',
        'about': 'درباره',
        'app_version': 'اگتسبادینو  v3  —  ساخته شده برای دانشجویان',
        'by': 'Itsahoora',
        'monthly_comparison': 'مقایسه ماهانه',
        'monthly_trend': 'روند ماهانه (۶ ماه اخیر)',
        'expense_breakdown': 'شکل هزینه‌ها (۳۰ روز)',
        'recurring_expenses': 'هزینه‌های تکراری (۲+ ماه)',
        'spending_insights': 'نکات هزینه (۳۰ روز)',
        'add_transaction': 'افزودن تراکنش',
        'add_goal': 'افزودن هدف',
        'goals': 'اهداف',
        'balance': 'موجودی',
        'income': 'درآمد',
        'expense': 'هزینه',
        'daily_avg': 'میانگین روزانه',
        'savings_rate': 'نرخ پس‌انداز',
        'spending': 'خرج',
        'learning_corner': 'گوشه یادگیری',
        'no_transactions': 'هنوز تراکنشی نیست.',
        'no_goals': 'هنوز هدفی نیست. یکی اضافه کنید!',
        'no_data': 'داده‌ای وجود ندارد',
        'all_good': 'همه خوب است',
        'finances_on_track': 'وضعیت مالی شما در مسیر است. ادامه دهید!',
        'sign_in': 'ورود',
        'register': 'حساب ندارید؟  یکی بسازید',
        'password': 'رمز عبور',
        'username': 'نام کاربری',
        'welcome': 'خوش آمدید،',
        'login_failed': 'ورود ناموفق',
        'invalid_credentials': 'نام کاربری یا رمز عبور اشتباه است',
        'registered': 'حساب ساخته شد',
        'register_failed': 'ثبت‌نام ناموفق',
        'scale_changed': 'مقیاس نمایش بروز شد. برخی عناصر ممکن است نیاز به راه‌اندازی مجدد داشته باشند.',
        'insufficient_balance': 'موجودی کافی نیست',
        'goal_reached': 'هدف قبلاً رسیده شده است',
        'allocation_success': 'تخصیص انجام شد',
        'recent_transactions': 'تراکنش‌های اخیر',
        'allocate': 'تخصیص',
        'financial_insights': 'نکات مالی',
        'suggestions': 'پیشنهادات',
        'student_lessons': 'دروس آموزشی',
        'goal_required': 'لطفاً یک هدف انتخاب کنید',
        'goal_deleted': 'هدف حذف شد',
        'no_transactions': 'هنوز تراکنشی نیست.',
        'insufficient_balance': 'موجودی کافی نیست',
        'invalid': 'ورودی نامعتبر',
        'required': 'الزامی است',
        'profile_save_failed': 'ذخیره پروفایل ناموفق بود',
        'display': 'نمایش',
        'apply': 'اعمال',
        'colors_applied': 'رنگ‌های سفارشی با موفقیت اعمال شد',
        'reset_complete': 'تمام تنظیمات به حالت پیش‌فرض بازگشت',
        'language_changed': 'زبان تغییر یافت. برای اعمال کامل لطفاً برنامه را راه‌اندازی مجدد کنید.',
        'amount': 'مبلغ',
        'description': 'توضیحات',
    },
}


def _get_lang():
    return _load_language()


def tr(key, lang=None):
    """Return the localized string for *key* in the active language."""
    if lang is None:
        lang = _get_lang()
    locale = LOCALES.get(lang, LOCALES['en'])
    return locale.get(key, key)


def set_language(lang):
    """Switch the active language and persist the choice."""
    if lang not in LOCALES:
        return False
    _save_language(lang)
    return True


def get_available_languages():
    """Return a list of (code, name) tuples for supported languages."""
    return [
        ('en', 'English'),
        ('fa', 'فارسی'),
    ]