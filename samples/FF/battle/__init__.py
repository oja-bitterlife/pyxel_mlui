import pyxel

# バトル画面
from xmlui.core import XURect
from xmlui.lib.debug import DebugXMLUI
from xmlui.ext.scene import XUEFadeScene

# ui
import ui_common
from FF.battle import ui_command,ui_status,act

# データ
from db import enemy_data,user_data

class Battle(XUEFadeScene):
    def __init__(self):
        super().__init__(DebugXMLUI(pyxel.width, pyxel.height))

        # XMLの読み込み
        self.xmlui.load_template("assets/ui/common.xml")
        self.xmlui.load_template("assets/ui/battle.xml")
        self.xmlui.open("ui_battle")

        ui_common.ui_init(self.xmlui)
        ui_status.ui_init(self.xmlui)
        ui_command.ui_init(self.xmlui)

        self.enemy_img = pyxel.Image.from_image(filename="assets/images/fantasy_goblin.png")
        self.bg_img = pyxel.Image.from_image(filename="assets/images/bg.png")
        self.player_imgs = [
            pyxel.Image.from_image(filename="assets/images/heishi.png"),
            pyxel.Image.from_image(filename="assets/images/basaka.png"),
            pyxel.Image.from_image(filename="assets/images/yousei.png"),
            pyxel.Image.from_image(filename="assets/images/majyo.png"),
        ]

        # actとのデータ受け渡し用
        self.xmlui.data_ref = act.BattleData(self)

        # 敵の座標設定
        for data in enemy_data.data:
            x = data["x"]*48 + 24
            y = data["y"]*56 + 56
            self.xmlui.data_ref.enemy_pos.append(XURect(x, y, 48, 56))

        # 最初をスライドインに変更
        self.clear_act()
        self.add_act(act.BattleStart(self.xmlui), act.BattleCmdStart(self.xmlui))

    def closed(self):
        self.xmlui.close()

    def draw(self):
        # バトル中のデータ一元管理を参照する
        battle_data = self.xmlui.data_ref

        # 背景の表示
        pyxel.blt(0, 0, self.bg_img, 0, 0, 256, 40, 0)

        # 敵の表示
        for i in range(len(enemy_data.data)):
            x: float = battle_data.enemy_pos[i].x - 128*self.alpha  # スライドイン
            pyxel.blt(x, battle_data.enemy_pos[i].y, self.enemy_img, 0, 0, 64, 64, 0)

        # プレイヤの表示
        front_target = 256-80
        for i,data in enumerate(user_data.player_data):
            img = self.player_imgs[i]
            x = 256-32 - int((1+(1-data["fb"])) * 16*(1-self.alpha))

            # 順番のキャラは前に出す
            battle_data.player_offset[i] += battle_data.player_move_dir[i] * 4
            if x + battle_data.player_offset[i] < front_target:
                battle_data.player_offset[i] = front_target - x
                battle_data.player_move_dir[i] = 0
            elif battle_data.player_offset[i] > 0:
                battle_data.player_move_dir[i] = 0

            x += battle_data.player_offset[i]

            pyxel.blt(x, 40+i*32, img, 0, 0, 64, 64, 0)

        # UIの表示
        self.xmlui.draw()
