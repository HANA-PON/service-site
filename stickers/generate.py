# -*- coding: utf-8 -*-
"""「〜ても、シリーズ」ステッカー入稿データ生成スクリプト

SUZURI入稿用の透過PNG(2000x2000)を stickers/png/ に出力する。
デザインは正方形の付箋風: 生成り色の正方形に右下の紙めくれ、
全体をわずかに傾けて「手で貼った」感を出す。1枚ものなので
カットラインは外周1本になる。
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
COLOR = (110, 110, 110, 255)  # グレー1色。色数を増やすと脱力が死ぬ

NOTE_SIZE = 1560       # 付箋の一辺
NOTE_FILL = (245, 242, 234, 255)    # 生成り(付箋の紙色)
NOTE_BORDER = (208, 204, 194, 255)  # うっすら輪郭(白地で消えないように)
NOTE_BORDER_W = 6
FOLD_SIZE = 250        # 右下の紙めくれの大きさ
FOLD_FILL = (226, 222, 211, 255)    # めくれの裏面(本体よりやや暗い)
NOTE_ANGLE = -1.6      # 全体の傾き(手で貼った感)

PAD_X = 150            # 付箋の端から文字までの余白
MAX_FONT_SIZE = 260    # 短い行が間延びしないよう上限を設ける
LINE_SPACING = 1.35    # 行間(脱力感を出すためやや広め)

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
    max_width = NOTE_SIZE - PAD_X * 2
    size = MAX_FONT_SIZE
    while size > 10:
        font = load_font(size)
        if max(font.getbbox(line)[2] for line in lines) <= max_width:
            return size
        size -= 4
    return size


def fusen_note(lines, font):
    """付箋(右下めくれつき)を透過レイヤーで返す"""
    n = NOTE_SIZE
    layer = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    b = NOTE_BORDER_W
    f = FOLD_SIZE
    # 右下の角を三角に落とした本体
    body = [
        (b, b), (n - b, b),
        (n - b, n - b - f), (n - b - f, n - b),
        (b, n - b),
    ]
    draw.polygon(body, fill=NOTE_FILL, outline=NOTE_BORDER, width=b)
    # めくれた紙の裏面
    fold = [(n - b - f, n - b), (n - b, n - b - f), (n - b - f, n - b - f)]
    draw.polygon(fold, fill=FOLD_FILL, outline=NOTE_BORDER, width=b)

    ascent, descent = font.getmetrics()
    line_height = int((ascent + descent) * LINE_SPACING)
    total_height = line_height * (len(lines) - 1) + ascent + descent
    y = (n - total_height) // 2
    for line in lines:
        w = draw.textlength(line, font=font)
        draw.text(((n - w) // 2, y), line, font=font, fill=COLOR)
        y += line_height
    return layer


def render(slug, text):
    lines = split_lines(text)
    size = fit_font_size(lines)
    font = load_font(size)

    note = fusen_note(lines, font)
    note = note.rotate(NOTE_ANGLE, expand=True, resample=Image.BICUBIC)

    img = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    img.alpha_composite(
        note, ((CANVAS - note.width) // 2, (CANVAS - note.height) // 2)
    )

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
    # ステッカーの輪郭(カットライン)が見えるよう、付箋より暗い背景にする
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
