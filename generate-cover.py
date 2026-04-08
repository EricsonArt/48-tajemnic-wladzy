"""
Generate professional ebook cover: dark background, mask with red eyes, red title text.
Style: similar to 99mocumyslu.pl book cover.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np
import random

# ---- CONFIG ----
W, H = 864, 1184
MASK_IMG = "C:/Users/cosmi/Downloads/tiktok_video_hkbwI.jpeg"
OUTPUT = "c:/Users/cosmi/Desktop/AI/Project/48-tajemnic-wladzy/cover.jpg"

# Colors
BG_DARK = (18, 18, 18)
RED = (220, 20, 60)
WHITE = (255, 255, 255)

# Fonts
FONT_HEAVY = "C:/Windows/Fonts/impact.ttf"
FONT_BOLD = "C:/Windows/Fonts/arialbd.ttf"
FONT_REG = "C:/Windows/Fonts/arial.ttf"


def create_textured_background(w, h):
    """Create dark concrete/stone textured background."""
    img = Image.new("RGB", (w, h), BG_DARK)
    draw = ImageDraw.Draw(img)

    # Add noise/grain texture
    pixels = img.load()
    for y in range(h):
        for x in range(w):
            r, g, b = pixels[x, y]
            noise = random.randint(-12, 12)
            v = max(0, min(255, r + noise))
            pixels[x, y] = (v, v, v)

    # Add subtle lighter patches (stone texture)
    overlay = Image.new("RGB", (w, h), (0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for _ in range(15):
        cx = random.randint(0, w)
        cy = random.randint(0, h)
        rx = random.randint(100, 300)
        ry = random.randint(80, 250)
        c = random.randint(20, 40)
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(c, c, c))

    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=60))
    img = Image.blend(img, overlay, 0.5)

    # Darken edges (vignette)
    vignette = Image.new("L", (w, h), 255)
    vd = ImageDraw.Draw(vignette)
    for i in range(40):
        alpha = int(255 * (i / 40))
        margin = i * 8
        vd.rectangle([margin, margin, w - margin, h - margin], fill=alpha)
    vignette = vignette.filter(ImageFilter.GaussianBlur(radius=50))

    # Apply vignette
    r, g, b = img.split()
    r = Image.composite(r, Image.new("L", (w, h), 0), vignette)
    g = Image.composite(g, Image.new("L", (w, h), 0), vignette)
    b = Image.composite(b, Image.new("L", (w, h), 0), vignette)
    img = Image.merge("RGB", (r, g, b))

    return img


def blend_mask_image(bg, mask_path):
    """Blend mask face image into the lower portion of the background."""
    mask_img = Image.open(mask_path).convert("RGB")

    # Make mask BRIGHT and vivid — face and red eyes must be clearly visible
    enhancer = ImageEnhance.Brightness(mask_img)
    mask_img = enhancer.enhance(1.4)
    enhancer = ImageEnhance.Contrast(mask_img)
    mask_img = enhancer.enhance(1.5)
    enhancer = ImageEnhance.Color(mask_img)
    mask_img = enhancer.enhance(2.0)

    # Resize mask to fill lower ~75% of cover — bigger face
    target_h = int(H * 0.75)
    target_w = W
    mask_ratio = mask_img.width / mask_img.height
    if mask_ratio > target_w / target_h:
        new_w = target_w
        new_h = int(target_w / mask_ratio)
    else:
        new_h = target_h
        new_w = int(target_h * mask_ratio)

    mask_img = mask_img.resize((new_w, new_h), Image.LANCZOS)

    # Center horizontally, position at bottom
    x_offset = (W - new_w) // 2
    y_offset = H - new_h + 20  # slight overflow at bottom

    # Create alpha mask for smooth blending — radial fade
    alpha = Image.new("L", (new_w, new_h), 0)
    ad = ImageDraw.Draw(alpha)

    # Build alpha — large visible center, smooth fade at edges only
    cx, cy = new_w // 2, int(new_h * 0.5)
    max_rx, max_ry = int(new_w * 0.75), int(new_h * 0.7)

    for i in range(100):
        t = i / 100.0
        rx = int(max_rx * (1 - t * 0.5))
        ry = int(max_ry * (1 - t * 0.5))
        a = int(255 * (1 - t * 0.8))
        if rx > 0 and ry > 0:
            ad.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=a)

    alpha = alpha.filter(ImageFilter.GaussianBlur(radius=40))

    # Fade top edge — only top 30%
    top_fade = Image.new("L", (new_w, new_h), 255)
    td = ImageDraw.Draw(top_fade)
    fade_zone = int(new_h * 0.35)
    for y in range(fade_zone):
        opacity = int(255 * (y / fade_zone))
        td.line([(0, y), (new_w, y)], fill=opacity)

    # Combine alpha masks
    alpha_arr = bytearray(alpha.tobytes())
    top_arr = bytearray(top_fade.tobytes())
    combined = bytes([min(a, t) for a, t in zip(alpha_arr, top_arr)])
    alpha = Image.frombytes("L", (new_w, new_h), combined)

    # Gentle side fade — only 40px
    side_fade = 40
    for y in range(new_h):
        for x in range(side_fade):
            factor = x / side_fade
            px = alpha.getpixel((x, y))
            alpha.putpixel((x, y), int(px * factor))
            px2 = alpha.getpixel((new_w - 1 - x, y))
            alpha.putpixel((new_w - 1 - x, y), int(px2 * factor))

    # Paste mask image onto background using alpha
    bg.paste(mask_img, (x_offset, y_offset), alpha)

    # Add red glow around eyes area
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    glow_cx = W // 2
    glow_cy = y_offset + int(new_h * 0.35)
    # Strong red glow for the eyes area
    gd.ellipse([glow_cx - 180, glow_cy - 100, glow_cx + 180, glow_cy + 100],
               fill=(160, 10, 25))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=50))
    bg = Image.blend(bg, glow, 0.3)

    return bg


def add_fog(img):
    """Add smoke/fog at the bottom."""
    fog = Image.new("RGB", (W, H), (0, 0, 0))
    fd = ImageDraw.Draw(fog)

    # Several fog layers
    for _ in range(8):
        cx = random.randint(0, W)
        cy = random.randint(H - 200, H + 50)
        rx = random.randint(200, 500)
        ry = random.randint(40, 100)
        c = random.randint(15, 35)
        fd.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(c, c, c))

    fog = fog.filter(ImageFilter.GaussianBlur(radius=40))

    # Blend fog — subtle, don't darken the face
    img = Image.blend(img, fog, 0.15)

    # Bottom gradient darken
    gradient = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gradient)
    for y in range(H - 150, H):
        t = (y - (H - 150)) / 150
        a = int(180 * t)
        gd.line([(0, y), (W, y)], fill=(10, 10, 10, a))

    img = img.convert("RGBA")
    img = Image.alpha_composite(img, gradient)
    img = img.convert("RGB")

    return img


def add_text(img):
    """Add title text, subtitle, and branding."""
    draw = ImageDraw.Draw(img)

    # @mindtriki — top center
    font_brand = ImageFont.truetype(FONT_REG, 18)
    brand_text = "@mindtriki"
    bbox = draw.textbbox((0, 0), brand_text, font=font_brand)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 40), brand_text, fill=(180, 180, 180), font=font_brand)

    # Main title: "24" big
    font_num = ImageFont.truetype(FONT_HEAVY, 140)
    draw.text((60, 100), "24", fill=RED, font=font_num)

    # "TAJEMNICE"
    font_title = ImageFont.truetype(FONT_HEAVY, 88)
    draw.text((60, 240), "TAJEMNICE", fill=RED, font=font_title)

    # "MANIPULACJI"
    font_title2 = ImageFont.truetype(FONT_HEAVY, 82)
    draw.text((60, 330), "MANIPULACJI", fill=RED, font=font_title2)

    # Subtitle: "TERAZ TO TY / ROZDAJESZ KARTY"
    font_sub = ImageFont.truetype(FONT_BOLD, 22)
    draw.text((65, 440), "TERAZ TO TY", fill=(220, 220, 220), font=font_sub)
    draw.text((65, 468), "ROZDAJESZ KARTY", fill=(220, 220, 220), font=font_sub)

    # Add subtle text shadow by drawing text offset first
    # (already dark bg so shadow is subtle)

    return img


def main():
    print("Creating textured background...")
    cover = create_textured_background(W, H)

    print("Blending mask image...")
    cover = blend_mask_image(cover, MASK_IMG)

    print("Adding fog effects...")
    cover = add_fog(cover)

    print("Adding text...")
    cover = add_text(cover)

    # Final adjustments
    enhancer = ImageEnhance.Contrast(cover)
    cover = enhancer.enhance(1.05)

    cover.save(OUTPUT, "JPEG", quality=95)
    print(f"Cover saved: {OUTPUT}")
    print(f"Size: {cover.size}")


if __name__ == "__main__":
    main()
