from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime
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
            connect_args={
                "check_same_thread": False,
                "timeout": 5.0,  # 避免短暂锁导致的立即失败
            }
        )
        try:
            with self.engine.connect() as conn:
                # SQLAlchemy 2.0 推荐使用 exec_driver_sql 执行原生 PRAGMA
                conn.exec_driver_sql("PRAGMA journal_mode=WAL;")
        except Exception:
            # Non-fatal if PRAGMA fails
            log.debug("设置SQLite WAL模式失败，继续以默认模式运行")

        # 创建单表
        Base.metadata.create_all(self.engine)
        self.SessionFactory = sessionmaker(bind=self.engine)
        # Thread-safe session
        self.Session = scoped_session(self.SessionFactory)

    def ensure_init(self):
        if self.engine is None or self.Session is None:
            self.init_db()

    def get(self, path: str) -> str | None:
        self.ensure_init()
        session = self.Session()
        try:
            record = session.query(ConfigContent).filter_by(path=path).first()
            if record:
                return record.content
            else:
                return None
        finally:
            session.close()

    def save(self, path: str, content: str):
        self.ensure_init()
        session = self.Session()
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
        finally:
            session.close()

    def delete(self, path: str):
        self.ensure_init()
        session = self.Session()
        try:
            record = session.query(ConfigContent).filter_by(path=path).first()
            if record:
                session.delete(record)
                session.commit()
        except Exception:
            session.rollback()
            log.error(f"删除配置失败 {path}", exc_info=True)
        finally:
            session.close()

    def exists(self, path: str) -> bool:
        self.ensure_init()
        session = self.Session()
        try:
            return session.query(ConfigContent.id).filter_by(path=path).first() is not None
        finally:
            session.close()


SQLITE_OPERATOR = SqliteOperator()
