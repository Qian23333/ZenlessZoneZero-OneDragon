from qfluentwidgets import ComboBox as qtComboBox
from one_dragon.base.config.config_item import ConfigItem
from typing import List, Any, Optional, Iterable
from one_dragon_qt.widgets.setting_card.yaml_config_adapter import YamlConfigAdapter
from enum import Enum


class ComboBox(qtComboBox):

    def __init__(self, parent=None):
        qtComboBox.__init__(self, parent)
        self.adapter: Optional[YamlConfigAdapter] = None
        self._opts_list: List[ConfigItem] = []  # 存储选项列表
        # 添加值变化信号连接
        self.currentIndexChanged.connect(self._on_index_changed)

    def initialize_options(self, options_enum: Optional[Iterable[Enum]] = None, 
                         options_list: Optional[List[ConfigItem]] = None) -> None:
        """初始化下拉框选项，可从枚举或ConfigItem列表"""
        self.clear()
        self._opts_list.clear()
        
        if options_enum:
            for opt in options_enum:
                if isinstance(opt.value, ConfigItem):
                    self._opts_list.append(opt.value)
                    self.addItem(opt.value.ui_text, userData=opt.value.value)
        elif options_list:
            for opt_item in options_list:
                self._opts_list.append(opt_item)
                self.addItem(opt_item.ui_text, userData=opt_item.value)
        
        # 如果有选项，默认选中第一个
        if self.count() > 0:
            self.setCurrentIndex(0)
            
    def get_option_desc(self, index: int) -> Optional[str]:
        """获取指定索引选项的描述"""
        if 0 <= index < len(self._opts_list):
            return self._opts_list[index].desc
        return None

    def set_items(self, items: List[ConfigItem], target_value: Any = None) -> None:
        """
        更新选项
        且尽量复用原来的选项
        """
        self.blockSignals(True)

        old_data = self.currentData() if target_value is None else target_value
        old_len, new_len = len(self.items), len(items)
        new_idx = -1

        # 更新已有选项和查找当前选项索引
        for i in range(min(old_len, new_len)):
            self.setItemText(i, items[i].ui_text)
            self.setItemData(i, items[i].value)
            if items[i].value == old_data:
                new_idx = i

        # 移除多余的选项
        for i in range(new_len, old_len):
            self.removeItem(new_len)

        # 添加新选项
        for i in range(old_len, new_len):
            item = items[i]
            self.addItem(item.ui_text, userData=item.value)
            if item.value == old_data:
                new_idx = i

        self.setCurrentIndex(new_idx)
        self.blockSignals(False)

    def init_with_value(self, target_value: Any = None) -> None:
        """
        根据目标值初始化 不抛出事件
        :param target_value:
        :return:
        """
        self.blockSignals(True)
        self.setCurrentIndex(self.findData(target_value))
        self.blockSignals(False)
        
    def init_with_adapter(self, adapter: Optional[YamlConfigAdapter]) -> None:
        """初始化配置适配器。"""
        self.adapter = adapter
        if adapter is not None:
            self.setValue(adapter.get_value())
        
    def setValue(self, value: Any) -> None:
        """设置下拉框的值"""
        self.blockSignals(True)
        self.setCurrentIndex(self.findData(value))
        self.blockSignals(False)
        
    def getValue(self) -> Any:
        """获取当前选中的值"""
        return self.currentData()
    
    def _on_index_changed(self, index: int) -> None:
        """处理索引变化，更新适配器"""
        if index >= 0 and self.adapter is not None:
            value = self.itemData(index)
            self.adapter.set_value(value)
