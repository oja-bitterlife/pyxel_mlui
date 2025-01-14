from xmlui.core import XURect
from xmlui.ext.scene import XUEFadeScene

from xmlui.ext.timer import XUETimeout

from db import user_data

class BattleDamage(XUETimeout):
    def __init__(self, damage:int, hit:int, target:int):
        super().__init__(24)
        self.damage = damage
        self.hit = hit
        self.target = target

# バトル中のデータ持ち運び用
class BattleData:
    JOBS = ["heishi", "basaka", "yousei", "majyo"]

    def __init__(self, scene:XUEFadeScene):
        self.scene = scene

        # 敵
        self.enemy_idx = -1
        self.enemy_rect:list[XURect] = []  # 基準位置

        # プレイヤ
        self.player_idx = -1
        self.player_rect:list[XURect] = []  # 基準位置

        # プレイヤがアクティブな時に一番前に出す用
        self.player_move_dir = [0, 0, 0, 0]
        self.player_offset = [0, 0, 0, 0]

        # ターゲット
        self.target = [0, 0, 0, 0]  # プレイヤが選んだターゲット(-で味方側)

        # コマンド
        self.command = ["", "", "", ""]

        # ダメージ表示
        self.damage:list[BattleDamage] = []

    @property
    def is_player_turn(self) -> bool:
        return self.enemy_idx < 0
