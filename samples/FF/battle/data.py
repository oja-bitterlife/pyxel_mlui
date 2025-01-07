from xmlui.core import XURect
from xmlui.ext.scene import XUEFadeScene

# バトル中のデータ持ち運び用
class BattleData:
    JOBS = ["heishi", "basaka", "yousei", "majyo"]

    def __init__(self, scene:XUEFadeScene):
        self.scene = scene
        self.enemy_rect:list[XURect] = []

        self.player_idx = -1
        self.player_rect:list[XURect] = []

        self.player_move_dir = [0, 0, 0, 0]
        self.player_offset = [0, 0, 0, 0]
        self.player_target = []  # プレイヤが選んだターゲット(-で味方側)

