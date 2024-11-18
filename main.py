import pyxel # Pyxelモジュールをインポート

pyxel.init(256, 256) # 初期化(ウィンドウサイズを指定)

from xmlui import XMLUI
ui_template = XMLUI.createFromFile("assets/ui/test.xml")
ui_worker = XMLUI.createWorker("xmlui")


# お試しサンプルUI
import xmlui_pyxel
xmlui_pyxel.setDefaults(ui_worker)

from xmlui import UI_MENU
command_item_data = [
    ["speak", "tool"],
    ["status", "check"],
]

template_menu_cmd = ui_template.root.findByID("menu_cmd")
if template_menu_cmd is None:
    raise Exception("menu_cmd not found")

menu_cmd = ui_worker.root.addChild(template_menu_cmd.duplicate()).openMenu(UI_MENU(command_item_data, 0, 0))

# Main
def update(): # フレームの更新処理
    if pyxel.btnp(pyxel.KEY_Q):
        pyxel.quit()

    active_menu = menu_cmd.menu
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
            win_message_worker = menu_cmd.findByTag("win_message")
            #  表示中なら消す
            if win_message_worker:
                win_message_worker.remove()

            # 非表示なら新規で追加
            elif active_menu.getData() == "speak":
                template_win_message = ui_template.root.findByID("win_message")
                if template_win_message is None:
                    raise Exception("menu_cmd not found")
                msg_text = ui_worker.root.addChild(template_win_message.duplicate()).findByTag("msg_text")
                if msg_text:
                    msg_text.update_count = 0
                    msg_text.setAttr("finish", False)

        if pyxel.btnp(pyxel.KEY_BACKSPACE):
            menu_cmd.remove()

    ui_worker.update()

def draw(): # 描画処理
    pyxel.cls(0)

    # UI描画
    ui_worker.draw()

# アプリケーションの実行
pyxel.run(update, draw)
