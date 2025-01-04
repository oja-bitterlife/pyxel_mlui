import pyxel

# フィールド関係
from field.system.player import Player
from field.system.bg import BG
from field.system.npc import NPCManager
from field.system.field_obj import FieldObj
from msg_dq import MsgDQ
from db import user_data

# UI
from xmlui.core import XUElem,XUEvent,XUEventItem,XUWinBase
from xmlui.lib.debug import DebugXMLUI
from xmlui.ext.scene import XUEFadeScene

import ui_common
from field.ui import msg_win,menu,talk_dir,tools

class Field(XUEFadeScene):
    def __init__(self):
        super().__init__(DebugXMLUI(pyxel.width, pyxel.height))

        # UIの読み込み
        self.xmlui.load_template("assets/ui/field.xml")
        self.xmlui.load_template("assets/ui/common.xml")

        ui_common.ui_init(self.xmlui)
        for module in [msg_win, menu, talk_dir, tools]:
            module.ui_init(self.xmlui)

        # ゲーム本体(仮)
        self.player = Player(self.xmlui, 10, 10)
        self.bg = BG()
        self.npc = NPCManager()
        self.field_obj = FieldObj()

        # 画像読み込み
        pyxel.images[1].load(0, 0, "assets/images/field_tile.png" )

    def closed(self):
        self.xmlui.close()  # 読みこんだUIの削除

        from battle import Battle
        self.set_next_scene(Battle())

    def update(self):
        # UIメニューが開いていたらキャラが動かないように
        if not self.xmlui.exists_id("menu"):
            # プレイヤの移動
            self.player.update([self.npc.hit_check, self.bg.hit_check, self.field_obj.hit_check])

            # キャラが動いていなければメニューオープン可能
            if not self.player.is_moving:
                self.xmlui.open_by_event(XUEvent.Key.BTN_A, "menu")

    def draw(self):
        # プレイヤを中心に世界が動く。さす勇
        scroll_x = -self.player.x +160-32
        scroll_y = -self.player.y +160-32-8

        # ゲーム画面構築
        self.bg.draw(scroll_x, scroll_y)
        self.npc.draw(scroll_x, scroll_y)
        self.field_obj.draw(scroll_x, scroll_y)
        self.player.draw()

        # UIの描画(fieldとdefaultグループ)
        self.xmlui.draw()

    # メニューで起こったイベントの処理を行う
    def event(self, event:XUEventItem):
        match event:
            # かいだんチェック
            case "down_stairs":
                menu = self.xmlui.find_by_id("menu")
                if self.bg.check_stairs(menu, self.player.block_x, self.player.block_y):
                    # バトル開始
                    XUWinBase(menu).start_close()
                    self.fade_close()
                else:
                    msg_text = MsgDQ(menu.open("message").find_by_id("msg_text"))
                    msg_text.append_msg("かいだんがない")  # systemメッセージ

            # とびらチェック
            case "open_door":
                menu = self.xmlui.find_by_id("menu")
                door = self.field_obj.find_door(self.player.block_x, self.player.block_y)
                if door != None:
                    self.field_obj.open(door)
                    XUWinBase(menu).start_close()
                else:
                    msg_text = MsgDQ(menu.open("message").find_by_id("msg_text"))
                    msg_text.append_msg("とびらがない")  # systemメッセージ

        # 会話イベントチェック
        for talk_event in self.npc.TALK_EVENTS:
            if talk_event == event:
                menu = self.xmlui.find_by_id("menu")

                # メッセージウインドウを開く
                msg_text = MsgDQ(menu.open("message").find_by_id("msg_text"))

                talk = self.npc.check_talk(talk_event, self.player.block_x, self.player.block_y)
                if talk is not None:
                    msg_text.append_talk(talk, user_data.data)  # talkでテキスト開始
                else:
                    msg_text.append_msg("だれもいません")  # systemメッセージ

        # ウインドウが閉じたときの対応
        if event.startswith("close_win:"):
            # メッセージウインドウの時はメニューごと閉じる
            if event[len("close_win:"):].strip() == "message":
                menu = self.xmlui.find_by_id("menu")
                XUWinBase(menu).start_close()
