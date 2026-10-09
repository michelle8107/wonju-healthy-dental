# 한글날 정상진료 안내 카드 (폰 화면 느낌) - 점프 정지컷 위에 띄운다
# 진료시간은 사용자에게 확인받지 않았으므로 카드에 넣지 않는다 (날짜 + 정상진료만).
from PIL import Image, ImageDraw, ImageFont
FONT = r"D:/OneDrive/Claude_Dental Clinic/assets/geonchi_shorts/fonts/Jua-Regular.ttf"
def f(s): return ImageFont.truetype(FONT, s)
TEAL, INK, SOFT = (46,122,120), (16,30,51), (90,104,125)

def card(path):
    im = Image.new("RGBA", (720, 1280), (0,0,0,0))
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = 70, 330, 650, 760
    d.rounded_rectangle([x0+6, y0+10, x1+6, y1+10], 36, fill=(0,0,0,90))
    d.rounded_rectangle([x0, y0, x1, y1], 36, fill=(255,255,255,250))
    d.rounded_rectangle([x0, y0, x1, y0+130], 36, fill=TEAL)
    d.rectangle([x0, y0+90, x1, y0+130], fill=TEAL)
    def ctext(y, t, font, fill):
        bb = d.textbbox((0,0), t, font=font); d.text(((720-(bb[2]-bb[0]))/2-bb[0], y), t, font=font, fill=fill)
    ctext(y0+22, "원주 건강한치과", f(36), (220,245,242))
    ctext(y0+66, "한글날 진료 안내", f(46), "white")
    ctext(y0+175, "10/9 (금)", f(96), INK)
    ctext(y0+300, "한글날", f(40), SOFT)
    bb = d.textbbox((0,0), "정상진료", font=f(52))
    w = bb[2]-bb[0]
    bx0 = (720-w)/2 - 28
    d.rounded_rectangle([bx0, y0+345, bx0+w+56, y0+415], 36, fill=(226,242,240))
    d.text((360-w/2-bb[0], y0+352), "정상진료", font=f(52), fill=TEAL)
    im.save(path)
    return "원주 건강한치과한글날 진료 안내10/9 (금)한글날정상진료"

if __name__ == "__main__":
    card("card.png")
