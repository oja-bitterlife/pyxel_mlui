import sqlite3

# DB関係
# ゲームではストレージに書き込まないのでmemory_dbに移して使う
class XUXMemoryDB:
    # 空のDB。主にデバッグ用
    @classmethod
    def empty(cls) -> "XUXMemoryDB":
        conn = sqlite3.connect(":memory:")
        return XUXMemoryDB(conn)

    # DBを読み込む
    @classmethod
    def load(cls, db_path) -> "XUXMemoryDB":
        conn = sqlite3.connect(":memory:")
        with open(db_path, "rb") as f:
            conn.deserialize(f.read())
        return XUXMemoryDB(conn)

    def __init__(self, conn:sqlite3.Connection):
        self._conn:sqlite3.Connection = conn
        self._conn.row_factory = sqlite3.Row 

    def close(self):
        self._conn.close()

    def cursor(self) -> sqlite3.Cursor:
        return self._conn.cursor()

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()
