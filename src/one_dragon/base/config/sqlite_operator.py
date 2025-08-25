import os
from datetime import datetime

from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

from one_dragon.utils import os_utils
from one_dragon.utils.log_utils import log

Base = declarative_base()


class ConfigContent(Base):
    """
    配置内容
    """
    __tablename__ = 'config_content'

    id = Column(Integer, primary_key=True)
    path = Column(String(255), nullable=False, unique=True)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class SqliteOperator:

    def __init__(self):
        self.engine = None
        self.Session = None
        self.limit = 200

    def init_db(self, db_name: str = "config.db"):
        db_dir = os_utils.get_path_under_work_dir('config')
        os.makedirs(db_dir, exist_ok=True)
        db_path = os.path.join(db_dir, db_name)
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_config(self, path: str):
        session = self.Session()
        try:
            record = session.query(ConfigContent).filter_by(path=path).first()
            if record:
                return record.content
            else:
                return None
        finally:
            session.close()

    def save_config(self, path: str, content: str):
        session = self.Session()
        try:
            record = session.query(ConfigContent).filter_by(path=path).first()
            if record:
                record.content = content
            else:
                record = ConfigContent(path=path, content=content)
                session.add(record)

            # Enforce the limit
            if session.query(ConfigContent).count() > self.limit:
                oldest_record = session.query(ConfigContent).order_by(ConfigContent.timestamp).first()
                session.delete(oldest_record)

            session.commit()
        except Exception:
            session.rollback()
            log.error(f"保存配置失败 {path}", exc_info=True)
        finally:
            session.close()

    def delete_config(self, path: str):
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


sqlite_operator = SqliteOperator()
