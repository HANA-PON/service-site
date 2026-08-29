#!/usr/bin/env python3
"""隙間収納キャンペーンの日本語LP（docs/jp/）を生成する。

blog_10_articles.csv の設計に、記事ごとの本文（下の ARTICLES）を組み合わせて
1商品1ページのLPを出力する。文面を直したいときは ARTICLES を編集して再実行する。

  python3 content/slim-storage-jp/build_lp.py
"""
import csv, io, os, pathlib, html

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "jp"
CSV = pathlib.Path(__file__).with_name("blog_10_articles.csv")

SITE = "すきま収納ノート"
VERIFY = "76b98bcf2847d663e1bc4067be4a20bd"   # Pinterest サイト認証（全ページ共通）
DISCLOSURE = "Amazonのアソシエイトとして、適格販売により収入を得ています。このページには広告リンクが含まれます。"
SOURCE_NOTE = ("このページは各メーカーの公表スペックと、狭い部屋に置くときの設置条件をもとに"
               "まとめています。寸法・耐荷重は商品ページの最新の表記をご確認ください。")

# 記事ごとの本文。key は blog_10_articles.csv の slug。
# lead: 導入 / why: 選んだ理由 / fit: サイズの見合わせ方 / rent: 賃貸での設置
# card_h2, card_body: 商品カード / alt: 写真の代替テキスト / outro: 締め
ARTICLES = {
"slim-storage-1": dict(
  place="キッチンの冷蔵庫横・シンク横",
  lead="6畳のワンルームでいちばん散らかるのは、たいていキッチンです。物が多いからではなく、置き場所が足りないから。"
       "その足りない分は、たぶん冷蔵庫の横で眠っています。",
  why=["キッチンの隙間は、22cm前後で空いていることがとても多い場所です。冷蔵庫と壁、シンク台と冷蔵庫、"
       "food台と壁——どれも中途半端で、市販の棚だと入らないか、入ってもスカスカになります。",
       "SPACEKEEPER の22cm・4段は、その中途半端な幅にそのまま収まる設計です。4段あるので、"
       "調味料・レトルト・ストック・掃除用品と用途で分けられます。キャスター付きなので、"
       "奥に落ちた物を取るときは手前に引き出せます。"],
  fit=["買う前に測るのは3つだけです。<strong>隙間の幅</strong>、<strong>奥行き</strong>、"
       "そして<strong>手前にどれだけ引き出せるか</strong>。幅は22cmぴったりではなく、"
       "左右に1cmずつ余裕を見ておくと出し入れが楽になります。",
       "見落としがちなのが奥行きです。冷蔵庫より前に出てしまうと、扉の開閉や通路の邪魔になります。"
       "冷蔵庫の奥行きを測って、それ以下に収まるかを商品ページの寸法表記と見比べてください。"],
  rent=["キャスター式なので壁に穴を開ける必要はありません。賃貸でそのまま置けます。",
        "ただし床が傷まないよう、フローリングには薄いマットかフェルトを1枚敷いておくと安心です。"
        "退去時の原状回復で指摘されるのは、たいていキャスターの跡です。"],
  card_h2="22cmの隙間が、そのまま収納庫になる",
  card_body="冷蔵庫横・シンク横の「使えていない22cm」に差し込むタイプのスリムワゴン。4段で用途別に分けられて、"
            "引き出せば奥の物にも手が届きます。床置きの物が減ると、キッチンは一気に広く見えます。",
  alt="キッチンの冷蔵庫横の隙間に収まったスリムな4段ワゴン",
  outro="片付けは、部屋を広くすることではなく「使えていない場所を使う」ことです。"
        "気になっている隙間をひとつだけ測ってみてください。数字が分かれば、あとは選ぶだけです。"),

"slim-storage-2": dict(
  place="トイレの便器横・タンク横",
  lead="トイレの横に空いた13cm。ここに何か置きたいけれど、ちょうどいい物が見つからない——そう思ったまま、"
       "何年か経っていませんか。",
  why=["13cmという幅は、収納用品の中でもかなり狭い部類です。選択肢が少ないうえに、"
       "細いものは「倒れそう」「たわみそう」で結局買えません。",
       "TKUIN の13cmモデルが選びやすいのは、耐荷重32kg（メーカー表記）をうたっている点です。"
       "トイレットペーパーのストックや掃除用品はかさばる割に軽いので、"
       "この耐荷重ならぐらつきを気にせず上まで詰められます。"],
  fit=["トイレは、幅より<strong>奥行き</strong>で失敗します。便器のフチや配管が思ったより前に出ていて、"
       "壁にぴったり付けられないことがあるからです。壁から便器のいちばん出っ張った部分までを測って、"
       "その中に奥行きが収まるか確認してください。",
       "高さも一度見ておきます。タンクの上や窓枠にぶつかると、いちばん上の段が使えません。"
       "「置ける高さ」ではなく「使える高さ」で考えるのがコツです。"],
  rent=["置くだけなので工事も穴あけも不要です。トイレは床が濡れやすいので、"
        "キャスターや脚のサビが気になる場合は下に防水シートを敷いておくと長持ちします。",
        "扉が内開きのトイレでは、扉の可動範囲に入っていないかも確認してください。"
        "毎日ぶつかると、それだけで使わなくなります。"],
  card_h2="13cmでも、諦めなくていい",
  card_body="トイレの便器横に差し込める細身のワゴン。メーカー表記で耐荷重32kgあるので、"
            "ペーパーのストックや洗剤をまとめて置いても不安がありません。床に物を置かずに済むと、掃除が一気に楽になります。",
  alt="トイレの便器横の細い隙間に収まった13cm幅のスリムワゴン",
  outro="トイレの13cmは、家の中でいちばん見過ごされている収納スペースです。"
        "ここが片付くと、ストックの置き場所に悩む回数がぐっと減ります。"),

"slim-storage-3": dict(
  place="冷蔵庫横・キッチンのカウンター脇",
  lead="収納が増えるのは嬉しい。でも、生活感が増えるのは嬉しくない。その両方を叶えたいなら、天板が木のものを選ぶのが近道です。",
  why=["白い樹脂のワゴンは便利ですが、キッチンに置くと「収納用品」の顔をします。"
       "部屋の見た目を気にする人ほど、買ったあとに後悔しやすいポイントです。",
       "Roweida の13cmモデルは天板が木目仕上げなので、上に置いたコーヒーミルやマグが様になります。"
       "収納として使いながら、いちばん上だけは「見せる場所」にできる——狭い部屋ではこの二役がよく効きます。"],
  fit=["13cm幅は、冷蔵庫と壁のあいだに多い寸法です。まず隙間の幅を測り、"
       "<strong>左右に1cmずつ余裕</strong>があるかを見てください。ぴったりだと、引き出すたびに擦れます。",
       "天板を「置き場所」として使うなら、高さも大事です。カウンターや冷蔵庫より高いと出っ張って見えます。"
       "隣にあるものの高さに揃えると、置いたときの収まりがきれいです。"],
  rent=["置くだけなので穴あけは不要です。木天板は水に弱いので、"
        "シンクのすぐ横に置く場合は水はねの届く範囲かどうかだけ見ておいてください。",
        "コンロの真横は避けます。熱と油が天板を傷める上に、可燃物を近づけないという基本もあります。"],
  card_h2="収納なのに、置くと部屋が良くなる",
  card_body="天板が木目仕上げの13cmスリムワゴン。中は普通に収納として使いながら、"
            "上だけはコーヒー道具やグリーンを置く場所にできます。生活感を増やさずに収納を増やしたい人向け。",
  alt="木目の天板が付いた細いワゴンが冷蔵庫の横に置かれたキッチン",
  outro="狭い部屋こそ、目に入る面積が少ないぶん、置いた物の見た目が効きます。"
        "収納を足すときは「隠す量」と「見せる場所」を一緒に決めておくと失敗しません。"),

"slim-storage-4": dict(
  place="洗濯機の横・洗面所",
  lead="洗面所の床に、洗剤の詰め替えとタオルとハンガーが直置きになっていませんか。"
       "洗濯機の横の24cmが空いているなら、それは全部しまえます。",
  why=["洗面所は、家の中でいちばん「置き場所のない物」が集まる場所です。"
       "洗剤、柔軟剤、ネット、ハンガー、タオル——どれも毎日使うのに、決まった住所がありません。",
       "アイリスオーヤマの24cmランドリーワゴンは、天板付きなので上に洗剤を出したまま置けます。"
       "しまう物と、出しっぱなしにしたい物を1台で分けられるのがこのタイプの強みです。"
       "国内メーカーなので、部品や仕様の情報が探しやすいのも安心材料です。"],
  fit=["洗濯機まわりは<strong>防水パン</strong>の存在を先に確認してください。"
       "パンのフチが張り出していると、測った幅どおりには入りません。パンの外側で測るのが正解です。",
       "もうひとつは水栓と排水ホースの位置です。ワゴンがホースを押し潰すと、"
       "排水不良の原因になります。ホースの通り道を空けたうえで、残りの幅に収まるかで判断してください。"],
  rent=["据え置きなので工事は不要です。洗面所は湿気がこもるので、"
        "壁にぴったり付けず数cm離すと、裏側のカビと結露を避けやすくなります。",
        "キャスター付きを選ぶ場合は、洗濯機の振動で少しずつ動くことがあります。"
        "ストッパー付きのものを選ぶか、使わないときはロックしておくと安心です。"],
  card_h2="洗濯機の横24cmが、洗面所の収納になる",
  card_body="天板付きのランドリーワゴン。中に詰め替えやネットをしまいながら、"
            "上は洗剤の定位置として使えます。床置きがなくなると、洗面所の掃除が驚くほど楽になります。",
  alt="洗濯機の横の隙間に置かれた天板付きのランドリーワゴン",
  outro="洗面所は、片付けの効果がいちばん早く実感できる場所です。"
        "床に置いてある物をゼロにするところから始めてみてください。"),

"slim-storage-5": dict(
  place="押入れ・クローゼットの中",
  lead="押入れは広いのに、なぜか物が入らない。理由は単純で、"
       "布団と衣装ケースのあいだに<strong>使えていない縦の隙間</strong>ができているからです。",
  why=["押入れは奥行きが深いぶん、奥の物が取り出せなくなります。"
       "結果、手前だけ使って奥は死蔵——これが「広いのに入らない」の正体です。",
       "ぼん家具の20cm木製ワゴンはキャスター付きなので、押入れの奥に入れても手前に引き出せます。"
       "木製で見た目が落ち着いているので、押入れの中だけでなく、"
       "襖を外して見せる収納にした場合もそのまま使えます。"],
  fit=["押入れは<strong>中段の高さ</strong>が最大の制約です。上段に入れるのか下段に入れるのかを先に決めて、"
       "その段の内寸（高さ）を測ってください。ここを外すと入りません。",
       "次に、<strong>敷居と襖のレール</strong>です。引き出すときにレールを越えられるか、"
       "キャスターが引っかからないかを見ておきます。段差が大きいときは、手前だけ板を渡すと解決します。"],
  rent=["押入れの中に置くだけなので、壁も襖も傷めません。",
        "湿気だけ注意します。押入れは空気が動かないので、壁から数cm離し、"
        "月に一度は襖を開けて風を通すと、木製でもカビにくくなります。"],
  card_h2="押入れの奥行きを、引き出して使う",
  card_body="キャスター付きの20cm木製ワゴン。押入れの奥に入れても手前に引き出せるので、"
            "これまで死蔵していた奥のスペースがそのまま使えるようになります。布団の脇の細い縦空間にも収まります。",
  alt="押入れの中に収まった木製のキャスター付きスリムワゴン",
  outro="押入れは、床面積を増やさずに収納を倍にできる数少ない場所です。"
        "奥に手が届くようにするだけで、入る量は変わります。"),

"slim-storage-6": dict(
  place="キッチン・洗面所・リビングの隙間",
  lead="収納用品を選ぶとき、多くの人が最後に行き着くのが tower です。理由は、"
       "収納力ではなく<strong>置いても部屋がうるさくならない</strong>ことにあります。",
  why=["白か黒、直線、ロゴなし。tower シリーズの見た目のルールはそれだけです。"
       "でも狭い部屋では、この「主張しない」という性質が効きます。"
       "物が増えても、視界の情報量が増えないからです。",
       "13cmのスリムワゴンは、そのルールのまま隙間に入る一台です。"
       "キッチンでも洗面所でも浮かないので、あとから置き場所を変えても使い続けられます。"],
  fit=["13cmは狭いので、<strong>入れる物のほうを先に決める</strong>のが失敗しないコツです。"
       "ラップの箱、詰め替えボトル、スプレー缶——いちばん大きい物の幅と高さを測って、"
       "それが各段に収まるかで判断してください。",
       "見た目重視で選ぶ場合は、周りの家電の色も見ておきます。"
       "白物家電の横なら白、黒い家電やレンジフードの近くなら黒のほうが馴染みます。"],
  rent=["置き型なので穴あけ不要です。tower シリーズは同じトーンで揃うので、"
        "1台置いて気に入ったら、同じ場所に少しずつ足していくのが賃貸向きの増やし方です。",
        "スチール製は水気が残るとサビの原因になります。洗面所やキッチンで使うなら、"
        "水はねしたら拭く、という一手間だけ習慣にしておくと長く保ちます。"],
  card_h2="置いても、部屋がうるさくならない13cm",
  card_body="白か黒、直線だけのスリムワゴン。収納を足しても視界の情報量が増えないので、"
            "狭い部屋ほど効きます。キッチンでも洗面所でも浮かず、置き場所を変えても使い続けられます。",
  alt="白いスリムなスチールワゴンがキッチンの細い隙間に収まっている様子",
  outro="狭い部屋の片付けは、物を減らすことと同じくらい「見た目の情報を減らす」ことが効きます。"
        "揃うシリーズを1つ決めておくと、増やすたびに部屋が整っていきます。"),

"slim-storage-7": dict(
  place="洗面台の横",
  lead="洗面台の上に、化粧水とドライヤーとコンタクトと歯ブラシが並んでいる。"
       "毎朝ここでイライラしているなら、原因は物の量ではなく<strong>高さを使えていない</strong>ことです。",
  why=["洗面台の上は平面です。平面に物を並べると、置ける量はすぐ頭打ちになり、"
       "そこから先はただ散らかっていきます。",
       "tower の洗面台横ラックは、その平面の横に縦の置き場所を足す形です。"
       "毎日使うスキンケアとヘアケアを縦に並べられるので、"
       "洗面台の上は「今使っている物だけ」に戻せます。掃除のとき全部どかす必要もなくなります。"],
  fit=["洗面台の横は、<strong>幅より高さの制約</strong>が強い場所です。"
       "鏡の下端やコンセント、タオルバーにぶつからないかを先に確認してください。",
       "奥行きも見ておきます。洗面台より前に出ると、"
       "しゃがんだときや扉を開けたときに当たります。洗面台の奥行き以内に収まるかが目安です。"],
  rent=["置き型を選べば穴あけは不要です。突っ張り式や壁付け式は収納力が上がりますが、"
        "賃貸では跡が残らないタイプかを必ず確認してください。",
        "洗面所は湿気が多いので、床に接する脚の部分に水が溜まらないようにします。"
        "掃除のとき一度どかせる重さかどうかも、選ぶときの基準にしていいポイントです。"],
  card_h2="洗面台の「横」に、縦の置き場所を足す",
  card_body="洗面台の脇に置いて、スキンケアやヘアケアを縦に並べられるラック。"
            "洗面台の上が空くので、朝の動線が短くなり、掃除のときに全部どかす手間もなくなります。",
  alt="洗面台の横に置かれた白いスリムなラックに化粧品が並んでいる様子",
  outro="毎日触る場所ほど、片付けの効果は大きく返ってきます。"
        "洗面台の上に何も置かない日が作れると、その状態を保ちたくなります。"),

"slim-storage-8": dict(
  place="キッチン・洗面所",
  lead="組み立てが苦手な人にとって、収納用品選びのいちばんの壁は「届いてから」です。"
       "完成品で届くタイプなら、そこを丸ごと飛ばせます。",
  why=["スリムストッカーは細長いぶん、組み立てを間違えると歪んで引き出しが引っかかります。"
       "工具に慣れていない人ほど、完成品を選ぶ価値があります。",
       "JEJアステージの17cm・5段は日本製の完成品タイプです。"
       "届いたその日に使えて、引き出しの動きも最初から揃っています。"
       "5段あるので、細かい物を種類ごとに分けたい人に向いています。"],
  fit=["17cmは、キッチンでも洗面所でもよくある隙間幅です。"
       "まず幅を測り、<strong>左右の余裕1cm</strong>を引いた寸法で探してください。",
       "5段タイプは<strong>引き出しを開けたときの前面のスペース</strong>も要ります。"
       "壁際や通路で使うなら、引き出しを全部引いた状態で通れるかを一度想像してみてください。"
       "ここを見落とすと、置けても使いにくくなります。"],
  rent=["置くだけなので工事は不要です。完成品は箱が大きいので、"
        "玄関から置き場所までの通路と、エレベーターに入るかだけ先に確認しておくと安心です。",
        "キャスター付きの場合は、フローリングに直接だと跡が残ることがあります。"
        "薄いマットを1枚挟んでおくと、退去のときに気を揉まずに済みます。"],
  card_h2="届いたその日から使える、17cmの5段",
  card_body="日本製の完成品スリムストッカー。組み立て不要なので、届いてすぐ中身を入れられます。"
            "5段あるので、細かい物を種類ごとに分けたい人に向いています。",
  alt="キッチンの隙間に置かれた17cm幅の5段スリムストッカー",
  outro="収納用品は、買ったあと組み立てずに放置されがちです。"
        "「その日のうちに使い始められるか」を選ぶ基準に入れると、無駄になりません。"),

"slim-storage-9": dict(
  place="キッチン・洗面所・玄関",
  lead="6畳で収納を増やす方法は、実はひとつしかありません。<strong>横ではなく縦に伸ばす</strong>ことです。",
  why=["床に置ける面積は決まっています。だから収納を増やそうとして幅の広い家具を買うと、"
       "収納は増えても部屋が狭くなり、結局後悔します。",
       "天馬のスキピタは幅17cmのまま高さ140cmまで積み上げるタイプです。"
       "占有する床面積は増やさずに、収納量だけを縦に伸ばせます。"
       "狭い部屋で「収納力2倍」を目指すなら、この形がいちばん理にかなっています。"],
  fit=["高さ140cmは、多くの人の目線より少し下です。"
       "<strong>いちばん上の段に手が届くか</strong>を先に確認してください。"
       "背伸びが必要な段は、結局使わなくなります。",
       "もうひとつ、高さがあるぶん<strong>重心</strong>に気を配ります。"
       "重い物を上に入れると不安定になるので、下段から重い順に入れるのが基本です。"],
  rent=["置き型なので穴あけ不要です。ただし高さがあるので、地震対策は考えておいたほうがいい高さです。"
        "壁に穴を開けられない賃貸では、粘着タイプの転倒防止マットや、"
        "上部に隙間を作らない配置（壁と家具に挟む）で対応できます。",
        "床が沈む柔らかい床材だと、高さのある家具は傾きます。"
        "気になる場合は下に硬めの板を1枚敷いて、荷重を分散させてください。"],
  card_h2="床は増やさず、収納だけ縦に伸ばす",
  card_body="幅17cmのまま高さ140cmまで使えるスリムストッカー。"
            "占有する床面積を増やさずに収納量だけを増やせるので、6畳のような限られた部屋と相性がいいタイプです。",
  alt="幅の狭い背の高いスリムストッカーが部屋の隙間に置かれている様子",
  outro="狭い部屋の収納は、床の取り合いです。縦に伸ばせる場所を1つ見つけるだけで、"
        "部屋の広さを変えずに収納量を増やせます。"),

"slim-storage-10": dict(
  place="キッチン・洗面所・トイレ",
  lead="隙間収納は「効くかどうか」が置いてみるまで分かりません。"
       "だから最初の1台は、失敗しても諦めがつくものから試すのが現実的です。",
  why=["いきなりブランド品を買って、置いてみたらサイズが合わなかった——これがいちばんもったいないパターンです。"
       "隙間収納は、幅・奥行き・高さの3つが揃って初めて機能します。",
       "SVOHZAV の18cm・4段は、まず1台試すのに向いた選択肢です。"
       "18cmは家の中でよくある隙間幅なので、置き場所が合わなくても別の部屋に回しやすい。"
       "「この隙間、本当に使えるのか」を確かめる用途に向いています。"],
  fit=["18cmは、キッチンの調味料やレトルト、洗面所の詰め替えボトルがちょうど入る幅です。"
       "<strong>いちばん大きい物の幅</strong>を測ってから決めると外しません。",
       "安価なモデルは、耐荷重の表記が控えめなことがあります。"
       "重い缶詰や瓶をまとめて入れる予定があるなら、商品ページの耐荷重を必ず確認してください。"
       "軽い物中心なら十分に使えます。"],
  rent=["置くだけなので穴あけ不要、退去時もそのまま持ち出せます。",
        "1台置いてみて「この場所は効く」と分かったら、同じ場所を"
        "より丈夫なものや見た目の良いものに置き換えていくのが、失敗の少ない増やし方です。"],
  card_h2="まず1台、試してみるための18cm",
  card_body="18cm幅・4段のスリムワゴン。家の中でよくある隙間幅なので、"
            "置き場所が合わなくても別の部屋に回せます。「この隙間は使えるのか」を確かめる最初の1台に。",
  alt="18cm幅の4段スリムワゴンがキッチンの隙間に置かれている様子",
  outro="隙間収納は、正解を一発で当てるより、試して合わせていくほうが早く片付きます。"
        "気になる隙間を測って、1台置いてみるところから始めてください。"),
}

