import os
from typing import Optional, Callable, Tuple

from one_dragon.envs.env_config import DEFAULT_ENV_PATH, EnvConfig
from one_dragon.envs.project_config import ProjectConfig
from one_dragon.envs.download_service import DownloadService
from one_dragon.envs.mirrorchyan_service import MirrorChyanService
from one_dragon.envs.git_service import GitService
from one_dragon.utils import app_utils, os_utils, file_utils
from one_dragon.utils.i18_utils import gt
from one_dragon.utils.log_utils import log


class LauncherService:
    """启动器服务，处理启动器的安装、检测和更新"""

    def __init__(self, project_config: ProjectConfig, env_config: EnvConfig,
                 download_service: DownloadService, mirrorchyan_service: MirrorChyanService,
                 git_service: GitService):
        self.project_config: ProjectConfig = project_config
        self.env_config: EnvConfig = env_config
        self.download_service: DownloadService = download_service
        self.mirrorchyan_service: MirrorChyanService = mirrorchyan_service
        self.git_service: GitService = git_service

    def get_launcher_path(self) -> str:
        """
        获取启动器文件路径
        :return: 启动器exe文件路径
        """
        return os.path.join(os_utils.get_work_dir(), 'OneDragon-Launcher.exe')

    def check_launcher_exist(self) -> bool:
        """
        检查启动器是否存在
        :return: 是否存在
        """
        launcher_path = self.get_launcher_path()
        return os.path.exists(launcher_path)

    def get_current_version(self) -> str:
        """
        获取当前启动器版本
        :return: 当前版本号
        """
        return app_utils.get_launcher_version()

    def get_latest_version(self) -> str:
        """
        获取最新版本号
        :return: 最新版本号，失败时返回空字符串
        """
        # 优先使用Mirror酱获取版本号
        latest_version = self.mirrorchyan_service.get_latest_version()
        if latest_version:
            return latest_version

        # 如果Mirror酱失败，回退到GitHub
        latest_version = self.git_service.get_latest_tag()
        return latest_version if latest_version else gt('未知')

    def check_launcher_update(self) -> Tuple[bool, str, str]:
        """
        检查启动器更新状态
        :return: (是否为最新版本, 最新版本, 当前版本)
        """
        current_version = self.get_current_version()
        latest_version = self.get_latest_version()

        if current_version == latest_version:
            return True, latest_version, current_version
        else:
            return False, latest_version, current_version

    def install_launcher(self, progress_callback: Optional[Callable[[float, str], None]] = None) -> Tuple[bool, str]:
        """
        安装启动器
        :param progress_callback: 进度回调函数
        :return: (是否成功, 消息)
        """
        msg = gt('正在安装启动器...')
        if progress_callback is not None:
            progress_callback(-1, msg)
        log.info(msg)

        for _ in range(2):
            zip_file_name = f'{self.project_config.project_name}-Launcher.zip'
            zip_file_path = os.path.join(DEFAULT_ENV_PATH, zip_file_name)
            download_url = f'{self.project_config.github_homepage}/releases/latest/download/{zip_file_name}'

            if not os.path.exists(zip_file_path):
                success = self.download_service.download_file_from_url(
                    download_url, zip_file_path, progress_callback=progress_callback
                )
                if not success:
                    return False, gt('下载启动器失败 请尝试到「设置」更改网络代理')

            msg = f"{gt('正在解压')} {zip_file_name} ..."
            log.info(msg)
            if progress_callback is not None:
                progress_callback(0, msg)

            # 删除旧的启动器
            old_launcher_path = self.get_launcher_path()
            if os.path.exists(old_launcher_path):
                try:
                    os.remove(old_launcher_path)
                except Exception as e:
                    log.error(f"删除旧启动器失败: {e}")

            # 解压新的启动器
            success = file_utils.unzip_file(zip_file_path, os_utils.get_work_dir())

            msg = gt('解压成功') if success else gt('解压失败 准备重试')
            log.info(msg)
            if progress_callback is not None:
                progress_callback(1 if success else 0, msg)

            # 清理zip文件
            try:
                os.remove(zip_file_path)
            except Exception as e:
                log.error(f"删除zip文件失败: {e}")

            if not success:  # 解压失败的话 可能是之前下的zip包坏了 尝试删除重来
                continue
            else:
                return True, gt('安装启动器成功')

        # 重试之后还是失败了
        return False, gt('安装启动器失败')

    def update_launcher(self, progress_callback: Optional[Callable[[float, str], None]] = None) -> Tuple[bool, str]:
        """
        更新启动器（实际上就是重新安装）
        :param progress_callback: 进度回调函数
        :return: (是否成功, 消息)
        """
        return self.install_launcher(progress_callback)

    def get_launcher_status(self) -> Tuple[str, str]:
        """
        获取启动器状态信息
        :return: (状态文本, 状态类型: 'installed'/'update_available'/'not_installed')
        """
        if not self.check_launcher_exist():
            return gt('需下载'), 'not_installed'

        is_latest, latest_version, current_version = self.check_launcher_update()

        if is_latest or os_utils.run_in_exe():  # 安装器中不检查更新
            status_text = f"{gt('已安装')} {current_version}"
            return status_text, 'installed'
        else:
            status_text = f"{gt('需更新')} {gt('当前版本')}: {current_version}; {gt('最新版本')}: {latest_version}"
            return status_text, 'update_available'

    def check_launcher_update_optimized(self) -> Tuple[bool, str, str, Optional[str], Optional[str]]:
        """
        按照优化流程检查启动器更新状态
        :return: (是否为最新版本, 最新版本, 当前版本, Mirror酱下载URL, 错误信息)
        """
        current_version = self.get_current_version()

        # A: 启动更新检查 -> B: 调用Mirror酱API
        log.info("开始检查启动器更新...")

        try:
            # 获取Mirror酱的完整数据
            mirror_data = self.mirrorchyan_service._get_latest_resource_data()

            # C: Mirror酱返回code 0？
            if not mirror_data:
                # Y: 提示错误，回退到GitHub
                log.warning("Mirror酱API调用失败，回退到GitHub获取版本信息")
                latest_version = self.git_service.get_latest_tag()
                if not latest_version:
                    latest_version = gt('未知')
                return False, latest_version, current_version, None, gt('Mirror酱API调用失败')

            latest_version = mirror_data.get('version_name', '').strip()
            if not latest_version:
                log.warning("Mirror酱返回的版本号为空，回退到GitHub")
                latest_version = self.git_service.get_latest_tag()
                if not latest_version:
                    latest_version = gt('未知')
                return False, latest_version, current_version, None, gt('Mirror酱返回版本号为空')

            # D: 版本号比对
            if current_version == latest_version:
                # Z: 结束流程 - 无更新
                log.info(f"启动器已是最新版本: {current_version}")
                return True, latest_version, current_version, None, None

            # 有更新 -> F: Mirror酱返回url？
            mirror_url = mirror_data.get('url', '').strip()
            log.info(f"发现启动器更新: {current_version} -> {latest_version}")

            if mirror_url:
                # G: 调用url下载 -> I: 触发增量更新
                log.info(f"Mirror酱提供下载链接: {mirror_url}")
                return False, latest_version, current_version, mirror_url, None
            else:
                # H: 通过GitHub下载
                log.info("Mirror酱未提供下载链接，将通过GitHub下载")
                return False, latest_version, current_version, None, None

        except Exception as e:
            # Y: 提示错误
            error_msg = f"检查更新时发生错误: {str(e)}"
            log.error(error_msg)
            # 回退到GitHub
            latest_version = self.git_service.get_latest_tag()
            if not latest_version:
                latest_version = gt('未知')
            return False, latest_version, current_version, None, error_msg

    def install_launcher_optimized(self, progress_callback: Optional[Callable[[float, str], None]] = None) -> Tuple[bool, str]:
        """
        按照优化流程安装启动器
        :param progress_callback: 进度回调函数
        :return: (是否成功, 消息)
        """
        msg = gt('正在检查启动器更新...')
        if progress_callback is not None:
            progress_callback(-1, msg)
        log.info(msg)

        # 使用优化的更新检查
        is_latest, latest_version, current_version, mirror_url, error_msg = self.check_launcher_update_optimized()

        if error_msg:
            log.warning(f"更新检查出现问题: {error_msg}")

        if is_latest:
            return True, gt('启动器已是最新版本')

        # 确定下载URL和文件名
        zip_file_name = f'{self.project_config.project_name}-Launcher.zip'
        zip_file_path = os.path.join(DEFAULT_ENV_PATH, zip_file_name)

        if mirror_url:
            # 使用Mirror酱提供的URL
            download_url = mirror_url
            msg = gt('正在从Mirror酱下载启动器...')
        else:
            # 使用GitHub URL
            download_url = f'{self.project_config.github_homepage}/releases/latest/download/{zip_file_name}'
            msg = gt('正在从GitHub下载启动器...')

        if progress_callback is not None:
            progress_callback(0.1, msg)
        log.info(msg)

        # 重试逻辑
        for attempt in range(2):
            try:
                # 如果文件已存在，先删除
                if os.path.exists(zip_file_path):
                    os.remove(zip_file_path)

                # 下载文件
                success = self.download_service.download_file_from_url(
                    download_url, zip_file_path, progress_callback=progress_callback
                )

                if not success:
                    if mirror_url and attempt == 0:
                        # 第一次尝试Mirror酱失败，回退到GitHub
                        log.warning("Mirror酱下载失败，回退到GitHub下载")
                        download_url = f'{self.project_config.github_homepage}/releases/latest/download/{zip_file_name}'
                        msg = gt('Mirror酱下载失败，正在从GitHub重试...')
                        if progress_callback is not None:
                            progress_callback(0.1, msg)
                        log.info(msg)
                        continue
                    else:
                        return False, gt('下载启动器失败 请尝试到「设置」更改网络代理')

                # 解压文件
                msg = f"{gt('正在解压')} {zip_file_name} ..."
                log.info(msg)
                if progress_callback is not None:
                    progress_callback(0.8, msg)

                # 删除旧的启动器
                old_launcher_path = self.get_launcher_path()
                if os.path.exists(old_launcher_path):
                    try:
                        os.remove(old_launcher_path)
                    except Exception as e:
                        log.error(f"删除旧启动器失败: {e}")

                # 解压新的启动器
                success = file_utils.unzip_file(zip_file_path, os_utils.get_work_dir())

                msg = gt('解压成功') if success else gt('解压失败 准备重试')
                log.info(msg)
                if progress_callback is not None:
                    progress_callback(1 if success else 0.5, msg)

                # 清理zip文件
                try:
                    os.remove(zip_file_path)
                except Exception as e:
                    log.error(f"删除zip文件失败: {e}")

                if success:
                    return True, gt('安装启动器成功')
                elif attempt == 0:
                    # 第一次解压失败，可能是zip文件损坏，重试
                    log.warning("解压失败，可能是文件损坏，准备重试")
                    continue
                else:
                    return False, gt('安装启动器失败')

            except Exception as e:
                error_msg = f"安装过程中发生错误: {str(e)}"
                log.error(error_msg)
                if attempt == 1:  # 最后一次尝试
                    return False, error_msg

        # 重试之后还是失败了
        return False, gt('安装启动器失败')

    def update_launcher_optimized(self, progress_callback: Optional[Callable[[float, str], None]] = None) -> Tuple[bool, str]:
        """
        按照优化流程更新启动器
        :param progress_callback: 进度回调函数
        :return: (是否成功, 消息)
        """
        return self.install_launcher_optimized(progress_callback)
