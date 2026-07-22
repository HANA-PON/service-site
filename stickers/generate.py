# -*- coding: utf-8 -*-
"""「〜ても、シリーズ」ステッカー入稿データ生成スクリプト

SUZURI入稿用の透過PNG(2000x2000)を stickers/png/ に出力する。
デザインは背景イラスト版: 各フレーズに合わせたフラットな
情景イラストを角丸正方形いっぱいに描き、生成りの薄いスクリムを
かけて、その上に縦書き2列の言葉を重ねる。1枚ものなので
カットラインは外周1本。
フォント: Zen Maru Gothic Light (SIL Open Font License 1.1 / 商用利用可)

使い方:
    python3 stickers/generate.py
"""
import math
import os
import urllib.request

from PIL import Image, ImageDraw, ImageFont

FONT_URL = (
    "https://fonts.gstatic.com/s/zenmarugothic/v19/"
    "o-0XIpIxzW5b-RxT-6A8jWAtCp-cQWpCPA.ttf"
)
FONT_CACHE = os.path.join(os.path.dirname(__file__), "ZenMaruGothic-Light.ttf")

CANVAS = 2000          # SUZURI推奨の大判サイズ
COLOR = (74, 74, 74, 255)  # 濃いめのグレー1色(文字)

BASE_SIZE = (1840, 1840)   # 角丸正方形(イラストを見せるため大きめ)
BASE_RADIUS = 140
BASE_BORDER = (188, 184, 175, 255)
BASE_BORDER_W = 8
SCRIM = (247, 245, 240, 150)  # 文字を立たせる生成りの薄がけ

PAD_Y = 170            # 上下端から文字までの最低余白
MAX_FONT_SIZE = 240    # 短い句が間延びしないよう上限を設ける
COL_GAP_EM = 1.60      # 右列と左列の中心間隔(フォントサイズ比)
DROP_EM = 0.55         # 左列(2句目)を下げる量(句のリズム)

# イラストの共通パレット(くすませて文字より前に出さない)
NAVY = (104, 114, 134)
NIGHT = (82, 90, 108)
CREAM = (240, 236, 226)
PAPER = (230, 225, 214)
BLUE = (170, 183, 197)
LIGHT = (236, 219, 170)
INK = (94, 94, 96)
WOOD = (198, 182, 158)

STICKERS = [
    ("01-kaettemo", "かえっても、かえりたい"),
    ("02-netemo", "ねても、ねむい"),
    ("03-yasundemo", "やすんでも、つかれてる"),
    ("04-warattemo", "わらっても、めがしんでる"),
    ("05-nondemo", "のんでも、さめてる"),
    ("06-kinyobidemo", "きんようびでも、うれしくない"),
    ("07-susundemo", "すすんでも、まえじゃない"),
    ("08-shabettemo", "しゃべっても、ひとりごと"),
    ("09-ikitetemo", "いきてても、たいきじかん"),
]


# ---------------------------------------------------------------- 情景イラスト
# 各シーンは1840x1840の不透明な正方形いっぱいに描く

def scene_home(d, s):
    """夜道から見た我が家: 窓は明るいのに、まだ帰りたい"""
    d.rectangle((0, 0, s, s), fill=NIGHT)
    d.ellipse((s - 560, 180, s - 300, 440), fill=LIGHT)  # 月
    d.rectangle((0, 1450, s, s), fill=(66, 72, 88))       # 地面
    d.rectangle((260, 980, 940, 1450), fill=(58, 64, 78))  # 家
    d.polygon([(200, 980), (600, 700), (1000, 980)], fill=(50, 55, 68))  # 屋根
    d.rectangle((520, 1130, 690, 1310), fill=LIGHT)        # 明かりのついた窓
    d.rectangle((600, 1130, 610, 1310), fill=(58, 64, 78))  # 窓の桟
    d.rectangle((520, 1215, 690, 1225), fill=(58, 64, 78))


def scene_sleep(d, s):
    """夜明け前の布団: 何時間寝ても足りない"""
    d.rectangle((0, 0, s, s), fill=NIGHT)
    d.ellipse((560, 260, 1280, 980), fill=LIGHT)           # 三日月
    d.ellipse((420, 220, 1100, 900), fill=NIGHT)
    for x, y in [(300, 300), (1500, 480), (1620, 200), (240, 720)]:
        d.ellipse((x, y, x + 26, y + 26), fill=CREAM)      # 星
    d.rounded_rectangle((240, 1330, 1600, 1620), 60, fill=BLUE)   # 掛け布団
    d.rounded_rectangle((280, 1190, 700, 1360), 50, fill=CREAM)   # 枕


