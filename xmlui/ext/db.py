from typing import Self
import sqlite3,csv

# DB関係
# ゲームではストレージに書き込まないのでmemory_dbに移して使う
class XUEMemoryDB(sqlite3.Connection):
    # DB作成
    # -----------------------------------------------------
    # 空のメモリDB作成
    def __init__(self):
        super().__init__(":memory:")
        self.row_factory = sqlite3.Row 

        # sqlite_sequenceテーブル(AUTO_INCREMENT用)を作っておく
        self.execute("CREATE TABLE _dummy (id INTEGER PRIMARY KEY AUTOINCREMENT);")
        self.execute("DROP TABLE _dummy")

    # メモリDBを作成してDBをデータを読み込んでおく
    @classmethod
    def load(cls, db_path) -> Self:
        self = cls()
        with open(db_path, "rb") as f:
            self.deserialize(f.read())
            f.close()
        return self

    # DB読み込み
    # -----------------------------------------------------
    # 別DBを取り込む
    def attach(self, db_path):
        # 一旦テンポラリDBに展開
        tmp_conn = sqlite3.connect(":memory:")
        with open(db_path, "rb") as f:
            tmp_conn.deserialize(f.read())
            f.close()

        # dumpを使って取り込み
        for sql in tmp_conn.iterdump():
            self.execute(sql)
        tmp_conn.close()

    # CSVを読み込んでメモリDB上にINSERT
    def import_csv(self, table_name:str, csv_path:str):
        lines = []
        with open(csv_path, "r", encoding="utf-8") as f:
            # 先頭に#があればコメント行
            lines = [line for line in f.readlines() if not line.strip().startswith("#")]
            f.close()

        # CSVを読み込み(１行目はヘッダー)
        dict_reader = csv.DictReader(lines, skipinitialspace=True)
        if dict_reader.fieldnames is None:
            raise ValueError(f"csv header is None: {csv_path}")

        # SQLの構築
        columns = ",".join([header for header in dict_reader.fieldnames])
        values = ",".join(["?"] * len(dict_reader.fieldnames))
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"

        # 一気にINSERT
        try:
            cur = self.begin()
            cur.executemany(sql, [tuple(dict.values()) for dict in dict_reader])
            self.commit()
        except Exception as e:
            raise RuntimeError(f"csv import error: {csv_path}") from e


    # DB操作
    # -----------------------------------------------------
    # トランザクション
    def begin(self, cursor:sqlite3.Cursor|None=None) -> sqlite3.Cursor:
        if cursor is None:
            return self.execute("BEGIN TRANSACTION")
        else:
            return cursor.execute("BEGIN TRANSACTION")
