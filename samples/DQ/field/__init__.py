import pyxel

# フィールド関係
from field.system.player import Player
from field.system.bg import BG
from field.system.npc import NPC
from field.system.treasure import Treasure

# UI
from xmlui.core import XMLUI,XUEvent
from xmlui.ext.scene import XUXScene

from field.ui import msg_win,menu,talk_dir,tools
from battle import Battle  # 次シーン


class Field(XUXScene):
    def __init__(self, xmlui:XMLUI):
        super().__init__(xmlui)

        # ゲーム本体(仮)
        self.player = Player(10, 10)
        self.bg = BG()
        self.npc = NPC()
        self.treasure = Treasure()

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
        if not self.xmlui.exists_id("menu"):
            # プレイヤの移動
            self.player.update(self.bg.blocks, self.npc.npc_data)

            # キャラが動いていなければメニューオープン可能
            if not self.player.is_moving:
                self.xmlui.open_by_event(XUEvent.Key.BTN_A, "menu")

        else:
            menu = self.xmlui.find_by_id("menu")

            # 会話イベントチェック
            self.npc.check_talk(menu, self.player)
            self.bg.check_door(menu, self.player)
            self.bg.check_stairs(menu, self.player)

        # バトル開始
        if "start_battle" in self.xmlui.event.trg:
            self.end_scene()

    def draw(self):
        # プレイヤを中心に世界が動く。さす勇
        scroll_x = -self.player.x +160-32
        scroll_y = -self.player.y +160-32-8

        # ゲーム画面構築
        self.bg.draw(scroll_x, scroll_y)
        self.npc.draw(scroll_x, scroll_y)
        self.treasure.draw(scroll_x, scroll_y)
        self.player.draw()

        # UIの描画(fieldとdefaultグループ)
        self.xmlui.draw()
