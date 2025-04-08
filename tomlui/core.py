# TOMLとSQLiteを使うよ
import toml,sqlite3,sqlalchemy

# SQLAlchemy関連のインポート
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    MetaData,
    Table,
)
from sqlalchemy.orm import sessionmaker, declarative_base, Query


# 型を使うよ
from typing import Callable,Any,Self
from enum import StrEnum

# 日本語対応
import unicodedata

# その他よく使う奴
import re
from copy import deepcopy

# ログも基本機能に
import logging
logging.basicConfig()


# 描画領域計算用
# #############################################################################
class XURect:
    class Align(StrEnum):
        CENTER = "center"
        LEFT = "left"
        RIGHT = "right"
        TOP = "top"
        BOTTOM = "bottom"

        @classmethod
        def from_str(cls, type_:str) -> Self:
            for v in cls.__members__.values():
                if v == type_.lower():
                    return v
            raise RuntimeError(f"Invalid Align type: {type_}")

    def __init__(self, x:int, y:int, w:int, h:int):
        self.x = x
        self.y = y
        self.w = max(0, w)
        self.h = max(0, h)

    def copy(self) -> "XURect":
        return XURect(self.x, self.y, self.w, self.h)

    # 変換
    def intersect(self, other:"XURect") -> "XURect":
        right = min(self.x+self.w, other.x+other.w)
        left = max(self.x, other.x)
        bottom = min(self.y+self.h, other.y+other.h)
        top = max(self.y, other.y)
        return XURect(left, top, right-left, bottom-top)

    def inflate(self, w, h) -> "XURect":
        return XURect(self.x-w, self.y-h, self.w+w*2, self.h+h*2)

    # offset化
    def to_offset(self) -> "XURect":
        return XURect(0, 0, self.w, self.h)

    # 内包チェック
    def contains_x(self, x:int) -> bool:
        return self.x <= x < self.x+self.w

    def contains_y(self, y:int) -> bool:
        return self.y <= y < self.y+self.h

    def contains(self, x, y) -> bool:
        return self.x <= x < self.x+self.w and self.y <= y < self.y+self.h

    # 空チェック
    @property
    def is_empty(self) -> int:
        return self.w <= 0 or self.h <= 0

    # 座標取得
    @property
    def center_x(self) -> int:
        return self.x + self.w//2

    @property
    def center_y(self) -> int:
        return self.y + self.h//2

    @property
    def right(self) -> int:
        return self.x + self.w

    @property
    def bottom(self) -> int:
        return self.y + self.h

    # 座標をずらす量を取得(w,h = 内容物のw,h)。配置するためにどれだけ座標をずらすべきか取得する
    @classmethod
    def align_offset(cls, area_w:int, area_h:int, w:int=0, h:int=0, align:Align=Align.CENTER, valign:Align=Align.CENTER) -> tuple[int, int]:
        area = XURect(0, 0, area_w, area_h)
        match align:
            case cls.Align.LEFT:
                offset_x = 0
            case cls.Align.CENTER:
                offset_x = (area.w-w)//2
            case cls.Align.RIGHT:
                offset_x = area.w - w
            case _:
                raise ValueError(f"align:{align} is not supported.")

        match valign:
            case cls.Align.TOP:
                offset_y = 0
            case cls.Align.CENTER:
                offset_y = (area.h-h)//2
            case cls.Align.BOTTOM:
                offset_y = area.h - h
            case _:
                raise ValueError(f"align:{valign} is not supported.")
        return offset_x,offset_y

    # 配置座標取得
    def aligned_pos(self, w:int, h:int, align:Align=Align.CENTER, valign:Align=Align.CENTER) -> tuple[int, int]:
        offset_x, offset_y = self.align_offset(self.w, self.h, w, h, align, valign)
        return self.x + offset_x, self.y + offset_y

    def __repr__(self) -> str:
        return f"RECT({self.x}, {self.y}, {self.w}, {self.h})"


# SQLAlchemyのBase
TOMLUI_Base = declarative_base()

# SQLAlchemyのモデル定義
class XUStateCore(TOMLUI_Base):
    __tablename__ = "STATE_CORE"

    id = Column(Integer, primary_key=True, autoincrement=True)  # UIパーツごとに一意のID
    value = Column(String)  # 汎用値取得
    selected = Column(Integer)  # 選択アイテムの選択状態
    x = Column(Integer)  # 親からの相対座標x
    y = Column(Integer)  # 親からの相対座標y
    abs_x = Column(Integer)  # 絶対座標x
    abs_y = Column(Integer)  # 絶対座標y
    w = Column(Integer)  # elementの幅
    h = Column(Integer)  # elementの高さ
    update_count = Column(Integer)  # updateが行われた回数
    use_event = Column(String)  # eventの検知方法, listener or absorber or none
    enable = Column(Boolean)  # イベント有効フラグ(表示は使う側でどうするか決める)
    removed = Column(Boolean)  # 内部管理用削除済みフラグ


# TOMLのElement管理
class TOMLUI:
    def __init__(self):
        # SQLAlchemyのエンジン作成
        self.engine = create_engine("sqlite:///:memory:")

        # テーブル作成
        TOMLUI_Base.metadata.create_all(self.engine)

        # セッション作成
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    # # テーブルアクセス
    # def query(self, cls:type) -> Query[Any]:
    #     return self.session.query(cls)
