#!/usr/bin/env python3
"""投稿ダッシュボード（docs/jp/pins/index.html）を作る。

30ピンぶんの「画像・タイトル・説明文・リンク先・ボード・日時」を1ページに並べ、
コピーボタンを付ける。zipを開かなくてもブラウザだけで投稿できるようにするため。

  python3 content/slim-storage-jp/build_dashboard.py
"""
import csv, io, html, pathlib

HERE = pathlib.Path(__file__).parent
OUT = pathlib.Path(__file__).parents[2] / "docs" / "jp" / "pins" / "index.html"
VERIFY = "76b98bcf2847d663e1bc4067be4a20bd"

CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#F5F6F4;--card:#fff;--ink:#35393B;--charcoal:#26292B;
      --accent:#6E8A94;--accent-dk:#566E77;--line:#E1E2DE;--muted:#767A78}
body{font-family:'Hiragino Sans','Noto Sans JP','Yu Gothic',Meiryo,sans-serif;
     background:var(--bg);color:var(--ink);line-height:1.75;font-size:15px}
.wrap{max-width:1040px;margin:0 auto;padding:0 20px 64px}
header{text-align:center;padding:44px 20px 30px;border-bottom:1px solid var(--line);
       margin-bottom:28px}
h1{font-size:1.5rem;font-weight:700;color:var(--charcoal);margin-bottom:10px}
header p{color:var(--muted);font-size:.92rem}
.how{background:var(--card);border:1px solid var(--line);border-radius:8px;
     padding:20px 24px;margin-bottom:30px;font-size:.92rem}
.how b{color:var(--charcoal)}
.how ol{margin:10px 0 0 1.3em}.how li{margin-bottom:4px}
.warn{color:#8C4A3F;font-weight:700}
.day{font-size:1.02rem;font-weight:700;color:var(--charcoal);
     margin:34px 0 14px;padding-left:12px;border-left:4px solid var(--accent)}
.pin{background:var(--card);border:1px solid var(--line);border-radius:8px;
     padding:18px;margin-bottom:16px;display:flex;gap:20px;align-items:flex-start}
.pin img{width:150px;flex-shrink:0;border-radius:5px;border:1px solid var(--line)}
.meta{flex:1;min-width:0}
.tags{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:10px;
      font-size:.8rem;color:var(--muted)}
.chip{background:var(--bg);border:1px solid var(--line);border-radius:999px;
      padding:3px 12px}
.chip.time{background:var(--accent);color:#fff;border-color:var(--accent);font-weight:700}
.row{margin-bottom:9px}
.lbl{font-size:.74rem;letter-spacing:.08em;color:var(--muted);display:block;
     margin-bottom:2px}
.val{word-break:break-all}
button{font:inherit;font-size:.78rem;background:var(--accent);color:#fff;border:0;
       border-radius:5px;padding:5px 13px;cursor:pointer;margin-left:6px;
       vertical-align:middle;white-space:nowrap}
button:hover{background:var(--accent-dk)}
button.done{background:#5B7A55}
a.dl{display:inline-block;margin-top:8px;font-size:.8rem;color:var(--accent-dk)}
footer{text-align:center;color:var(--muted);font-size:.8rem;padding:30px 20px}
@media(max-width:640px){.pin{flex-direction:column}.pin img{width:120px}}
"""

JS = """
function cp(btn,id){
  const t=document.getElementById(id).textContent;
  navigator.clipboard.writeText(t).then(()=>{
    const o=btn.textContent;btn.textContent='コピーしました';btn.classList.add('done');
    setTimeout(()=>{btn.textContent=o;btn.classList.remove('done')},1400);
  });
}
"""


def main():
    pins = list(csv.DictReader(io.open(HERE / "pinterest_30pins.csv", encoding="utf-8-sig")))
    e = html.escape
    parts, last_date = [], None
    for p in pins:
        n = int(p["pin_no"])
        img = f"pin-{n:02d}-{p['blog_slug']}-{p['template'][0]}.png"
        if p["post_date"] != last_date:
            last_date = p["post_date"]
            parts.append(f'<div class="day">{e(last_date)}（3枚）</div>')
        parts.append(f"""
      <div class="pin">
        <img src="{img}" alt="ピン{n}のプレビュー" loading="lazy">
        <div class="meta">
          <div class="tags">
            <span class="chip time">{e(p['post_time_JST'])}</span>
            <span class="chip">{e(p['board'])}</span>
            <span class="chip">{e(p['template'])}</span>
            <span>#{n}</span>
          </div>
          <div class="row"><span class="lbl">タイトル</span>
            <span class="val" id="t{n}">{e(p['title'])}</span>
            <button onclick="cp(this,'t{n}')">コピー</button></div>
          <div class="row"><span class="lbl">説明文</span>
            <span class="val" id="d{n}">{e(p['description'])}</span>
            <button onclick="cp(this,'d{n}')">コピー</button></div>
          <div class="row"><span class="lbl">リンク先（必ず入れる）</span>
            <span class="val" id="u{n}">{e(p['blog_url'])}</span>
            <button onclick="cp(this,'u{n}')">コピー</button></div>
          <a class="dl" href="{img}" download>画像をダウンロード（{img}）</a>
        </div>
      </div>""")

    page = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="p:domain_verify" content="{VERIFY}"/>
<meta name="robots" content="noindex">
<title>ピン投稿ダッシュボード | すきま収納ノート</title>
<style>{CSS}</style>
</head>
<body>
<header>
  <h1>ピン投稿ダッシュボード</h1>
  <p>30枚ぶんの画像・タイトル・説明文・リンク先をまとめたページです。<br>
     zipを開かず、ここから直接コピーして投稿できます。</p>
</header>
<div class="wrap">
  <div class="how">
    <b>投稿のしかた</b>
    <ol>
      <li>画像を右クリック →「画像を保存」（または「画像をダウンロード」リンク）</li>
      <li>Pinterestで「＋」→「ピンを作成」→ 保存した画像をアップロード</li>
      <li>タイトル・説明文・<b>リンク先</b>を、下のコピーボタンで貼り付ける</li>
      <li>「ボード」の欄に書いてあるボードを選んで公開</li>
    </ol>
    <p style="margin-top:10px"><span class="warn">リンク先を空欄のまま公開しないでください。</span>
       ここが空だと、見てもらってもブログに来てもらえず、収益になりません。</p>
    <p style="margin-top:6px">自分のピンは自分でクリックしないでください（数字が狂います）。
       確認は別のブラウザかスマホで。</p>
  </div>
{"".join(parts)}
</div>
<footer>1日3枚・21:00 / 21:30 / 22:00 JST ・ すきま収納ノート</footer>
<script>{JS}</script>
</body>
</html>
"""
    OUT.write_text(page, encoding="utf-8")
    print(f"生成: {OUT.relative_to(pathlib.Path(__file__).parents[2])}（{len(pins)}件）")


if __name__ == "__main__":
    main()
