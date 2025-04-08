# TOML(?)でUIを構築しようライブラリ for Pyxel

SQLiteをガッツリ使いたくなったのでXMLに保存してた状態をSQLiteに保存するよう方針を変更します。

ただそうなるとXMLに状態を保存する必要がなくなり、UIの構築はXMLでなくてもYAMLやTOML等のMLでいいんじゃないかなって。

状態をSQliteに保存するので、UIのガワをFlutterにするとか互換的にもイケてるかもしれない。

というわけで、一旦開発中止

<s>

## 動機
UI構築、面倒ですかー？

ゲームの遊びの部分を楽しく作ってある程度までできてくると、ぼちぼちUIも作らなきゃなーってなりますよね。<br>
そこでだいたい手が止まる_(:3」∠)_

とりあえずでいいので動かせるUIをぱっと出して、全体ができたらブラッシュアップでいいじゃない。<br>
そんなとりあえずを間に合わせるためのライブラリ。


## 特徴
Web公開や別言語への移植も簡単にできるよう基本機能と組み込みモジュールのみで構築しているので、ライブラリをディレクトリごとポンっておいたらすぐ使える。導入に依存解決やらで環境汚したくないねん……

時はまさにステートレス、ヒャッハー！OOPは消毒だーっ！<br>
というわけでできる限りクラスに状態を持たないように工夫してみました。

代わりにXMLツリー(DB代わり)にがんがん状態を書き込んじゃうんだけどナ！(ﾟ∀ﾟ)

# 使い方

まだライブラリが固まってないので今後まだちょっと変わるかも。

大きく変わることはない、はず。

## クイックスタート

### まずはpyxelのプロジェクトを用意しよう

pipでpyxelを入れたら最低限のpyxelアプリを作ってしまいます。

```python
import pyxel
pyxel.init(256, 256)

def update():
    pass

def draw():
    pass

pyxel.run(update, draw)
```

### pyxel_xmluiの導入

pyxel_xmluiのリポジトリをcloneやzipで取得したら、中のxmluiというディレクトリが本体ですので自分のプロジェクトにコピーします。

あとはimportすれば使えます。

```python
import pyxel
pyxel.init(256, 256)

# ライブラリのimport
from xmlui import XMLUI

# ライブラリのインスタンス作成
xmlui = XMLUI()

def update():
    pass

def draw():
    # ライブラリの実行
    xmlui.draw()

pyxel.run(update, draw)
```

### ラベルを描画してみよう

XMLベースということで、UIを記述したXMLファイルが必要です。

```XML
<?xml version="1.0" encoding="utf-8"?>
<xmlui id="test_ui">
    <label x="16" y="16", w="64" h="32">てきすと！</label>
</xmlui>
```

これを`test.xml`という名前で保存した場合、次のように読み込んで使います。

```python
import pyxel
pyxel.init(256, 256)

from xmlui import XMLUI
# タグ処理コールバック関数のパラメータ用
from xmlui import XUState,XUEvent

xmlui = XMLUI()
# XMLファイルの読み込み
test_template = xmlui.template_fromfile("test.xml")
# タグのid指定でUIをopen(表示開始)
xmlui.open("test_ui")

def update():
    pass

def draw():
    xmlui.draw()

# 描画用関数を用意する(デコレータ方式)
# デコレータの引数にタグ名を書く
# 関数名はかぶらなければなんでもいい
@test_template.tag_draw("label")
def label(label:XUState, event:XUEvent):
    # 第一パラメータのareaにUIのスクリーン座標
    area = label.area
    # pyxelで好きに描画
    pyxel.text(area.x, area.y, label.text, 7)

pyxel.run(update, draw)
```

以下工事中
</s>
