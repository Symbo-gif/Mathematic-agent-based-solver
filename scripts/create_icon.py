"""Create Claude Code icon with dark background and gold sparkle."""
from PIL import Image, ImageDraw
import math

def create_claude_sparkle_icon(size=256, output_path="claude_code_gold.ico"):
    """Create a Claude-style sparkle icon with dark bg and gold foreground."""

    # Colors
    dark_bg = (26, 26, 46)  # #1a1a2e
    gold = (255, 215, 0)     # #FFD700

    # Create image with dark background
    img = Image.new('RGBA', (size, size), dark_bg + (255,))
    draw = ImageDraw.Draw(img)

    center = size // 2

    # Claude sparkle - sharp 4-pointed star
    # Parameters for pointy star shape
    outer_radius = size * 0.44  # Long sharp points
    inner_radius = size * 0.08  # Very thin waist for sharp look

    points = []
    num_main_points = 4
    smoothness = 20  # More points for smoother curves

    for i in range(num_main_points * smoothness):
        angle = (2 * math.pi * i) / (num_main_points * smoothness) - math.pi / 2

        # Position within segment (0 to 1)
        t = (i % smoothness) / smoothness

        # Use power function for sharper points
        # At t=0 (main point): factor = 1
        # At t=0.5 (indent): factor = 0
        # Sharp falloff using higher power
        if t < 0.5:
            # Sharp descent from point to indent
            factor = (1 - (t * 2)) ** 2.5
        else:
            # Sharp ascent from indent to point
            factor = ((t - 0.5) * 2) ** 2.5

        radius = inner_radius + (outer_radius - inner_radius) * factor

        x = center + radius * math.cos(angle)
        y = center + radius * math.sin(angle)
        points.append((x, y))

    # Draw the sparkle
    draw.polygon(points, fill=gold)

    # Save as ICO with multiple sizes for best quality
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    images = []
    for s in sizes:
        resized = img.resize(s, Image.Resampling.LANCZOS)
        images.append(resized)

    # Save ICO
    img.save(output_path, format='ICO', sizes=[(s[0], s[1]) for s in sizes])
    print(f"Icon saved to: {output_path}")

    # Also save PNG for preview
    png_path = output_path.replace('.ico', '.png')
    img.save(png_path, format='PNG')
    print(f"Preview saved to: {png_path}")

    return output_path

if __name__ == "__main__":
    output = r"c:\dev\Mathematic agent based solver\claude_code_gold.ico"
    create_claude_sparkle_icon(256, output)
