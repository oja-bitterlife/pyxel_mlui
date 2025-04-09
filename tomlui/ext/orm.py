import sqlalchemy,toml,sqlite3
from sqlalchemy.orm.session import Session, SessionTransaction
from typing import Callable,Any,Self

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


class XUEORM:
    def __init__(self):
        sqlalchemy.engine.Engine = create_engine("sqlite:///:memory:")
        self.engine = sqlalchemy.engine.Engine
        self.mk_session = sessionmaker(bind=self.engine)

    def execute(self, session:Session, sql:str):
        return session.execute(sqlalchemy.text(sql))

class XUEStateCore(Base):
    __tablename__ = core.XUDBStateCore.__tablename__
    id = Column(Integer, primary_key=True)
    parent = Column(Integer)
    tag = Column(String)
    text = Column(String)
    value = Column(String)
    selected = Column(Integer)
    x = Column(Integer, default=0)
    y = Column(Integer, default=0)
    abs_x = Column(Integer)
    abs_y = Column(Integer)
    w = Column(Integer, default=256)
    h = Column(Integer, default=256)
    update_count = Column(Integer, default=0)
    use_event = Column(String)
    enable = Column(Boolean, default=True)
    removed = Column(Boolean, default=False)

    @classmethod
    def create_session_from_toml(cls, orm:XUEORM, path:str) -> Session:
        tmp = core.TOMLUI()
        tmp.import_toml("samples/DQ/assets/ui/title.toml")
        return XUEStateCore.create_session_from_sqlite3(orm, tmp.db)

    @classmethod
    def create_session_from_sqlite3(cls, orm:XUEORM, db:sqlite3.Connection) -> Session:
        session = orm.mk_session()
        sqls = "\n".join(line for line in db.iterdump())
        for sql in sqls.split(";"):
            sql = sql.strip()
            if sql != "":
                session.execute(sqlalchemy.text(sql))

        return session
