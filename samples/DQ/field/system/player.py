import pyxel
from typing import Callable

from xmlui.core import XMLUI,XUEvent,XUEventItem
from xmlui.ext.tilemap import XUETilemap
from xmlui.ext.scene import XUEActItem

from msg_dq import MsgDQ
from db import user_data

class PlayerMoveAct(XUEActItem):
    def __init__(self, player:"Player", move_x:int, move_y:int):
        super().__init__()
        self.player = player
        self.move_x = move_x
        self.move_y = move_y

    def waiting(self) -> bool:
        # プレイヤの移動
        if self.move_x < 0:
            self.player.x -= 1
            self.move_x += 1
        if self.move_x > 0:
            self.player.x += 1
            self.move_x -= 1
        if self.move_y < 0:
            self.player.y -= 1
            self.move_y += 1
        if self.move_y > 0:
            self.player.y += 1
            self.move_y -= 1

        # 移動完了チェック
        return self.move_x == 0 and self.move_y == 0

class Player:
    def __init__(self, xmlui:XMLUI, x:int, y:int):
        self.xmlui = xmlui

        # 座標
        self.x = x*16
        self.y = y*16
        self.move_x = 0
        self.move_y = 0

        # 表示イメージ設定
        self.anim_pat = [32, 33]
        self.tile = XUETilemap(1)

        # 死亡でFieldに飛ばされた時
        self.is_dead = user_data.hp <= 0
        if self.is_dead:
            user_data.hp = 1
            self.x = 8*16
            self.y = 9*16

            # メッセージウインドウを開く
            menu = self.xmlui.open("menu")
            msg_text = MsgDQ(menu.open("message").find_by_id("msg_text"))
            talk = "おお　{name}！\nしんでしまうとは　なにごとだ！\\p…………\\pちょっと　いってみたかったの\\pがんばってね"
            msg_text.append_talk(talk, user_data.data)  # talkでテキスト開始

    def move(self, event_now:set[XUEventItem], hitcheck_funcs:list[Callable[[int,int],bool]]):
        if XUEvent.Key.UP in event_now and all([not hit(self.block_x, self.block_y-1) for hit in hitcheck_funcs]):
            return PlayerMoveAct(self, 0, -16)
        if XUEvent.Key.DOWN in event_now and all([not hit(self.block_x, self.block_y+1) for hit in hitcheck_funcs]):
            return PlayerMoveAct(self, 0, 16)
        if XUEvent.Key.LEFT in event_now and all([not hit(self.block_x-1, self.block_y) for hit in hitcheck_funcs]):
            return PlayerMoveAct(self, -16, 0)
        if XUEvent.Key.RIGHT in event_now and all([not hit(self.block_x+1, self.block_y) for hit in hitcheck_funcs]):
            return PlayerMoveAct(self, 16, 0)
        return None

    @property
    def is_moving(self) -> bool:
        return self.move_x != 0 or self.move_y != 0

    @property
    def block_x(self) -> int:
        return self.x // 16

    @property
    def block_y(self) -> int:
        return self.y // 16

    def draw(self):
        self.tile._update()
        self.tile.draw(127, 127-8, self.anim_pat)
