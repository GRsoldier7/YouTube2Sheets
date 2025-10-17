"""
Modern Theme System - 2025 Design Language
Designed by the Front End Architect & Designer
"""

from __future__ import annotations

import customtkinter as ctk
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ColorPalette:
    """Modern color palette with semantic naming."""
    
    # Primary Colors - Vibrant and modern
    primary: str = "#007AFF"          # iOS Blue
    primary_dark: str = "#0056CC"     # Darker blue
    primary_light: str = "#4DA6FF"    # Lighter blue
    
    # Secondary Colors - Complementary
    secondary: str = "#5856D6"        # Purple
    secondary_dark: str = "#3D3B99"   # Dark purple
    secondary_light: str = "#7A78E8"  # Light purple
    
    # Success Colors
    success: str = "#34C759"          # Green
    success_dark: str = "#28A745"     # Dark green
    success_light: str = "#5DD979"    # Light green
    
    # Warning Colors
    warning: str = "#FF9500"          # Orange
    warning_dark: str = "#E6850E"     # Dark orange
    warning_light: str = "#FFB84D"    # Light orange
    
    # Error Colors
    error: str = "#FF3B30"            # Red
    error_dark: str = "#D70015"       # Dark red
    error_light: str = "#FF6B6B"      # Light red
    
    # Neutral Colors
    background: str = "#000000"        # Pure black
    surface: str = "#1C1C1E"          # Dark surface
    surface_secondary: str = "#2C2C2E" # Secondary surface
    surface_tertiary: str = "#3A3A3C"  # Tertiary surface
    
    # Text Colors
    text_primary: str = "#FFFFFF"      # Primary text
    text_secondary: str = "#EBEBF5"    # Secondary text
    text_tertiary: str = "#8E8E93"    # Tertiary text
    text_quaternary: str = "#48484A"  # Quaternary text
    
    # Border Colors
    border: str = "#38383A"           # Primary border
    border_secondary: str = "#48484A"  # Secondary border
    border_tertiary: str = "#636366"  # Tertiary border
    
    # Glass Effects
    glass_light: str = "rgba(255,255,255,0.1)"
    glass_medium: str = "rgba(255,255,255,0.2)"
    glass_dark: str = "rgba(0,0,0,0.3)"
    
    # Gradients
    gradient_primary: tuple = ("#007AFF", "#5856D6")
    gradient_success: tuple = ("#34C759", "#30D158")
    gradient_warning: tuple = ("#FF9500", "#FFCC02")
    gradient_error: tuple = ("#FF3B30", "#FF6B6B")


@dataclass
class Typography:
    """Modern typography system."""
    
    # Font Sizes
    font_size_xs: int = 12
    font_size_sm: int = 14
    font_size_base: int = 16
    font_size_lg: int = 18
    font_size_xl: int = 20
    font_size_2xl: int = 24
    font_size_3xl: int = 30
    font_size_4xl: int = 36
    
    # Font Weights (CustomTkinter only supports normal and bold)
    font_weight_light: str = "normal"
    font_weight_normal: str = "normal"
    font_weight_medium: str = "normal"
    font_weight_semibold: str = "bold"
    font_weight_bold: str = "bold"
    
    # Line Heights
    line_height_tight: float = 1.2
    line_height_normal: float = 1.5
    line_height_relaxed: float = 1.75


@dataclass
class Spacing:
    """Consistent spacing system."""
    
    # Base spacing unit (8px)
    space_1: int = 8
    space_2: int = 16
    space_3: int = 24
    space_4: int = 32
    space_5: int = 40
    space_6: int = 48
    space_8: int = 64
    space_10: int = 80
    space_12: int = 96
    
    # Border radius
    radius_sm: int = 8
    radius_md: int = 12
    radius_lg: int = 16
    radius_xl: int = 20
    radius_2xl: int = 24
    
    # Shadows
    shadow_sm: str = "0 1px 2px rgba(0,0,0,0.05)"
    shadow_md: str = "0 4px 6px rgba(0,0,0,0.1)"
    shadow_lg: str = "0 10px 15px rgba(0,0,0,0.1)"
    shadow_xl: str = "0 20px 25px rgba(0,0,0,0.1)"


