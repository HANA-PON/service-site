# service-site リポジトリの構成メモ

hana-pon（建築設備士）の事業まわりのファイルを1つに置いているリポジトリ。
中身は大きく **2系統** に分かれる。混ぜないこと。

## 系統A：本業（建築設備士 × SNS × AI コンサル）

| ファイル | 中身 | 公開 |
|---|---|---|
| `index.html` | サービスサイト本体（強み／サービス3本柱／実績／問い合わせフォーム） | 非公開（Pages公開元は `main / docs` のため） |
| `sales-proposal.html` | 商談で渡す3ページの提案書（課題→差別化→実績→料金→無料相談） | 非公開 |
| `strategy/90day-revenue-strategy.md` | 90日で売上を作る戦略（1商品・1導線に絞った実行計画） | 非公開 |

### 掲載している実績（サイト・提案書で使い回す数字）
- SNS運用での売上貢献：月5,000万円
- AI導入による効率化：社員20人分の業務を2人体制へ
- 建築設備士（国家資格）＋設備設計の実務経験

### 料金（現状のサイト表記）
- SNS×AI運用代行：月15〜50万円
- AI業務効率化コンサル：月10〜30万円／導入支援 100万円〜
- オンライン講座：5〜10万円/人

> 2026-09 の戦略見直しで、**AI業務効率化1本に絞る**方針を決めた。
> サイト・提案書の書き換えは未着手（`PROGRESS.md` 参照）。

## 系統B：Pinterest × Amazon アフィリエイト（隙間収納）

| 場所 | 中身 |
|---|---|
| `content/slim-storage-jp/` | ピン30枚・LP10本の元データとビルドスクリプト。詳細はこの中の `README.md` |
| `docs/jp/` | 公開されるLP本体（GitHub Pages） |
| `docs/*.html` | 米国向けLP（お茶・Japandi・収納）とトップページ |
| `.claude/skills/pinterest-amazon-affiliate/` | この作業を進めるためのスキル定義 |

**守るルール**：ピンにアフィリリンクを直貼りしない（必ずLP経由）／Amazon商品画像の転載NG／
LPに価格表記NG／LP末尾に開示文／アフィリリンクは `rel="nofollow sponsored"`。

## 公開の仕組み

- GitHub Pages の公開元は **`main` ブランチの `/docs`**。
  → `docs/` 配下だけが公開され、`index.html` や `sales-proposal.html`、`strategy/` は公開されない
- 公開URLの形：`https://hana-pon.github.io/service-site/jp/slim-storage-1.html`

## 作業の進め方

- 変更のたびに最新 main から作業ブランチを作る
  （`git fetch origin main && git checkout -B <branch> origin/main`）
- 私が変更 → PR → hana-pon がマージ → 数分後にPagesへ反映
- 作業の経過は `PROGRESS.md` に追記する（作業開始時にも必ず読む）
- LPの文面を直すときはHTMLを直接触らず、`content/slim-storage-jp/build_lp.py` の
  `ARTICLES` を編集して再実行する
