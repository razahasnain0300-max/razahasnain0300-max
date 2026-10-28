from PIL import Image, ImageDraw, ImageFont
import urllib.request, io, math, os
url="https://avatars.githubusercontent.com/u/239327170?v=4"
with urllib.request.urlopen(url,timeout=30) as response:
    portrait=Image.open(io.BytesIO(response.read())).convert("RGB")
portrait=portrait.resize((210,210),Image.Resampling.LANCZOS)
mask=Image.new("L",(210,210),0)
ImageDraw.Draw(mask).ellipse((0,0,209,209),fill=255)
frames=[]
W,H=680,330
lines=[
"const name = 'Syed Hasnain Raza';",
"const skills = ['Web','Android','iOS'];",
"function create() {",
"  return 'Apps + Software + Cloud';",
"}",
"// build complete: ONLINE"
]
for k in range(48):
    im=Image.new("RGB",(W,H),(8,12,29))
    d=ImageDraw.Draw(im)
    for x in range(0,W,34):d.line((x,0,x,H),fill=(17,26,51))
    for y in range(0,H,34):d.line((0,y,W,y),fill=(17,26,51))
    d.rectangle((7,7,W-8,H-8),outline=(111,83,235),width=2)
    d.rectangle((7,7,W-8,38),fill=(27,29,65))
    for x,c in [(26,(255,91,125)),(45,(255,201,90)),(64,(64,244,169))]:d.ellipse((x-5,17,x+5,27),fill=c)
    d.text((250,18),"hasnain@cyber:~/profile",fill=(190,196,248))
    im.paste(portrait,(45,66),mask)
    d=ImageDraw.Draw(im)
    cx,cy=150,171
    for r,col,w in [(111,(76,40,130),9),(112,(145,93,255),3),(121,(39,207,250),2)]:
        d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=col,width=w)
    for j in range(13):
        a=(k*7.5+j*360/13)*math.pi/180
        x=cx+119*math.cos(a);y=cy+119*math.sin(a)
        color=[(175,101,255),(41,215,255),(69,255,175)][j%3]
        d.ellipse((x-3,y-3,x+3,y+3),fill=color)
    d.text((306,67),"root@hasnain:~$",fill=(70,244,182))
    d.line((306,87,654,87),fill=(91,103,232),width=2)
    progress=int(k/47*(sum(len(v) for v in lines)+len(lines)*3))
    for j,line in enumerate(lines):
        count=max(0,min(len(line),progress))
        if count:d.text((306,106+j*30),line[:count],fill=(90,222,249) if j%2 else (213,190,255))
        progress-=len(line)+3
    d.text((35,301),"SYED HASNAIN RAZA  |  FULL-STACK / WEB / ANDROID / iOS",fill=(83,223,244))
    frames.append(im.quantize(colors=96))
os.makedirs("assets",exist_ok=True)
frames[0].save("assets/hasnain-coding-animation.gif",save_all=True,append_images=frames[1:],duration=90,loop=0,optimize=True)
