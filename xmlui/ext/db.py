from typing import Self
import sqlite3,csv

# DB関係
# ゲームではストレージに書き込まないのでmemory_dbに移して使う
class XUEMemoryDB:
    # コネクションラッパー。通常自分で呼び出すことはない
    def __init__(self, conn:sqlite3.Connection):
        self._conn:sqlite3.Connection = conn
        self._conn.row_factory = sqlite3.Row 

    # 空のメモリDB作成。主にデバッグ用
    @classmethod
    def empty(cls) -> Self:
        conn = sqlite3.connect(":memory:")

        # sqlite_sequenceテーブル(AUTO_INCREMENT用)を作っておく
        conn.execute("CREATE TABLE _dummy (id INTEGER PRIMARY KEY AUTOINCREMENT);")
        conn.execute("DROP TABLE _dummy")
        return cls(conn)

    # DBを読み込んでメモリDB上に展開する
    @classmethod
    def load(cls, db_path) -> Self:
        conn = sqlite3.connect(":memory:")
        with open(db_path, "rb") as f:
            conn.deserialize(f.read())
        return cls(conn)

    # 別DBを取り込む
    def attach(self, db_path):
        tmp_conn = sqlite3.connect(":memory:")
        with open(db_path, "rb") as f:
            tmp_conn.deserialize(f.read())
            f.close()

        # 取り込み
        for sql in tmp_conn.iterdump():
            self._conn.execute(sql)
        tmp_conn.close()

    # CSVを読み込んでメモリDB上にINSERT
    def import_csv(self, table_name:str, csv_path:str):
        with open(csv_path, "r", encoding="utf-8") as f:
            dict_reader = csv.DictReader(f, skipinitialspace=True)
            if dict_reader.fieldnames is None:
                raise ValueError("csv header is None")

            for dict in dict_reader:
                columns = ",".join([header for header in dict.keys()])
                values = ",".join(["?"] * len(dict.values()))
                sql = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
                self._conn.execute(sql, tuple(dict.values()))
        f.close()


    # 閉じる、、、んだけど、たぶんcursor.connection.close()を呼ぶ気がする
    # :memory:なので閉じ忘れても特に問題はないはず
    def close(self):
        self._conn.close()

    # 新しいカーソルを作成する
    @property
    def cursor(self) -> sqlite3.Cursor:
        return self._conn.cursor()
