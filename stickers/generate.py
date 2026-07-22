# -*- coding: utf-8 -*-
"""「〜ても、シリーズ」ステッカー入稿データ生成スクリプト

SUZURI入稿用の透過PNG(2000x2000)を stickers/png/ に出力する。
デザインは縦書き版: 生成り色の縦長角丸台座に、右列→左列の
2列組みで縦書き(左列は少し下げて句のリズムを作る)。
縦書きの組版(句読点・拗促音の位置)はlibraqm+フォントの
縦書き用グリフに任せる。1枚ものなのでカットラインは外周1本。
フォント: Zen Maru Gothic Light (SIL Open Font License 1.1 / 商用利用可)

使い方:
    python3 stickers/generate.py
"""
import os
import urllib.request

from PIL import Image, ImageDraw, ImageFont

FONT_URL = (
    "https://fonts.gstatic.com/s/zenmarugothic/v19/"
    "o-0XIpIxzW5b-RxT-6A8jWAtCp-cQWpCPA.ttf"
)
FONT_CACHE = os.path.join(os.path.dirname(__file__), "ZenMaruGothic-Light.ttf")

CANVAS = 2000          # SUZURI推奨の大判サイズ
COLOR = (74, 74, 74, 255)  # 濃いめのグレー1色

# 台座: 生成りの縦長角丸長方形(シリーズ共通)
BASE_SIZE = (1280, 1840)
BASE_RADIUS = 140
BASE_FILL = (247, 245, 240, 255)    # 生成り(真っ白より脱力する)
BASE_BORDER = (201, 197, 188, 255)  # うっすら枠線
BASE_BORDER_W = 8

PAD_Y = 160            # 台座の上下端から文字までの最低余白
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

    img = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    size = fit_font_size(draw, lines)
    font = load_font(size)
    drop = int(size * DROP_EM)

    bw, bh = BASE_SIZE
    bx, by = (CANVAS - bw) // 2, (CANVAS - bh) // 2
    draw.rounded_rectangle(
        (bx, by, bx + bw, by + bh),
        radius=BASE_RADIUS,
        fill=BASE_FILL,
        outline=BASE_BORDER,
        width=BASE_BORDER_W,
    )

    # 縦書きは右列から読むので、1句目を右・2句目を左に置く
    gap = int(size * COL_GAP_EM)
    h1 = column_height(draw, lines[0], font)
    h2 = column_height(draw, lines[1], font) + drop
    y_top = (CANVAS - max(h1, h2)) // 2
    draw.text(
        (CANVAS // 2 + gap // 2, y_top),
        lines[0], font=font, fill=COLOR, direction="ttb", anchor="mt",
    )
    draw.text(
        (CANVAS // 2 - gap // 2, y_top + drop),
        lines[1], font=font, fill=COLOR, direction="ttb", anchor="mt",
    )

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
    # ステッカーの輪郭(カットライン)が見えるよう、台座より暗い背景にする
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
