"""
YouTube2Sheets Custom Icon Generator
Creates a professional YouTube-themed icon with Google Sheets elements
"""

import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("❌ Pillow not installed. Installing now...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image, ImageDraw, ImageFont


def create_youtube2sheets_icon(output_path: Path) -> None:
    """
    Creates a modern 2025 YouTube2Sheets icon with:
    - Sleek dark gradient background
    - Modern YouTube play button with glass effect
    - Clean Google Sheets grid design
    - Contemporary flat design elements
    - Professional 2025 aesthetic
    """
    # Create base image at high resolution
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Modern dark gradient background (dark blue to black)
    margin = 8
    bg_rect = [(margin, margin), (size - margin, size - margin)]
    
    # Create sleek gradient from dark blue to black
    for i in range(size - 2 * margin):
        ratio = i / (size - 2 * margin)
        r = int(30 * (1 - ratio) + 0 * ratio)    # 30 -> 0
        g = int(40 * (1 - ratio) + 0 * ratio)    # 40 -> 0  
        b = int(60 * (1 - ratio) + 0 * ratio)    # 60 -> 0
        
        y = margin + i
        draw.line([(margin, y), (size - margin, y)], fill=(r, g, b, 255))
    
    # Add subtle shadow for depth
    shadow_offset = 2
    draw.rounded_rectangle(
        [(margin + shadow_offset, margin + shadow_offset), 
         (size - margin + shadow_offset, size - margin + shadow_offset)],
        radius=20,
        fill=(0, 0, 0, 30)
    )
    
    # Main background with modern rounded corners
    draw.rounded_rectangle(
        bg_rect,
        radius=20,
        fill=(30, 40, 60, 255)
    )
    
    # Modern YouTube play button (center-left)
    play_center_x = size // 2 - 25
    play_center_y = size // 2
    play_size = 50
    
    # Play button background with glass effect
    play_bg_rect = [
        (play_center_x - play_size//2 - 8, play_center_y - play_size//2 - 8),
        (play_center_x + play_size//2 + 8, play_center_y + play_size//2 + 8)
    ]
    draw.rounded_rectangle(play_bg_rect, radius=12, fill=(255, 255, 255, 20))
    
    # Play triangle
    play_triangle = [
        (play_center_x - play_size//3, play_center_y - play_size//2),
        (play_center_x - play_size//3, play_center_y + play_size//2),
        (play_center_x + play_size*2//3, play_center_y)
    ]
    draw.polygon(play_triangle, fill='#FF0000')  # YouTube red
    
    # Play button highlight
    highlight_triangle = [
        (play_center_x - play_size//3 + 3, play_center_y - play_size//2 + 3),
        (play_center_x - play_size//3 + 3, play_center_y + play_size//2 - 3),
        (play_center_x + play_size*2//3 - 6, play_center_y)
    ]
    draw.polygon(highlight_triangle, fill=(255, 100, 100, 200))
    
    # Modern Google Sheets grid (top-right)
    grid_size = 60
    grid_x = size - margin - grid_size - 8
    grid_y = margin + 15
    
    # Grid background with modern styling
    grid_bg_rect = [
        (grid_x - 4, grid_y - 4),
        (grid_x + grid_size + 4, grid_y + grid_size + 4)
    ]
    draw.rounded_rectangle(grid_bg_rect, radius=8, fill=(255, 255, 255, 15))
    
    # Main grid
    draw.rounded_rectangle(
        [(grid_x, grid_y), (grid_x + grid_size, grid_y + grid_size)],
        radius=6,
        fill='#34A853'  # Google Sheets green
    )
    
    # Clean grid lines
    cell_size = grid_size // 3
    for i in range(1, 3):
        # Vertical lines
        x = grid_x + i * cell_size
        draw.line([(x, grid_y + 4), (x, grid_y + grid_size - 4)], fill='white', width=1)
        # Horizontal lines
        y = grid_y + i * cell_size
        draw.line([(grid_x + 4, y), (grid_x + grid_size - 4, y)], fill='white', width=1)
    
    # Modern data visualization (mini charts)
    chart_x = grid_x + 8
    chart_y = grid_y + 8
    chart_width = grid_size - 16
    chart_height = grid_size - 16
    
    # Bar chart data
    bar_data = [0.3, 0.7, 0.5, 0.9, 0.6, 0.4]
    bar_width = chart_width // 6
    for i, height_ratio in enumerate(bar_data):
        bar_x = chart_x + i * bar_width
        bar_height = int(chart_height * height_ratio)
        bar_y = chart_y + chart_height - bar_height
        draw.rectangle(
            [(bar_x + 1, bar_y), (bar_x + bar_width - 1, chart_y + chart_height)],
            fill=(255, 255, 255, 180)
        )
    
    # Modern accent elements
    # Top-left corner accent
    accent_size = 20
    accent_x = margin + 15
    accent_y = margin + 15
    
    # Gradient circle accent
    for i in range(accent_size):
        alpha = int(100 * (1 - i / accent_size))
        color = (255, 255, 255, alpha)
        draw.ellipse(
            [(accent_x, accent_y + i), (accent_x + accent_size - i, accent_y + accent_size)],
            fill=color
        )
    
    # Bottom-right corner accent
    accent2_x = size - margin - accent_size - 15
    accent2_y = size - margin - accent_size - 15
    
    for i in range(accent_size):
        alpha = int(80 * (1 - i / accent_size))
        color = (100, 200, 255, alpha)
        draw.ellipse(
            [(accent2_x, accent2_y + i), (accent2_x + accent_size - i, accent2_y + accent_size)],
            fill=color
        )
    
    # Save as .ico with multiple sizes
    icon_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    icon_images = []
    
    for icon_size in icon_sizes:
        icon_img = img.resize(icon_size, Image.Resampling.LANCZOS)
        icon_images.append(icon_img)
    
    # Save as .ico
    icon_images[0].save(
        output_path,
        format='ICO',
        sizes=[img.size for img in icon_images],
        append_images=icon_images[1:]
    )
    
    print(f"✅ Icon created successfully: {output_path}")


def main():
    """Main entry point"""
    # Determine project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Output path for icon
    icon_path = project_root / "YouTube2Sheets.ico"
    
    print("\n🎨 Creating YouTube2Sheets custom icon...")
    print(f"📍 Output: {icon_path}\n")
    
    create_youtube2sheets_icon(icon_path)
    
    print("\n🎯 Modern 2025 Icon features:")
    print("   • Sleek dark gradient background (dark blue to black)")
    print("   • Modern YouTube play button with glass effect")
    print("   • Clean Google Sheets grid with data visualization")
    print("   • Contemporary flat design elements")
    print("   • Professional multi-resolution .ico format")
    print("   • 2025 aesthetic - no more 1995 look!")
    print("\n✅ Done!\n")


if __name__ == "__main__":
    main()

