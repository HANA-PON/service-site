# -*- coding: utf-8 -*-
"""「〜ても、シリーズ」ステッカー入稿データ生成スクリプト

SUZURI入稿用の透過PNG(2000x2000)を stickers/png/ に出力する。
デザインはリッチ背景版: 各フレーズに合わせた情景イラストを
グラデーション・光・影・紙のような粒子感つきで描き、生成りの
薄いスクリムをかけて縦書き2列の言葉を重ねる。1枚ものなので
カットラインは外周1本。
フォント: Zen Maru Gothic Light (SIL Open Font License 1.1 / 商用利用可)

使い方:
    python3 stickers/generate.py
"""
import os
import urllib.request

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT_URL = (
    "https://fonts.gstatic.com/s/zenmarugothic/v19/"
    "o-0XIpIxzW5b-RxT-6A8jWAtCp-cQWpCPA.ttf"
)
FONT_CACHE = os.path.join(os.path.dirname(__file__), "ZenMaruGothic-Light.ttf")

CANVAS = 2000          # SUZURI推奨の大判サイズ
COLOR = (66, 66, 68, 255)  # 濃いめのグレー1色(文字)

BASE_SIZE = (1840, 1840)   # 角丸正方形(イラストを見せるため大きめ)
BASE_RADIUS = 140
BASE_BORDER = (188, 184, 175, 255)
BASE_BORDER_W = 8
SCRIM = (247, 245, 240, 132)  # 文字を立たせる生成りの薄がけ

PAD_Y = 170            # 上下端から文字までの最低余白
MAX_FONT_SIZE = 240    # 短い句が間延びしないよう上限を設ける
COL_GAP_EM = 1.60      # 右列と左列の中心間隔(フォントサイズ比)
DROP_EM = 0.55         # 左列(2句目)を下げる量(句のリズム)

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


# ---------------------------------------------------------------- 描画ヘルパー

def vgrad(s, top, bottom):
    """上下グラデーションの背景を作る"""
    t = np.linspace(0.0, 1.0, s)[:, None, None]
    arr = (1 - t) * np.array(top)[None, None, :] + t * np.array(bottom)[None, None, :]
    return Image.fromarray(arr.astype(np.uint8)).resize((s, s))


