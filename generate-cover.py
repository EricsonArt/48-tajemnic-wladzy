"""
Generate ebook cover: mask image fills entire cover, text overlaid on top.
No blending seams — the photo IS the background.
"""
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

W, H = 864, 1184
MASK_IMG = "C:/Users/cosmi/Downloads/tiktok_video_hkbwI.jpeg"
OUTPUT = "c:/Users/cosmi/Desktop/AI/Project/48-tajemnic-wladzy/cover.jpg"

RED = (220, 20, 60)
FONT_HEAVY = "C:/Windows/Fonts/impact.ttf"
FONT_BOLD = "C:/Windows/Fonts/arialbd.ttf"
FONT_REG = "C:/Windows/Fonts/arial.ttf"


def main():
    # 1. Load mask image and fill the entire cover
    img = Image.open(MASK_IMG).convert("RGB")

    # Crop/resize to fill 864x1184 (cover ratio)
    src_ratio = img.width / img.height
    target_ratio = W / H

    if src_ratio > target_ratio:
        # Image is wider — crop sides
        new_w = int(img.height * target_ratio)
        left = (img.width - new_w) // 2
        img = img.crop((left, 0, left + new_w, img.height))
    else:
        # Image is taller — crop top/bottom
        new_h = int(img.width / target_ratio)
        top = (img.height - new_h) // 2
        img = img.crop((0, top, img.width, top + new_h))

    img = img.resize((W, H), Image.LANCZOS)

    # 2. Slightly boost contrast and saturation for impact
    img = ImageEnhance.Contrast(img).enhance(1.3)
    img = ImageEnhance.Color(img).enhance(1.4)

    # 3. Dark gradient at top for text readability (60% of height)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_ov = ImageDraw.Draw(overlay)
    for y in range(int(H * 0.55)):
        t = 1 - (y / (H * 0.55))
        alpha = int(200 * t * t)  # quadratic falloff — dark at top, fades out
        draw_ov.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))

    # Slight darkening at very bottom too
    for y in range(H - 120, H):
        t = (y - (H - 120)) / 120
        alpha = int(120 * t)
        draw_ov.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))

    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay)
    img = img.convert("RGB")

    # 4. Add text
    draw = ImageDraw.Draw(img)

    # @mindtriki — top center
    font_brand = ImageFont.truetype(FONT_REG, 18)
    txt = "@mindtriki"
    bbox = draw.textbbox((0, 0), txt, font=font_brand)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 38), txt, fill=(200, 200, 200), font=font_brand)

    # "24"
    font_num = ImageFont.truetype(FONT_HEAVY, 150)
    draw.text((55, 85), "24", fill=RED, font=font_num)

    # "TAJEMNICE"
    font_t1 = ImageFont.truetype(FONT_HEAVY, 92)
    draw.text((55, 235), "TAJEMNICE", fill=RED, font=font_t1)

    # "MANIPULACJI"
    font_t2 = ImageFont.truetype(FONT_HEAVY, 86)
    draw.text((55, 330), "MANIPULACJI", fill=RED, font=font_t2)

    # "TERAZ TO TY / ROZDAJESZ KARTY"
    font_sub = ImageFont.truetype(FONT_BOLD, 22)
    draw.text((60, 440), "TERAZ TO TY", fill=(230, 230, 230), font=font_sub)
    draw.text((60, 468), "ROZDAJESZ KARTY", fill=(230, 230, 230), font=font_sub)

    img.save(OUTPUT, "JPEG", quality=95)
    print(f"Done: {OUTPUT}")


if __name__ == "__main__":
    main()
