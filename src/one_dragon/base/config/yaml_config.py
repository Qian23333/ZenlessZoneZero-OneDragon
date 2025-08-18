import os
from typing import Optional, List

from one_dragon.base.config.yaml_operator import YamlOperator
from one_dragon.utils import os_utils


class YamlConfig(YamlOperator):

    def __init__(
            self,
            module_name: str,
            backup_model_name: str | None = None,
            instance_idx: Optional[int] = None,
            sub_dir: Optional[List[str]] = None,
            sample: bool = False, copy_from_sample: bool = False,
            is_mock: bool = False
    ):
        self.instance_idx: Optional[int] = instance_idx
        self.sub_dir: Optional[List[str]] = sub_dir
        self.module_name: str = module_name
        self.is_mock: bool = is_mock

        super().__init__(self._get_yaml_file_path())

    def _get_yaml_file_path(self) -> Optional[str]:
        if self.is_mock:
            return None

        sub_dir_parts = ['config']
        if self.instance_idx is not None:
            sub_dir_parts.append('%02d' % self.instance_idx)
        if self.sub_dir is not None:
            sub_dir_parts.extend(self.sub_dir)

        return os.path.join(*sub_dir_parts, f'{self.module_name}.yml')

    @property
    def is_sample(self) -> bool:
        return False

    def get_prop_adapter(self, prop: str,
                         getter_convert: Optional[str] = None,
                         setter_convert: Optional[str] = None):
        """
        获取一个配置适配器
        :param prop: 配置字段
        :param getter_convert: 获取时的转换器
        :param setter_convert: 设置时的转换器
        :return:
        """
        from one_dragon_qt.widgets.setting_card.yaml_config_adapter import YamlConfigAdapter
        return YamlConfigAdapter(
            config=self,
            field=prop,
            getter_convert=getter_convert,
            setter_convert=setter_convert
        )
