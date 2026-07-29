# Light-mode palette
LIGHT_COLORS = {
    # Brand
    'primary': '#2563EB',
    'primary_hover': '#1D4ED8',
    'secondary': '#7C3AED',
    'accent': '#10B981',
    'success': '#10B981',
    'danger': '#EF4444',
    'warning': '#F59E0B',
    'info': '#3B82F6',

    # Surfaces
    'dark_bg': '#F8FAFC',
    'light_bg': '#F1F5F9',
    'card_bg': '#FFFFFF',
    'elevated_bg': '#FFFFFF',
    'input_bg': '#F8FAFC',
    'divider': '#E2E8F0',

    # Text
    'text': '#0F172A',
    'text_secondary': '#475569',
    'muted_text': '#94A3B8',
    'text_on_primary': '#FFFFFF',

    # Gradients (used as single accent fills)
    'balance_gradient_start': '#2563EB',
    'balance_gradient_end': '#7C3AED',
}

# Dark-mode palette
DARK_COLORS = {
    # Brand
    'primary': '#3B82F6',
    'primary_hover': '#60A5FA',
    'secondary': '#8B5CF6',
    'accent': '#34D399',
    'success': '#34D399',
    'danger': '#F87171',
    'warning': '#FBBF24',
    'info': '#60A5FA',

    # Surfaces
    'dark_bg': '#0F172A',
    'light_bg': '#1E293B',
    'card_bg': '#1E293B',
    'elevated_bg': '#334155',
    'input_bg': '#0F172A',
    'divider': '#334155',

    # Text
    'text': '#F1F5F9',
    'text_secondary': '#CBD5E1',
    'muted_text': '#64748B',
    'text_on_primary': '#FFFFFF',

    # Gradients
    'balance_gradient_start': '#3B82F6',
    'balance_gradient_end': '#8B5CF6',
}

PRESETS = {
    'default': {
        'dark': dict(DARK_COLORS),
        'light': dict(LIGHT_COLORS),
    },
    'blue': {
        'dark': {
            **DARK_COLORS,
            'primary': '#2563EB',
            'primary_hover': '#1D4ED8',
            'accent': '#60A5FA',
            'success': '#3B82F6',
            'balance_gradient_start': '#2563EB',
            'balance_gradient_end': '#3B82F6',
        },
        'light': {
            **LIGHT_COLORS,
            'primary': '#2563EB',
            'primary_hover': '#1D4ED8',
            'accent': '#3B82F6',
            'success': '#2563EB',
            'balance_gradient_start': '#2563EB',
            'balance_gradient_end': '#3B82F6',
        },
    },
    'green': {
        'dark': {
            **DARK_COLORS,
            'primary': '#059669',
            'primary_hover': '#047857',
            'accent': '#34D399',
            'success': '#10B981',
            'balance_gradient_start': '#059669',
            'balance_gradient_end': '#34D399',
        },
        'light': {
            **LIGHT_COLORS,
            'primary': '#059669',
            'primary_hover': '#047857',
            'accent': '#10B981',
            'success': '#059669',
            'balance_gradient_start': '#059669',
            'balance_gradient_end': '#34D399',
        },
    },
    'purple': {
        'dark': {
            **DARK_COLORS,
            'primary': '#7C3AED',
            'primary_hover': '#6D28D9',
            'accent': '#A78BFA',
            'success': '#8B5CF6',
            'balance_gradient_start': '#7C3AED',
            'balance_gradient_end': '#A78BFA',
        },
        'light': {
            **LIGHT_COLORS,
            'primary': '#7C3AED',
            'primary_hover': '#6D28D9',
            'accent': '#8B5CF6',
            'success': '#7C3AED',
            'balance_gradient_start': '#7C3AED',
            'balance_gradient_end': '#A78BFA',
        },
    },
    'orange': {
        'dark': {
            **DARK_COLORS,
            'primary': '#EA580C',
            'primary_hover': '#C2410C',
            'accent': '#FB923C',
            'success': '#F97316',
            'balance_gradient_start': '#EA580C',
            'balance_gradient_end': '#FB923C',
        },
        'light': {
            **LIGHT_COLORS,
            'primary': '#EA580C',
            'primary_hover': '#C2410C',
            'accent': '#F97316',
            'success': '#EA580C',
            'balance_gradient_start': '#EA580C',
            'balance_gradient_end': '#FB923C',
        },
    },
}