class ModernTheme:
    """Modern theme system for YouTube2Sheets."""
    
    def __init__(self):
        self.colors = ColorPalette()
        self.typography = Typography()
        self.spacing = Spacing()
        
        # Theme state
        self.is_dark = True
        self.current_theme = "dark"
        
    def apply_theme(self, root: ctk.CTk):
        """Apply the modern theme to the application."""
        # Set appearance mode
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Configure root window
        root.configure(fg_color=self.colors.background)
        
    def get_button_style(self, variant: str = "primary") -> Dict[str, Any]:
        """Get button styling for different variants."""
        styles = {
            "primary": {
                "fg_color": self.colors.primary,
                "hover_color": self.colors.primary_dark,
                "text_color": self.colors.text_primary,
                "corner_radius": self.spacing.radius_md,
                "font": ctk.CTkFont(size=self.typography.font_size_base, weight=self.typography.font_weight_medium),
                "height": 44,
            },
            "secondary": {
                "fg_color": self.colors.surface,
                "hover_color": self.colors.surface_secondary,
                "text_color": self.colors.text_primary,
                "corner_radius": self.spacing.radius_md,
                "font": ctk.CTkFont(size=self.typography.font_size_base, weight=self.typography.font_weight_medium),
                "height": 44,
            },
            "success": {
                "fg_color": self.colors.success,
                "hover_color": self.colors.success_dark,
                "text_color": self.colors.text_primary,
                "corner_radius": self.spacing.radius_md,
                "font": ctk.CTkFont(size=self.typography.font_size_base, weight=self.typography.font_weight_medium),
                "height": 44,
            },
            "warning": {
                "fg_color": self.colors.warning,
                "hover_color": self.colors.warning_dark,
                "text_color": self.colors.text_primary,
                "corner_radius": self.spacing.radius_md,
                "font": ctk.CTkFont(size=self.typography.font_size_base, weight=self.typography.font_weight_medium),
                "height": 44,
            },
            "error": {
                "fg_color": self.colors.error,
                "hover_color": self.colors.error_dark,
                "text_color": self.colors.text_primary,
                "corner_radius": self.spacing.radius_md,
                "font": ctk.CTkFont(size=self.typography.font_size_base, weight=self.typography.font_weight_medium),
                "height": 44,
            },
            "ghost": {
                "fg_color": "transparent",
                "hover_color": self.colors.surface,
                "text_color": self.colors.text_primary,
                "corner_radius": self.spacing.radius_md,
                "font": ctk.CTkFont(size=self.typography.font_size_base, weight=self.typography.font_weight_medium),
                "height": 44,
            }
        }
        return styles.get(variant, styles["primary"])
        
    def get_input_style(self) -> Dict[str, Any]:
        """Get input field styling."""
        return {
            "fg_color": self.colors.surface,
            "border_color": self.colors.border,
            "corner_radius": self.spacing.radius_md,
            "height": 44,
            "border_width": 1,
        }
        
    def get_card_style(self) -> Dict[str, Any]:
        """Get card styling."""
        return {
            "fg_color": self.colors.surface,
            "corner_radius": self.spacing.radius_lg,
            "border_width": 1,
            "border_color": self.colors.border,
        }
        
    def get_slider_style(self) -> Dict[str, Any]:
        """Get slider styling."""
        return {
            "fg_color": self.colors.surface,
            "progress_color": self.colors.primary,
            "button_color": self.colors.primary,
            "button_hover_color": self.colors.primary_dark,
            "corner_radius": self.spacing.radius_sm,
            "height": 20,
        }
        
    def get_text_style(self, variant: str = "body") -> Dict[str, Any]:
        """Get text styling for different variants."""
        styles = {
            "heading": {
                "font": ctk.CTkFont(size=self.typography.font_size_3xl, weight=self.typography.font_weight_bold),
                "text_color": self.colors.text_primary,
            },
            "subheading": {
                "font": ctk.CTkFont(size=self.typography.font_size_2xl, weight=self.typography.font_weight_semibold),
                "text_color": self.colors.text_primary,
            },
            "body": {
                "font": ctk.CTkFont(size=self.typography.font_size_base, weight=self.typography.font_weight_normal),
                "text_color": self.colors.text_primary,
            },
            "caption": {
                "font": ctk.CTkFont(size=self.typography.font_size_sm, weight=self.typography.font_weight_normal),
                "text_color": self.colors.text_secondary,
            },
            "small": {
                "font": ctk.CTkFont(size=self.typography.font_size_xs, weight=self.typography.font_weight_normal),
                "text_color": self.colors.text_tertiary,
            }
        }
        return styles.get(variant, styles["body"])
        
    def toggle_theme(self):
        """Toggle between dark and light themes."""
        self.is_dark = not self.is_dark
        self.current_theme = "dark" if self.is_dark else "light"
        
        # Update colors based on theme
        if not self.is_dark:
            # Light theme colors
            self.colors.background = "#FFFFFF"
            self.colors.surface = "#F2F2F7"
            self.colors.surface_secondary = "#FFFFFF"
            self.colors.text_primary = "#000000"
            self.colors.text_secondary = "#3C3C43"
            self.colors.border = "#C6C6C8"
        else:
            # Dark theme colors (default)
            self.colors.background = "#000000"
            self.colors.surface = "#1C1C1E"
            self.colors.surface_secondary = "#2C2C2E"
            self.colors.text_primary = "#FFFFFF"
            self.colors.text_secondary = "#EBEBF5"
            self.colors.border = "#38383A"


# Global theme instance
theme = ModernTheme()
