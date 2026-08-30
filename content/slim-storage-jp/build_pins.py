#!/usr/bin/env python3
"""30ピンのタイトル・説明文を、LPの内容に合わせて生成する。

pinterest_30pins.csv / canva_bulk_30pins.csv / schedule_30days.csv を書き出す。
商品や記事を変えたら PINS を直して再実行する。

  python3 content/slim-storage-jp/build_pins.py
"""
import csv, io, pathlib, datetime

HERE = pathlib.Path(__file__).parent
BASE_URL = "https://hana-pon.github.io/service-site/jp/"
CTA = "詳しくはブログで ▶︎"

BOARDS = {                       # テンプレート -> 投稿先ボード
    "A Before/After": "6畳ワンルーム収納アイデア",
    "B 5選まとめ":     "賃貸OK！穴あけ不要収納",
    "C 悩み解決":      "隙間を活用する神家具5選",
}

# 商品ごとの素材。size=画像に大きく出す数字、place=設置場所、
# hook=Cで刺す一行、win=Aで見せる変化、point=Bで並べる要点
PRODUCTS = [
 dict(slug="slim-storage-1", name="SPACEKEEPER 22cm 4段", size="22cm", place="冷蔵庫横",
      hook="この22cm、ずっと諦めてた", win="床置きの調味料が消えた",
      point="4段で調味料もストックも分けられる", tags=["隙間収納","キッチン収納","一人暮らし"]),
 dict(slug="slim-storage-2", name="山崎実業 スリムトイレラック", size="13cm", place="トイレの横",
      hook="トイレの13cm、使えます", win="床のストックがゼロになった",
      point="奥行きを使って縦に積める", tags=["トイレ収納","隙間収納","賃貸暮らし"]),
 dict(slug="slim-storage-3", name="TORIBIO 13cm 5段 天板付き", size="13cm", place="冷蔵庫横",
      hook="収納なのに、部屋が良くなる", win="キッチンがカフェっぽくなった",
      point="木の天板だけ見せる場所にできる", tags=["キッチン収納","隙間収納","インテリア"]),
 dict(slug="slim-storage-4", name="アイリスオーヤマ 天板付きワゴン", size="24cm", place="洗濯機の横",
      hook="洗面所の床置き、やめられます", win="洗剤とタオルに住所ができた",
      point="天板に洗剤を出したまま置ける", tags=["洗面所収納","ランドリー収納","隙間収納"]),
 dict(slug="slim-storage-5", name="ぼん家具 木製ワゴン", size="20cm", place="押入れの中",
      hook="押入れの奥、死んでませんか", win="奥の物に手が届くようになった",
      point="キャスターで手前に引き出せる", tags=["押入れ収納","クローゼット収納","収納アイデア"]),
 dict(slug="slim-storage-6", name="山崎実業 tower スリムワゴン", size="13cm", place="キッチンの隙間",
      hook="置いても部屋がうるさくならない", win="物が増えたのに散らかって見えない",
      point="本体完成品でキャスターを付けるだけ", tags=["tower","山崎実業","隙間収納"]),
 dict(slug="slim-storage-7", name="Goowin スリムワゴン", size="12cm", place="洗面台の横",
      hook="洗面台の上、何も置かない日", win="朝の身支度が1分短くなった",
      point="スキンケアを段ごとに分けられる", tags=["洗面所収納","美容収納","隙間収納"]),
 dict(slug="slim-storage-8", name="JEJ スリムチェスト 5段", size="17cm", place="キッチンの隙間",
      hook="組み立てが苦手でも大丈夫", win="届いたその日に片付いた",
      point="日本製の完成品・工具いらず", tags=["日本製","隙間収納","一人暮らし"]),
 dict(slug="slim-storage-9", name="天馬 スキピタ 5段", size="17cm×140cm", place="キッチン・洗面所",
      hook="床は増やさず、収納だけ増やす", win="同じ床面積で収納が倍になった",
      point="幅17cmのまま高さ140cmまで使える", tags=["縦収納","隙間収納","6畳"]),
 dict(slug="slim-storage-10", name="SVOHZAV スリムワゴン 4段", size="18cm", place="洗面所・トイレ",
      hook="まず1台、試してみる", win="この隙間が使えると分かった",
      point="よくある18cm幅・別の部屋にも回せる", tags=["隙間収納","収納アイデア","賃貸OK"]),
]


def pin_text(p, template):
    """テンプレートごとに、見出し・説明文・画像に載せる文字を作り分ける。"""
    tags = " ".join("#" + t for t in p["tags"])
    if template == "A Before/After":
        return dict(
            title=f"{p['place']}の{p['size']}が収納庫に変わった｜{p['name']}",
            desc=(f"{p['place']}の使えていなかった{p['size']}に置いたら、{p['win']}。"
                  f"賃貸OK・穴あけ不要です。サイズの測り方と設置のコツはブログにまとめました→ {tags}"),
            overlay_top="before → after",
            overlay_main=p["win"],
        )
    if template == "B 5選まとめ":
        return dict(
            title=f"{p['size']}の隙間に置ける{p['name']}｜狭い部屋の収納アイデア",
            desc=(f"{p['name']}（{p['size']}）を{p['place']}に。{p['point']}のが決め手でした。"
                  f"買う前に測る3か所もブログに書いています→ {tags}"),
            overlay_top=f"{p['place']}に置ける",
            overlay_main=p["point"],
        )
    return dict(
        title=f"{p['hook']}｜{p['size']}で{p['place']}を片付ける",
        desc=(f"{p['hook']}——{p['place']}の{p['size']}は、まだ使えます。"
              f"{p['point']}。賃貸でもそのまま置けます。詳しくはブログで→ {tags}"),
        overlay_top=p["place"],
        overlay_main=p["hook"],
    )


def build():
    start = datetime.date(2026, 8, 28)
    times = ["21:00", "21:30", "22:00"]
    pins, canva, sched = [], [], []
    n = 0
    for day, p in enumerate(PRODUCTS):
        for slot, template in enumerate(BOARDS):
            n += 1
            t = pin_text(p, template)
            date = (start + datetime.timedelta(days=day)).isoformat()
            pins.append({
                "pin_no": n, "product": p["name"], "template": template,
                "board": BOARDS[template], "title": t["title"], "description": t["desc"],
                "blog_slug": p["slug"], "blog_url": BASE_URL + p["slug"] + ".html",
                "cta": CTA, "post_date": date, "post_time_JST": times[slot],
            })
            canva.append({
                "Title": t["title"], "Product": p["name"], "Template": template,
                "Size": p["size"], "OverlayTop": t["overlay_top"],
                "OverlayMain": t["overlay_main"], "CTA": CTA, "Desc": t["desc"],
            })
            sched.append({
                "date": date, "time_JST": times[slot], "pin_no": n, "product": p["name"],
                "template": template, "board": BOARDS[template], "title": t["title"],
                "action": "投稿", "blog_url": BASE_URL + p["slug"] + ".html",
            })

    for name, rows in (("pinterest_30pins.csv", pins),
                       ("canva_bulk_30pins.csv", canva),
                       ("schedule_30days.csv", sched)):
        with io.open(HERE / name, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)
        print(f"{name}: {len(rows)}行")
    return pins


if __name__ == "__main__":
    build()