# 元データからの修正：価格を含むタイトルは規約（価格表記NG）に反するため差し替える。
TITLE_OVERRIDE = {
    "slim-storage-10": "コスパで選ぶ隙間ワゴン｜18cm4段なら最初の1台にちょうどいい",
}

CSS = """    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --bg:        #F5F6F4;
      --card:      #FFFFFF;
      --charcoal:  #26292B;
      --ink:       #35393B;
      --accent:    #6E8A94;
      --accent-dk: #566E77;
      --line:      #E1E2DE;
      --muted:     #767A78;
    }
    body {
      font-family: 'Hiragino Sans', 'Hiragino Kaku Gothic ProN', 'Noto Sans JP',
                   'Yu Gothic Medium', 'Yu Gothic', Meiryo, sans-serif;
      background: var(--bg); color: var(--ink); line-height: 1.9;
      font-size: 16px; -webkit-text-size-adjust: 100%;
    }
    .wrap { max-width: 680px; margin: 0 auto; padding: 0 24px; }
    a { color: var(--accent-dk); }

    .hero { text-align: center; padding: 64px 24px 44px; border-bottom: 1px solid var(--line); }
    .hero-tag {
      display: inline-block; font-size: .78rem; letter-spacing: .14em;
      color: var(--accent-dk); margin-bottom: 14px;
    }
    h1 {
      font-size: clamp(1.35rem, 4.4vw, 1.95rem); font-weight: 700;
      color: var(--charcoal); line-height: 1.55; max-width: 620px; margin: 0 auto 18px;
    }
    .hero p { max-width: 560px; margin: 0 auto; color: var(--muted); font-size: .95rem; }

    .intro { padding: 44px 0 8px; }
    .intro p { margin-bottom: 1.3em; }

    section.body { padding: 8px 0; }
    section.body h2 {
      font-size: 1.18rem; font-weight: 700; color: var(--charcoal);
      line-height: 1.5; margin: 40px 0 16px; padding-left: 14px;
      border-left: 3px solid var(--accent);
    }
    section.body p { margin-bottom: 1.3em; }

    .card {
      background: var(--card); border: 1px solid var(--line);
      border-radius: 6px; padding: 32px 28px; margin: 40px 0;
    }
    .card-no {
      font-size: .78rem; letter-spacing: .14em; color: var(--accent-dk); margin-bottom: 8px;
    }
    .card h2 {
      font-size: 1.2rem; font-weight: 700; color: var(--charcoal);
      margin: 0 0 18px; line-height: 1.5; padding: 0; border: 0;
    }
    .card-img {
      width: 100%; aspect-ratio: 4 / 3; border-radius: 4px; margin-bottom: 20px;
      background: var(--bg); border: 1px dashed var(--line);
      display: flex; align-items: center; justify-content: center;
      color: var(--muted); font-size: .82rem; text-align: center; padding: 16px;
    }
    .card p { margin-bottom: 1.2em; }
    .btn {
      display: inline-block; background: var(--accent); color: #fff;
      text-decoration: none; font-size: .95rem; font-weight: 700; letter-spacing: .03em;
      padding: 14px 30px; border-radius: 4px; transition: background .2s;
    }
    .btn:hover { background: var(--accent-dk); }
    .btn-note {
      display: block; margin-top: 10px; font-size: .78rem; color: var(--muted); line-height: 1.7;
    }

    .note {
      font-size: .82rem; color: var(--muted); line-height: 1.8;
      border-top: 1px solid var(--line); padding-top: 20px; margin-top: 8px;
    }
    .outro { padding: 8px 0 44px; }
    .outro p { margin-bottom: 1.3em; }
    .back { display: inline-block; margin-top: 8px; font-size: .9rem; }

    footer {
      background: var(--charcoal); color: #CDCFC9; text-align: center;
      padding: 36px 24px; font-size: .8rem; line-height: 1.9;
    }
    footer .disclosure { max-width: 560px; margin: 0 auto 10px; }"""


