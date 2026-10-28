from PIL import Image, ImageDraw, ImageFont, ImageOps
import urllib.request, io, math, os, random
random.seed(19)
url = "https://avatars.githubusercontent.com/u/239327170?v=4"
with urllib.request.urlopen(url, timeout=30) as r:
    portrait = Image.open(io.BytesIO(r.read())).convert("RGB")
portrait = ImageOps.fit(portrait,(290,290),method=Image.Resampling.LANCZOS)
portrait = portrait.convert("L").convert("RGB")
font_path="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
font=ImageFont.truetype(font_path,12)
small=ImageFont.truetype(font_path,10)
W,H=760,400
mask=Image.new("L",(290,290),0)
ImageDraw.Draw(mask).ellipse((0,0,289,289),fill=255)
pixels=portrait.load()
points=[]
for y in range(6,286,6):
    for x in range(6,286,6):
        if (x-145)**2+(y-145)**2<138**2:
            v=pixels[x,y][0]
            if random.random() < .20 + .70*(1-v/255):
                points.append((x,y,v))
frames=[]
for k in range(64):
    im=Image.new("RGB",(W,H),(5,9,28))
    d=ImageDraw.Draw(im)
    for x in range(0,W,30):d.line((x,0,x,H),fill=(12,19,45))
    for y in range(0,H,30):d.line((0,y,W,y),fill=(12,19,45))
    d.rounded_rectangle((10,10,750,390),radius=14,outline=(102,80,239),width=3)
    d.rectangle((11,11,749,45),fill=(24,25,62))
    for x,c in [(32,(255,85,119)),(54,(255,200,85)),(76,(55,235,160))]:
        d.ellipse((x-6,22,x+6,34),fill=c)
    d.text((245,24),"hasnain / README.md — VISUAL.AI",font=small,fill=(192,197,244))
    d.rounded_rectangle((27,59,366,369),radius=9,fill=(9,12,40),outline=(85,154,255),width=2)
    d.rounded_rectangle((381,59,734,369),radius=9,fill=(11,16,44),outline=(76,72,146),width=2)
    # video-style: portrait assembles from thousands of code-like luminous particles,
    # then becomes an animated angle-bracket symbol before returning to the portrait.
    phase=k%64
    fade=1 if phase<20 else max(0,(31-phase)/11) if phase<31 else 0 if phase<45 else min(1,(phase-45)/13)
    if fade>0:
        # real portrait is drawn underneath, while the purple pixel field animates on top
        if fade>.55:
            im.paste(portrait,(52,68),mask)
            d=ImageDraw.Draw(im)
            d.ellipse((51,67,343,359),outline=(167,104,255),width=3)
        for idx,(x,y,v) in enumerate(points):
            if (idx+k)%5==0 or fade<.55:
                alpha=max(25,int((255-v)*fade))
                col=(min(255,70+alpha//2),min(255,42+alpha//5),min(255,130+alpha//2))
                px=52+x;py=68+y
                d.rectangle((px,py,px+2,py+2),fill=col)
    else:
        # particle angle brackets, as in the reference video
        for x in range(54,344,5):
            for y in range(70,356,5):
                xx=(x-199)/145;yy=(y-210)/145
                left=abs(xx+.45+0.55*abs(yy))<.065 and abs(yy)<.68
                right=abs(xx-.45-0.55*abs(yy))<.065 and abs(yy)<.68
                slash=abs(xx+yy*.30)<.055 and abs(yy)<.74
                if left or right or slash:
                    if random.random()>.2:
                        d.rectangle((x,y,x+2,y+2),fill=(150+(x%80),94+(y%55),210+(k%40)))
    d.text((398,88),"SYSTEM.INFO",font=font,fill=(57,221,255))
    fields=["Name: Syed Hasnain Raza","Role: Full-Stack Developer","Platforms: Web / Android / iOS","Build: SaaS / Apps / APIs","Core: Frontend + Backend","Status: ONLINE"]
    for j,line in enumerate(fields):
        visible=max(0,min(len(line),int((k%64)*2.6)-j*14))
        d.text((399,125+j*34),line[:visible],font=font,fill=(180,155,255) if j%2 else (206,221,255))
    d.text((398,339),"root@hasnain:~$ "+("_" if k%10<6 else " "),font=font,fill=(67,255,175))
    frames.append(im.quantize(colors=128))
os.makedirs("assets",exist_ok=True)
frames[0].save("assets/hasnain-coding-animation.gif",save_all=True,append_images=frames[1:],duration=85,loop=0,optimize=True)
