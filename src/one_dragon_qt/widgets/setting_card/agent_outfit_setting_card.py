from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtWidgets import QWidget, QHBoxLayout
from qfluentwidgets import FluentIcon, BodyLabel, ExpandGroupSettingCard
from zzz_od.context.zzz_context import ZContext
from one_dragon.utils.i18_utils import gt
from one_dragon_qt.widgets.combo_box import ComboBox


class AgentOutfitSettingCard(ExpandGroupSettingCard):

    def __init__(self, ctx: ZContext):
        super().__init__(FluentIcon.PEOPLE, "代理人皮肤", "按账号选择代理人皮肤")
        self.ctx: ZContext = ctx

        # 妮可设置
        self.outfit_nicole_label = BodyLabel(text='妮可')
        self.outfit_nicole_opt = ComboBox()
        self.outfit_nicole_opt.currentIndexChanged.connect(self.on_agent_outfit_changed)

        # 艾莲设置
        self.outfit_ellen_label = BodyLabel(text='艾莲')
        self.outfit_ellen_opt = ComboBox()
        self.outfit_ellen_opt.currentIndexChanged.connect(self.on_agent_outfit_changed)

        # 耀嘉音设置
        self.outfit_astra_yao_label = BodyLabel(text='耀嘉音')
        self.outfit_astra_yao_opt = ComboBox()
        self.outfit_astra_yao_opt.currentIndexChanged.connect(self.on_agent_outfit_changed)

        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.setSpacing(0)
        
        # 添加各组到设置卡中
        self.add(self.outfit_nicole_label, self.outfit_nicole_opt)
        self.add(self.outfit_ellen_label, self.outfit_ellen_opt)
        self.add(self.outfit_astra_yao_label, self.outfit_astra_yao_opt)

    def on_agent_outfit_changed(self) -> None:
        self.ctx.init_agent_template_id()

    def add(self, label, widget):
        w = QWidget()
        w.setFixedHeight(60)

        layout = QHBoxLayout(w)
        layout.setContentsMargins(48, 12, 48, 12)

        layout.addWidget(label)
        layout.addStretch(1)
        layout.addWidget(widget)

        # 添加组件到设置卡
        self.addGroupWidget(w)
