import os
from typing import Optional
import yaml
from one_dragon.base.config.sqlite_operator import sqlite_operator
from one_dragon.utils.log_utils import log


class YamlOperator:

    def __init__(self, file_path: Optional[str] = None):
        self.file_path: Optional[str] = file_path
        self.data: dict = {}
        self.__read_from_db()

    def __read_from_db(self) -> None:
        if self.file_path is None:
            return

        content = sqlite_operator.get_config(self.file_path)
        if content:
            try:
                self.data = yaml.safe_load(content)
            except yaml.YAMLError:
                log.error(f"Failed to parse YAML from DB for path: {self.file_path}", exc_info=True)
                self.data = {}
        else:
            self.__read_from_yaml_and_save_to_db()

    def __read_from_yaml_and_save_to_db(self):
        """
        从 yml 文件中读取数据 并保存到数据库中
        :return:
        """
        if not os.path.exists(self.file_path):
            self.data = {}
            return

        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                self.data = yaml.safe_load(file)
            if self.data is None:
                self.data = {}
            else:
                log.info(f'从 {self.file_path} 加载配置并迁移到数据库')
                self.save()
        except Exception:
            log.error(f'从 {self.file_path} 文件读取失败 将使用默认值', exc_info=True)
            self.data = {}

    def save(self):
        if self.file_path is None:
            return
        content = yaml.dump(self.data, allow_unicode=True, sort_keys=False)
        sqlite_operator.save_config(self.file_path, content)

    def save_diy(self, text: str):
        if self.file_path is None:
            return
        sqlite_operator.save_config(self.file_path, text)

    def get(self, prop: str, value=None):
        return self.data.get(prop, value)

    def update(self, key: str, value, save: bool = True):
        if self.data is None:
            self.data = {}
        if key in self.data and not isinstance(value, list) and self.data[key] == value:
            return
        self.data[key] = value
        if save:
            self.save()

    def delete(self):
        if self.file_path is None:
            return
        sqlite_operator.delete_config(self.file_path)

    def is_file_exists(self) -> bool:
        if self.file_path is None:
            return False
        return sqlite_operator.get_config(self.file_path) is not None
