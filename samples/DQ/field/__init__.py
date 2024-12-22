import pyxel

# フィールド関係
from field.system.player import Player
from field.system.bg import BG
from field.system.npc import NPCManager
from field.system.field_obj import FieldObj
from msg_dq import MsgDQ
from db import user_data

# UI
from xmlui.core import XMLUI,XUElem,XUEvent,XUWinBase
from xmlui.ext.scene import XUXScene

from field.ui import msg_win,menu,talk_dir,tools
from battle import Battle  # 次シーン


class Field(XUXScene):
    def __init__(self, xmlui:XMLUI):
        super().__init__(xmlui)

        # ゲーム本体(仮)
        self.player = Player(10, 10)
        self.bg = BG()
        self.npc = NPCManager()
        self.field_obj = FieldObj()

        # UIの読み込み
        self.template = self.xmlui.load_template("assets/ui/field.xml")
        for module in [msg_win, menu, talk_dir, tools]:
            module.ui_init(self.template)

        # 画像読み込み
        pyxel.images[1].load(0, 0, "assets/images/field_tile.png" )

    def closed(self):
        self.template.remove()  # 読みこんだUIの削除
        XUXScene.current_scene = Battle(self.xmlui)

    def update(self):
        # UIメニューが開いていたらキャラが動かないように
        if self.xmlui.exists_id("menu"):
            # メニューイベント処理
            menu = self.xmlui.find_by_id("menu")
            self.menu_event(menu, self.xmlui.event)
        else:
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
    def menu_event(self, menu:XUElem, event:XUEvent):
        # 会話イベントチェック
        for talk_event in self.npc.TALK_EVENTS:
            if talk_event in event.trg:
                # メッセージウインドウを開く
                msg_text = MsgDQ(menu.open("message").find_by_id("msg_text"))

                talk = self.npc.check_talk(talk_event, self.player.block_x, self.player.block_y)
                if talk is not None:
                    msg_text.append_talk(talk, user_data.data)  # talkでテキスト開始
                else:
                    msg_text.append_msg("だれもいません")  # systemメッセージ

        # かいだんチェック
        if "down_stairs" in menu.xmlui.event.trg:
            if self.bg.check_stairs(menu, self.player.block_x, self.player.block_y):
                # バトル開始
                XUWinBase(menu).start_close()
                self.end_scene()
            else:
                msg_text = MsgDQ(menu.open("message").find_by_id("msg_text"))
                msg_text.append_msg("かいだんがない")  # systemメッセージ

        # とびらチェック
        if "open_door" in menu.xmlui.event.trg:
            door = self.field_obj.find_door(self.player.block_x, self.player.block_y)
            if door != None:
                self.field_obj.open(door)
                XUWinBase(menu).start_close()
            else:
                msg_text = MsgDQ(menu.open("message").find_by_id("msg_text"))
                msg_text.append_msg("とびらがない")  # systemメッセージ
