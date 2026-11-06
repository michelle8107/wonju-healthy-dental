# 입가 주름 블로그: 부드러운 스타일 AI 일러스트(src_ai/) + 한글 라벨 → mw_01, mw_02, mw_03 (직접 라벨링)
from PIL import Image, ImageDraw, ImageFont
import os
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "blog_mouth_wrinkle")
FP = "C:/Windows/Fonts/NotoSansKR-VF.ttf"
def F(sz, w="Bold"):
    f = ImageFont.truetype(FP, sz); f.set_variation_by_name(w); return f
BG = "#F7F9F8"; TEAL = "#0F3D3A"; CORAL = "#D9694F"; INK = "#222222"; SOFT = "#666666"; MINT = "#CFE6E1"
W, H = 1200, 675
NOTE_AI = "AI로 생성한 설명용 일러스트이며 실제 사람·구조와 차이가 있을 수 있습니다"
NOTE = "이해를 돕기 위해 직접 그린 설명용 도식이며, 개인차가 있을 수 있습니다"

def canvas(title, note):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 10], fill=TEAL)
    d.text((W // 2, 55), title, font=F(38), fill=TEAL, anchor="mm")
    d.text((W // 2, H - 26), note, font=F(20, "Regular"), fill=SOFT, anchor="mm")
    return im, d

def dot_label(d, pt, text, lp, color):
    d.line([pt, lp], fill=color, width=3)
    d.ellipse([pt[0] - 7, pt[1] - 7, pt[0] + 7, pt[1] + 7], fill="#FFFFFF", outline=color, width=4)
    d.multiline_text((lp[0] + 12, lp[1]), text, font=F(28), fill=INK, anchor="lm", spacing=6)

def img1():
    im, d = canvas("스마일라인, 입가 라인의 위치", NOTE_AI)
    src = Image.open(os.path.join(BASE, "src_ai", "face2.png")).convert("RGB")
    k = src.size[0] / 900.0
    box = tuple(int(v * k) for v in (190, 40, 710, 560))
    im.paste(src.crop(box).resize((520, 520)), (60, 110))
    d.rounded_rectangle([60, 110, 580, 630], radius=6, outline=MINT, width=3)
    m = lambda x, y: (60 + (x - 190), 110 + (y - 40))
    dot_label(d, m(527, 410), "① 팔자주름\n콧방울 옆 → 입꼬리", (640, 250), TEAL)
    dot_label(d, m(522, 465), "② 마리오네트 라인\n입꼬리 → 턱선 방향", (640, 430), CORAL)
    return im

def img2():
    im, d = canvas("입가 라인에는 여러 층이 함께 영향을 줍니다", NOTE_AI)
    src = Image.open(os.path.join(BASE, "src_ai", "layers2.png")).convert("RGB")
    h = 520; w = int(src.size[0] * h / src.size[1])
    im.paste(src.resize((w, h)), (50, 110))
    d.rounded_rectangle([50, 110, 50 + w, 110 + h], radius=6, outline=MINT, width=3)
    s = w / 900.0
    m = lambda x, y: (int(50 + x * s), int(110 + y * s))
    dot_label(d, m(400, 200), "피부·결합조직\n탄력 변화", (770, 170), "#B8643F")
    dot_label(d, m(520, 330), "지방층\n양·위치 변화", (770, 290), "#B8860B")
    dot_label(d, m(500, 430), "근육·인대\n입꼬리를 당기는 힘", (770, 410), "#B03A2E")
    dot_label(d, m(480, 560), "턱뼈\n받쳐 주는 구조", (770, 530), "#7A6A3A")
    return im

def img3():
    im, d = canvas("스마일라인 케어, 이런 흐름으로 안내합니다", NOTE)
    steps = [("1", "상담", "고민되는 부위와\n궁금한 점 듣기"),
             ("2", "구강 안팎 상태 확인", "구강 안쪽과 피부 쪽\n상태 살펴보기"),
             ("3", "적합 여부와 방법 안내", "내 상태에 맞는지\n자세히 설명")]
    cw, gap = 320, 40; x0 = (W - (3 * cw + 2 * gap)) // 2
    for i, (n, t, s) in enumerate(steps):
        x = x0 + i * (cw + gap); y = 130
        d.rounded_rectangle([x, y, x + cw, y + 420], radius=24, fill="#FFFFFF", outline=MINT, width=4)
        d.ellipse([x + cw // 2 - 45, y + 30, x + cw // 2 + 45, y + 120], fill=TEAL)
        d.text((x + cw // 2, y + 76), n, font=F(52, "Black"), fill="#FFFFFF", anchor="mm")
        d.text((x + cw // 2, y + 190), t, font=F(30), fill=TEAL, anchor="mm")
        d.multiline_text((x + cw // 2, y + 300), s, font=F(27, "Regular"), fill=INK, anchor="mm", align="center", spacing=10)
        if i < 2:
            d.polygon([(x + cw + 6, y + 190), (x + cw + gap - 6, y + 210), (x + cw + 6, y + 230)], fill=TEAL)
    return im

for name, fn in (("mw_01", img1), ("mw_02", img2), ("mw_03", img3)):
    fn().save(os.path.join(BASE, name + ".jpg"), quality=93)
print("done")
