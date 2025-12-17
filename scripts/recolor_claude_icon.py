"""Extract Claude icon from exe, recolor to dark bg + gold, save as ico."""
from PIL import Image
import icoextract
import io
import os

def extract_icon_from_exe(exe_path):
    """Extract the main icon from an exe file."""
    extractor = icoextract.IconExtractor(exe_path)
    # Get the first icon group - returns a BytesIO object
    ico_stream = extractor.get_icon(0)
    return Image.open(ico_stream)

def recolor_icon(img, dark_bg=(26, 26, 46), gold=(255, 215, 0)):
    """
    Recolor icon:
    - Light/white areas -> gold
    - Dark areas -> dark background
    """
    # Convert to RGBA
    img = img.convert('RGBA')
    pixels = img.load()
    width, height = img.size

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]

            if a < 10:
                # Fully transparent - make dark bg
                pixels[x, y] = dark_bg + (255,)
            else:
                # Calculate brightness
                brightness = (r + g + b) / 3

                if brightness > 128:
                    # Light pixels -> gold (preserve some alpha blending)
                    alpha_factor = a / 255
                    pixels[x, y] = (
                        int(gold[0] * alpha_factor + dark_bg[0] * (1 - alpha_factor)),
                        int(gold[1] * alpha_factor + dark_bg[1] * (1 - alpha_factor)),
                        int(gold[2] * alpha_factor + dark_bg[2] * (1 - alpha_factor)),
                        255
                    )
                else:
                    # Dark pixels -> dark bg
                    pixels[x, y] = dark_bg + (255,)

    return img

def create_recolored_ico(exe_path, output_path):
    """Main function to extract, recolor, and save icon."""
    print(f"Extracting icon from: {exe_path}")

    # Extract icon
    icon = extract_icon_from_exe(exe_path)
    print(f"Extracted icon size: {icon.size}")

    # Get the largest size if it's an ICO with multiple sizes
    if hasattr(icon, 'n_frames'):
        # ICO files can have multiple sizes
        sizes = []
        for i in range(icon.n_frames):
            icon.seek(i)
            sizes.append(icon.size)
        print(f"Available sizes: {sizes}")
        # Use largest
        icon.seek(sizes.index(max(sizes, key=lambda s: s[0])))

    # Resize to 256x256 for processing if needed
    if icon.size[0] < 256:
        icon = icon.resize((256, 256), Image.Resampling.LANCZOS)

    print(f"Processing at size: {icon.size}")

    # Recolor
    recolored = recolor_icon(icon)

    # Create multiple sizes for ICO
    sizes_to_save = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    images = []
    for s in sizes_to_save:
        resized = recolored.resize(s, Image.Resampling.LANCZOS)
        images.append(resized)

    # Save ICO
    recolored.save(output_path, format='ICO', sizes=[(s[0], s[1]) for s in sizes_to_save])
    print(f"Icon saved to: {output_path}")

    # Save PNG preview
    png_path = output_path.replace('.ico', '.png')
    recolored.save(png_path, format='PNG')
    print(f"Preview saved to: {png_path}")

    return output_path

def create_recolored_ico_custom(exe_path, output_path, fg_color, bg_color=(26, 26, 46)):
    """Create recolored icon with custom colors."""
    print(f"Extracting icon from: {exe_path}")

    icon = extract_icon_from_exe(exe_path)
    print(f"Extracted icon size: {icon.size}")

    if icon.size[0] < 256:
        icon = icon.resize((256, 256), Image.Resampling.LANCZOS)

    recolored = recolor_icon(icon, dark_bg=bg_color, gold=fg_color)

    sizes_to_save = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

    recolored.save(output_path, format='ICO', sizes=[(s[0], s[1]) for s in sizes_to_save])
    print(f"Icon saved to: {output_path}")

    png_path = output_path.replace('.ico', '.png')
    recolored.save(png_path, format='PNG')
    print(f"Preview saved to: {png_path}")

    return output_path

if __name__ == "__main__":
    import sys

    exe_path = r"C:\Users\there\.local\bin\claude.exe"

    # Check for color argument
    if len(sys.argv) > 1 and sys.argv[1] == "teal":
        output_path = r"c:\dev\Mathematic agent based solver\claude_code_teal.ico"
        teal = (0, 206, 209)  # Dark cyan/teal
        create_recolored_ico_custom(exe_path, output_path, fg_color=teal)
    else:
        output_path = r"c:\dev\Mathematic agent based solver\claude_code_gold.ico"
        gold = (255, 215, 0)
        create_recolored_ico_custom(exe_path, output_path, fg_color=gold)
