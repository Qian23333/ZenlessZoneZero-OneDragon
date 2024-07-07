from qfluentwidgets import qrouter, FluentIcon

from one_dragon.gui.component.interface.pivot_navi_interface import PivotNavigatorInterface
from one_dragon.gui.view.setting.setting_env_interface import SettingEnvInterface


class AppDevtoolsInterface(PivotNavigatorInterface):

    def __init__(self, parent=None):
        PivotNavigatorInterface.__init__(self, object_name='app_devtools_interface', parent=parent,
                                         nav_text_cn='开发工具', nav_icon=FluentIcon.DEVELOPER_TOOLS)

        self.env_interface = SettingEnvInterface()

        # add items to pivot
        self.add_sub_interface(self.env_interface)
        qrouter.setDefaultRouteKey(self.stacked_widget, self.env_interface.objectName())

    def init_on_shown(self) -> None:
        """
        子界面显示时 进行初始化
        :return:
        """
        self.stacked_widget.currentWidget().init_on_shown()