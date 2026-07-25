# LP 制作・公開ワークフロー

`assets/lp-template.html` を土台に紹介ページを作り、リンク・写真を差し替えて
公開するまでの手順。ノンテクニカルなユーザー向けに、GitHub 操作は毎回
「私が変更 → PR → あなたがマージ → 数分後に反映」の流れを明示する。

## 1. テンプレートを埋める

`assets/lp-template.html` をコピーし、`{{...}}` を埋めて `docs/<genre>.html` に置く。

| プレースホルダー | 内容 |
|---|---|
| `{{PAGE_TITLE}}` / `{{META_DESCRIPTION}}` | SEO用。英語。キーワードを含める |
| `{{SITE_NAME}}` | サイト名（例: Tokyo Home Picks） |
| `{{CATEGORY_TAG}}` | ジャンル小見出し（例: Japanese Tea） |
| `{{H1_HEADLINE}}` | 主見出し。英語。数字を入れると強い（例: 3 Japanese Kitchen Essentials...） |
| `{{HERO_SUBHEAD}}` | 一行サブ。日本在住の立場を活かす |
| `{{INTRO_PARAGRAPH_*}}` | 導入2段落。実感ベースで信頼を作る |
| `{{PRODUCT_n_TITLE}}` / `{{PRODUCT_n_BODY}}` | 各商品の見出しと短い紹介文 |
| `{{PRODUCT_n_LINK}}` | 取得前は `#`。取得後にアフィリリンク |
| `{{OUTRO_*}}` | 締め。「一点から始めよう」「保存してね」 |
| `{{YEAR}}` | 年 |

商品が3つでない場合は `<article class="card">` ブロックを増減する。

## 2. アフィリリンクの差し替え

ユーザーが SiteStripe で作った短縮リンク（`https://amzn.to/xxxx` 形式）を送って
きたら、該当商品の `href="#"` をそのリンクに差し替え、その下の
`<span class="btn-note">【ここにAmazon USのアフィリリンクを貼る】</span>` を削除する。
`rel="nofollow sponsored"` は残す。

リンクは1つずつ届くことが多い。届いた分だけ順次反映し、最後にまとめて
1つの PR にしてよい（毎回別 PR でもよい）。差し替え時は商品ページの在庫が
切れていることもあるので、切れていたら代替候補を提案する。

## 3. 商品写真の差し替え

写真が用意できたら、`<div class="card-img placeholder">[ Product photo ]</div>` を
`<img class="card-img" src="<画像URL>" alt="<説明>" loading="lazy">` に置換する。

- Amazon の商品画像は転載 NG。ユーザー撮影か AI 生成のイメージ写真を使う
- AI 生成する場合は `references/image-prompts.md` の商品写真プロンプトを参照
- 画像を外部CDN参照にする場合、リンク切れリスクがあることを伝える。恒久化する
  なら画像を `docs/img/` に取り込む方式に切り替える

## 4. 公開（GitHub Pages）

初回のみ、リポジトリの Settings → Pages で:
- Source: Deploy from a branch
- Branch: `main` / フォルダ `/docs`

これで `docs/` 内だけが公開され、リポジトリ直下の他ファイルは非公開になる。
公開 URL は `https://<user>.github.io/<repo>/<genre>.html`。

サービスページ等を非公開にしたい既存リポジトリでは、LP を `docs/` に `git mv`
して公開元を `/docs` に切り替える（ファイル内容は変えずに済む）。

## 5. 毎回のブランチ運用

作業のたびに最新 main からブランチを作り直す:
```
git fetch origin main && git checkout -B <branch> origin/main
```
コミットは日本語で分かりやすく。変更をプッシュしたら PR を作り、URL を
ユーザーに渡す。「この PR リンク = マージ待ちの合図」と伝える。マージは
ユーザーが GitHub 画面で行う。
