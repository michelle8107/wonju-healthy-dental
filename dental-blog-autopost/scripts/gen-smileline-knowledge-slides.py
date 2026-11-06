# 치과지식 페이지용 4:5 슬라이드 4장 (블로그 설명 그림 재사용) → assets/instagram_carousels/smileline_guide/
from PIL import Image, ImageDraw, ImageFont
import os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
SRC = os.path.join(ROOT, "assets", "blog_mouth_wrinkle")
OUT = os.path.join(ROOT, "assets", "instagram_carousels", "smileline_guide")
os.makedirs(OUT, exist_ok=True)
FP = "C:/Windows/Fonts/NotoSansKR-VF.ttf"
def F(sz, w="Bold"):
    f = ImageFont.truetype(FP, sz); f.set_variation_by_name(w); return f
TEAL = "#0F3D3A"; BG = "#F7F9F8"; INK = "#222222"; SOFT = "#666666"; MINT = "#CFE6E1"
W, H = 1080, 1350

def center_lines(d, lines, y, font, fill, gap=14):
    for ln in lines:
        bb = d.textbbox((0, 0), ln, font=font)
        d.text(((W - (bb[2] - bb[0])) / 2 - bb[0], y), ln, font=font, fill=fill)
        y += (bb[3] - bb[1]) + gap + 10
    return y

def cover():
    im = Image.new("RGB", (W, H), TEAL); d = ImageDraw.Draw(im)
    d.text((W // 2, 420), "입가 고민 · 스마일라인", font=F(40, "Medium"), fill="#9FD3C7", anchor="mm")
    center_lines(d, ["웃을 때 입가 라인이", "신경 쓰인다면?"], 500, F(88, "Black"), "#FFFFFF")
    center_lines(d, ["치과에서 하는", "스마일라인 케어 이야기"], 770, F(48, "Medium"), "#D7EEE8")
    d.text((W // 2, H - 90), "원주 건강한치과", font=F(32, "Medium"), fill="#9FD3C7", anchor="mm")
    return im

def card(title_lines, img_name, caption, ai_note):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 10], fill=TEAL)
    y = center_lines(d, title_lines, 150, F(56), TEAL)
    pic = Image.open(os.path.join(SRC, img_name)).convert("RGB")
    pic = pic.resize((960, int(pic.size[1] * 960 / pic.size[0])))
    py = 420
    im.paste(pic, (60, py))
    d.rounded_rectangle([60, py, 1020, py + pic.size[1]], radius=6, outline=MINT, width=3)
    center_lines(d, caption, py + pic.size[1] + 50, F(34, "Medium"), INK)
    d.text((W // 2, H - 70), ai_note, font=F(24, "Regular"), fill=SOFT, anchor="mm")
    return im

AI = "AI로 생성한 설명용 일러스트이며 실제 사람·구조와 차이가 있을 수 있습니다"
DG = "이해를 돕기 위해 직접 그린 설명용 도식이며, 개인차가 있을 수 있습니다"
slides = [
    cover(),
    card(["스마일라인,", "어디를 말하는 걸까요?"], "mw_01.jpg", ["팔자주름, 마리오네트 라인 등", "웃을 때 도드라지는 입가 주변 라인"], AI),
    card(["입가 라인은", "피부만의 문제가 아니에요"], "mw_02.jpg", ["피부, 지방, 근육, 턱뼈 등", "여러 층이 함께 영향을 줍니다"], AI),
    card(["스마일라인 케어는", "이런 흐름으로 안내합니다"], "mw_03.jpg", ["구강 안쪽과 피부 바깥쪽을 함께 살펴보고", "내 상태에 맞는지 상담에서 확인하세요"], DG),
]
for i, s in enumerate(slides, 1):
    s.save(os.path.join(OUT, f"{i:02d}.png"))
print("done", OUT)
