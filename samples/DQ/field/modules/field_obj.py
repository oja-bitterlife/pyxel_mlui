from xmlui.ext.tilemap import XUETilemap
from db import fieldobj_data

class FieldObj:
    def __init__(self):
        self.tile_anim = XUETilemap(1)

    def draw(self, scroll_x, scroll_y):
        self.tile_anim.update()

        for field_obj in fieldobj_data.data:
            if field_obj["closed"]:
                self.tile_anim.draw(field_obj["block_x"]*16+scroll_x, field_obj["block_y"]*16+scroll_y, field_obj["anim_pat"])

    # ぶつかりチェック
    def hit_check(self, block_x:int, block_y:int):
        for field_obj in fieldobj_data.data:
            # 移動不可オブジェクトのみ当たる
            if not field_obj["movable"] and field_obj["closed"]:
                if field_obj["block_x"] == block_x and field_obj["block_y"] == block_y:
                    return True
        return False
    
    # 周りにドアがあるか調べる。鍵の数チェックは今回はナシで
    def find_door(self, block_x:int, block_y:int):
        for i,field_obj in enumerate(fieldobj_data.data):
            if field_obj["block_x"] == block_x-1 and field_obj["block_y"] == block_y and field_obj["type"] == "door":
                return i
            if field_obj["block_x"] == block_x+1 and field_obj["block_y"] == block_y and field_obj["type"] == "door":
                return i
            if field_obj["block_x"] == block_x and field_obj["block_y"]-1 == block_y and field_obj["type"] == "door":
                return i
            if field_obj["block_x"] == block_x and field_obj["block_y"]+1 == block_y and field_obj["type"] == "door":
                return i
        return None

    def open(self, data_no:int):
        fieldobj_data.open(data_no)
