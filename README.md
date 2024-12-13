# XMLでUIを構築しようライブラリ for Pyxel

## 動機
UI構築、面倒ですか？

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
# ライブラリのimport
from xmlui import XMLUI

# ライブラリのインスタンス作成
xmlui = XMLUI()

def update():
    pass

def draw():
    # ライブラリの実行
    xmlui.draw([])

pyxel.run(update, draw)
```

### ウインドウを描画してみよう

XMLベースということで、UIを記述したXMLファイルが必要です。

```XML
<?xml version="1.0" encoding="utf-8"?>
<xmlui id="test_ui">
    <window x="16" y="16", w="64" h="32">
    </window>
</xmlui>
```

これを`test.xml`という名前で保存した場合、次のように読み込んで使います。

```python
import pyxel
from xmlui import XMLUI
# タグ処理コールバック関数のパラメータ用
from xmlui import XUState,XUEvent

xmlui = XMLUI()
# XMLファイルの読み込み。第二引数はテンプレート名
xmlui.template_fromfile("test.xml", "test_template")

def update():
    pass

def draw():
    # テンプレート名とタグのidをもとにopen(表示開始)
    xmlui.open("test_template", "test_ui")

    xmlui.draw([])

# 描画用関数を用意する(デコレータ方式)
# デコレータの引数にタグ名を書く
# 関数名はなんでもいい。デコレータ内でラップされる
@xmlui.tag_bind("window")
def window(window:XUState, event:XUEvent):  
    # 第一パラメータのareaにUIのスクリーン座標
    area = window.area
    # pyxelで好きに描画
    pyxel.boxb(area.x, area.y, area.w, area.h, 7)

pyxel.run(update, draw)
```

### ウインドウを増やす

XMLに新しいウインドウ情報を追加します。

タグが同じであれば先程のpythonプログラムが処理するので、新たに描画コードを書く必要はありません。

```XML
<?xml version="1.0" encoding="utf-8"?>
<xmlui>
    <window x="16" y="16", w="64" h="32" id="test_win">
    </window>

    <info>新しいウインドウ</info>
    <window x="16" y="100", w="64" h="32" id="test_win">
    </window>
</xmlui>
```

以下工事中