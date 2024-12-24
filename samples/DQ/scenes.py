# 循環参照対策
# 各シーンクラスを使うときはimport sceneして、scene.クラス名で使用する
from xmlui.ext.scene import XUXSceneManager
from ui_common import xmlui

from title import Title
from field import Field
from battle import Battle

# 最初はタイトル
#scene_manager = XUXSceneManager(scenes.Title(xmlui))
#scene_manager = XUXSceneManager(scenes.Field(xmlui))
scene_manager = XUXSceneManager(Battle(xmlui))
