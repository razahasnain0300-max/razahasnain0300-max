from PIL import Image, ImageDraw, ImageFont, ImageOps
import urllib.request, io, math, os, random
random.seed(23)
with urllib.request.urlopen("https://avatars.githubusercontent.com/u/239327170?v=4",timeout=30) as response:
    original=Image.open(io.BytesIO(response.read())).convert("RGB")
photo=ImageOps.fit(original,(286,286),method=Image.Resampling.LANCZOS)
gray=photo.convert("L")
font="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
regular=ImageFont.truetype(font,13)
small=ImageFont.truetype(font,11)
W,H=760,400
cx,cy=195,215
photo_x,photo_y=52,72
mask=Image.new("L",(286,286))
ImageDraw.Draw(mask).ellipse((0,0,285,285),fill=255)
# Code symbol is built from particles; no random pixels are drawn over the face.
def symbol(x,y):
    x=(x-cx)/128
    y=(y-cy)/128
    left=abs(x+0.43+0.48*abs(y))<0.065 and abs(y)<.68
    right=abs(x-0.43-0.48*abs(y))<0.065 and abs(y)<.68
    slash=abs(x+0.27*y)<0.055 and abs(y)<.72
    return left or right or slash
portrait_points=[]
logo_points=[]
for y in range(75,357,5):
    for x in range(55,337,5):
        local_x=x-photo_x
        local_y=y-photo_y
        if 0<=local_x<286 and 0<=local_y<286 and (local_x-143)**2+(local_y-143)**2<137**2:
            intensity=gray.getpixel((local_x,local_y))
            if random.random() < 0.25+0.67*(1-intensity/255):
                portrait_points.append((x,y,intensity))
        if symbol(x,y) and random.random()>.13:
            logo_points.append((x,y))
frames=[]
N=72
for k in range(N):
    im=Image.new("RGB",(W,H),(7,10,30))
    d=ImageDraw.Draw(im)
    for x in range(0,W,34):d.line((x,0,x,H),fill=(14,20,47))
    for y in range(0,H,34):d.line((0,y,W,y),fill=(14,20,47))
    d.rounded_rectangle((9,9,W-10,H-10),radius=13,outline=(106,73,236),width=3)
    d.rectangle((11,11,W-11,46),fill=(26,28,66))
    for x,color in [(33,(255,95,126)),(55,(255,206,88)),(77,(58,241,167))]:
        d.ellipse((x-6,23,x+6,35),fill=color)
    d.text((255,25),"hasnain / README.md - VISUAL LAB",font=small,fill=(198,205,245))
    d.rounded_rectangle((29,59,365,369),radius=8,fill=(7,10,35),outline=(71,151,255),width=2)
    d.rounded_rectangle((382,59,731,369),radius=8,fill=(11,15,43),outline=(79,76,157),width=2)
    # Timeline: clean portrait -> particle portrait -> </> particle logo -> clean portrait.
    if k<17 or k>=62:
        im.paste(photo,(photo_x,photo_y),mask)
        d=ImageDraw.Draw(im)
        d.ellipse((photo_x-1,photo_y-1,photo_x+287,photo_y+287),outline=(165,105,255),width=3)
    elif k<28:
        ratio=(k-17)/11
        im.paste(photo,(photo_x,photo_y),mask)
        d=ImageDraw.Draw(im)
        # progressively cover photo with dark rows as the face dissolves into particles
        for yy in range(photo_y,photo_y+286):
            if (yy-photo_y)/286 < ratio:
                for xx in range(photo_x,photo_x+286):
                    if (xx-(photo_x+143))**2+(yy-(photo_y+143))**2<142**2:
                        d.point((xx,yy),fill=(7,10,35))
        for x,y,v in portrait_points:
            if (y-photo_y)/286<ratio:
                d.rectangle((x,y,x+2,y+2),fill=(min(255,115+(255-v)//3),65,225))
    elif k<36:
        alpha=(k-28)/8
        for i,(x,y,v) in enumerate(portrait_points):
            if (i%100)/100>alpha:
                d.rectangle((x,y,x+2,y+2),fill=(162,88,244))
        for i,(x,y) in enumerate(logo_points):
            if (i%100)/100<alpha:
                d.rectangle((x,y,x+3,y+3),fill=(191,118,255))
    elif k<53:
        for x,y in logo_points:
            flicker=20+((x*7+y*13+k*17)%60)
            d.rectangle((x,y,x+3,y+3),fill=(min(255,153+flicker),93+flicker//3,245))
    elif k<62:
        alpha=(k-53)/9
        for i,(x,y) in enumerate(logo_points):
            if (i%100)/100>alpha:d.rectangle((x,y,x+3,y+3),fill=(188,112,255))
        for i,(x,y,v) in enumerate(portrait_points):
            if (i%100)/100<alpha:d.rectangle((x,y,x+2,y+2),fill=(165,94,247))
    d.text((399,89),"SYSTEM.INFO",font=regular,fill=(70,218,250))
    lines=["Name: Syed Hasnain Raza","Role: Full-Stack Developer","Platforms: Web / Android / iOS","Build: Apps / SaaS / APIs","Core: Frontend + Backend","Status: ONLINE"]
    for j,line in enumerate(lines):
        shown=min(len(line),max(0,k*3-j*15))
        d.text((399,127+j*33),line[:shown],font=regular,fill=(73,255,187) if j==5 else ((186,157,255) if j%2 else (209,221,255)))
    d.text((398,339),"root@hasnain:~$ "+("█" if k%10<6 else " "),font=regular,fill=(57,245,174))
    frames.append(im.quantize(colors=128))
os.makedirs("assets",exist_ok=True)
frames[0].save("assets/hasnain-coding-animation.gif",save_all=True,append_images=frames[1:],duration=90,loop=0,optimize=True)
