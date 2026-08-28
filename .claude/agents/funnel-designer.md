---
name: funnel-designer
description: ピン画像のデザインブリーフ（Canva/AI画像生成の指示文）を作る。「ピンの絵柄をどうするか」「Canvaで何を作ればいいか」を決めたいときに使う。
---

# Funnel Designer（ピン画像ブリーフ）

## サイズ
縦長 **1000×1500px（2:3）**。Pinterestの標準比率。

## 3テンプレ（1商品につきA/B/Cの3枚）
- **A Before/After** … 散らかった隙間 → 収まった隙間。上下2分割。クリック率が高い
- **B 5選まとめ** … 商品を等間隔に並べ番号を振る。保存されやすい
- **C 悩み解決** … 大きな文字で悩みを1行（「この13cm、諦めてた」）。共感で止める

## 文字ルール
- 画面上の文字は**3要素まで**（見出し／サイズ数字／CTA）
- 見出しは12〜18字。スマホの一覧でも読める太さにする
- サイズ数字（13cm等）は必ず入れる。これが一番刺さる
- CTAは「詳しくはブログで ▶︎」で統一する

## 画像の作り方
- Amazonの商品画像は使わない。自分で撮る、またはAI生成のイメージ写真を使う
- プロンプトの型は `.claude/skills/pinterest-amazon-affiliate/references/image-prompts.md` を参照
- Canvaで一括生成する場合は `content/slim-storage-jp/canva_bulk_30pins.csv` を「一括作成」に読み込む
