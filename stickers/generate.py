# -*- coding: utf-8 -*-
"""「〜ても、シリーズ」ステッカー入稿データ生成スクリプト

SUZURI入稿用の透過PNG(2000x2000)を stickers/png/ に出力する。
デザインは角丸台座のくすみブルー版: 全種共通の角丸長方形ベースに
2行組みの文字。1枚ものなのでカットラインは外周1本になる。
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
MAX_LINE_WIDTH = 1460  # 文字の最大幅(台座の内側に収める)
MAX_FONT_SIZE = 300    # 短い行が間延びしないよう上限を設ける
LINE_SPACING = 1.30    # 行間(脱力感を出すためやや広め)
COLOR = (88, 97, 110, 255)  # スレートグレー。ブルー台座に沈まない濃さにする

# 台座: くすみブルーの角丸長方形(シリーズ共通)
BASE_SIZE = (1840, 1280)
BASE_RADIUS = 140
BASE_FILL = (178, 190, 202, 255)    # くすみブルー
BASE_BORDER = (148, 160, 174, 255)  # うっすら枠線
BASE_BORDER_W = 8

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
    # 読点で2行に割る。読点は1行目の末尾に残す(諦めの「間」を作る)
    head, _, tail = text.partition("、")
    return [head + "、", tail]


def fit_font_size(lines):
    size = MAX_FONT_SIZE
    while size > 10:
        font = load_font(size)
        if max(font.getbbox(line)[2] for line in lines) <= MAX_LINE_WIDTH:
            return size
        size -= 4
    return size


def render(slug, text):
    lines = split_lines(text)
    size = fit_font_size(lines)
    font = load_font(size)

    img = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    bw, bh = BASE_SIZE
    bx, by = (CANVAS - bw) // 2, (CANVAS - bh) // 2
    draw.rounded_rectangle(
        (bx, by, bx + bw, by + bh),
        radius=BASE_RADIUS,
        fill=BASE_FILL,
        outline=BASE_BORDER,
        width=BASE_BORDER_W,
    )

    ascent, descent = font.getmetrics()
    line_height = int((ascent + descent) * LINE_SPACING)
    total_height = line_height * (len(lines) - 1) + ascent + descent
    y = (CANVAS - total_height) // 2

    for line in lines:
        w = draw.textlength(line, font=font)
        draw.text(((CANVAS - w) // 2, y), line, font=font, fill=COLOR)
        y += line_height

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
    sheet = Image.new("RGB", (cell * cols, cell * rows), (222, 220, 215))
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
