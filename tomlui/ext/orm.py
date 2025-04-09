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


class XUEORM:
    def __init__(self):
        sqlalchemy.engine.Engine = create_engine("sqlite:///:memory:")
        self.engine = sqlalchemy.engine.Engine
        self.mk_session = sessionmaker(bind=self.engine)

    def execute(self, session:Session, sql:str):
        return session.execute(sqlalchemy.text(sql))

class XUEStateCore(Base):
    __tablename__ = core.XUDBStateCore.__tablename__
    id = Column(Integer, primary_key=True, autoincrement=True)
    parent = Column(Integer)
    tag = Column(String)
    text = Column(String)
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

    @classmethod
    def create_session_from_toml(cls, orm:XUEORM, path:str) -> Session:
        Base.metadata.create_all(orm.engine, tables=[cls.__table__])

        def __import_toml(session:Session, toml_dict:dict):
            obj = cls()
            for key,value in toml_dict.items():
                if isinstance(value, dict):
                    __import_toml(session, value)
                if isinstance(value, list):
                    for v in value:
                        if isinstance(v, dict):
                            __import_toml(session, v)
                        else:
                            obj.__setattr__(key, value)
                else:
                    obj.__setattr__(key, value)
            print(obj.__dict__)
            session.add(obj)

        session = orm.mk_session()
        __import_toml(session, toml.load(path))
        session.commit()

        return session

    @classmethod
    def create_session_from_sqlite3(cls, orm:XUEORM, db:sqlite3.Connection) -> Session:
        session = orm.mk_session()
        sqls = "\n".join(line for line in db.iterdump())
        for sql in sqls.split(";"):
            sql = sql.strip()
            if sql != "":
                session.execute(sqlalchemy.text(sql))

        return session
