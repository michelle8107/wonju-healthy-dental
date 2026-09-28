# 10월 진료 일정 카드 (폰 화면 느낌) - n5 내레이션 동안 화면 가운데에 띄운다
from PIL import Image, ImageDraw, ImageFont
FONT = r"D:/OneDrive/Claude_Dental Clinic/assets/geonchi_shorts/fonts/Jua-Regular.ttf"
def f(s): return ImageFont.truetype(FONT, s)
TEAL, INK, SOFT, WINE = (46,122,120), (16,30,51), (90,104,125), (181,71,63)

def card(path):
    im = Image.new("RGBA", (720, 1280), (0,0,0,0))
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = 70, 300, 650, 900
    d.rounded_rectangle([x0+6, y0+10, x1+6, y1+10], 36, fill=(0,0,0,90))          # 그림자
    d.rounded_rectangle([x0, y0, x1, y1], 36, fill=(255,255,255,250))
    d.rounded_rectangle([x0, y0, x1, y0+130], 36, fill=TEAL)
    d.rectangle([x0, y0+90, x1, y0+130], fill=TEAL)
    def ctext(y, t, font, fill):
        bb = d.textbbox((0,0), t, font=font); d.text(((720-(bb[2]-bb[0]))/2-bb[0], y), t, font=font, fill=fill)
    ctext(y0+22, "원주 건강한치과", f(36), (220,245,242))
    ctext(y0+66, "10월 진료 안내", f(46), "white")
    rows = [("10/3 (토)", "개천절"), ("10/5 (월)", "대체공휴일"), ("10/9 (금)", "한글날")]
    y = y0 + 165
    for date, name in rows:
        d.text((x0+34, y), date, font=f(40), fill=INK)
        d.text((x0+215, y+8), name, font=f(30), fill=SOFT)
        bb = d.textbbox((0,0), "정상진료", font=f(34))
        bx = x1-40-(bb[2]-bb[0])
        d.rounded_rectangle([bx-16, y-6, x1-24, y+50], 26, fill=(226,242,240))
        d.text((bx-4, y+4), "정상진료", font=f(34), fill=TEAL)
        y += 92
    d.line([x0+40, y+4, x1-40, y+4], fill=(214,224,238), width=3)
    ctext(y+26, "10/14 (수) ~ 10/18 (일)", f(38), WINE)
    ctext(y+76, "학회 세미나로 휴진", f(34), WINE)
    im.save(path)
    return "원주 건강한치과10월 진료 안내정상진료" + "".join(a+b for a,b in rows) + "10/14 (수) ~ 10/18 (일)학회 세미나로 휴진"

if __name__ == "__main__":
    card("card.png")
