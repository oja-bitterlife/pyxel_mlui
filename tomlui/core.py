# TOMLとSQLiteを使うよ
import toml,sqlite3,sqlalchemy

# 型を使うよ
from typing import Callable,Any,Self,cast
from enum import StrEnum,Enum,auto

# 日本語対応
import unicodedata

# その他よく使う奴
import re
from copy import deepcopy

# ログも基本機能に
import logging
logging.basicConfig()

# SQLAlchemy関連のインポート
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    REAL,
    String,
    Boolean,
    MetaData,
    Table,
    ForeignKey,
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

ORMBase = declarative_base()

class XUStatePos(ORMBase):
    __tablename__ = "STATE_POS"
    id = Column(Integer, ForeignKey('STATE_CORE.id'), primary_key=True)  # 1to1で

    x = Column(Integer, default=0)  # 親からの相対座標x
    y = Column(Integer, default=0)  # 親からの相対座標y
    abs_x = Column(Integer)  # 絶対座標x
    abs_y = Column(Integer)  # 絶対座標y
    w = Column(Integer, default=256)  # elementの幅
    h = Column(Integer, default=256)  # elementの高さ

class XUStateCore(ORMBase):
    __tablename__ = "STATE_CORE"

    id = Column(Integer, primary_key=True, autoincrement=True)  # UIパーツごとに一意のID
    tag = Column(String, nullable=False)  # タグ名(tomlのtable名)
    text = Column(String)  # ラベル
    value = Column(String)  # 汎用値
    update_count = Column(Integer, default=0)  # updateが行われた回数
    removed = Column(Boolean, default=False)  # 内部管理用削除済みフラグ

    pos = relationship(XUStatePos, uselist=False)

class XUStateEvent(ORMBase):
    __tablename__ = "STATE_EVENT"
    id = Column(Integer, ForeignKey('STATE_CORE.id'), primary_key=True)  # 1to1で

    use_event = Column(String)  # eventの検知方法, listener or absorber
    enable = Column(Boolean, default=True)  # イベント有効フラグ(表示は使う側でどうするか決める)

    base = relationship(XUStateCore, uselist=False)

class XUSelectBase(ORMBase):
    __tablename__ = "STATE_SELECT"
    id = Column(Integer, ForeignKey('STATE_CORE.id'), primary_key=True)  # 1to1で

    selected = Column(Integer)  # 選択アイテムの選択状態
    item_w = Column(Integer, default=0)  # 選択item配置間隔x
    item_h = Column(Integer, default=0)  # 選択item配置間隔y

    base = relationship(XUStateCore, uselist=False)

class XUSelectItem(ORMBase):
    __tablename__ = "STATE_SELECT_ITEM"
    id = Column(Integer, ForeignKey('STATE_CORE.id'), primary_key=True)  # 1to1で

    base = relationship(XUStateCore, uselist=False)
    action = Column(String)  # 押された用




class TOMLUI():
    def __init__(self):
        # sqlalchemyの初期化
        self.engine = create_engine("sqlite:///:memory:")
        self.inspector = sqlalchemy.inspect(self.engine)  # デバッグ用
        self.mk_session = sessionmaker(bind=self.engine, autocommit=False)

        # テーブル作成
        ORMBase.metadata.create_all(self.engine)

        # セッション開始
        self.session = self.mk_session()

    # TOMLを読み込んで辞書ツリーで返すユーティリティ
    # def load_toml(self, path:str):
    #     def __rec_import_toml(table:Any, toml_dict:dict, parent:int|None=None):

    #         # 自分のデータを処理する
    #         data = {"tag":table, "parent":parent}
    #         for key,value in toml_dict.items():
    #             # 無視するキー
    #             if key == "type":
    #                 continue

    #             # 子は後回しでまずは自分だけ
    #             if not isinstance(value, dict) and not (isinstance(value, list) and isinstance(value[0], dict)):
    #                 data[key] = value

    #         match toml_dict.get("type", None):
    #             case "select":
    #                 item = XUStateSelect(**data)
    #             case "select_item":
    #                 item = XUStateSelectItem(**data)
    #             case _:
    #                 item = XUStateCore(**data)

    #         self.session.add(item)
    #         self.session.commit()
    #         parent = cast(int, item.id)

    #         # 子を処理する
    #         for key,value in toml_dict.items():
    #             if isinstance(value, dict):
    #                 __rec_import_toml(key, value, parent)
    #             if (isinstance(value, list) and isinstance(value[0], dict)):
    #                 for v in value:
    #                     __rec_import_toml(key, v, parent)

    #     return  __rec_import_toml("root", toml.load(path))


