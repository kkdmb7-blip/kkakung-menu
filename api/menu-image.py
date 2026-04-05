from http.server import BaseHTTPRequestHandler
import json
import io
import urllib.request
import os
from PIL import Image, ImageDraw, ImageFont

FONT_URLS = {
    'bold':    'https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Korean/NotoSansCJKkr-Bold.otf',
    'regular': 'https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Korean/NotoSansCJKkr-Regular.otf',
    'light':   'https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Korean/NotoSansCJKkr-Light.otf',
}
_font_cache = {}

def get_font(style, size):
    key = f"{style}_{size}"
    if key in _font_cache:
        return _font_cache[key]
    tmp = f"/tmp/noto_{style}.otf"
    if not os.path.exists(tmp):
        urllib.request.urlretrieve(FONT_URLS[style], tmp)
    f = ImageFont.truetype(tmp, size)
    _font_cache[key] = f
    return f

COL_BG        = (255, 252, 244)
COL_WHITE     = (255, 255, 255)
COL_GREEN_HDR = (110, 170, 100)
COL_STAGE_BG  = (245, 244, 238)
COL_GREEN_M   = (190, 225, 180)
COL_BLUE_M    = (180, 215, 235)
COL_PEACH_M   = (240, 208, 182)
COL_BORDER    = (180, 175, 160)
COL_DARK      = (35, 35, 35)
COL_MID       = (75, 75, 75)
COL_LIGHT     = (130, 125, 110)
COL_GREEN_TXT = (55, 130, 65)
COL_ACCENT    = (75, 155, 85)

