"""
YouTube2Sheets Style Helpers
Centralized style definitions to ensure consistent button colors and text contrast.
"""
from typing import Dict, Any
from .tokens import tokens


def primary_button(**kwargs) -> Dict[str, Any]:
    """Primary button style (green, for main actions)."""
    return {
        'fg_color': tokens.colors['primary'],
        'hover_color': tokens.colors['primary_dark'],
        'text_color': tokens.colors['text_1'],  # Force white text
        'corner_radius': tokens.radius['button'],
        'font': tokens.fonts['button'],
        **kwargs
    }


def secondary_button(**kwargs) -> Dict[str, Any]:
    """Secondary button style (blue, for secondary actions)."""
    return {
        'fg_color': tokens.colors['info'],
        'hover_color': tokens.colors['info_dark'],
        'text_color': tokens.colors['text_1'],  # Force white text
        'corner_radius': tokens.radius['button'],
        'font': tokens.fonts['button'],
        **kwargs
    }


def danger_button(**kwargs) -> Dict[str, Any]:
    """Danger button style (red, for destructive actions)."""
    return {
        'fg_color': tokens.colors['danger'],
        'hover_color': tokens.colors['danger_dark'],
        'text_color': tokens.colors['text_1'],  # Force white text
        'text_color_disabled': tokens.colors['text_1'],  # Force white text even when disabled
        'corner_radius': tokens.radius['button'],
        'font': tokens.fonts['button'],
        **kwargs
    }


def success_button(**kwargs) -> Dict[str, Any]:
    """Success button style (green, for positive actions)."""
    return {
        'fg_color': tokens.colors['success'],
        'hover_color': tokens.colors['success_dark'],
        'text_color': tokens.colors['text_1'],  # Force white text
        'corner_radius': tokens.radius['button'],
        'font': tokens.fonts['button'],
        **kwargs
    }


def warning_button(**kwargs) -> Dict[str, Any]:
    """Warning button style (amber, for caution actions)."""
    return {
        'fg_color': tokens.colors['warning'],
        'hover_color': tokens.colors['warning_dark'],
        'text_color': tokens.colors['text_1'],  # Force white text
        'corner_radius': tokens.radius['button'],
        'font': tokens.fonts['button'],
        **kwargs
    }


def ghost_button(**kwargs) -> Dict[str, Any]:
    """Ghost button style (transparent, for subtle actions)."""
    return {
        'fg_color': 'transparent',
        'hover_color': tokens.colors['surface_2'],
        'text_color': tokens.colors['text_2'],
        'corner_radius': tokens.radius['button'],
        'font': tokens.fonts['button'],
        'border_width': 1,
        'border_color': tokens.colors['border'],
        **kwargs
    }


def card_style(**kwargs) -> Dict[str, Any]:
    """Card container style."""
    return {
        'fg_color': tokens.colors['surface'],
        'corner_radius': tokens.radius['card'],
        'border_width': 1,
        'border_color': tokens.colors['border'],
        **kwargs
    }


def elevated_card_style(**kwargs) -> Dict[str, Any]:
    """Elevated card style (surface_2)."""
    return {
        'fg_color': tokens.colors['surface_2'],
        'corner_radius': tokens.radius['card'],
        'border_width': 1,
        'border_color': tokens.colors['border'],
        **kwargs
    }


def input_style(**kwargs) -> Dict[str, Any]:
    """Input field style."""
    return {
        'fg_color': tokens.colors['surface_light'],
        'border_color': tokens.colors['border'],
        'text_color': tokens.colors['text_1'],
        'corner_radius': tokens.radius['field'],
        'font': tokens.fonts['input'],
        **kwargs
    }


def label_style(**kwargs) -> Dict[str, Any]:
    """Label style."""
    return {
        'text_color': tokens.colors['text_1'],
        'font': tokens.fonts['label'],
        **kwargs
    }


def helper_text_style(**kwargs) -> Dict[str, Any]:
    """Helper text style."""
    return {
        'text_color': tokens.colors['muted'],
        'font': tokens.fonts['helper'],
        **kwargs
    }