def page(row):
    slug = row["slug"]
    a = ARTICLES[slug]
    title = TITLE_OVERRIDE.get(slug, row["blog_title"])
    e = html.escape
    why = "\n".join(f"      <p>{p}</p>" for p in a["why"])
    fit = "\n".join(f"      <p>{p}</p>" for p in a["fit"])
    rent = "\n".join(f"      <p>{p}</p>" for p in a["rent"])
    desc = f"{a['place']}の隙間に。{e(row['product'])}を、狭い部屋に置くときのサイズの測り方と賃貸での設置のコツからまとめました。"
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="p:domain_verify" content="{VERIFY}"/>
  <title>{e(title)} | {SITE}</title>
  <meta name="description" content="{desc}">
  <style>
{CSS}
  </style>
</head>
<body>

  <!-- ══════════════════════════════════════════════════
       メモ：Amazonのアフィリリンクは href="#" の1か所を差し替える。
       写真は div.card-img を <img class="card-img"> に置き換える。
       文面の修正は content/slim-storage-jp/build_lp.py の ARTICLES を編集して再生成。
     ══════════════════════════════════════════════════ -->

  <section class="hero">
    <span class="hero-tag">{e(a['place'])} ・ {SITE}</span>
    <h1>{e(title)}</h1>
    <p>{a['lead']}</p>
  </section>

  <div class="wrap">

    <section class="body">

      <h2>{e(row['h2_1'])}</h2>
{why}

      <article class="card">
        <div class="card-no">今回の1台</div>
        <h2>{e(a['card_h2'])}</h2>
        <div class="card-img">［ここに商品イメージ写真を入れる：{e(a['alt'])}］</div>
        <p>{a['card_body']}</p>
        <a class="btn" href="#" rel="nofollow sponsored" target="_blank">Amazonで詳細を見る&nbsp;&rarr;</a>
        <span class="btn-note">【ここにAmazonのアフィリリンクを貼る】<br>
        SiteStripeで「{e(row['amazon_search'])}」を検索して短縮リンクを取得し、上の href="#" と差し替えてください。</span>
      </article>

      <h2>サイズの合わせ方｜買う前に測る3か所</h2>
{fit}

      <h2>{e(row['h2_3'])}</h2>
{rent}

      <p class="note">{SOURCE_NOTE}</p>

    </section>

    <section class="outro">
      <p>{a['outro']}</p>
      <p>このページをPinterestで保存しておくと、次に隙間が気になったときにすぐ戻ってこられます。</p>
      <a class="back" href="index.html">&larr; 隙間収納の記事一覧へ</a>
    </section>

  </div>

  <footer>
    <p class="disclosure">{DISCLOSURE}</p>
    <p>&copy; 2026 {SITE}</p>
  </footer>

