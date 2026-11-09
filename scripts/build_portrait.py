from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import io
import math
import os
import urllib.request

# Preserve the actual GitHub portrait pixels; no face regeneration.
AVATAR = "https://avatars.githubusercontent.com/u/239327170?v=4"
with urllib.request.urlopen(AVATAR, timeout=30) as response:
    source = Image.open(io.BytesIO(response.read())).convert("RGB")
portrait = ImageOps.fit(source, (360, 360), method=Image.Resampling.LANCZOS)
W, H = 900, 520
PX, PY, SIZE = 530, 104, 320
GREEN = (117, 255, 15)
PALE = (233, 248, 234)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
font = ImageFont.truetype(FONT, 22)
small = ImageFont.truetype(FONT, 16)
code = [
    "> SYEDSTECH_PROFILE.exe",
    "> Initializing...",
    "> Loading modules...",
    "> Rendering profile...",
    "> Generating image",
]
portrait = ImageOps.fit(source, (SIZE, SIZE), method=Image.Resampling.LANCZOS)
circle = Image.new("L", (SIZE, SIZE), 0)
ImageDraw.Draw(circle).ellipse((2, 2, SIZE-3, SIZE-3), fill=255)

def background():
    im = Image.new("RGB", (W, H), (2, 16, 10))
    d = ImageDraw.Draw(im)
    for x in range(0, W, 30):
        d.line((x, 0, x, H), fill=(9, 34, 19))
    for y in range(0, H, 30):
        d.line((0, y, W, y), fill=(9, 34, 19))
    d.rounded_rectangle((8, 8, W-9, H-9), radius=14, outline=(37, 104, 44), width=2)
    for x in (44, 67, 90):
        d.ellipse((x-6, 37, x+6, 49), fill=GREEN)
    return im

frames = []
for i in range(46):
    im = background()
    d = ImageDraw.Draw(im)
    # Terminal types in, then progress builds the original photo.
    for j, line in enumerate(code[:4]):
        start = j * 5
        count = max(0, min(len(line), (i-start)*7))
        if count:
            d.text((42, 86+j*41), line[:count], fill=GREEN if j==0 else PALE, font=font)
            if i >= start+4 and j in (1,2,3):
                d.text((42+len(line)*14, 86+j*41), "✓", fill=GREEN, font=font)
    if i < 16 and i%4 < 2:
        d.rectangle((42, 255, 54, 278), fill=GREEN)
    if i >= 15:
        progress = max(0, min(100, round((i-15)/19*100)))
        d.text((42, 278), f"> Generating image ({progress}%)...", fill=PALE, font=font)
        d.rounded_rectangle((42, 320, 474, 341), radius=6, outline=GREEN, width=2)
        if progress:
            d.rounded_rectangle((45, 323, 45+round(426*progress/100), 338), radius=4, fill=GREEN)
        # Horizontal digital scanline reveal; original portrait remains unaltered.
        if progress:
            mask = circle.copy()
            cutoff = round(SIZE*progress/100)
            ImageDraw.Draw(mask).rectangle((0, cutoff, SIZE, SIZE), fill=0)
            im.paste(portrait, (PX, PY), mask)
            d = ImageDraw.Draw(im)
            for ring in range(9, 0, -2):
                color=(max(0, GREEN[0]-ring*8), max(0,GREEN[1]-ring*7), max(0,GREEN[2]-ring))
                d.arc((PX-2-ring, PY-2-ring, PX+SIZE+ring, PY+SIZE+ring), 270, 270+round(360*progress/100), fill=color, width=2)
            d.arc((PX-2, PY-2, PX+SIZE+2, PY+SIZE+2), 270, 270+round(360*progress/100), fill=GREEN, width=4)
        if progress==100:
            d.text((42, 369), "> PROFILE READY ✓", fill=GREEN, font=font)
    frames.append(im.quantize(colors=128, method=Image.Quantize.FASTOCTREE))
os.makedirs("assets", exist_ok=True)
frames[0].save("assets/hasnain-coding-animation.gif", save_all=True, append_images=frames[1:], duration=[145]*45+[3000], loop=0, optimize=True, disposal=2)
