from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os
import urllib.request

AVATAR = "https://avatars.githubusercontent.com/u/239327170?v=4"
with urllib.request.urlopen(AVATAR, timeout=30) as response:
    source = Image.open(io.BytesIO(response.read())).convert("RGB")
portrait = ImageOps.fit(source, (255, 255), method=Image.Resampling.LANCZOS)
photo_mask = Image.new("L", (255, 255), 0)
ImageDraw.Draw(photo_mask).ellipse((0, 0, 254, 254), fill=255)

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
font = ImageFont.truetype(FONT_PATH, 17)
small = ImageFont.truetype(FONT_PATH, 13)
W, H = 900, 350
PX, PY = 604, 54
GREEN = (141, 255, 36)
LIGHT = (226, 247, 229)
BACKGROUND = (4, 16, 10)
CODE = [
    "$ syedstech --init",
    'const engineer = "Syed Hasnain Raza";',
    'const stack = ["React", "PHP", "AI"];',
    'renderPortrait({ source: "profile" });',
    "> Compiling personal identity...",
    "> Profile render complete!",
]

def draw_background():
    im = Image.new("RGB", (W, H), BACKGROUND)
    d = ImageDraw.Draw(im)
    for x in range(0, W, 31):
        d.line((x, 0, x, H), fill=(13, 39, 21))
    for y in range(0, H, 31):
        d.line((0, y, W, y), fill=(13, 39, 21))
    d.rounded_rectangle((13, 12, 887, 337), radius=16, outline=(91, 205, 57), width=2)
    d.rounded_rectangle((34, 33, 580, 316), radius=12, fill=(7, 26, 14), outline=(61, 132, 60), width=2)
    d.rectangle((36, 35, 578, 71), fill=(13, 37, 21))
    for x, color in [(55, (255, 103, 91)), (75, (248, 197, 61)), (95, (44, 220, 96))]:
        d.ellipse((x - 6, 47, x + 6, 59), fill=color)
    d.text((126, 44), "SYEDSTECH / PROFILE TERMINAL", fill=GREEN, font=small)
    return im

frames = []
for frame_index in range(38):
    im = draw_background()
    d = ImageDraw.Draw(im)
    typed = min(6 * frame_index, sum(map(len, CODE)))
    cursor_y = 91
    for j, line in enumerate(CODE):
        y = 91 + j * 32
        start = sum(map(len, CODE[:j]))
        amount = max(0, min(len(line), typed - start))
        if amount:
            d.text((51, y), line[:amount], fill=GREEN if j in (0, 5) else LIGHT, font=font)
            cursor_y = y
    if frame_index % 4 < 2 and frame_index < 21:
        d.rectangle((537, cursor_y, 544, cursor_y + 19), fill=GREEN)

    # Reveal the actual GitHub avatar without regenerating or changing its facial features.
    reveal = max(0, min(1, (frame_index - 14) / 13))
    if reveal > 0:
        mask = photo_mask.copy()
        cutoff = round(255 * reveal)
        ImageDraw.Draw(mask).rectangle((cutoff, 0, 255, 255), fill=0)
        im.paste(portrait, (PX, PY), mask)
        d = ImageDraw.Draw(im)
        if reveal >= .99:
            d.ellipse((PX - 2, PY - 2, PX + 256, PY + 256), outline=GREEN, width=4)
        else:
            d.arc((PX - 2, PY - 2, PX + 256, PY + 256), 90, 90 + round(360 * reveal), fill=GREEN, width=4)
    if frame_index >= 27:
        d.text((621, 320), "PROFILE READY", fill=GREEN, font=small)
    frames.append(im.quantize(colors=96, method=Image.Quantize.FASTOCTREE))

os.makedirs("assets", exist_ok=True)
frames[0].save("assets/hasnain-coding-animation.gif", save_all=True, append_images=frames[1:], duration=[130]*37 + [2600], loop=0, optimize=True, disposal=2)
