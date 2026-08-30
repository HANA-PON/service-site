# 隙間収納キャンペーン（slim-storage-jp）

Pinterest → ブログLP → Amazon の導線用データ一式。
狙うジャンル：**6畳ワンルーム／賃貸OKの隙間収納**。

## 運用ルール
- Pinterest規約：ピンにアフィリリンクを直貼りしない。**必ずブログLP経由**
- Amazon規約：**価格表記NG**、商品画像の転載NG、クッキーは24時間
- 1日3ピン／1ピン1商品／CTAは「詳しくはブログで ▶︎」
- LPのAmazonリンクは1ページ1つまで、`rel="nofollow sponsored"`
- LP末尾に開示文：`Amazonのアソシエイトとして、適格販売により収入を得ています。`

## ファイル
| ファイル | 中身 |
|---|---|
| `pinterest_30pins.csv` | 30ピンの一覧（商品・テンプレ・ボード・タイトル・説明文・LPスラッグ・投稿日） |
| `schedule_30days.csv` | 10日分の投稿スケジュール（JST 21:00 / 21:30 / 22:00） |
| `pinterest_schedule.ics` | 上記をカレンダーに取り込む用 |
| `canva_bulk_30pins.csv` | Canva「一括作成」に読み込む用 |
| `blog_10_articles.csv` | LP10本の設計（スラッグ・タイトル・SEOキーワード・H2構成・Amazon検索語） |

## 構成
10商品 × 3テンプレ（A Before/After・B 5選まとめ・C 悩み解決）= 30ピン。
ピンの `blog_slug`（`slim-storage-1` 〜 `slim-storage-10`）が、対応するLPのファイル名になる。

## 元データからの修正点
`pinterest_30pins.csv` の `post_date` に **存在しない日付（2026-08-32〜2026-08-36）** が入っていたため、
`pinterest_schedule.ics` と `schedule_30days.csv` を正として **2026-08-28 開始**で振り直した。
現在は3ファイルの pin_no・日付・タイトルが一致している。

## LPとピンのリンク先URL
LP本体は `docs/jp/`（GitHub Pagesの公開元が `main / docs` のため、URLは `/jp/` 配下）。
文面を直したいときは `build_lp.py` の `ARTICLES` を編集して再実行する：

```
python3 content/slim-storage-jp/build_lp.py
```

| ピンのblog_slug | 商品 | ピンに貼るURL |
|---|---|---|
| `slim-storage-1` | SPACEKEEPER 22cm 4段 | https://hana-pon.github.io/service-site/jp/slim-storage-1.html |
| `slim-storage-2` | TKUIN 13cm 耐荷重32kg | https://hana-pon.github.io/service-site/jp/slim-storage-2.html |
| `slim-storage-3` | Roweida 13cm 木天板 | https://hana-pon.github.io/service-site/jp/slim-storage-3.html |
| `slim-storage-4` | アイリスオーヤマ 24cm | https://hana-pon.github.io/service-site/jp/slim-storage-4.html |
| `slim-storage-5` | ぼん家具 20cm 木製 | https://hana-pon.github.io/service-site/jp/slim-storage-5.html |
| `slim-storage-6` | 山崎実業 tower 13cm | https://hana-pon.github.io/service-site/jp/slim-storage-6.html |
| `slim-storage-7` | 山崎実業 tower 洗面台横 | https://hana-pon.github.io/service-site/jp/slim-storage-7.html |
| `slim-storage-8` | JEJアステージ 17cm 5段 | https://hana-pon.github.io/service-site/jp/slim-storage-8.html |
| `slim-storage-9` | 天馬 スキピタ 17cm 140cm | https://hana-pon.github.io/service-site/jp/slim-storage-9.html |
| `slim-storage-10` | SVOHZAV 18cm 4段 | https://hana-pon.github.io/service-site/jp/slim-storage-10.html |

## 元データから直したもう2点
1. `slim-storage-10` のタイトル「1000円台から！〜」は**価格表記**にあたるため、
   「コスパで選ぶ隙間ワゴン｜18cm4段なら最初の1台にちょうどいい」に差し替えた
   （このCSV自身の `affiliate_note` が「価格表記NG」と指定しているため）
2. H2「実際に置いてみたサイズ感レビュー」は、未使用の商品について実体験を書くことになるため、
   「サイズの合わせ方｜買う前に測る3か所」に変更し、公表スペックと採寸の話として書いた。
   実際に購入して使ったら、体験談に書き換えるとページの説得力が上がる

## ピン画像（pins/）
30枚を `build_pin_images.py` で生成している（1000×1500px）。
文言を直すときは `build_pins.py` の `PRODUCTS` を編集して、次の順で再実行する：

```
python3 content/slim-storage-jp/build_pins.py        # 文章とCSVを作り直す
python3 content/slim-storage-jp/build_pin_images.py  # 画像30枚を作り直す
```

ファイル名は `pin-<番号>-<記事スラッグ>-<A|B|C>.png`。

投稿するときは **`投稿用早見表.tsv`** を開く。1行が1枚ぶんで、
投稿日・時刻・ボード・画像ファイル名・タイトル・説明文・リンク先が
横に並んでいるので、上から順にコピーしていけばよい（表計算ソフトで開ける）。

商品写真は入れていない（Amazonの商品画像は転載できず、生成した写真は
このリポジトリの外にあるため）。写真入りにしたい場合は
`canva_bulk_30pins.csv` をCanvaの「一括作成」に読み込み、
LPで使っている写真を背景に敷く。

## 未完了
- [x] LP 10本（`slim-storage-1` 〜 `-10`）の作成 → `docs/jp/`
- [x] 記事一覧ページ → `docs/jp/index.html`
- [ ] 各LPへのAmazonアフィリリンク設定（SiteStripeで取得したものを `href="#"` と差し替え）
- [ ] 商品イメージ写真10枚（今はプレースホルダー枠）
- [x] ピン画像30枚の作成 → `pins/`
- [ ] Amazonアソシエイト・ジャパンの登録（日本のAmazon商品のため、米国アソシエイトIDでは報酬が出ない）

## Amazonアソシエイト・ジャパン 申請までの順番
審査担当は申請時のURLを実際に見るので、**サイトが完成して見える状態にしてから申請する**。
詳しい手順は `.claude/skills/pinterest-amazon-affiliate/references/setup-guide.md` を参照。

1. PRをマージしてGitHub Pagesに公開する
2. 商品イメージ写真10枚を入れる（プレースホルダーが見えたまま申請しない）
3. `href="#"` のままのボタンは、申請時点では素のAmazon商品ページURLにしておく
   （リンク切れに見えるのを避けるため。IDが出たらアフィリリンクに差し替える）
4. affiliate.amazon.co.jp から申請 → 仮トラッキングID（`〜-22`）が即発行される
5. SiteStripeでリンクを取得し、10ページの `href` を差し替える
6. Pinterest投稿を開始 → 180日以内に3件の適格販売（3つの別注文）で本審査へ

記事数は10本あるので「オリジナルコンテンツ10件以上」の目安は満たしている。
