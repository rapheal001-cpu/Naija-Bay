"""Placeholder product image generation shared by seed commands."""

import io
import random

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

from products.models import ProductImage


IMAGE_FORMATS = [
    "JPEG",
    "JPEG",
    "JPEG",
    "PNG",
]  # weighted more toward jpg, like real uploads

PLACEHOLDER_BG_COLORS = [
    (241, 196, 15),
    (231, 76, 60),
    (52, 152, 219),
    (46, 204, 113),
    (155, 89, 182),
    (52, 73, 94),
    (230, 126, 34),
    (26, 188, 156),
    (149, 165, 166),
    (44, 62, 80),
]


def generate_placeholder_image(product_name, image_format, width=800, height=800):
    """Generates a simple colored image with the product name printed on it."""
    bg_color = random.choice(PLACEHOLDER_BG_COLORS)
    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except IOError:
        font = ImageFont.load_default()

    words = product_name.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] > width - 80:
            lines.append(current_line)
            current_line = word
        else:
            current_line = test_line
    if current_line:
        lines.append(current_line)

    total_text_height = len(lines) * 55
    y = (height - total_text_height) // 2

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y), line, fill="white", font=font)
        y += 55

    buffer = io.BytesIO()
    img.save(
        buffer, format=image_format, quality=85 if image_format == "JPEG" else None
    )
    buffer.seek(0)
    return buffer


def attach_images_to_product(product):
    """Creates between 6 and 10 ProductImage objects for a product."""
    count = random.randint(6, 10)
    for i in range(count):
        image_format = random.choice(IMAGE_FORMATS)
        extension = "jpg" if image_format == "JPEG" else "png"

        buffer = generate_placeholder_image(product.product_name, image_format)
        filename = f"{product.product_slug}-{i + 1}.{extension}"

        product_image = ProductImage(product=product)
        product_image.image.save(filename, ContentFile(buffer.read()), save=True)
