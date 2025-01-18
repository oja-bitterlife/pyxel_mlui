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

    # DB読み込み
    # -----------------------------------------------------
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
            # CSVを読み込み(１行目はヘッダー)
            dict_reader = csv.DictReader(f, skipinitialspace=True)
            if dict_reader.fieldnames is None:
                raise ValueError(f"csv header is None: {csv_path}")

            # SQLの構築
            columns = ",".join([header for header in dict_reader.fieldnames])
            values = ",".join(["?"] * len(dict_reader.fieldnames))
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"

            # 一気にINSERT
            try:
                self._conn.executemany(sql, [tuple(dict.values()) for dict in dict_reader])
            except Exception as e:
                raise RuntimeError(f"csv import error: {csv_path}") from e

        f.close()

    # close
    # -----------------------------------------------------
    # 閉じる、、、んだけど、たぶんcursor.connection.close()を呼ぶ気がする
    # :memory:なので閉じ忘れても特に問題はないはず
    def close(self):
        self._conn.close()


    # DB操作
    # -----------------------------------------------------
    # 新しいカーソルを作成する
    @property
    def cursor(self) -> sqlite3.Cursor:
        return self._conn.cursor()

    # トランザクション
    def begin(self, cursor:sqlite3.Cursor|None):
        if cursor is not None:
            cursor.execute("BEGIN TRANSACTION")
        else:
            self._conn.execute("BEGIN TRANSACTION")
    def commit(self):
        self._conn.commit()
