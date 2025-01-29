from xmlui.core import XURect
from xmlui.ext.tilemap import XUETileSet
from db import fieldobj_data

class FieldObj:
    def __init__(self):
        rects = []
        for field_obj in fieldobj_data.data:
            pat = field_obj["anim_pat"]
            rects.append(XURect(pat%16*16, pat//16*16, 16, 16))
        self.tile_obj = XUETileSet(1, rects)

    def draw(self, scroll_x, scroll_y):
        for i,field_obj in enumerate(fieldobj_data.data):
            if field_obj["closed"]:
                self.tile_obj.draw(i, field_obj["block_x"]*16+scroll_x, field_obj["block_y"]*16+scroll_y)

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
        for door_no,field_obj in enumerate(fieldobj_data.data):
            if field_obj["block_x"] == block_x-1 and field_obj["block_y"] == block_y and field_obj["type"] == "door":
                return door_no
            if field_obj["block_x"] == block_x+1 and field_obj["block_y"] == block_y and field_obj["type"] == "door":
                return door_no
            if field_obj["block_x"] == block_x and field_obj["block_y"]-1 == block_y and field_obj["type"] == "door":
                return door_no
            if field_obj["block_x"] == block_x and field_obj["block_y"]+1 == block_y and field_obj["type"] == "door":
                return door_no
        return None

    def open(self, data_no:int):
        fieldobj_data.open(data_no)

    def is_opened(self, data_no:int):
        return fieldobj_data.is_opened(data_no)
