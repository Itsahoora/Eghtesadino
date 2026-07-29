"""Simple smoke tests for theme features.
Run with: python tests/run_theme_tests.py
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.theme_manager import theme_manager

errors = []

# toggle mode roundtrip
try:
    prev = theme_manager.mode
    theme_manager.toggle_mode()
    theme_manager.toggle_mode()
    if theme_manager.mode != prev:
        errors.append('toggle_mode roundtrip failed')
except Exception as e:
    errors.append(f'toggle_mode failed: {e}')

# listener
try:
    called = {'ok': False}

    def cb():
        called['ok'] = True

    theme_manager.register_listener(cb)
    theme_manager.set_mode('light')
    theme_manager.set_mode('dark')
    theme_manager.unregister_listener(cb)
    if not called['ok']:
        errors.append('listener was not called on set_mode')
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