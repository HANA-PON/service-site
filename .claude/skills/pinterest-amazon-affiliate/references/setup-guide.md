# Amazon アソシエイト / Pinterest 初期設定ガイド（日本在住者向け）

ユーザーが未登録・設定途中のときに案内する内容。すべてノンテクニカル前提で、
画面の「押す場所」を一段ずつ具体的に説明する。税務は税理士ではない旨を添える。

## 米国 Amazon アソシエイト登録

1. https://affiliate-program.amazon.com で Sign up（amazon.com のアカウントが必要。
   日本の amazon.co.jp とは別物）
2. 受取人名・住所は英語表記、国は Japan
3. 掲載先に公開済みLPのURLと Pinterest プロフィールを登録（先にLPを公開しておくと
   審査に通りやすい）
4. Store ID を決める（`〜-20` が付くトラッキングID になる）
5. 電話認証（+81、先頭0を除く）

## 税務インタビュー（W-8BEN）

紙の記入ではなく、管理画面の質問に答えると W-8BEN が自動生成される。
「税務情報の表示/提供」から開始。日本在住・個人の回答:

- Who will receive income? → **Individual**
- Are you a U.S. person? → **No**
- Country of citizenship → **Japan**、住所は英語表記
- TIN → 「foreign (non-U.S.) TIN を持っている」を選び **マイナンバー12桁** を入力
  （米国 SSN/ITIN は不要）
- 租税条約 → 居住国 **Japan** を選ぶと日米租税条約が適用され、源泉徴収が
  **30%→0%** になる（これを飛ばすと30%引かれる）
- Location of services performed → **All services performed outside the U.S.**
  （日本で作業しているため）
- Are you acting as an intermediary...? → **No**（自分の報酬を自分で受け取る個人）
- 最後に署名欄へローマ字氏名（税務情報の氏名と一字一句一致させる）→ Submit

完了すると納税状況が「不完全」→「完了(Complete)」に変わる。

## 報酬の受け取り

- 手軽なのは **Amazon ギフトカード受取**（最低 $10）。まずこれでOK
- 現金化するなら **Wise** か **Payoneer** の米ドル受取口座を作り、Direct Deposit に
  Bank name / Routing number / Account number / Checking を登録
  - Wise: 両替コスト約0.5%・維持費なし・日本住所は残高100万円相当まで。小規模なら有利
  - Payoneer: 引き出し最大2%・未利用だと年$29.95。規模が大きくなってから
- 設定は後から変更できるので「最初はギフトカード→伸びたら銀行振込」でよい

## SiteStripe でアフィリリンク作成

登録後、amazon.com の商品ページ上部に黒いバー（SiteStripe）が出る。
「Get Link」→「Text」でその商品のトラッキングID入りリンク（`amzn.to/xxxx`）を
コピーできる。これをLPに貼る。短縮URLの自作は規約違反なので、必ずツール生成の
リンクを使う。自分のリンクからは購入しない（規約違反）。

## Pinterest 初期設定

1. ビジネスアカウントを無料作成（アナリティクスが使える）
2. プロフィール名・自己紹介を英語に。居住国が日本でも英語のピンなら米国に届く
3. ボードをジャンルごとに作る（例: Japanese Tea & Kitchen / Japandi & Japanese Home）。
   ボード説明にも英語キーワードを入れる。非公開(secret)にはしない
4. ピン作成: 画像アップ → タイトル・説明文（キーワード入り）→ **リンクにLPのURL**
   → ボード選択 → 公開。商品タグ機能は使わない（導線が崩れる）
5. サイト認証: 設定 → アカウント連携 → ウェブサイト「認証する」→ 表示される
   `<meta name="p:domain_verify" content="...">` を全ページの `<head>` に追加して
   公開 → 数分待ってから「認証」ボタン。「No relevant meta tag was found」は
   タグ反映前に押しただけなので数分待って再実行

## 運用の勘所

- 週2〜3枚を継続投稿。1枚のLP宛てで画像違いを量産してよい
- 成果が見え始めるのは2〜4週間後（Pinterestは検索型でタイムラグがある）。
  投稿直後に検索で自分のピンが出ないのは正常
- **登録から180日以内に3件の適格販売**が最初の関門。未達だと閉鎖されるが再申請可
- 規模が育ったら独自ドメイン＋商用OKなホスティング（Cloudflare Pages 等）へ移行を検討
