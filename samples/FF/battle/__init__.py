import math
import pyxel

# バトル画面
from xmlui.core import XURect,XUTextUtil
from xmlui.lib.debug import DebugXMLUI
from xmlui.ext.scene import XUEFadeScene

# ui
import ui_common
from FF.battle import ui_command,ui_status,act,ui_target,ui_result
from FF.battle.act import BattleStart,BattlePlayPlayerDamage
from FF.battle.data import BattleData

# データ
from db import enemy_data,user_data
from system import system_font

class Battle(XUEFadeScene):
    def __init__(self):
        xmlui = DebugXMLUI[act.BattleData](pyxel.width, pyxel.height)
        super().__init__(xmlui)

        # XMLの読み込み
        self.xmlui.load_template("assets/ui/common.xml")
        self.xmlui.load_template("assets/ui/battle.xml")
        self.xmlui.open("ui_battle")

        ui_common.ui_init(xmlui)
        ui_status.ui_init(xmlui)
        ui_command.ui_init(xmlui)
        ui_target.ui_init(xmlui)
        ui_result.ui_init(xmlui)

        self.enemy_img = pyxel.Image.from_image(filename="assets/images/fantasy_goblin.png")
        self.bg_img = pyxel.Image.from_image(filename="assets/images/bg.png")
        self.player_imgs = [
            pyxel.Image.from_image(filename="assets/images/heishi.png"),
            pyxel.Image.from_image(filename="assets/images/basaka.png"),
            pyxel.Image.from_image(filename="assets/images/yousei.png"),
            pyxel.Image.from_image(filename="assets/images/majyo.png"),
        ]

        # actとのデータ受け渡し用
        battle_data = act.BattleData(self)

        # 敵の座標設定
        for data in enemy_data.data:
            # 背景分ずらす
            battle_data.enemy_rect.append(XURect(data["x"], data["y"] + self.bg_img.height, self.enemy_img.width, self.enemy_img.height))

        # プレイヤの座標設定
        for i,data in enumerate(user_data.player_data):
            x = 256-48 - (1-data["fb"])*16
            y = 40 + i*32
            battle_data.player_rect.append(XURect(x, y, self.player_imgs[i].width, self.player_imgs[i].height))

        self.xmlui.data_ref = battle_data

        # 最初をスライドインに変更
        self.clear_act()
        self.add_act(BattleStart(self.xmlui))

    def closed(self):
        self.xmlui.close()

    def draw(self):
        # バトル中のデータ一元管理を参照する
        battle_data:BattleData = self.xmlui.data_ref

        # 背景の表示
        pyxel.blt(0, 0, self.bg_img, 0, 0, 256, 40, 0)

        # 敵の表示
        for i in range(len(enemy_data.data)):
            rect = battle_data.enemy_rect[i].copy()
            x = rect.x - int(128*self.alpha)  # スライドイン
            pyxel.blt(x, rect.y, self.enemy_img, 0, 0, rect.w, rect.h, 0)

        # プレイヤの表示
        front_target = 256-80
        for i,data in enumerate(user_data.player_data):
            img = self.player_imgs[i]
            rect = battle_data.player_rect[i]

            x = max(rect.x, int(256-48-16 + self.alpha*32))  # スライドイン

            # 順番のキャラを前に出す
            battle_data.player_offset[i] += battle_data.player_move_dir[i] * 4
            if x + battle_data.player_offset[i] < front_target:
                battle_data.player_offset[i] = front_target - x
                battle_data.player_move_dir[i] = 0
            elif battle_data.player_offset[i] > 0:
                battle_data.player_move_dir[i] = 0
            x += battle_data.player_offset[i]

            pyxel.blt(x, rect.y, img, 0, 0, rect.w, rect.h, 0)

        # ダメージ表示
        if isinstance(self.current_act, BattlePlayPlayerDamage):
            for damage in battle_data.damage:
                damage.update()

                if damage.count < 10:
                    alpha = damage.count/10
                    alpha = min(1, abs(alpha - 0.5)*2)
                    offset_y = int((1-pow(alpha, 2)) * 32)
                else:
                    alpha = (damage.count-10)/10
                    alpha = min(1, abs(alpha - 0.5)*2)
                    offset_y = int((1-pow(alpha, 2)) * 16)

                if damage.target >= 0:
                    area = battle_data.enemy_rect[damage.target]
                    offset_y -= self.enemy_img.height
                else:
                    area = battle_data.player_rect[abs(damage.target)-1]
                    offset_y -= area.h

                damage_text = XUTextUtil.format_zenkaku(f"{damage.damage}")
                x = area.center_x - system_font.text_width(damage_text)//2
                y = area.y - offset_y - system_font.size
                pyxel.text(x, y, damage_text, 8, system_font.font)

        # UIの表示
        self.xmlui.draw()
