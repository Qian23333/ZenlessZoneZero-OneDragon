from PySide6.QtWidgets import QWidget
from numpy.core.defchararray import title
from qfluentwidgets import FluentIcon

from one_dragon.base.config.config_item import ConfigItem
from one_dragon.gui.widgets.vertical_scroll_interface import VerticalScrollInterface
from one_dragon.gui.widgets.setting_card.combo_box_setting_card import ComboBoxSettingCard
from one_dragon.gui.widgets.setting_card.switch_setting_card import SwitchSettingCard
from zzz_od.application.battle_assistant.auto_battle_config import get_auto_battle_op_config_list
from zzz_od.application.coffee.coffee_config import CoffeeChooseWay, CoffeeChallengeWay, CoffeeCardNumEnum
from zzz_od.context.zzz_context import ZContext

from phosdeiz.gui.widgets import Column

class CoffeePlanInterface(VerticalScrollInterface):

    def __init__(self, ctx: ZContext, parent=None):
        self.ctx: ZContext = ctx

        VerticalScrollInterface.__init__(
            self,
            object_name='zzz_coffee_plan_interface',
            content_widget=None, parent=parent,
            nav_text_cn='咖啡计划'
        )

    def get_content_widget(self) -> QWidget:
        content_widget = Column()

        self.choose_way_opt = ComboBoxSettingCard(icon=FluentIcon.CALENDAR, title='咖啡选择', options_enum=CoffeeChooseWay)
        content_widget.add_widget(self.choose_way_opt)

        self.challenge_way_opt = ComboBoxSettingCard(icon=FluentIcon.GAME, title='喝后挑战', options_enum=CoffeeChallengeWay)
        content_widget.add_widget(self.challenge_way_opt)

        self.card_num_opt = ComboBoxSettingCard(icon=FluentIcon.GAME, title='体力计划外的数量', options_enum=CoffeeCardNumEnum)
        content_widget.add_widget(self.card_num_opt)

        self.predefined_team_opt = ComboBoxSettingCard(icon=FluentIcon.PEOPLE, title='预备编队')
        self.predefined_team_opt.value_changed.connect(self.on_predefined_team_changed)
        content_widget.add_widget(self.predefined_team_opt)

        self.auto_battle_opt = ComboBoxSettingCard(icon=FluentIcon.GAME, title='自动战斗')
        content_widget.add_widget(self.auto_battle_opt)

        self.run_charge_plan_afterwards_opt = SwitchSettingCard(
            icon=FluentIcon.CALENDAR, title='结束后运行体力计划', content='咖啡店在体力计划后运行可开启'
        )
        content_widget.add_widget(self.run_charge_plan_afterwards_opt)

        content_widget.add_stretch(1)

        return content_widget

    def on_interface_shown(self) -> None:
        VerticalScrollInterface.on_interface_shown(self)

        self.choose_way_opt.setValue(self.ctx.coffee_config.choose_way)
        self.challenge_way_opt.setValue(self.ctx.coffee_config.challenge_way)
        self.card_num_opt.setValue(self.ctx.coffee_config.card_num)

        config_list = ([ConfigItem('游戏内配队', -1)] +
                       [ConfigItem(team.name, team.idx) for team in self.ctx.team_config.team_list])
        self.predefined_team_opt.set_options_by_list(config_list)
        self.predefined_team_opt.init_with_adapter(self.ctx.coffee_config.get_prop_adapter('predefined_team_idx'))

        self.auto_battle_opt.set_options_by_list(get_auto_battle_op_config_list('auto_battle'))
        self.auto_battle_opt.setValue(self.ctx.coffee_config.auto_battle)
        team_idx = self.predefined_team_opt.combo_box.currentData()
        self.auto_battle_opt.setVisible(team_idx == -1)

        self.run_charge_plan_afterwards_opt.init_with_adapter(self.ctx.coffee_config.run_charge_plan_afterwards_adapter)

        self.choose_way_opt.value_changed.connect(self._on_choose_way_changed)
        self.challenge_way_opt.value_changed.connect(self._on_challenge_way_changed)
        self.card_num_opt.value_changed.connect(self._on_card_num_changed)
        self.auto_battle_opt.value_changed.connect(self._on_auto_battle_changed)

    def on_interface_hidden(self) -> None:
        VerticalScrollInterface.on_interface_hidden(self)

        self.choose_way_opt.value_changed.disconnect(self._on_choose_way_changed)
        self.challenge_way_opt.value_changed.disconnect(self._on_challenge_way_changed)
        self.card_num_opt.value_changed.disconnect(self._on_card_num_changed)
        self.auto_battle_opt.value_changed.disconnect(self._on_auto_battle_changed)

    def _on_choose_way_changed(self, idx: int, value: str) -> None:
        self.ctx.coffee_config.choose_way = value

    def _on_challenge_way_changed(self, idx: int, value: str) -> None:
        self.ctx.coffee_config.challenge_way = value

    def _on_card_num_changed(self, idx: int, value: str) -> None:
        self.ctx.coffee_config.card_num = value

    def _on_auto_battle_changed(self, idx: int, value: str) -> None:
        self.ctx.coffee_config.auto_battle = value

    def on_predefined_team_changed(self, idx: int, value: str) -> None:
        team_idx = self.predefined_team_opt.combo_box.currentData()
        self.auto_battle_opt.setVisible(team_idx == -1)
