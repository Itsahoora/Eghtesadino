"""Simple smoke tests for theme features.
Run with: python tests/run_theme_tests.py
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.theme_manager import theme_manager

errors = []

# Build settings screen — only when a display server is available
if os.environ.get('DISPLAY'):
    try:
        from screens.settings_screen import SettingsScreen
        from models.financial_advisor import FinancialAdvisor
        s = SettingsScreen(FinancialAdvisor(), None)
    except Exception as e:
        errors.append(f'SettingsScreen build failed: {e}')
else:
    print('Skipping SettingsScreen build (no DISPLAY)')

# apply_preset is currently a no-op; just ensure it doesn't crash
try:
    theme_manager.apply_preset('Ocean')
except Exception as e:
    errors.append(f'apply_preset failed: {e}')

# toggle mode roundtrip
try:
    prev = theme_manager.mode
    theme_manager.toggle_mode()
    theme_manager.toggle_mode()
    if theme_manager.mode != prev:
        errors.append('toggle_mode roundtrip failed')
except Exception as e:
    errors.append(f'toggle_mode failed: {e}')

# export / import
try:
    data = theme_manager.export_theme()
    theme_manager.import_theme(data)
except Exception as e:
    errors.append(f'export/import failed: {e}')

# color set / listeners
try:
    called = {'ok': False}

    def cb():
        called['ok'] = True

    theme_manager.register_listener(cb)
    theme_manager.set_color('primary', '#123456')
    theme_manager.unregister_listener(cb)
    if not called['ok']:
        errors.append('listener was not called on set_color')
except Exception as e:
    errors.append(f'listener test failed: {e}')

# final report
if errors:
    print('TESTS FAILED')
    for e in errors:
        print('-', e)
    raise SystemExit(1)
else:
    print('All theme smoke tests passed')
