# Zenless Zone Zero - One Dragon

__绝区零 - 一条龙__

基于 绝区零 && 图像识别 的相关学习资料，适用于PC端。

无修改游戏、读取内存等作弊行为。低调学习的~~好~~学生应该不会被米哈游老师抓。

学习后，你可以

- ~~领悟 `图像识别` 相关知识~~
- 领悟 `自动闪避` 能力(测试中)
- 领悟 `自动每日` 的护肝方法 (开发中)

如果喜欢本项目，可右上角送作者一个```Star```

## 学习方式

### 使用自己的Python环境

1. 创建你自己的虚拟环境
2. `git clone git@github.com:DoctorReid/ZenlessZoneZero-OneDragon.git`
3. `pip install -r requirements-prod.txt`
4. 运行 （以下二选一）
   - 复制 `env.sample.bat`，重命名为 `env.bat`，并修改内容为你的虚拟环境的python路径，使用 `app.bat` 运行。
   - 将`src`文件夹加入环境变量`PYTHONPATH`，执行 `python src/zzz_od/gui/app.py` 。


### 常见报错

#### 动态链接库(DLL)初始化例程失败

安装最新版的 [Microsoft Visual C++](https://aka.ms/vs/17/release/vc_redist.x64.exe)


## 功能说明

### 自动闪避

__手残救星，只管输出即可__

训练了一个模型，判断画面黄光/红光后进行自动闪避，可设置成切人格挡。

支持使用GPU运算，模型运行在50ms内应该就能正常使用。（整个闪光过程大概持续100ms）

闪避、切人格挡目前内置1S的CD，与你的键盘输入共用，即自动闪避(切人)或者你人工闪避(切人)的1S内，不会再次触发自动闪避。

目前模型只喂了100+张图，效果感觉还行，就放出来大家试用一下。

后续优化方向

- 类似安比的攻击自带黄光可能会被误判，后续会再多喂点图优化模型。
- 支持 闪A切人。
- 支持 切人时优先切换到指定角色。

## 免责声明

本项目仅供学习交流使用。

开发者团队拥有本项目的最终解释权。

使用本项目产生的所有问题与本项目与及开发者团队无关。


## 赞助

如果喜欢本项目，可以为作者的赞助一点狗粮~

感谢 [小伙伴们的支持](https://github.com/DoctorReid/OneDragon-Thanks)

![赞助](./image/sponsor.png)