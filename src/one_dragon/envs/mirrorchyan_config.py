from one_dragon.base.config.yaml_config import YamlConfig

class MirrorChyanConfig(YamlConfig):

    def __init__(self):
        YamlConfig.__init__(self, module_name='mirror_chyan')

    @property
    def cdk(self) -> str:
        """
        获取Mirror酱的CDK
        :return: CDK字符串
        """
        return self.get('cdk', '')

    @cdk.setter
    def cdk(self, new_value: str) -> None:
        """
        设置Mirror酱的CDK
        :return:
        """
        self.update('cdk', new_value)