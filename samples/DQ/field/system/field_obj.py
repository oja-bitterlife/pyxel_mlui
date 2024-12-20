from xmlui.ext.tilemap import XUXTilemap
import db

class FieldObj:
    def __init__(self):
        self.tile_anim = XUXTilemap(1)

    def draw(self, scroll_x, scroll_y):
        self.tile_anim.update()

        for field_obj in db.field_obj_data:
            if field_obj.visible:
                self.tile_anim.draw(field_obj.x*16+scroll_x, field_obj.y*16+scroll_y, field_obj.anim_pat)

    def hit_check(self, block_x:int, block_y:int):
        for field_obj in db.field_obj_data:
            # 移動不可オブジェクトのみ当たる
            if not field_obj.movable:
                if field_obj.x == block_x and field_obj.y == block_y:
                    return True
        return False
    
    def find_door(self, block_x:int, block_y:int):
        for i,field_obj in enumerate(db.field_obj_data):
            if field_obj.x == block_x-1 and field_obj.y == block_y and field_obj.name == "door":
                return i
            if field_obj.x == block_x+1 and field_obj.y == block_y and field_obj.name == "door":
                return i
            if field_obj.x == block_x and field_obj.y-1 == block_y and field_obj.name == "door":
                return i
            if field_obj.x == block_x and field_obj.y+1 == block_y and field_obj.name == "door":
                return i
        return None