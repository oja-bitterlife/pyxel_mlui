import pyxel

from xmlui.core import XMLUI,XUEvent,XUEventItem,XUWinInfo
from xmlui.lib.debug import DebugXMLUI
from xmlui.ext.scene import XUEFadeScene,XUEActItem

from db import user_data

# フィールド関係
from field.modules.player import Player
from field.modules.bg import BG
from field.modules.npc import NPCManager
from field.modules.field_obj import FieldObj

# UI
import ui_common
from msg_dq import MsgDQ
from field.ui import msg_win,menu,talk_dir,tools

# メニューが開いている状態
class MenuOpenAct(XUEActItem):
    def __init__(self, xmlui:XMLUI):
        super().__init__()
        self.menu = xmlui.open("menu")

    # メニューが閉じられるまで待機
    def waiting(self):
        if self.menu.removed:
            self.finish()

class Field(XUEFadeScene):
    def __init__(self):
        super().__init__(DebugXMLUI(pyxel.width, pyxel.height))

        # UIの読み込み
        self.xmlui.load_template("assets/ui/field.xml")
        self.xmlui.load_template("assets/ui/common.xml")

        ui_common.ui_init(self.xmlui)
        msg_win.ui_init(self.xmlui)
        menu.ui_init(self.xmlui)
        talk_dir.ui_init(self.xmlui)
        tools.ui_init(self.xmlui)

        # ゲーム本体(仮)
        self.player = Player(self.xmlui, 10, 10)
        self.bg = BG()
        self.npc = NPCManager()
        self.field_obj = FieldObj()

        # 画像読み込み
        pyxel.images[1].load(0, 0, "assets/images/field_tile.png" )

    def closed(self):
        self.xmlui.close()  # 読みこんだUIの削除

        # バトルへ
        from battle import Battle
        self.set_next_scene(Battle())

    # 何もしていない(actがない)ときだけここにくる、Idle関数
    def update(self):
        # プレイヤの移動。移動できれば移動Actが返る
        player_move_act = self.player.move(self.xmlui.event.now, [
            self.npc.hit_check,  # 当たり判定リスト
            self.bg.hit_check,
            self.field_obj.hit_check])

        if player_move_act:
            self.add_act(player_move_act)

        # キャラが動いていなければメニューオープン可能
        if self.xmlui.event.check_now(XUEvent.Key.BTN_A):
            self.add_act(MenuOpenAct(self.xmlui))

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
                    XUWinInfo(menu).setter.start_close()
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
                    XUWinInfo(menu).setter.start_close()
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
                XUWinInfo(menu).setter.start_close()
