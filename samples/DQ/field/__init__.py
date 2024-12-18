# フィールド関係
from field.system.player import Player
from field.system.bg import BG
from field.system.npc import NPC
from field.system.treasure import Treasure

# UI
from xmlui.core import XMLUI,XUEvent
from field.ui import msg_win,menu,talk_dir,tools

# シーン関係
from scene import SceneBase

class Field(SceneBase):
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

    def __del__(self):
        # 読みこんだUIの削除
        self.template.remove()

    def run(self):
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
        # if "start_battle" in self.xmlui.event.trg:
        #     return "battle"

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