def glow(img, center, radius, color, alpha=90):
    """柔らかい光(月明かり・電灯など)を落とす"""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = center
    d.ellipse((cx - radius, cy - radius, cx + radius, cy + radius),
              fill=color + (alpha,))
    layer = layer.filter(ImageFilter.GaussianBlur(radius // 3))
    return Image.alpha_composite(img.convert("RGBA"), layer)


def soft_shadow(img, box, alpha=60, blur=40):
    """物の足元に落ちる影"""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse(box, fill=(30, 30, 40, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(img.convert("RGBA"), layer)


def finish(img, s):
    """紙のような粒子感と、四隅を落とすビネットで質感を出す"""
    rng = np.random.default_rng(7)
    arr = np.asarray(img.convert("RGB")).astype(np.int16)
    arr = arr + rng.integers(-7, 8, size=arr.shape, dtype=np.int16)
    y, x = np.mgrid[0:s, 0:s]
    dist = np.sqrt((x - s / 2) ** 2 + (y - s / 2) ** 2) / (s * 0.72)
    vign = (1.0 - 0.13 * np.clip(dist, 0, 1) ** 2)[:, :, None]
    arr = np.clip(arr * vign, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


# ---------------------------------------------------------------- 情景イラスト
# 各シーンは1840x1840の正方形いっぱいに描いたRGB画像を返す

def scene_home(s):
    """夜道から見た我が家: 窓は明るいのに、まだ帰りたい"""
    img = vgrad(s, (64, 72, 94), (108, 116, 134))
    img = glow(img, (s - 430, 310), 300, (236, 219, 170), 70)   # 月明かり
    d = ImageDraw.Draw(img)
    d.ellipse((s - 560, 180, s - 300, 440), fill=(240, 228, 188))  # 月
    rng = np.random.default_rng(3)
    for _ in range(26):                                          # 星
        x, y = rng.integers(60, s - 60), rng.integers(60, 900)
        r = int(rng.integers(3, 9))
        d.ellipse((x, y, x + r, y + r), fill=(226, 226, 220))
    d.rectangle((0, 1430, s, s), fill=(52, 58, 74))              # 地面
    img = soft_shadow(img, (180, 1400, 1060, 1500), 80)
    d = ImageDraw.Draw(img)
    d.rectangle((260, 980, 940, 1450), fill=(44, 50, 64))        # 家
    d.polygon([(200, 980), (600, 690), (1000, 980)], fill=(37, 42, 54))  # 屋根
    d.rectangle((830, 1160, 900, 1450), fill=(37, 42, 54))       # 玄関ドア
    img = glow(img, (605, 1220), 210, (236, 219, 170), 95)       # 窓の光のにじみ
    d = ImageDraw.Draw(img)
    d.rectangle((520, 1130, 690, 1310), fill=(240, 224, 168))    # 明かりのついた窓
    d.rectangle((598, 1130, 612, 1310), fill=(44, 50, 64))       # 窓の桟
    d.rectangle((520, 1213, 690, 1227), fill=(44, 50, 64))
    return img


def scene_sleep(s):
    """夜明け前の布団: 何時間寝ても足りない"""
    img = vgrad(s, (56, 63, 84), (112, 118, 136))
    img = glow(img, (900, 620), 420, (236, 219, 170), 60)        # 月のにじみ
    d = ImageDraw.Draw(img)
    d.ellipse((560, 260, 1280, 980), fill=(240, 228, 188))       # 三日月
    d.ellipse((408, 212, 1092, 896), fill=(66, 73, 94))
    rng = np.random.default_rng(5)
    for _ in range(22):
        x, y = rng.integers(60, s - 60), rng.integers(60, 1000)
        r = int(rng.integers(3, 9))
        d.ellipse((x, y, x + r, y + r), fill=(226, 226, 220))
    img = soft_shadow(img, (200, 1560, 1660, 1680), 70)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((240, 1330, 1600, 1620), 60, fill=(150, 165, 184))  # 掛け布団
    d.rounded_rectangle((240, 1330, 1600, 1470), 60, fill=(170, 183, 199))  # 布団の折り返し
    d.rounded_rectangle((280, 1180, 700, 1350), 50, fill=(238, 234, 224))   # 枕
    d.rounded_rectangle((320, 1215, 660, 1240), 12, fill=(216, 210, 196))   # 枕のくぼみ
    return img


def scene_rest(s):
    """休日のソファ: 座っているだけで日が暮れる"""
    img = vgrad(s, (238, 231, 216), (216, 206, 188))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 1400, s, s), fill=(206, 194, 174))           # 床
    d.line((0, 1400, s, 1400), fill=(184, 172, 152), width=6)
    d.ellipse((420, 1560, 1420, 1720), fill=(192, 180, 160))     # ラグ
    img = soft_shadow(img, (200, 1360, 1640, 1470), 70)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((250, 800, 1590, 1180), 70, fill=(164, 178, 194))   # 背もたれ
    d.rounded_rectangle((300, 860, 900, 1160), 50, fill=(150, 165, 184))    # へたったクッション
    d.rounded_rectangle((940, 860, 1540, 1160), 50, fill=(150, 165, 184))
    d.rounded_rectangle((250, 1100, 1590, 1420), 60, fill=(140, 155, 174))  # 座面
    d.rounded_rectangle((160, 980, 330, 1420), 60, fill=(164, 178, 194))    # 肘掛け
    d.rounded_rectangle((1510, 980, 1680, 1420), 60, fill=(164, 178, 194))
    d.rounded_rectangle((1280, 930, 1424, 1110), 30, fill=(202, 184, 156))  # 置きっぱなしのマグ
    d.ellipse((1300, 920, 1404, 960), fill=(120, 96, 76))        # 冷めたコーヒー
    for i, x in enumerate((1320, 1372)):                          # 消えかけの湯気
        d.arc((x, 790 - i * 34, x + 44, 894 - i * 34), 90, 270,
              fill=(172, 160, 144), width=8)
    return img


def scene_face(s):
    """笑顔の練習: 口は覚えたが目が覚えない"""
    img = vgrad(s, (240, 234, 220), (222, 214, 198))
    img = glow(img, (920, 860), 560, (244, 232, 196), 70)        # 顔まわりの淡い光
    img = soft_shadow(img, (560, 1310, 1280, 1400), 50)
    d = ImageDraw.Draw(img)
    d.ellipse((460, 420, 1380, 1340), fill=(240, 226, 190))      # 顔
    d.ellipse((560, 1020, 720, 1120), fill=(230, 202, 168))      # 血色のない頬
    d.ellipse((1120, 1020, 1280, 1120), fill=(230, 202, 168))
    d.line((690, 790, 850, 790), fill=(70, 70, 72), width=24)    # 死んだ目(横線)
    d.line((990, 790, 1150, 790), fill=(70, 70, 72), width=24)
    d.arc((790, 940, 1050, 1140), 25, 155, fill=(70, 70, 72), width=24)  # 笑っている口
    return img


def scene_beer(s):
    """一杯目: 乾杯の音だけ聞こえて、酔いは来ない"""
    img = vgrad(s, (66, 58, 62), (110, 98, 100))
    img = glow(img, (890, 900), 520, (232, 190, 120), 55)        # 提灯みたいな暖色
    d = ImageDraw.Draw(img)
    d.rectangle((0, 1400, s, s), fill=(148, 128, 104))           # カウンター
    d.line((0, 1400, s, 1400), fill=(110, 94, 76), width=8)
    img = soft_shadow(img, (600, 1380, 1240, 1450), 90, blur=30)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((660, 640, 1120, 1400), 40, fill=(226, 186, 116))  # ジョッキ
    d.rounded_rectangle((690, 720, 750, 1340), 26, fill=(240, 206, 148))   # ハイライト
    d.rounded_rectangle((1040, 720, 1084, 1340), 20, fill=(206, 162, 96))  # 陰
    d.rounded_rectangle((1120, 800, 1290, 1180), 70, outline=(226, 186, 116), width=52)  # 取っ手
    for x in (664, 776, 890, 1000):                               # 泡
        d.ellipse((x, 552, x + 170, 726), fill=(244, 240, 230))
    d.rectangle((660, 676, 1120, 730), fill=(244, 240, 230))
    d.ellipse((730, 900, 762, 932), fill=(240, 206, 148))        # 炭酸の気泡
    d.ellipse((900, 1060, 924, 1084), fill=(240, 206, 148))
    d.ellipse((820, 1210, 840, 1230), fill=(240, 206, 148))
    return img


def scene_friday(s):
    """カレンダーの金曜日: 丸をつけたのに、心が動かない"""
    img = vgrad(s, (234, 228, 214), (214, 206, 190))
    img = soft_shadow(img, (360, 1500, 1500, 1580), 60)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((320, 300, 1520, 1540), 40, fill=(246, 243, 235),
                        outline=(120, 118, 114), width=10)
    d.rectangle((328, 308, 1512, 470), fill=(160, 175, 192))     # ヘッダー
    d.ellipse((560, 240, 640, 320), fill=(200, 196, 188))        # 綴じリング
    d.ellipse((1200, 240, 1280, 320), fill=(200, 196, 188))
    for i in range(1, 7):                                         # 縦罫(7列)
        x = 320 + i * (1200 // 7)
        d.line((x, 470, x, 1540), fill=(206, 200, 188), width=8)
    for j in range(1, 5):                                         # 横罫(5行)
        y = 470 + j * (1070 // 5)
        d.line((320, y, 1520, y), fill=(206, 200, 188), width=8)
    fx = 320 + 5 * (1200 // 7) + (1200 // 14)                     # 金曜の列の2行目
    fy = 470 + (1070 // 5) + (1070 // 10)
    d.ellipse((fx - 92, fy - 92, fx + 92, fy + 92), outline=(150, 108, 108), width=18)
    return img


def scene_train(s):
    """いつもの電車: 進んでいるのは電車であって自分ではない"""
    img = vgrad(s, (198, 205, 214), (222, 224, 226))
    d = ImageDraw.Draw(img)
    d.ellipse((160, 200, 560, 380), fill=(232, 234, 236))        # 雲
    d.ellipse((360, 150, 720, 330), fill=(232, 234, 236))
    d.ellipse((1300, 300, 1660, 460), fill=(232, 234, 236))
    d.rectangle((0, 1360, s, s), fill=(178, 182, 188))           # ホーム
    d.line((0, 1360, s, 1360), fill=(226, 200, 120), width=26)   # 黄色い線
    for x in range(80, s, 240):                                   # 点字ブロック
        d.rectangle((x, 1394, x + 150, 1410), fill=(206, 184, 116))
    img = soft_shadow(img, (100, 1280, 1740, 1360), 80, blur=30)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((80, 760, 1760, 1300), 60, fill=(162, 176, 192))   # 車体
    d.rectangle((80, 1120, 1760, 1164), fill=(120, 138, 158))    # 帯
    for x in range(180, 1700, 320):                               # 窓
        d.rounded_rectangle((x, 850, x + 200, 1030), 30, fill=(238, 240, 240))
        d.rounded_rectangle((x, 850, x + 200, 940), 30, fill=(220, 226, 230))
    for x in (480, 1120):                                         # ドア
        d.rectangle((x, 840, x + 26, 1300), fill=(120, 138, 158))
    return img


def scene_talk(s):
    """会議室: 発言はぜんぶ、空中で消える"""
    img = vgrad(s, (236, 231, 219), (218, 212, 198))
    bubbles = [(280, 340, 760, 620), (1020, 500, 1560, 800), (520, 900, 1080, 1200)]
    for x0, y0, x1, y1 in bubbles:
        img = soft_shadow(img, (x0 + 30, y1 - 20, x1 + 30, y1 + 40), 40, blur=26)
    d = ImageDraw.Draw(img)
    for x0, y0, x1, y1 in bubbles:
        d.rounded_rectangle((x0, y0, x1, y1), 90, fill=(246, 243, 235),
                            outline=(128, 126, 122), width=10)
        cx = (x0 + x1) // 2
        d.polygon([(cx - 40, y1 - 4), (cx + 40, y1 - 4), (cx - 10, y1 + 90)],
                  fill=(246, 243, 235), outline=(128, 126, 122))
        cy = (y0 + y1) // 2
        for k in range(3):                                        # 中身は「…」だけ
            dot = cx - 90 + k * 90
            d.ellipse((dot - 18, cy - 18, dot + 18, cy + 18), fill=(128, 126, 122))
    return img


def scene_wait(s):
    """待合室: 呼ばれる予定のない番号を持って座っている"""
    img = vgrad(s, (226, 226, 222), (208, 208, 204))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 1380, s, s), fill=(192, 192, 188))           # 床
    d.line((0, 1380, s, 1380), fill=(170, 170, 166), width=6)
    for x in range(140, 1600, 420):                               # 床の反射
        d.rectangle((x + 20, 1420, x + 320, 1440), fill=(200, 200, 196))
    for x in range(140, 1600, 420):                               # 並んだ椅子
        img = soft_shadow(img, (x - 20, 1350, x + 340, 1420), 50, blur=24)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((x, 950, x + 300, 1110), 30, fill=(164, 178, 194))   # 背
        d.rounded_rectangle((x, 1090, x + 300, 1215), 30, fill=(140, 155, 174))  # 座面
        d.rectangle((x + 30, 1215, x + 62, 1380), fill=(96, 98, 102))            # 脚
        d.rectangle((x + 238, 1215, x + 270, 1380), fill=(96, 98, 102))
    d.ellipse((1440, 210, 1700, 470), fill=(246, 243, 235))      # 壁の時計
    d.ellipse((1440, 210, 1700, 470), outline=(110, 110, 112), width=14)
    d.line((1570, 340, 1570, 252), fill=(110, 110, 112), width=16)  # 針
    d.line((1570, 340, 1634, 372), fill=(110, 110, 112), width=16)
    d.rounded_rectangle((240, 300, 760, 480), 30, fill=(246, 243, 235),
                        outline=(150, 148, 144), width=10)       # 案内板(空白)
    return img


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

    # 情景イラストを描いて質感を足し、角丸に切り抜く
    scene = finish(SCENES[slug](bw).convert("RGB"), bw)
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
    # 文字の後ろにほんのり白を敷いて絵と喧嘩させない
    halo = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    for dx in (-3, 0, 3):
        for dy in (-3, 0, 3):
            hd.text((CANVAS // 2 + gap // 2 + dx, y_top + dy), lines[0],
                    font=font, fill=(247, 245, 240, 255), direction="ttb", anchor="mt")
            hd.text((CANVAS // 2 - gap // 2 + dx, y_top + drop + dy), lines[1],
                    font=font, fill=(247, 245, 240, 255), direction="ttb", anchor="mt")
    halo = halo.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img, halo)
    # 縦書きは右列から読むので、1句目を右・2句目を左に置く
    d.text((CANVAS // 2 + gap // 2, y_top),
           lines[0], font=font, fill=COLOR, direction="ttb", anchor="mt")
    d.text((CANVAS // 2 - gap // 2, y_top + drop),
           lines[1], font=font, fill=COLOR, direction="ttb", anchor="mt")
    d.rounded_rectangle((bx, by, bx + bw, by + bh), BASE_RADIUS,
                        outline=BASE_BORDER, width=BASE_BORDER_W)
    img = Image.alpha_composite(img, top)

    # 文字ハロのボカシが台座の外へ漏れた分を切り落とす
    outer = Image.new("L", (CANVAS, CANVAS), 0)
    ImageDraw.Draw(outer).rounded_rectangle(
        (bx, by, bx + bw, by + bh), BASE_RADIUS, fill=255
    )
    r, g, b, a = img.split()
    a = Image.composite(a, Image.new("L", (CANVAS, CANVAS), 0), outer)
    img = Image.merge("RGBA", (r, g, b, a))

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
