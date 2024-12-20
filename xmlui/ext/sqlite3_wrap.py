# sqlite3/sqlite3.wasmラッパー

from xmlui.ext.web import WebIF

class XUXSQLite3(WebIF):
    def __init__(self, wasm_path:str|None=None):
        super().__init__()
        if self.is_web and wasm_path==None:
            raise Exception("wasm_path is required for web")
        self.wasm_path = wasm_path

    def connect(self, db_path):
        if self.is_web:
            self.conn = None
        else:
            import sqlite3 as db
            self.conn = db.connect(db_path)
