# 스케일링 블로그 글용 설명 그림 4장 (직접 그린 도식, 스톡/AI 이미지 아님)
from PIL import Image, ImageDraw, ImageFont
import os, random
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "blog_scaling")
FP = "C:/Windows/Fonts/NotoSansKR-VF.ttf"
def F(sz, w="Bold"):
    f = ImageFont.truetype(FP, sz); f.set_variation_by_name(w); return f
BG="#F7F9F8"; TEAL="#0F3D3A"; MINT="#CFE6E1"; GUM="#F2A9A0"
TOOTH="#FFFDF7"; TOOTHL="#D9D2C0"; DENT="#F3E7C4"; TART="#9A7B4F"; PLQ="#E8D27A"; INK="#222222"; SOFT="#666666"
W,H=1200,675

def canvas(title):
    im=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(im)
    d.rectangle([0,0,W,10],fill=TEAL)
    d.text((W//2,55),title,font=F(38),fill=TEAL,anchor="mm")
    d.text((W//2,H-26),"이해를 돕기 위해 직접 그린 설명용 도식이며, 실제 구조와 차이가 있을 수 있습니다",font=F(20,"Regular"),fill=SOFT,anchor="mm")
    return im,d

def label(d,text,tp,lp):
    d.line([tp,lp],fill=TEAL,width=3); d.ellipse([tp[0]-6,tp[1]-6,tp[0]+6,tp[1]+6],fill=TEAL)
    d.multiline_text(lp,text,font=F(30),fill=INK,anchor="lm",spacing=8)

def scene(d,cx,top,gy,x0,x1,bottom,crown_h=230,w=300,rl=240):
    """잇몸 → 치근 → 치관 순으로 겹쳐 그린 단면 도식. 치관 하단 y를 반환."""
    d.rectangle([x0,gy,x1,bottom],fill=GUM)
    r=top+crown_h
    d.polygon([(cx-w//2+30,r-60),(cx+w//2-30,r-60),(cx+60,r+rl),(cx-60,r+rl)],fill=DENT,outline=TOOTHL)
    d.rounded_rectangle([cx-w//2,top,cx+w//2,r],radius=70,fill=TOOTH,outline=TOOTHL,width=4)
    return r

def img1():
    im,d=canvas("치석은 어떻게 생길까요?")
    cx,top,w=380,120,300; gy=top+215
    scene(d,cx,top,gy,60,700,H-70)
    random.seed(3)
    for _ in range(30):
        x=random.randint(cx-w//2-20,cx-w//2+4); y=random.randint(gy-70,gy+6)
        d.ellipse([x-7,y-7,x+7,y+7],fill=PLQ)
    xr=cx+w//2
    d.polygon([(xr-2,gy-80),(xr+22,gy-62),(xr+14,gy-36),(xr+38,gy-14),(xr+20,gy+14),(xr-2,gy+14)],fill=TART)
    label(d,"① 세균막(플라크)\n    아직 칫솔질로 닦을 수 있음",(cx-w//2-14,gy-35),(740,170))
    label(d,"② 치석\n    굳으면 칫솔질로 제거 어려움",(xr+30,gy-30),(740,330))
    label(d,"잇몸",(cx+250,gy+110),(740,520))
    return im

def img2():
    im,d=canvas("스케일링은 이렇게 진행됩니다")
    steps=[("1","구강 상태 확인","치석 위치와\n잇몸 상태 살펴보기"),("2","초음파 스케일러","미세한 진동으로\n치석 제거"),
           ("3","손기구 마무리","닿기 어려운 부위\n세심하게 정리"),("4","표면 연마","치아 표면을\n매끄럽게 다듬기")]
    cw,gap=250,26; x0=(W-(4*cw+3*gap))//2
    for i,(n,t,s) in enumerate(steps):
        x=x0+i*(cw+gap); y=120
        d.rounded_rectangle([x,y,x+cw,y+430],radius=24,fill="#FFFFFF",outline=MINT,width=4)
        d.ellipse([x+cw//2-45,y+30,x+cw//2+45,y+120],fill=TEAL)
        d.text((x+cw//2,y+76),n,font=F(52,"Black"),fill="#FFFFFF",anchor="mm")
        d.text((x+cw//2,y+185),t,font=F(31),fill=TEAL,anchor="mm")
        d.multiline_text((x+cw//2,y+290),s,font=F(27,"Regular"),fill=INK,anchor="mm",align="center",spacing=10)
        if i<3: d.polygon([(x+cw+4,y+215),(x+cw+gap-4,y+235),(x+cw+4,y+255)],fill=TEAL)
    return im

def img3():
    im,d=canvas("스케일링 후 시릴 수 있는 이유")
    def panel(cx,exposed,cap):
        d.rounded_rectangle([cx-270,100,cx+270,H-60],radius=20,fill="#FFFFFF",outline=MINT,width=3)
        d.text((cx,135),cap,font=F(28),fill=TEAL,anchor="mm")
        top,w,ch=175,240,190; r=top+ch
        gy=r+95 if exposed else r-20
        scene(d,cx,top,gy,cx-250,cx+250,H-120,ch,w,rl=150)
        xl,xr=cx-w//2,cx+w//2
        if not exposed:
            for sx in (xl-2,xr+2):
                d.ellipse([sx-26,gy-44,sx+26,gy+14],fill=TART)
            d.text((cx,H-90),"치석이 뿌리 쪽을 덮고 있는 상태",font=F(24,"Medium"),fill=SOFT,anchor="mm")
        else:
            for k in range(-3,4):
                x=cx+k*24; d.line([(x,r-10),(x,gy-4)],fill="#C4A85A",width=3)
            d.text((cx,H-90),"드러난 뿌리 쪽에 자극이 전달될 수 있음",font=F(24,"Medium"),fill="#C0392B",anchor="mm")
    panel(330,False,"제거 전"); panel(870,True,"제거 후, 뿌리 쪽이 드러났을 때")
    d.polygon([(590,360),(632,360),(632,335),(682,385),(632,435),(632,410),(590,410)],fill=TEAL)
    return im

def img4():
    im,d=canvas("스케일링으로 하는 것 · 별도 진료가 필요할 수 있는 것")
    cols=[("스케일링으로 하는 것",TEAL,["치아 표면·잇몸 가장자리 치석 제거","세균막이 덜 붙도록 표면 연마","잇몸 상태 확인(정기 관리)"]),
          ("별도 진료가 필요할 수 있는 것","#8A5A1C",["충치 치료","치아 색을 바꾸는 미백","잇몸 속 깊은 치석·진행된 잇몸병"])]
    for i,(t,c,items) in enumerate(cols):
        x=70+i*550; d.rounded_rectangle([x,115,x+510,H-70],radius=24,fill="#FFFFFF",outline=c,width=4)
        d.rounded_rectangle([x,115,x+510,195],radius=24,fill=c); d.rectangle([x,155,x+510,195],fill=c)
        d.text((x+255,155),t,font=F(32),fill="#FFFFFF",anchor="mm")
        for j,it in enumerate(items):
            y=270+j*100; d.ellipse([x+30,y-14,x+58,y+14],fill=c)
            d.text((x+80,y),it,font=F(27,"Medium"),fill=INK,anchor="lm")
    return im

os.makedirs(OUT,exist_ok=True)
for n,fn in enumerate([img1,img2,img3,img4],1):
    fn().save(os.path.join(OUT,f"scaling_0{n}.jpg"),quality=92)
print("ok")