</body>
</html>
"""


def index(rows):
    e = html.escape
    items = []
    for row in rows:
        slug = row["slug"]
        a = ARTICLES[slug]
        title = TITLE_OVERRIDE.get(slug, row["blog_title"])
        items.append(f"""      <a class="guide" href="{slug}.html">
        <div class="guide-cat">{e(a['place'])}</div>
        <h2>{e(title)}</h2>
        <p>{e(a['card_body'][:70])}…</p>
        <span class="guide-more">記事を読む &rarr;</span>
      </a>""")
    guides = "\n\n".join(items)
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="p:domain_verify" content="{VERIFY}"/>
  <title>{SITE} — 6畳・賃貸でもできる隙間収納</title>
  <meta name="description" content="6畳ワンルーム・賃貸で使える隙間収納の記事10本。冷蔵庫横、トイレ、洗面台、押入れ——使えていない隙間ごとに、置ける物とサイズの測り方をまとめています。">
  <style>
{CSS}
    .guides {{ padding: 44px 0 56px; }}
    .guides-label {{
      text-align: center; font-size: .78rem; letter-spacing: .14em;
      color: var(--muted); margin-bottom: 28px;
    }}
    .guide {{
      display: block; background: var(--card); border: 1px solid var(--line);
      border-radius: 6px; padding: 26px 28px; margin-bottom: 18px;
      text-decoration: none; color: var(--ink);
      transition: border-color .2s, transform .2s;
    }}
    .guide:hover {{ border-color: var(--accent); transform: translateY(-2px); }}
    .guide-cat {{ font-size: .78rem; letter-spacing: .12em; color: var(--accent-dk); margin-bottom: 8px; }}
    .guide h2 {{
      font-size: 1.1rem; font-weight: 700; color: var(--charcoal);
      margin: 0 0 8px; line-height: 1.55; padding: 0; border: 0;
    }}
    .guide p {{ color: var(--muted); font-size: .9rem; margin-bottom: 10px; }}
    .guide-more {{ font-size: .88rem; color: var(--accent-dk); }}
  </style>
</head>
<body>

  <section class="hero">
    <span class="hero-tag">{SITE}</span>
    <h1>6畳でも、賃貸でも。<br>使えていない隙間から片付ける</h1>
    <p>部屋を広くすることはできません。でも、冷蔵庫の横やトイレの脇に眠っている数cmは、今日から収納にできます。</p>
  </section>

  <div class="wrap">
    <section class="guides">
      <div class="guides-label">記事一覧</div>

{guides}

    </section>
  </div>

  <footer>
    <p class="disclosure">{DISCLOSURE}</p>
    <p>&copy; 2026 {SITE}</p>
  </footer>

</body>
</html>
"""


def main():
    rows = list(csv.DictReader(io.open(CSV, encoding="utf-8-sig")))
    missing = [r["slug"] for r in rows if r["slug"] not in ARTICLES]
    if missing:
        raise SystemExit(f"本文が未執筆のslug: {missing}")
    OUT.mkdir(parents=True, exist_ok=True)
    for row in rows:
        (OUT / f"{row['slug']}.html").write_text(page(row), encoding="utf-8")
    (OUT / "index.html").write_text(index(rows), encoding="utf-8")
    print(f"生成: {len(rows)}本 + 一覧ページ -> {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
