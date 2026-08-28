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

## 未完了
- [ ] LP 10本（`slim-storage-1` 〜 `-10`）の作成
- [ ] 各LPへのAmazonアフィリリンク設定（SiteStripeで取得したものを差し替え）
- [ ] ピン画像30枚の作成（Canva一括作成 or AI生成）