def scene_rest(d, s):
    """休日のソファ: 座っているだけで日が暮れる"""
    d.rectangle((0, 0, s, s), fill=PAPER)
    d.rectangle((0, 1420, s, s), fill=(214, 206, 190))     # 床
    d.rounded_rectangle((250, 820, 1590, 1180), 70, fill=BLUE)    # 背もたれ
    d.rounded_rectangle((250, 1100, 1590, 1420), 60, fill=(150, 165, 182))  # 座面
    d.rounded_rectangle((170, 1000, 330, 1420), 60, fill=BLUE)    # 肘掛け
    d.rounded_rectangle((1510, 1000, 1670, 1420), 60, fill=BLUE)
    d.rounded_rectangle((1280, 940, 1420, 1120), 30, fill=WOOD)   # 置きっぱなしのマグ
    for i, x in enumerate((1320, 1370)):                    # 冷めていく湯気
        d.arc((x, 800 - i * 30, x + 44, 900 - i * 30), 90, 270, fill=INK, width=8)


def scene_face(d, s):
    """笑顔の練習: 口は覚えたが目が覚えない"""
    d.rectangle((0, 0, s, s), fill=PAPER)
    d.ellipse((460, 420, 1380, 1340), fill=LIGHT)          # 顔
    d.line((700, 800, 850, 800), fill=INK, width=22)       # 死んだ目(横線)
    d.line((990, 800, 1140, 800), fill=INK, width=22)
    d.arc((790, 950, 1050, 1150), 20, 160, fill=INK, width=22)  # 笑っている口


def scene_beer(d, s):
    """一杯目: 乾杯の音だけ聞こえて、酔いは来ない"""
    d.rectangle((0, 0, s, s), fill=(96, 90, 94))
    d.rectangle((0, 1400, s, s), fill=WOOD)                # カウンター
    d.rounded_rectangle((660, 640, 1120, 1400), 40, fill=(224, 186, 118))  # ジョッキ
    for x in (680, 800, 920, 1030):                         # 泡
        d.ellipse((x, 560, x + 160, 720), fill=CREAM)
    d.rectangle((660, 680, 1120, 720), fill=CREAM)
    d.rounded_rectangle((1120, 800, 1280, 1180), 60, outline=(224, 186, 118), width=50)  # 取っ手
    d.line((760, 760, 760, 1320), fill=(238, 206, 150), width=26)  # グラスのハイライト


