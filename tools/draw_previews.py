#!/usr/bin/env python3
"""Draw dial.png / preview.png for analog + digital faces (PIL only, no network)."""
import math
import os
from PIL import Image, ImageDraw, ImageFont

BASE = "/home/hatch/workspace/vivo-watchface/project/faces"
CJK = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
DJV = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

W, H = 432, 514
CX, CY = 216, 257


def F(path, size):
    return ImageFont.truetype(path, size)


def analog_dial():
    img = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([CX - 185, CY - 185, CX + 185, CY + 185], outline=(51, 51, 51), width=2)
    d.ellipse([CX - 155, CY - 155, CX + 155, CY + 155], outline=(34, 34, 34), width=1)
    for i in range(60):
        a = math.radians(i * 6)
        sa, ca = math.sin(a), math.cos(a)
        if i % 5 == 0:
            r1, r2, w, col = 163, 183, 4, (255, 255, 255)
        else:
            r1, r2, w, col = 173, 183, 2, (140, 140, 140)
        d.line([CX + r1 * sa, CY - r1 * ca, CX + r2 * sa, CY - r2 * ca], fill=col, width=w)
    nf = F(DJV, 46)
    for num, ang in [("12", 0), ("3", 90), ("6", 180), ("9", 270)]:
        a = math.radians(ang)
        d.text((CX + 128 * math.sin(a), CY - 128 * math.cos(a)), num,
               font=nf, fill=(255, 255, 255), anchor="mm")
    return img


def hand(d, angle_deg, length, width, color):
    a = math.radians(angle_deg)
    x2 = CX + length * math.sin(a)
    y2 = CY - length * math.cos(a)
    d.line([CX, CY, x2, y2], fill=color, width=width)
    r = width // 2
    d.ellipse([x2 - r, y2 - r, x2 + r, y2 + r], fill=color)


def analog_preview(dial):
    pv = dial.copy()
    d = ImageDraw.Draw(pv)
    d.text((CX, 45), "11月8日 星期五", font=F(CJK, 24), fill=(204, 204, 204), anchor="mm")
    hand(d, (10 % 12) * 30 + 9 * 0.5, 100, 10, (255, 255, 255))   # 时针 10:09
    hand(d, 9 * 6 + 36 * 0.1, 140, 7, (255, 255, 255))            # 分针
    hand(d, 36 * 6, 155, 4, (255, 59, 48))                        # 秒针
    d.ellipse([CX - 8, CY - 8, CX + 8, CY + 8], fill=(255, 255, 255))
    d.text((CX, 465), "12345 步 · 88%", font=F(CJK, 22), fill=(204, 204, 204), anchor="mm")
    return pv


def digital_preview():
    img = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(img)
    big = F(DJV, 110)
    d.text((CX, 170), "10:09", font=big, fill=(255, 255, 255), anchor="mm")
    d.text((392, 56), "36", font=F(DJV, 28), fill=(136, 136, 136), anchor="ra")
    d.text((CX, 278), "11月8日 星期五", font=F(CJK, 26), fill=(204, 204, 204), anchor="mm")
    d.text((CX, 328), "12345 步 · 78 心率 · 88% 电量", font=F(CJK, 22),
           fill=(204, 204, 204), anchor="mm")
    # 步数目标进度环：6200/10000 = 62%
    r, cx, cy = 48, CX, 418
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(51, 51, 51), width=6)
    d.arc([cx - r, cy - r, cx + r, cy + r], start=-90, end=-90 + 360 * 0.62,
          fill=(77, 163, 255), width=6)
    d.text((cx, cy), "62%", font=F(DJV, 20), fill=(255, 255, 255), anchor="mm")
    return img


def main():
    a_dir = os.path.join(BASE, "analog/src/watchface/assets/images")
    d_dir = os.path.join(BASE, "digital/src/watchface/assets/images")
    dial = analog_dial()
    dial.save(os.path.join(a_dir, "dial.png"))
    analog_preview(dial).save(os.path.join(a_dir, "preview.png"))
    digital_preview().save(os.path.join(d_dir, "preview.png"))
    for p in [os.path.join(a_dir, "dial.png"), os.path.join(a_dir, "preview.png"),
              os.path.join(d_dir, "preview.png")]:
        im = Image.open(p)
        print(p, im.size, os.path.getsize(p), "bytes")


if __name__ == "__main__":
    main()
