import dataclasses

from xmlui.core import XUElem
from xmlui.ext.tilemap import XUXTilemap

@dataclasses.dataclass
class BGType:
    name: str
    movable: bool
    anim_pat: list[int]|int

bgtype_data = [
    BGType('none', False, 0),   # 0
    BGType('roof', False, 6),   # 1
    BGType('wall', False, 7),   # 2
    BGType('floor', True, 5),   # 3
    BGType('chair', False, 23), # 4
    BGType('stair', True, 21), # 5
]

class BG:
    # 背景
    blocks = [
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,1,1,1,1,1],
        [1,1,1,1,1,2,3,3,3,3,3,3,3,3,2,1,1,1,1,1],
        [1,1,1,1,1,2,3,4,4,4,4,4,4,3,2,1,1,1,1,1],
        [1,1,1,1,1,2,3,4,3,4,4,3,4,3,2,1,1,1,1,1],
        [1,1,1,1,1,2,3,3,3,3,3,3,3,3,2,1,1,1,1,1],
        [1,1,1,1,1,2,3,3,3,3,3,3,3,3,2,1,1,1,1,1],
        [1,1,1,1,1,2,3,3,3,3,3,3,3,3,2,1,1,1,1,1],
        [1,1,1,1,1,2,2,2,2,3,2,2,2,2,2,1,1,1,1,1],
        [1,1,1,1,1,2,3,3,3,3,3,3,3,5,2,1,1,1,1,1],
        [1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    ]

    def __init__(self) -> None:
        self.tile_anim = XUXTilemap(1)

    def draw(self, scroll_x, scroll_y):
        # アニメ付き背景であれば更新
        self.tile_anim.update()

        # 地形描画
        for y,line in enumerate(self.blocks):
            for x,type_ in enumerate(line):
                data = bgtype_data[type_]
                self.tile_anim.draw(x*16+scroll_x, y*16+scroll_y, data.anim_pat)

    def hit_check(self, block_x:int, block_y:int) -> bool:
        type_ = self.blocks[block_y][block_x]
        data = bgtype_data[type_]
        return not data.movable

    # 階段チェック
    def check_stairs(self, menu:XUElem, block_x:int, block_y:int) -> bool:
        type_ = self.blocks[block_y][block_x]
        data = bgtype_data[type_]
        return data.name == 'stair'