def tcx(draw, text, x, y, w, font, color=None):
    color = color or COL_DARK
    bb = draw.textbbox((0, 0), text, font=font)
    tw = bb[2] - bb[0]
    draw.text((x + (w - tw) // 2, y), text, fill=color, font=font)

def draw_char(draw, cx, cy, r=30):
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(255,218,130), outline=(180,150,60), width=2)
    draw.ellipse([cx-r+4, cy-r+4, cx+r-4, cy+r-4], fill=(255,232,170))
    ey = cy - 6
    draw.ellipse([cx-11, ey-5, cx-3, ey+3], fill=COL_DARK)
    draw.ellipse([cx+3,  ey-5, cx+11, ey+3], fill=COL_DARK)
    draw.ellipse([cx-9, ey-4, cx-6, ey-1], fill=COL_WHITE)
    draw.ellipse([cx+5, ey-4, cx+8, ey-1], fill=COL_WHITE)
    draw.arc([cx-9, cy+2, cx+9, cy+18], 10, 170, fill=(180,100,60), width=2)
    draw.ellipse([cx-r-8, cy-10, cx-r+4, cy+4], fill=(255,218,130), outline=(180,150,60), width=1)
    draw.ellipse([cx+r-4, cy-10, cx+r+8, cy+4], fill=(255,218,130), outline=(180,150,60), width=1)

def make_yushik_image(data):
    date_str = data['date_str']
    menus    = data['menus']   # [{name, ingred:[lines]}, ...] 3개
    origins  = data.get('origins', '')

    W = 940; MARGIN = 35; TW = W - MARGIN*2
    COL1W = 138; COLMW = (TW - COL1W) // 3
    ROW_NAME_H = 38; ROW_INGRED_H = 100; ROW_H = ROW_NAME_H + ROW_INGRED_H
    HDR_ROW_H = 38; TABLE_TOP = 195
    TABLE_H = HDR_ROW_H + ROW_H * 3
    H = TABLE_TOP + TABLE_H + 130

    img = Image.new('RGB', (W, H), COL_BG)
    draw = ImageDraw.Draw(img)

    f_title  = get_font('bold', 26)
    f_stage  = get_font('bold', 14)
    f_stgsub = get_font('regular', 11)
    f_mname  = get_font('bold', 13)
    f_ingred = get_font('regular', 12)
    f_origin = get_font('light', 10)
    f_slogan = get_font('bold', 13)
    f_hdr    = get_font('bold', 15)

    draw_char(draw, W // 2, 46)
    title = f"까꿍  디미방  {date_str}  이유식  메뉴표"
    bb = draw.textbbox((0,0), title, font=f_title)
    draw.text(((W-(bb[2]-bb[0]))//2, 96), title, fill=COL_DARK, font=f_title)
    draw.line([(MARGIN,140),(W-MARGIN,140)], fill=COL_ACCENT, width=1)

    TR = TABLE_TOP
    draw.rectangle([MARGIN, TR, MARGIN+TW, TR+TABLE_H], outline=COL_BORDER, width=2)
    draw.rectangle([MARGIN, TR, MARGIN+TW, TR+HDR_ROW_H], fill=COL_GREEN_HDR, outline=COL_BORDER, width=1)
    tcx(draw, "단    계", MARGIN, TR+10, COL1W, f_hdr, COL_WHITE)
    tcx(draw, "메                                                      뉴", MARGIN+COL1W, TR+10, TW-COL1W, f_hdr, COL_WHITE)

    stages = [
        ("오물오물\n중  기", "(7 ~ 9 개월)"),
        ("잘근잘근\n후  기", "(9 ~ 14 개월)"),
        ("와구와구\n완 료 기", "(14 개월 ~)"),
    ]
    suffix  = ["죽", "무른밥", "진밥"]
    mcolors = [COL_GREEN_M, COL_BLUE_M, COL_PEACH_M]
    nums    = [["1.","2.","3."],["4.","5.","6."],["7.","8.","9."]]

    for ri, (stg, stgsub) in enumerate(stages):
        ry = TR + HDR_ROW_H + ri * ROW_H
        draw.rectangle([MARGIN, ry, MARGIN+COL1W, ry+ROW_H], fill=COL_STAGE_BG, outline=COL_BORDER, width=1)
        sy = ry + 20
        for sl in stg.split('\n'):
            bb = draw.textbbox((0,0), sl, font=f_stage)
            draw.text((MARGIN+(COL1W-(bb[2]-bb[0]))//2, sy), sl, fill=COL_DARK, font=f_stage)
            sy += 20
        bb = draw.textbbox((0,0), stgsub, font=f_stgsub)
        draw.text((MARGIN+(COL1W-(bb[2]-bb[0]))//2, sy+4), stgsub, fill=COL_LIGHT, font=f_stgsub)

        for mi, menu in enumerate(menus):
            mx = MARGIN + COL1W + mi * COLMW
            draw.rectangle([mx, ry, mx+COLMW, ry+ROW_NAME_H], fill=mcolors[mi], outline=COL_BORDER, width=1)
            tcx(draw, f"{nums[ri][mi]} {menu['name']} {suffix[ri]}", mx, ry+10, COLMW, f_mname, COL_DARK)
            draw.rectangle([mx, ry+ROW_NAME_H, mx+COLMW, ry+ROW_H], fill=COL_WHITE, outline=COL_BORDER, width=1)
            iy = ry + ROW_NAME_H + 12
            for il in menu['ingred']:
                bb = draw.textbbox((0,0), il, font=f_ingred)
                draw.text((mx+(COLMW-(bb[2]-bb[0]))//2, iy), il, fill=COL_MID, font=f_ingred)
                iy += 17

    oy = TR + TABLE_H + 14
    bb = draw.textbbox((0,0), origins, font=f_origin)
    draw.text(((W-(bb[2]-bb[0]))//2, oy), origins, fill=COL_LIGHT, font=f_origin)
    slogan = "☆ 까꿍 디미방은 재료 궁합까지 생각하며 만듭니다 ☆"
    bb = draw.textbbox((0,0), slogan, font=f_slogan)
    draw.text(((W-(bb[2]-bb[0]))//2, oy+18), slogan, fill=COL_GREEN_TXT, font=f_slogan)

    buf = io.BytesIO()
    img.save(buf, 'PNG', dpi=(150,150))
    return buf.getvalue()


def make_yusik_image(data):
    date_str = data['date_str']
    items    = data['items']   # 5개 [{name, ingred:[lines], origin}]
    soup     = data['soup']    # {name, ingred:[lines]}
    origins  = data.get('origins', '')
    notes    = data.get('notes', [])

    W = 940; MARGIN = 35; TW = W - MARGIN*2
    CELL_W = TW // 3; CELL_H = 170; TABLE_TOP = 195
    ROW1_H = CELL_H; ROW2_H = CELL_H; SOUP_H = 130
    TABLE_H = ROW1_H + ROW2_H + SOUP_H
    H = TABLE_TOP + TABLE_H + 180

    img = Image.new('RGB', (W, H), COL_BG)
    draw = ImageDraw.Draw(img)

    f_title  = get_font('bold', 26)
    f_iname  = get_font('bold', 14)
    f_ingred = get_font('regular', 12)
    f_orig   = get_font('light', 10)
    f_slogan = get_font('bold', 13)
    f_info   = get_font('regular', 12)
    f_price  = get_font('bold', 15)

    COL_ITEM_HDR = (195, 225, 185)
    COL_SOUP_HDR = (180, 215, 235)

    draw_char(draw, W // 2, 46)
    title = f"까꿍  디미방  {date_str}  유아식  메뉴표"
    bb = draw.textbbox((0,0), title, font=f_title)
    draw.text(((W-(bb[2]-bb[0]))//2, 96), title, fill=COL_DARK, font=f_title)
    draw.line([(MARGIN,140),(W-MARGIN,140)], fill=COL_ACCENT, width=1)

    TR = TABLE_TOP
    draw.rectangle([MARGIN, TR, MARGIN+TW, TR+TABLE_H], outline=COL_BORDER, width=2)

    HALF_W = TW // 2
    positions = [
        (MARGIN+0*CELL_W, TR,        CELL_W,    ROW1_H),
        (MARGIN+1*CELL_W, TR,        CELL_W,    ROW1_H),
        (MARGIN+2*CELL_W, TR,        CELL_W,    ROW1_H),
        (MARGIN,          TR+ROW1_H, HALF_W,    ROW2_H),
        (MARGIN+HALF_W,   TR+ROW1_H, TW-HALF_W, ROW2_H),
    ]
    NAME_H = 36
    for idx, (ix, iy, iw, ih) in enumerate(positions):
        item = items[idx]
        draw.rectangle([ix, iy, ix+iw, iy+NAME_H], fill=COL_ITEM_HDR, outline=COL_BORDER, width=1)
        tcx(draw, f"{idx+1}. {item['name']}", ix, iy+9, iw, f_iname, COL_DARK)
        draw.rectangle([ix, iy+NAME_H, ix+iw, iy+ih], fill=COL_WHITE, outline=COL_BORDER, width=1)
        cy = iy + NAME_H + 10
        for il in item['ingred']:
            bb = draw.textbbox((0,0), il, font=f_ingred)
            draw.text((ix+(iw-(bb[2]-bb[0]))//2, cy), il, fill=COL_MID, font=f_ingred)
            cy += 17
        if item.get('origin'):
            bb = draw.textbbox((0,0), item['origin'], font=f_orig)
            draw.text((ix+(iw-(bb[2]-bb[0]))//2, cy+2), item['origin'], fill=COL_LIGHT, font=f_orig)

    sy = TR + ROW1_H + ROW2_H
    draw.rectangle([MARGIN, sy, MARGIN+TW, sy+SOUP_H], fill=COL_WHITE, outline=COL_BORDER, width=1)
    SOUP_NAME_H = 34
    draw.rectangle([MARGIN, sy, MARGIN+TW, sy+SOUP_NAME_H], fill=COL_SOUP_HDR, outline=COL_BORDER, width=1)
    tcx(draw, f"6. {soup['name']}", MARGIN, sy+9, TW, f_iname, COL_DARK)
    cy = sy + SOUP_NAME_H + 10
    for il in soup['ingred']:
        bb = draw.textbbox((0,0), il, font=f_ingred)
        draw.text((MARGIN+(TW-(bb[2]-bb[0]))//2, cy), il, fill=COL_MID, font=f_ingred)
        cy += 17

    price_y = TR + TABLE_H + 18
    price_txt = "반찬5개  +  국1개  =  35,000원  세트판매"
    bb = draw.textbbox((0,0), price_txt, font=f_price)
    draw.text(((W-(bb[2]-bb[0]))//2, price_y), price_txt, fill=COL_DARK, font=f_price)

    iy2 = price_y + 30
    for line in notes:
        bb = draw.textbbox((0,0), line, font=f_info)
        draw.text(((W-(bb[2]-bb[0]))//2, iy2), line, fill=COL_MID, font=f_info)
        iy2 += 18

    oy = iy2 + 6
    bb = draw.textbbox((0,0), origins, font=f_orig)
    draw.text(((W-(bb[2]-bb[0]))//2, oy), origins, fill=COL_LIGHT, font=f_orig)
    slogan = "☆ 까꿍 디미방은 재료 궁합까지 생각하며 만듭니다 ☆"
    bb = draw.textbbox((0,0), slogan, font=f_slogan)
    draw.text(((W-(bb[2]-bb[0]))//2, oy+18), slogan, fill=COL_GREEN_TXT, font=f_slogan)

    buf = io.BytesIO()
    img.save(buf, 'PNG', dpi=(150,150))
    return buf.getvalue()


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body   = self.rfile.read(length)
            data   = json.loads(body)
            t      = data.get('type')

            if t == 'yushik':
                png = make_yushik_image(data)
                fname = f"이유식_{data.get('date_str','')}.png"
            elif t == 'yusik':
                png = make_yusik_image(data)
                fname = f"유아식_{data.get('date_str','')}.png"
            else:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'type must be yushik or yusik'}).encode())
                return

            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.send_header('Content-Disposition', f'attachment; filename="{fname}"')
            self.send_header('Content-Length', str(len(png)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(png)

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
