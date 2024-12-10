import pyxel

class Treasure:
    treasure = [
        # typ,        x, y, color, detai
        ["tresure1", 9, 9, 10, "やくそう"],
        ["tresure2", 10, 9, 10, "100G"],
        ["tresure3", 11, 6, 10, "10G"],
    ]
    def draw(self, scroll_x, scroll_y):
        for treasure in self.treasure:
            pyxel.rect(treasure[1]*16+scroll_x+1, treasure[2]*16+scroll_y+2, 14, 12, treasure[3])
