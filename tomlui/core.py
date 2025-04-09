# TOMLとSQLiteを使うよ
import toml,sqlite3

# 型を使うよ
from typing import Callable,Any,Self
from enum import StrEnum,Enum,auto

# 日本語対応
import unicodedata

# その他よく使う奴
import re
from copy import deepcopy

# ログも基本機能に
import logging
logging.basicConfig()

# SQLのテーブル定義
class XUDBColumn:
    class ValueType(Enum):
        Integer = auto()
        Real = auto()
        String = auto()
        Boolean = auto()

    def __init__(self, value_type:ValueType, *, default:Any=None, primary_key:bool=False, unique:bool=False, autoincrement:bool=False, nullable:bool=True):
        self.value_type = value_type
        self.default = default
        self.primary_key = primary_key
        self.unique = unique
        self.autoincrement = autoincrement
        self.nullable = nullable

    def to_sql(self):
        match self.value_type:
            case XUDBColumn.ValueType.Integer | XUDBColumn.ValueType.Boolean:
                sql = "INTEGER"
            case XUDBColumn.ValueType.String:
                sql = "TEXT"
            case XUDBColumn.ValueType.Real:
                sql = "REAL"
            case _:
                raise Exception("unknown type")

        if self.default is not None:
            sql += f" DEFAULT {self.default}"

        if self.primary_key:
            sql += " PRIMARY KEY"
        if self.unique:
            sql += " UNIQUE"
        if self.autoincrement:
            sql += " AUTOINCREMENT"
        if not self.nullable or self.default is not None:
            sql += " NOT NULL"
        return sql

class XUDBStateCore:
    __tablename__ = "STATE_CORE"
    core = {
        "id": XUDBColumn(XUDBColumn.ValueType.Integer, primary_key=True, autoincrement=True),  # UIパーツごとに一意のID
        "value": XUDBColumn(XUDBColumn.ValueType.String),  # 汎用値取得
        "selected": XUDBColumn(XUDBColumn.ValueType.Integer),  # 選択アイテムの選択状態
        "x": XUDBColumn(XUDBColumn.ValueType.Integer, default=0),  # 親からの相対座標x
        "y": XUDBColumn(XUDBColumn.ValueType.Integer, default=0),  # 親からの相対座標y
        "abs_x": XUDBColumn(XUDBColumn.ValueType.Integer),  # 絶対座標x
        "abs_y": XUDBColumn(XUDBColumn.ValueType.Integer),  # 絶対座標y
        "w": XUDBColumn(XUDBColumn.ValueType.Integer, default=256),  # elementの幅
        "h": XUDBColumn(XUDBColumn.ValueType.Integer, default=256),  # elementの高さ
        "update_count": XUDBColumn(XUDBColumn.ValueType.Integer, default=0),  # updateが行われた回数
        "use_event": XUDBColumn(XUDBColumn.ValueType.String),  # eventの検知方法, listener or absorber or none
        "enable": XUDBColumn(XUDBColumn.ValueType.Boolean, default=True),  # イベント有効フラグ(表示は使う側でどうするか決める)
        "removed": XUDBColumn(XUDBColumn.ValueType.Boolean, default=False),  # 内部管理用削除済みフラグ
    }

    def create_state_table(self, db:sqlite3.Connection):
        # 状態管理コアテーブル
        table_sql = ",\n".join([f"{column_key} {column.to_sql()}" for column_key,column in self.core.items()])
        db.execute(f"CREATE TABLE IF NOT EXISTS STATE_CORE ({table_sql})")

# TOMLのElement管理
class TOMLUI:
    def __init__(self):
        # UIの状態テーブルの作成
        self.db:sqlite3.Connection = sqlite3.connect(":memory:")
        self.db.row_factory = sqlite3.Row

        self.state_core = XUDBStateCore()
        self.state_core.create_state_table(self.db)

    # TOMLを読み込んでメモリDB上にINSERT
    def import_toml(self, path:str):
        def __rec_import_toml(toml_dict:dict):
            # 要素ごとにinsertしていく
            for key,value in toml_dict.items():
                if isinstance(value,dict):
                    __rec_import_toml(value)
                else:
                    if key in self.state_core.core.keys():
                        self.db.execute(f"INSERT INTO STATE_CORE ({key}) VALUES (?)", (value,))

        __rec_import_toml(toml.load(path))

tomlui = TOMLUI()
tomlui.import_toml("samples/DQ/assets/ui/title.toml")

from tomlui.ext import orm

orm = orm.XUEDB()
#session = orm.import_toml("samples/DQ/assets/ui/title.toml")
orm.import_sqlite3(tomlui.db)


