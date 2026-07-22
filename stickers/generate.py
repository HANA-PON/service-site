# -*- coding: utf-8 -*-
"""「〜ても、シリーズ」ステッカー入稿データ生成スクリプト

SUZURI入稿用の透過PNG(2000x2000)を stickers/png/ に出力する。
デザインはマスキングテープ風: 1行=1本のテープ(両端ちぎれ)を上下に
少し重ねて貼った見た目。重ねることでカットラインが1枚につながる。
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
MAX_LINE_WIDTH = 1380  # 文字の最大幅(テープの余白とちぎれ分を除く)
MAX_FONT_SIZE = 280    # 短い行が間延びしないよう上限を設ける
COLOR = (110, 110, 110, 255)  # グレー1色。色数を増やすと脱力が死ぬ

TAPE_FILL = (243, 240, 232, 255)    # 生成り(マステの紙色)
TAPE_BORDER = (208, 204, 194, 255)  # うっすら輪郭(白地で消えないように)
TAPE_BORDER_W = 6
TAPE_PAD_X = 110       # テープ端から文字までの余白
TAPE_HEIGHT_EM = 1.55  # フォントサイズに対するテープの高さ
TEAR_AMP = 26          # ちぎれのギザギザの深さ
TEAR_TEETH = 6         # ギザギザの山の数
OVERLAP_RATIO = 0.18   # 上下テープの重なり(切り離れないための連結部)
LINE_OFFSET_X = 55     # 上下テープの左右ズレ(手で貼った感)
ANGLES = (-1.3, 0.9)   # 上下テープの微妙な傾き(度)

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


def tear_edge(x_base, y_top, y_bottom, direction, phase):
    """テープ端のちぎれ(ギザギザ)の頂点列を上から下へ返す"""
    pts = []
    steps = TEAR_TEETH * 2
    for i in range(steps + 1):
        y = y_top + (y_bottom - y_top) * i / steps
        # 固定パターンの疑似乱数(再生成しても同じ形になる)
        wob = math.sin(phase + i * 2.1) * 0.5 + 0.5
        depth = TEAR_AMP * (0.35 + 0.65 * wob) if i % 2 else 0
        pts.append((x_base + direction * depth, y))
    return pts


def tape_strip(line, font, size, phase):
    """1行ぶんのテープ(ちぎれ両端)を透過レイヤーで返す"""
    text_w = int(font.getbbox(line)[2])
    strip_h = int(size * TAPE_HEIGHT_EM)
    strip_w = text_w + TAPE_PAD_X * 2 + TEAR_AMP * 2
    layer = Image.new("RGBA", (strip_w, strip_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    xl, xr = TEAR_AMP, strip_w - TEAR_AMP
    yt, yb = TAPE_BORDER_W, strip_h - TAPE_BORDER_W
    right = tear_edge(xr, yt, yb, +1, phase)
    left = tear_edge(xl, yb, yt, -1, phase + 3.7)
    poly = [(xl, yt), (xr, yt)] + right + [(xr, yb), (xl, yb)] + left
    draw.polygon(poly, fill=TAPE_FILL, outline=TAPE_BORDER, width=TAPE_BORDER_W)

    ascent, descent = font.getmetrics()
    ty = (strip_h - ascent - descent) // 2
    draw.text(((strip_w - text_w) // 2, ty), line, font=font, fill=COLOR)
    return layer


def render(slug, text):
    lines = split_lines(text)
    size = fit_font_size(lines)
    font = load_font(size)

    img = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))

    strips = []
    for i, line in enumerate(lines):
        layer = tape_strip(line, font, size, phase=1.3 + i * 2.9)
        layer = layer.rotate(ANGLES[i], expand=True, resample=Image.BICUBIC)
        strips.append(layer)

    strip_h = int(size * TAPE_HEIGHT_EM)
    overlap = int(strip_h * OVERLAP_RATIO)
    total_h = strips[0].height + strips[1].height - overlap - TEAR_AMP
    top = (CANVAS - total_h) // 2
    offsets = (-LINE_OFFSET_X, LINE_OFFSET_X)
    y = top
    for layer, dx in zip(strips, offsets):
        x = (CANVAS - layer.width) // 2 + dx
        img.alpha_composite(layer, (x, y))
        y += layer.height - overlap

    # 回転補間で生じるごく薄いノイズ画素を落とす
    # (残すとSUZURI側のカットライン自動生成が誤検出しかねない)
    r, g, b, a = img.split()
    a = a.point(lambda v: 0 if v < 24 else v)
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
    # ステッカーの輪郭(カットライン)が見えるよう、テープより暗い背景にする
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
