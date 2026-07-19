"""
Phase 1 - Captcha generation.

Generates a random alphanumeric captcha string and renders it as a
distorted PNG image (random rotation/offset per character, background
noise lines/dots) to make plain OCR harder.

The answer string produced here must NEVER be sent to the client.
Only the rendered image is sent; the answer is kept server-side,
tied to a session id (see main.py).
"""

import random
import string
import io
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Characters that are easy to confuse (0/O, 1/l/I) are excluded to keep
# the task fair for a human / air-writing user.
SAFE_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

IMG_WIDTH = 300
IMG_HEIGHT = 110
FONT_SIZE = 52


def generate_captcha_text(length: int = 5) -> str:
    return "".join(random.choice(SAFE_CHARS) for _ in range(length))


def _load_font():
    # Falls back to PIL's default bitmap font if no TTF is found,
    # but a real deployment should ship a proper .ttf under backend/fonts/.
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, FONT_SIZE)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def _random_line_noise(draw: ImageDraw.ImageDraw, count: int = 6):
    for _ in range(count):
        x1, y1 = random.randint(0, IMG_WIDTH), random.randint(0, IMG_HEIGHT)
        x2, y2 = random.randint(0, IMG_WIDTH), random.randint(0, IMG_HEIGHT)
        color = tuple(random.randint(120, 200) for _ in range(3))
        draw.line((x1, y1, x2, y2), fill=color, width=1)


def _random_dot_noise(draw: ImageDraw.ImageDraw, count: int = 250):
    for _ in range(count):
        x, y = random.randint(0, IMG_WIDTH), random.randint(0, IMG_HEIGHT)
        color = tuple(random.randint(150, 220) for _ in range(3))
        draw.point((x, y), fill=color)


def generate_captcha_image(text: str) -> bytes:
    """Render `text` as a distorted PNG and return raw PNG bytes."""
    image = Image.new("RGB", (IMG_WIDTH, IMG_HEIGHT), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    font = _load_font()

    _random_line_noise(draw, count=5)

    # Draw each character onto its own small canvas, rotate it slightly,
    # then paste it onto the main image at a jittered position.
    x_cursor = 15
    for ch in text:
        char_img = Image.new("RGBA", (FONT_SIZE + 20, FONT_SIZE + 20), (255, 255, 255, 0))
        char_draw = ImageDraw.Draw(char_img)
        color = (
            random.randint(20, 90),
            random.randint(20, 90),
            random.randint(20, 90),
        )
        char_draw.text((10, 5), ch, font=font, fill=color)

        angle = random.uniform(-30, 30)
        rotated = char_img.rotate(angle, expand=True, resample=Image.BICUBIC)

        y_offset = random.randint(-10, 15)
        paste_y = max(0, (IMG_HEIGHT - rotated.height) // 2 + y_offset)
        image.paste(rotated, (x_cursor, paste_y), rotated)

        x_cursor += FONT_SIZE - random.randint(5, 15)

    _random_dot_noise(draw, count=200)
    image = image.filter(ImageFilter.SMOOTH)

    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()


if __name__ == "__main__":
    # Quick manual test: python captcha_gen.py
    text = generate_captcha_text()
    print("Generated text:", text)
    with open("/tmp/sample_captcha.png", "wb") as f:
        f.write(generate_captcha_image(text))
    print("Saved sample to /tmp/sample_captcha.png")
