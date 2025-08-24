from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, event, Column, String, Integer, Text, DateTime
from sqlalchemy.orm import DeclarativeBase, scoped_session, sessionmaker

from one_dragon.utils import os_utils
from one_dragon.utils.log_utils import log


class Base(DeclarativeBase):
    pass


class ConfigContent(Base):
    """
    单表kv存储配置内容
    键名为相对于 config 目录的路径，如 '<idx>/...' 的路径。
    """
    __tablename__ = 'config_content'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    path = Column(String(255), nullable=False, unique=True)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class SqliteOperator:

    def __init__(self):
        self.engine = None
        self.SessionFactory = None
        self.Session = None  # scoped_session

    def init_db(self, db_name: str = "config.db"):
        """Initialize database engine and session factory (idempotent)."""
        if self.engine is not None and self.Session is not None:
            return

        db_dir = Path(os_utils.get_path_under_work_dir('config'))
        db_dir.mkdir(parents=True, exist_ok=True)
        db_path = (db_dir / db_name).resolve()
        # Enable cross-thread access and WAL for better concurrency
        self.engine = create_engine(
            f'sqlite:///{db_path}',
            connect_args={"check_same_thread": False}
        )

        # 使用事件监听器，确保每个连接都开启 WAL 模式
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """为每个 SQLite 连接设置 PRAGMA。"""
            cursor = dbapi_connection.cursor()
            try:
                cursor.execute("PRAGMA journal_mode=WAL;")
                cursor.execute("PRAGMA busy_timeout = 5000;") # 5秒超时
                cursor.execute("PRAGMA foreign_keys=ON;")
            finally:
                cursor.close()

        # 创建表和会话
        Base.metadata.create_all(self.engine)
        self.SessionFactory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.SessionFactory)

    def ensure_init(self):
        if self.engine is None or self.Session is None:
            self.init_db()

    def get(self, path: str) -> str | None:
        self.ensure_init()
        with self.Session() as session:
            record = session.query(ConfigContent).filter_by(path=path).first()
            if record:
                return record.content
            else:
                return None

    def save(self, path: str, content: str):
        self.ensure_init()
        with self.Session() as session:
            try:
                record = session.query(ConfigContent).filter_by(path=path).first()
                if record:
                    record.content = content
                    record.timestamp = datetime.now()
                else:
                    record = ConfigContent(path=path, content=content)
                    session.add(record)

                session.commit()
            except Exception:
                session.rollback()
                log.error(f"保存配置失败 {path}", exc_info=True)

    def delete(self, path: str):
        self.ensure_init()
        with self.Session() as session:
            try:
                record = session.query(ConfigContent).filter_by(path=path).first()
                if record:
                    session.delete(record)
                    session.commit()
            except Exception:
                session.rollback()
                log.error(f"删除配置失败 {path}", exc_info=True)

    def exists(self, path: str) -> bool:
        self.ensure_init()
        with self.Session() as session:
            return session.query(ConfigContent.id).filter_by(path=path).first() is not None


SQLITE_OPERATOR = SqliteOperator()
