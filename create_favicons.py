# -*- coding: utf-8 -*-
"""
Generate crisp, high-resolution Favicon, Apple Touch Icon, and SVG for
「全台科技＆產業園區地圖」
"""
from PIL import Image, ImageDraw, ImageFilter
import math

def create_icons():
    # 1. Generate SVG
    svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="100%" height="100%">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0F172A" />
      <stop offset="50%" stop-color="#1E293B" />
      <stop offset="100%" stop-color="#1E3A8A" />
    </linearGradient>
    <linearGradient id="pinGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FF5E3A" />
      <stop offset="50%" stop-color="#FF9500" />
      <stop offset="100%" stop-color="#FFD60A" />
    </linearGradient>
    <linearGradient id="coreGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38BDF8" />
      <stop offset="100%" stop-color="#2563EB" />
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="16" stdDeviation="16" flood-color="#000000" flood-opacity="0.45" />
    </filter>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="0" stdDeviation="8" flood-color="#38BDF8" flood-opacity="0.6" />
    </filter>
  </defs>

  <!-- Background Squircle -->
  <rect x="16" y="16" width="480" height="480" rx="112" fill="url(#bgGrad)" stroke="#38BDF8" stroke-width="8" stroke-opacity="0.4" />

  <!-- Radar / Map Lattice lines -->
  <circle cx="256" cy="230" r="140" fill="none" stroke="#38BDF8" stroke-width="4" stroke-opacity="0.25" stroke-dasharray="8 8" />
  <circle cx="256" cy="230" r="90" fill="none" stroke="#38BDF8" stroke-width="3" stroke-opacity="0.35" />
  <line x1="80" y1="230" x2="432" y2="230" stroke="#38BDF8" stroke-width="3" stroke-opacity="0.2" />
  <line x1="256" y1="60" x2="256" y2="400" stroke="#38BDF8" stroke-width="3" stroke-opacity="0.2" />

  <!-- Pin Shadow Ground Ellipse -->
  <ellipse cx="256" cy="430" rx="70" ry="20" fill="#000000" fill-opacity="0.4" />

  <!-- Map Pin Body -->
  <path d="M 256 90
           C 176 90 112 154 112 234
           C 112 320 226 418 250 438
           C 254 441 258 441 262 438
           C 286 418 400 320 400 234
           C 400 154 336 90 256 90 Z"
        fill="url(#pinGrad)" filter="url(#shadow)" />

  <!-- Inner Pin White Ring -->
  <circle cx="256" cy="230" r="64" fill="#FFFFFF" />

  <!-- Core Tech Chip / Satellite Node -->
  <circle cx="256" cy="230" r="46" fill="url(#coreGrad)" filter="url(#glow)" />
  <circle cx="256" cy="230" r="22" fill="#FFFFFF" />
  <circle cx="256" cy="230" r="10" fill="#0284C7" />
</svg>'''

    with open('favicon.svg', 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print("[OK] favicon.svg generated")

    # 2. Render PNG icons using Pillow
    size = 512
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded rectangle background
    bg_color_top = (15, 23, 42, 255)
    bg_color_bot = (30, 58, 138, 255)

    # Draw gradient background on a separate image
    bg_img = Image.new('RGBA', (size, size))
    for y in range(size):
        ratio = y / size
        r = int(bg_color_top[0] * (1 - ratio) + bg_color_bot[0] * ratio)
        g = int(bg_color_top[1] * (1 - ratio) + bg_color_bot[1] * ratio)
        b = int(bg_color_top[2] * (1 - ratio) + bg_color_bot[2] * ratio)
        for x in range(size):
            bg_img.putpixel((x, y), (r, g, b, 255))

    # Create mask for rounded squircle
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([16, 16, 496, 496], radius=110, fill=255)
    img.paste(bg_img, (0, 0), mask)

    # Draw border on squircle
    draw.rounded_rectangle([16, 16, 496, 496], radius=110, outline=(56, 189, 248, 160), width=6)

    # Radar rings
    cx, cy = 256, 230
    draw.ellipse([cx - 130, cy - 130, cx + 130, cy + 130], outline=(56, 189, 248, 70), width=4)
    draw.ellipse([cx - 85, cy - 85, cx + 85, cy + 85], outline=(56, 189, 248, 100), width=3)
    draw.line([80, cy, 432, cy], fill=(56, 189, 248, 60), width=3)
    draw.line([cx, 70, cx, 390], fill=(56, 189, 248, 60), width=3)

    # Shadow ellipse
    draw.ellipse([cx - 70, 420, cx + 70, 444], fill=(0, 0, 0, 100))

    # Map Pin points (polygon approximate)
    pin_points = []
    # Circle top of pin
    pin_r = 140
    for deg in range(-140, 140 + 1, 5):
        rad = math.radians(deg)
        x = cx + pin_r * math.cos(rad)
        y = cy + pin_r * math.sin(rad)
        pin_points.append((x, y))
    # Pin tip
    pin_points.append((cx, 434))

    # Gradient Pin fill
    pin_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    pin_draw = ImageDraw.Draw(pin_img)
    pin_draw.polygon(pin_points, fill=(245, 158, 11, 255))
    
    # Gradient overlay on pin
    for y in range(90, 440):
        ratio = (y - 90) / 350
        r = int(255 * (1 - ratio) + 239 * ratio)
        g = int(94 * (1 - ratio) + 68 * ratio)
        b = int(58 * (1 - ratio) + 68 * ratio)
        # horizontal line across pin
        for x in range(cx - 150, cx + 150):
            if pin_img.getpixel((x, y))[3] > 0:
                pin_img.putpixel((x, y), (r, g, b, 255))

    img.paste(pin_img, (0, 0), pin_img)

    # Inner White Circle
    draw.ellipse([cx - 62, cy - 62, cx + 62, cy + 62], fill=(255, 255, 255, 255))

    # Core Blue Satellite Circle
    draw.ellipse([cx - 44, cy - 44, cx + 44, cy + 44], fill=(37, 99, 235, 255))
    draw.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=(255, 255, 255, 255))
    draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=(2, 132, 199, 255))

    # Save PNG formats
    img.save('icon-512.png', 'PNG')
    img.resize((192, 192), Image.Resampling.LANCZOS).save('icon-192.png', 'PNG')
    img.resize((180, 180), Image.Resampling.LANCZOS).save('apple-touch-icon.png', 'PNG')
    img.resize((32, 32), Image.Resampling.LANCZOS).save('favicon-32x32.png', 'PNG')
    img.resize((16, 16), Image.Resampling.LANCZOS).save('favicon-16x16.png', 'PNG')
    
    # Save .ico
    img.save('favicon.ico', format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    print("[OK] favicon.ico, apple-touch-icon.png, favicon-32x32.png, icon-192.png generated!")

if __name__ == '__main__':
    create_icons()
