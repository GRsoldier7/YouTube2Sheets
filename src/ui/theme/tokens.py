"""
YouTube2Sheets Theme Tokens
Centralized design system for consistent UI styling.
"""
import customtkinter as ctk
from typing import Dict, Any


class Tokens:
    """Centralized design tokens for consistent UI styling."""
    
    def __init__(self):
        # 2026 Premium Color Palette
        self.colors = {
            # Core backgrounds
            'bg': '#0B0E14',           # Deep dark background
            'surface': '#111520',      # Card surface
            'surface_light': '#16213e', # Lighter surface
            'surface_2': '#151A28',    # Elevated surface
            'border': '#1E2433',       # Subtle borders
            'border_light': '#475569', # Lighter borders
            'border_dark': '#0F172A',  # Darker borders
            
            # Text hierarchy
            'text_1': '#F5F7FA',       # Primary text (high contrast)
            'text_2': '#C6CBD6',       # Secondary text
            'muted': '#8A90A4',        # Muted text
            
            # Action colors
            'primary': '#2DE37B',      # Run/confirm (green)
            'primary_dark': '#26C96C', # Darker green
            'primary_light': '#34D399', # Lighter green
            'secondary': '#00BFA6',    # Refresh/utility (teal)
            'secondary_dark': '#00A693', # Darker teal
            'secondary_light': '#00D4AA', # Lighter teal
            
            # Accent colors
            'accent': '#7C3AED',       # Purple accent
            'accent_dark': '#6D28D9',  # Darker purple
            'accent_light': '#A78BFA', # Lighter purple
            
            # Status colors
            'success': '#2DE37B',      # Success (green)
            'success_dark': '#26C96C', # Darker green
            'success_light': '#34D399', # Lighter green
            'info': '#38BDF8',         # Info (blue)
            'info_dark': '#0EA5E9',    # Darker blue
            'info_light': '#67E8F9',   # Lighter blue
            'warning': '#F59E0B',      # Warning (amber)
            'warning_dark': '#D97706', # Darker amber
            'warning_light': '#FBBF24', # Lighter amber
            'danger': '#EF4444',       # Danger (red)
            'danger_dark': '#DC2626',  # Darker red
            'danger_light': '#F87171', # Lighter red
            
            # Legacy compatibility
            'background': '#0B0E14',
            'text_primary': '#F5F7FA',
            'text_secondary': '#C6CBD6',
            'text_muted': '#8A90A4',
            'error': '#EF4444',
            'error_dark': '#DC2626',
            'error_light': '#F87171',
        }
        
        # Modern typography scale (lazy initialization)
        self.fonts = {}
        
        # Spacing scale (4px base unit)
        self.spacing = {
            'xs': 4,    # 4px
            'sm': 8,    # 8px
            'md': 16,   # 16px
            'lg': 24,   # 24px
            'xl': 32,   # 32px
            '2xl': 48,  # 48px
            '3xl': 64,  # 64px
        }
        
        # Border radius scale
        self.radius = {
            'xs': 4,    # 4px
            'sm': 8,    # 8px
            'field': 10, # 10px
            'card': 12, # 12px
            'button': 12, # 12px
            'chip': 16, # 16px
            'lg': 20,   # 20px
        }
        
        # Elevation (shadows)
        self.elevation = {
            'none': 'none',
            'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
            'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
            'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
            'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
        }
    
    def initialize_fonts(self):
        """Initialize fonts when a root window is available."""
        if not self.fonts:
            self.fonts = {
                'h1': ctk.CTkFont(size=32, weight="bold"),
                'h2': ctk.CTkFont(size=24, weight="bold"),
                'h3': ctk.CTkFont(size=20, weight="bold"),
                'h4': ctk.CTkFont(size=18, weight="bold"),
                'h5': ctk.CTkFont(size=16, weight="bold"),
                'h6': ctk.CTkFont(size=14, weight="bold"),
                'body': ctk.CTkFont(size=14, weight="normal"),
                'label': ctk.CTkFont(size=12, weight="normal"),
                'helper': ctk.CTkFont(size=11, weight="normal"),
                'button': ctk.CTkFont(size=14, weight="bold"),
                'chip': ctk.CTkFont(size=10, weight="normal"),
                'input': ctk.CTkFont(size=14, weight="normal"),
            }
    
    def get_font(self, font_name: str):
        """Get a font by name, initializing if needed."""
        if not self.fonts:
            self.initialize_fonts()
        return self.fonts.get(font_name, ctk.CTkFont())


# Global tokens instance
tokens = Tokens()


def get_tokens() -> Tokens:
    """Get the global tokens instance."""
    return tokens
