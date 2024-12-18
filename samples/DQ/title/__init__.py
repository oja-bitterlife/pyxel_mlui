import pyxel

# タイトル画面
from xmlui.core import XMLUI
from title.ui import start,speed
from scene import SceneBase

# 次シーン
from field import Field

class Title(SceneBase):
    NEXT_SCENE_EVENT = "game_start"

    def __init__(self, xmlui:XMLUI):
        super().__init__(xmlui)

        # XMLの読み込み
        self.template = self.xmlui.load_template("assets/ui/title.xml")
        self.xmlui.open("game_title")  # game_title以下表示開始

        # ui初期化
        start.ui_init(self.template)
        speed.ui_init(self.template)

        self.img = pyxel.Image.from_image(filename="assets/images/title.png")

    def __del__(self):
        # XMLの解放
        self.template.remove()


    def run(self):
        # 画面の描画
        pyxel.blt(0, 0, self.img, 0, 0, self.img.width, self.img.height)

        # UIの表示
        self.xmlui.draw()
        if "start" in self.xmlui.event.trg:  # startが実行された
            super().end_run()

    def closed(self):
        SceneBase.current_scene = Field(self.xmlui)

