from xmlui.ext.tilemap import XUETileAnim,XUETileMap,XUETileSet

class TileAnim(XUETileAnim):
    def action(self):
        match self.tile_no:
            case 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9:
                offset = [0, 48, 64]
                self.anim_no = self.tile_no + offset[self.action_count % len(offset)]

class TileMap(XUETileMap):
    # ステージごとに初期化する
    def __init__(self, stage_no:int):
        super().__init__(
            XUETileSet.from_aseprite(f"assets/stage/tileset-{stage_no}.png", f"assets/stage/tileset-{stage_no}.json"),
            f"assets/stage/tilemap-{stage_no}.csv")

    def convert(self, anim:XUETileAnim) -> TileAnim:
        return TileAnim.from_base(anim)
