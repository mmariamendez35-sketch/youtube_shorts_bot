# generate_thumbnail.py
"""Automated HD YouTube Thumbnail Generator (1280x720) for prayer videos.
Generates sacred, high-CTR thumbnails with golden framing, dark vignette,
and prominent typography that drives clicks and watch time on YouTube.
"""
import logging
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(level=logging.INFO)

def generate_long_thumbnail(
    topic: str,
    style_index: int = 0,
    output_path: Path = Path("output/thumbnail.jpg"),
    width: int = 1280,
    height: int = 720,
) -> Path:
    """Generate a high-converting HD 1280x720 thumbnail for a long-form prayer video."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. Select religious image from assets
    prayers_dir = Path("assets/prayers")
    images = list(prayers_dir.glob("*.jpg")) + list(prayers_dir.glob("*.png"))
    images = [img for img in images if img.stat().st_size > 1000]

    if not images:
        logging.warning("No images found in assets/prayers for thumbnail.")
        return None

    img_file = images[style_index % len(images)]
    logging.info(f"Generating thumbnail using sacred art: {img_file.name}")

    im = Image.open(img_file).convert("RGB")

    # 2. Aspect fill 1280x720
    im_ratio = im.width / im.height
    target_ratio = width / height
    if im_ratio > target_ratio:
        new_height = height
        new_width = int(height * im_ratio)
    else:
        new_width = width
        new_height = int(width / im_ratio)

    im = im.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Center crop
    left = (new_width - width) // 2
    top = (new_height - height) // 2
    im = im.crop((left, top, left + width, top + height))

    # 3. Add dark gradient vignette for superior text contrast
    gradient = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(gradient)

    for y in range(height):
        # Darker towards the bottom where headlines sit
        alpha = int(170 * (y / height) ** 1.2)
        g_draw.line([(0, y), (width, y)], fill=(0, 0, 0, min(220, alpha + 35)))

    im = Image.alpha_composite(im.convert("RGBA"), gradient)
    draw = ImageDraw.Draw(im)

    # 4. Golden decorative border (sacred YouTube style)
    border_width = 8
    draw.rectangle(
        [(border_width // 2, border_width // 2), (width - border_width // 2, height - border_width // 2)],
        outline=(255, 215, 0, 230),  # Bright Gold
        width=border_width,
    )

    # 5. Fonts setup
    font_main = None
    font_sub = None
    font_badge = None

    possible_fonts = [
        "arialbd.ttf",
        "DejaVuSans-Bold.ttf",
        "FreeSansBold.ttf",
        "NotoSans-Bold.ttf",
        "arial.ttf",
    ]
    for font_name in possible_fonts:
        try:
            font_main = ImageFont.truetype(font_name, 66)
            font_sub = ImageFont.truetype(font_name, 40)
            font_badge = ImageFont.truetype(font_name, 36)
            break
        except Exception:
            continue

    if not font_main:
        font_main = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_badge = ImageFont.load_default()

    def draw_text_with_outline(x, y, text, font, fill_color, outline_color=(0, 0, 0), outline_range=4):
        # Heavy black outline for maximum visibility on all screen sizes
        for ox in range(-outline_range, outline_range + 1):
            for oy in range(-outline_range, outline_range + 1):
                if ox != 0 or oy != 0:
                    draw.text((x + ox, y + oy), text, font=font, fill=outline_color)
        # Drop shadow
        draw.text((x + 5, y + 5), text, font=font, fill=(0, 0, 0, 200))
        # Main text
        draw.text((x, y), text, font=font, fill=fill_color)

    # 6. Parse headline and sub-hook from topic
    clean_topic = topic.replace("🙏", "").strip()
    
    # Category badge
    badge_text = "✝️ 10 MINUTOS CON DIOS — ORACIÓN COMPLETA"
    draw_text_with_outline(55, 45, badge_text, font_badge, (255, 235, 59), outline_range=3)

    # Headline formatting
    if "noche" in clean_topic.lower():
        main_headline = "ORACIÓN DE LA NOCHE"
        sub_headline = "Duerme en Paz y bajo la Protección de Dios"
    elif "mañana" in clean_topic.lower():
        main_headline = "ORACIÓN DE LA MAÑANA"
        sub_headline = "Comienza tu Día con Fe y Abre Puertas"
    elif "sanación" in clean_topic.lower() or "enfermedad" in clean_topic.lower():
        main_headline = "ORACIÓN DE SANACIÓN"
        sub_headline = "Poder Sobrenatural para Cuerpo y Alma"
    elif "protección" in clean_topic.lower():
        main_headline = "PROTECCIÓN TOTAL"
        sub_headline = "Ningún Mal Tocará tu Hogar ni a tu Familia"
    elif "provisión" in clean_topic.lower() or "trabajo" in clean_topic.lower():
        main_headline = "PROVISIÓN Y TRABAJO"
        sub_headline = "Dios Abrirá Puertas de Bendición Hoy"
    elif "guerra" in clean_topic.lower() or "liberación" in clean_topic.lower():
        main_headline = "GUERRA ESPIRITUAL"
        sub_headline = "Victoria y Rompimiento de Cadenas"
    else:
        main_headline = clean_topic.upper()[:28]
        sub_headline = "Oración Poderosa para Renovar tu Vida"

    draw_text_with_outline(55, height - 195, main_headline, font_main, (255, 255, 255), outline_range=5)
    draw_text_with_outline(55, height - 110, sub_headline, font_sub, (255, 215, 0), outline_range=4)

    final_rgb = im.convert("RGB")
    final_rgb.save(output_path, "JPEG", quality=95)
    logging.info(f"HD Thumbnail generated successfully: {output_path} ({output_path.stat().st_size} bytes)")
    return output_path
