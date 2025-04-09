import sqlalchemy,toml,sqlite3
from sqlalchemy.orm.session import Session, SessionTransaction

from tomlui import core

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
)
from sqlalchemy.orm import sessionmaker, declarative_base, Query

Base = declarative_base()

class XUEStateCore(Base):
    __tablename__ = core.XUDBStateCore.__tablename__
    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(String)
    selected = Column(Integer)
    x = Column(Integer)
    y = Column(Integer)
    abs_x = Column(Integer)
    abs_y = Column(Integer)
    w = Column(Integer)
    h = Column(Integer)
    update_count = Column(Integer)
    use_event = Column(String)
    enable = Column(Boolean)
    removed = Column(Boolean)

class XUEDB:
    def __init__(self):
        sqlalchemy.engine.Engine = create_engine("sqlite:///:memory:")
        self.mkSession = sessionmaker(bind=sqlalchemy.engine.Engine)

    def import_toml(self, path:str):
        XUEStateCore.metadata.create_all(sqlalchemy.engine.Engine)

        def __import_toml(session:Session, toml_dict:dict):
            state = XUEStateCore()
            for key,value in toml_dict.items():
                if isinstance(value,dict):
                    __import_toml(session, value)
                else:
                    state.__setattr__(key,value)
            session.add(state)

        session = self.mkSession()
        __import_toml(session, toml.load(path))
        session.commit()

        # sqlalchemyのexecuteでselectを実行する
        result = session.execute(sqlalchemy.text("SELECT * FROM STATE_CORE"))
        for row in result:
            print(row)

        return session

    def import_sqlite3(self, db:sqlite3.Connection):
        session = self.mkSession()
        sqls = "\n".join(line for line in db.iterdump())
        for sql in sqls.split(";"):
            sql = sql.strip()
            if sql != "":
                session.execute(sqlalchemy.text(sql))

        for obj in session.query(XUEStateCore).all():
            if(obj is not None):
                print(obj.__dict__)
