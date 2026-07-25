# ピン画像・商品写真の生成プロンプト

画像生成ツール（Higgsfield の generate_image 等）が使える場合、この場で画像を
作ってユーザーに URL を渡す。ツールが承認待ち・未接続なら、同じプロンプトを
Canva 等の指示文としてユーザーに渡す。

共通:
- ピン画像は縦長 **2:3（1000×1500px 相当、生成は 2k 推奨）**
- 商品写真は横長 **4:3（1k で十分）**
- 生成後は画像内の英文の綴りが崩れていないか必ず確認してもらう（AI文字は稀に崩れる）
- 生成URL（cloudfront 等）はブラウザで開いて保存してもらう。この実行環境からは
  直接ダウンロードできないことが多い

## ピン画像の3つの型（②に対応）

いずれも `Pinterest pin image, vertical 2:3` で始め、末尾に
`no other text or watermarks` を付ける。画像に乗せる英語コピーは
`text that reads exactly: "..."` の形で指定すると綴りが安定する。

### A 情緒型（主役1点・感情に刺す）
例（障子ランプ）:
> Pinterest pin image, vertical 2:3, moody atmospheric interior photograph.
> A Japanese shoji-style paper floor lamp glowing warmly in the dark corner of a
> japandi bedroom at night, soft amber light, charcoal walls, calm zen mood,
> shallow depth of field. Over the darker upper area, elegant off-white serif
> text that reads exactly: "Zen Home Aesthetic" on the first line and smaller
> text "The Lamp That Changes Everything" on the second line. High-end editorial
> photography, no other text or watermarks.

### B メイクオーバー／ビフォーアフター型（部屋全体・高クリック率）
例:
> Pinterest pin image, vertical 2:3. A calm japandi living room, bright and
> minimal, with a few key pieces. At the top, a clean cream-colored horizontal
> band with dark charcoal serif text that reads exactly: "Japanese Style Bedroom
> Makeover" on the first line and smaller "3 Easy Pieces" on the second line.
> High-end editorial interior photography, no other text or watermarks.

### C 図鑑／リスト型（並べる・保存されやすい）
複数商品を等間隔に並べ、各アイテムに小さな英語ラベル、上部にタイトル。番号付き
「◯◯7選」型もこれ。
例:
> Pinterest pin image, vertical 2:3, editorial catalog flat-lay. Clean warm cream
> background: three items arranged vertically with generous spacing, each with a
> small elegant serif label. At the top, dark charcoal serif title text that reads
> exactly: "3 Japandi Living Room Ideas". Minimal museum-catalog aesthetic, soft
> shadows, no other text or watermarks.

各ジャンルで A/B/C を1案ずつ、可能なら各2枚生成して良い方を選んでもらう。

## 商品写真（③のLP用）

`Product lifestyle photograph, 4:3 horizontal.` で始め、被写体・置き場所・光・
色調を書き、`no text, no watermarks, no people` を付ける。
例（抹茶セット）:
> Product lifestyle photograph, 4:3 horizontal. A Japanese matcha starter set on a
> warm wooden table: a bamboo whisk, a ceramic bowl with frothy green matcha, a
> bamboo scoop, soft natural window light, cream neutral background, shallow depth
> of field, high-end editorial product photography, no text, no watermarks, no people.

## 運用メモ

- 生成ツールに同時実行数の上限がある場合、数枚ずつに分けて投げる
- クレジットは1枚あたり数クレジット程度。使いすぎないよう、まず各案2枚に留める
- 画像内テキストは英語のみにする（日本語フォントは崩れやすい）