def scene_friday(d, s):
    """カレンダーの金曜日: 丸をつけたのに、心が動かない"""
    d.rectangle((0, 0, s, s), fill=PAPER)
    d.rounded_rectangle((320, 300, 1520, 1540), 40, fill=CREAM, outline=INK, width=10)
    d.rectangle((320, 300, 1520, 470), fill=BLUE)          # ヘッダー
    for i in range(1, 7):                                   # 縦罫(7列)
        x = 320 + i * (1200 // 7)
        d.line((x, 470, x, 1540), fill=(200, 195, 184), width=8)
    for j in range(1, 5):                                   # 横罫(5行)
        y = 470 + j * (1070 // 5)
        d.line((320, y, 1520, y), fill=(200, 195, 184), width=8)
    fx = 320 + 5 * (1200 // 7) + (1200 // 14)               # 金曜の列の2行目
    fy = 470 + (1070 // 5) + (1070 // 10)
    d.ellipse((fx - 90, fy - 90, fx + 90, fy + 90), outline=INK, width=16)


def scene_train(d, s):
    """いつもの電車: 進んでいるのは電車であって自分ではない"""
    d.rectangle((0, 0, s, s), fill=(206, 210, 216))
    d.rectangle((0, 1360, s, s), fill=(182, 186, 192))     # ホーム
    d.line((0, 1360, s, 1360), fill=(240, 214, 130), width=24)  # 黄色い線
    d.rounded_rectangle((80, 760, 1760, 1300), 60, fill=BLUE)   # 車体
    for x in range(180, 1700, 320):                         # 窓
        d.rounded_rectangle((x, 850, x + 200, 1030), 30, fill=CREAM)
    d.rectangle((80, 1120, 1760, 1160), fill=(150, 165, 182))   # 帯
    for x in (480, 1120):                                   # ドア
        d.rectangle((x, 840, x + 24, 1300), fill=(150, 165, 182))


def scene_talk(d, s):
    """会議室: 発言はぜんぶ、空中で消える"""
    d.rectangle((0, 0, s, s), fill=PAPER)
    bubbles = [(280, 340, 760, 620), (1020, 500, 1560, 800), (520, 900, 1080, 1200)]
    for i, (x0, y0, x1, y1) in enumerate(bubbles):
        d.rounded_rectangle((x0, y0, x1, y1), 90, fill=CREAM, outline=INK, width=10)
        cx = (x0 + x1) // 2
        tail_y = y1
        d.polygon([(cx - 40, tail_y), (cx + 40, tail_y), (cx - 10, tail_y + 90)],
                  fill=CREAM, outline=INK)
        cy = (y0 + y1) // 2
        for k in range(3):                                  # 中身は「…」だけ
            dot = cx - 90 + k * 90
            d.ellipse((dot - 18, cy - 18, dot + 18, cy + 18), fill=INK)


def scene_wait(d, s):
    """待合室: 呼ばれる予定のない番号を持って座っている"""
    d.rectangle((0, 0, s, s), fill=(222, 222, 218))
    d.rectangle((0, 1380, s, s), fill=(200, 200, 196))     # 床
    for x in range(200, 1500, 420):                         # 並んだ椅子
        d.rounded_rectangle((x, 980, x + 300, 1120), 30, fill=BLUE)      # 背
        d.rounded_rectangle((x, 1100, x + 300, 1220), 30, fill=(150, 165, 182))  # 座面
        d.rectangle((x + 30, 1220, x + 60, 1380), fill=INK)              # 脚
        d.rectangle((x + 240, 1220, x + 270, 1380), fill=INK)
    d.ellipse((1450, 220, 1690, 460), fill=CREAM)          # 壁の時計
    d.ellipse((1450, 220, 1690, 460), outline=INK, width=12)
    d.line((1570, 340, 1570, 260), fill=INK, width=14)     # 針
    d.line((1570, 340, 1630, 370), fill=INK, width=14)


SCENES = {
    "01-kaettemo": scene_home,
    "02-netemo": scene_sleep,
    "03-yasundemo": scene_rest,
    "04-warattemo": scene_face,
    "05-nondemo": scene_beer,
    "06-kinyobidemo": scene_friday,
    "07-susundemo": scene_train,
    "08-shabettemo": scene_talk,
    "09-ikitetemo": scene_wait,
}


# ---------------------------------------------------------------- 文字と合成

def load_font(size):
    if not os.path.exists(FONT_CACHE):
        urllib.request.urlretrieve(FONT_URL, FONT_CACHE)
    return ImageFont.truetype(FONT_CACHE, size)


def split_lines(text):
    # 読点で2句に割る。読点は1句目の末尾に残す(諦めの「間」を作る)
    head, _, tail = text.partition("、")
    return [head + "、", tail]


def column_height(draw, line, font):
    box = draw.textbbox((0, 0), line, font=font, direction="ttb", anchor="mt")
    return box[3] - box[1]


def fit_font_size(draw, lines):
    max_h = BASE_SIZE[1] - PAD_Y * 2
    size = MAX_FONT_SIZE
    while size > 10:
        font = load_font(size)
        drop = int(size * DROP_EM)
        h1 = column_height(draw, lines[0], font)
        h2 = column_height(draw, lines[1], font) + drop
        if max(h1, h2) <= max_h:
            return size
        size -= 4
    return size


def render(slug, text):
    lines = split_lines(text)
    bw, bh = BASE_SIZE
    bx, by = (CANVAS - bw) // 2, (CANVAS - bh) // 2

    # 情景イラストを描いて角丸に切り抜く
    scene = Image.new("RGB", (bw, bh))
    SCENES[slug](ImageDraw.Draw(scene), bw)
    mask = Image.new("L", (bw, bh), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, bw, bh), BASE_RADIUS, fill=255)

    img = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    img.paste(scene, (bx, by), mask)

    # 生成りのスクリム(文字の可読性を確保しつつイラストを透かす)
    overlay = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    ImageDraw.Draw(overlay).rounded_rectangle(
        (bx, by, bx + bw, by + bh), BASE_RADIUS, fill=SCRIM
    )
    img = Image.alpha_composite(img, overlay)

    # 縦書き2列の言葉と枠線(透明レイヤーに描いてから合成)
    top = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    d = ImageDraw.Draw(top)
    size = fit_font_size(d, lines)
    font = load_font(size)
    drop = int(size * DROP_EM)
    gap = int(size * COL_GAP_EM)
    h1 = column_height(d, lines[0], font)
    h2 = column_height(d, lines[1], font) + drop
    y_top = (CANVAS - max(h1, h2)) // 2
    # 縦書きは右列から読むので、1句目を右・2句目を左に置く
    d.text((CANVAS // 2 + gap // 2, y_top),
           lines[0], font=font, fill=COLOR, direction="ttb", anchor="mt")
    d.text((CANVAS // 2 - gap // 2, y_top + drop),
           lines[1], font=font, fill=COLOR, direction="ttb", anchor="mt")
    d.rounded_rectangle((bx, by, bx + bw, by + bh), BASE_RADIUS,
                        outline=BASE_BORDER, width=BASE_BORDER_W)
    img = Image.alpha_composite(img, top)

    out_dir = os.path.join(os.path.dirname(__file__), "png")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{slug}.png")
    img.save(path)
    print(f"wrote {path} (font {size}px)")


def preview_sheet():
    # 確認用の一覧シート(入稿には使わない)
    cell = 640
    cols = 3
    rows = (len(STICKERS) + cols - 1) // cols
    sheet = Image.new("RGB", (cell * cols, cell * rows), (206, 203, 197))
    out_dir = os.path.join(os.path.dirname(__file__), "png")
    for i, (slug, _) in enumerate(STICKERS):
        img = Image.open(os.path.join(out_dir, f"{slug}.png")).resize(
            (cell, cell), Image.LANCZOS
        )
        sheet.paste(img, ((i % cols) * cell, (i // cols) * cell), img)
    path = os.path.join(os.path.dirname(__file__), "preview.png")
    sheet.save(path)
    print(f"wrote {path}")


if __name__ == "__main__":
    for slug, text in STICKERS:
        render(slug, text)
    preview_sheet()
