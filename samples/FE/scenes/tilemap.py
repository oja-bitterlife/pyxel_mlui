from xmlui.ext.tilemap import XUETileAnim,XUETileMap,XUETileSet

class TileAnim(XUETileAnim):
    def converted(self):
        # 海岸のアニメーションを設定
        match self.tile_no_list[0]:
            case 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9:
                self.tile_no_list  = [self.tile_no_list[0] + offset for offset in [0, 48, 64]]

class TileMap(XUETileMap[XUETileAnim]):
    # ステージごとに初期化する
    def __init__(self, *, stage_no:int):
        super().__init__(
            XUETileSet.from_aseprite(f"assets/stage/tileset-{stage_no}.png", f"assets/stage/tileset-{stage_no}.json"),
            f"assets/stage/tilemap-{stage_no}.csv")

    def convert(self, anim:XUETileAnim) -> TileAnim:
        return TileAnim.from_base(anim)
