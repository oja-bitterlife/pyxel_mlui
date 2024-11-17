import pyxel # Pyxelモジュールをインポート

pyxel.init(256, 256) # 初期化(ウィンドウサイズを指定)

from xmlui import XMLUI
xmlui = XMLUI.createFromFile("assets/ui/test.xml")

# お試しサンプルUI
import xmlui_pyxel
xmlui_pyxel.setDefaults(xmlui)

from xmlui import UI_MENU,UI_MENU_GROUP
command_item_data = [
    ["speak", "tool"],
    ["status", "check"],
]

cmd_menu_template = xmlui.root.findByID("cmd_menu_template")
if cmd_menu_template:
    dup_cmd_menu = cmd_menu_template.duplicate("dup_cmd_menu")
    xmlui.root.addChild(dup_cmd_menu)
    command_win = UI_MENU(command_item_data, dup_cmd_menu, 0, 0)
    xmlui.openMenu(command_win)


# Main
def update(): # フレームの更新処理
    if pyxel.btnp(pyxel.KEY_Q):
        pyxel.quit()

    active_menu = xmlui.menu.getActive()
    if active_menu:
        if pyxel.btnp(pyxel.KEY_LEFT):
            active_menu.moveLeft()
        if pyxel.btnp(pyxel.KEY_RIGHT):
            active_menu.moveRight()
        if pyxel.btnp(pyxel.KEY_UP):
            active_menu.moveUp()
        if pyxel.btnp(pyxel.KEY_DOWN):
            active_menu.moveDown()

        if pyxel.btnp(pyxel.KEY_SPACE):
            dup_msg_win = xmlui.root.findByID("dup_msg_win")
            #  表示中なら消す
            if dup_msg_win:
                dup_msg_win._remove = True

            # 非表示なら新規で追加
            elif active_menu.getData() == "speak":
                msg_win_template = xmlui.root.findByID("msg_win_template")
                if msg_win_template:
                    xmlui.root.addChild(msg_win_template.duplicate("dup_msg_win"))

                    msg_text = msg_win_template.findByTag("msg_text")
                    if msg_text:
                        msg_text[0].update_count = 0
                        msg_text[0].setAttr("finish", False)

        if pyxel.btnp(pyxel.KEY_BACKSPACE):
            active_menu.close()


    xmlui.update()

def draw(): # 描画処理
    pyxel.cls(0)

    # UI描画
    xmlui.draw()

# アプリケーションの実行
pyxel.run(update, draw)
