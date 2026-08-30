#!/usr/bin/env python3
"""30枚のピン画像（1000x1500px）を生成する。

canva_bulk_30pins.csv の文言を、テンプレートA/B/Cごとのデザインに流し込み、
ヘッドレスChromiumでPNGに書き出す。文章を直したいときは build_pins.py を
編集して再実行してから、このスクリプトを実行する。

  python3 content/slim-storage-jp/build_pins.py
  python3 content/slim-storage-jp/build_pin_images.py
"""
import csv, io, html, pathlib, sys

HERE = pathlib.Path(__file__).parent
OUT = HERE / "pins"
W, H = 1000, 1500          # Pinterest推奨の 2:3

FONT = ("'Hiragino Sans','Hiragino Kaku Gothic ProN','Noto Sans JP',"
        "'IPAPGothic','IPAGothic','Yu Gothic',Meiryo,sans-serif")
INK, PAPER, ACCENT, DARK = "#26292B", "#F5F6F4", "#6E8A94", "#566E77"
BRAND = "すきま収納ノート"


def css():
    return f"""
  *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
  html,body{{width:{W}px;height:{H}px}}
  body{{font-family:{FONT};background:{PAPER};color:{INK};
       -webkit-font-smoothing:antialiased}}
  .pin{{width:{W}px;height:{H}px;position:relative;display:flex;
       flex-direction:column;overflow:hidden}}
  .size{{font-size:150px;font-weight:800;line-height:1;letter-spacing:-.03em}}
  .main{{font-size:74px;font-weight:800;line-height:1.34;letter-spacing:-.01em}}
  .top{{font-size:34px;font-weight:700;letter-spacing:.12em}}
  .prod{{font-size:30px;line-height:1.6;opacity:.9}}
  .cta{{display:flex;align-items:center;justify-content:space-between;
       padding:36px 64px;font-size:31px;font-weight:700}}
  .brand{{font-size:26px;letter-spacing:.1em;opacity:.75;font-weight:400}}
  .pad{{padding:0 64px}}
"""


# ---- テンプレートごとのレイアウト -------------------------------------------
def tpl_a(d):   # Before/After：上下2分割で変化を見せる
    return f"""
  <div class="pin">
    <div style="flex:1;background:#8E8B84;display:flex;flex-direction:column;
                justify-content:center;padding:0 64px;color:#fff">
      <div class="top" style="opacity:.85;margin-bottom:18px">BEFORE</div>
      <div style="font-size:52px;font-weight:700;line-height:1.4">
        {d['place']}の{d['size']}<br>使えていなかった</div>
    </div>
    <div style="flex:1.25;background:{PAPER};display:flex;flex-direction:column;
                justify-content:center;padding:0 64px;position:relative">
      <div class="top" style="color:{DARK};margin-bottom:22px">AFTER</div>
      <div class="main" style="color:{INK}">{d['main']}</div>
      <div style="position:absolute;right:56px;top:-84px;background:{ACCENT};color:#fff;
                  border-radius:999px;width:168px;height:168px;display:flex;
                  align-items:center;justify-content:center;font-size:46px;
                  font-weight:800;box-shadow:0 8px 28px rgba(0,0,0,.18)">{d['size']}</div>
    </div>
    <div class="cta" style="background:{DARK};color:#fff">
      <span>{d['cta']}</span><span class="brand">{BRAND}</span></div>
  </div>"""


def tpl_b(d):   # 要点まとめ：数字を主役に、商品名と決め手を添える
    return f"""
  <div class="pin" style="background:{PAPER}">
    <div style="flex:1;display:flex;flex-direction:column;justify-content:center;
                padding:0 64px">
      <div class="top" style="color:{DARK}">{d['top']}</div>
      <div class="size" style="color:{ACCENT};margin-top:34px">{d['size']}</div>
      <div style="width:132px;height:9px;background:{INK};margin:38px 0 44px"></div>
      <div class="main">{d['main']}</div>
      <div class="prod" style="border-top:2px solid #D9DBD7;padding-top:30px;
                               margin-top:62px">{d['product']}</div>
    </div>
    <div class="cta" style="background:{INK};color:#fff">
      <span>{d['cta']}</span><span class="brand">{BRAND}</span></div>
  </div>"""


def tpl_c(d):   # 悩み解決：一行で刺す
    return f"""
  <div class="pin" style="background:{DARK};color:#fff">
    <div style="flex:1;display:flex;flex-direction:column;justify-content:center;
                padding:0 64px">
      <div class="top" style="opacity:.8">{d['top']}</div>
      <div class="main" style="font-size:88px;margin-top:46px">「{d['main']}」</div>
      <div style="margin-top:56px;display:flex;align-items:center;gap:26px">
        <span style="background:#fff;color:{DARK};border-radius:999px;padding:18px 40px;
                     font-size:44px;font-weight:800">{d['size']}</span>
        <span style="font-size:31px;opacity:.9">なら、置けます</span>
      </div>
      <div class="prod" style="margin-top:70px;opacity:.75">{d['product']}</div>
    </div>
    <div class="cta" style="background:#fff;color:{INK}">
      <span>{d['cta']}</span><span class="brand">{BRAND}</span></div>
  </div>"""


LAYOUTS = {"A Before/After": tpl_a, "B 5選まとめ": tpl_b, "C 悩み解決": tpl_c}


def page(d):
    body = LAYOUTS[d["template"]](d)
    return (f'<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">'
            f"<style>{css()}</style></head><body>{body}</body></html>")


def main():
    rows = list(csv.DictReader(io.open(HERE / "canva_bulk_30pins.csv", encoding="utf-8-sig")))
    pins = list(csv.DictReader(io.open(HERE / "pinterest_30pins.csv", encoding="utf-8-sig")))
    OUT.mkdir(exist_ok=True)
    e = html.escape
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("playwright が必要です: pip install playwright")

    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
        pg = b.new_page(viewport={"width": W, "height": H})
        for row, pin in zip(rows, pins):
            d = {"template": row["Template"], "size": e(row["Size"]),
                 "top": e(row["OverlayTop"]), "main": e(row["OverlayMain"]),
                 "product": e(row["Product"]), "cta": e(row["CTA"]),
                 "place": e(row["Place"])}
            pg.set_content(page(d), wait_until="load")
            name = f"pin-{int(pin['pin_no']):02d}-{pin['blog_slug']}-{row['Template'][0]}.png"
            pg.screenshot(path=str(OUT / name), clip={"x": 0, "y": 0, "width": W, "height": H})
        b.close()
    print(f"生成: {len(rows)}枚 -> {OUT.relative_to(HERE.parents[1])}/")


if __name__ == "__main__":
    main()
