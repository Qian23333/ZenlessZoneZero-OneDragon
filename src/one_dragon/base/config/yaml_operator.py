import os
from typing import Optional
import yaml
from deepmerge import always_merger
from one_dragon.base.config.sqlite_operator import sqlite_operator
from one_dragon.utils.log_utils import log


class YamlOperator:

    def __init__(self, file_path: Optional[str] = None):
        self.file_path: Optional[str] = file_path
        self.data: dict = {}
        self._load_layered_data()

    def _load_layered_data(self) -> None:
        """
        分层加载配置数据：
        1. 基础层：从.yml文件读取默认值
        2. 覆写层：从数据库读取用户修改的值
        3. 合并：覆写层优先
        """
        if self.file_path is None:
            return

        # 步骤1: 加载基础层（从.yml文件）
        base_data = self._load_base_data()

        # 步骤2: 加载覆写层（从数据库）
        override_data = self._load_override_data()

        # 步骤3: 合并数据（覆写层优先）
        if override_data:
            self.data = always_merger.merge(base_data, override_data)
        else:
            self.data = base_data

    def _load_base_data(self) -> dict:
        """
        从.yml文件加载基础默认值
        """
        if not os.path.exists(self.file_path):
            return {}

        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
                if data is None:
                    return {}
                log.debug(f'从基础层加载配置: {self.file_path}')
                return data
        except Exception:
            log.error(f'基础层配置文件读取失败: {self.file_path}', exc_info=True)
            return {}

    def _load_override_data(self) -> dict:
        """
        从数据库加载用户覆写值
        """
        content = sqlite_operator.get_config(self.file_path)
        if not content:
            return {}

        try:
            data = yaml.safe_load(content)
            if data is None:
                return {}
            log.debug(f'从覆写层加载配置: {self.file_path}')
            return data
        except yaml.YAMLError:
            log.error(f"覆写层配置解析失败: {self.file_path}", exc_info=True)
            return {}

    def save(self):
        """
        将配置保存到数据库（覆写层）
        基础层文件永远不会被修改
        """
        if self.file_path is None:
            return
        content = yaml.dump(self.data, allow_unicode=True, sort_keys=False)
        sqlite_operator.save_config(self.file_path, content)
        log.debug(f'配置已保存到覆写层: {self.file_path}')

    def save_diy(self, text: str):
        """
        保存自定义格式的文本到数据库
        """
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
        """
        删除覆写层配置（数据库中的用户修改）
        基础层配置文件保持不变
        """
        if self.file_path is None:
            return
        sqlite_operator.delete_config(self.file_path)

    def is_file_exists(self) -> bool:
        """
        检查是否有配置数据（基础层或覆写层）
        """
        if self.file_path is None:
            return False
        # 检查基础层文件是否存在，或覆写层是否有数据
        return os.path.exists(self.file_path) or sqlite_operator.get_config(self.file_path) is not None
