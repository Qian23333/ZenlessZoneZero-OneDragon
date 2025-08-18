import os
from one_dragon.base.config.file_yaml_operator import FileYamlOperator
from one_dragon.utils import os_utils


class ProjectConfig(FileYamlOperator):

    def __init__(self):
        project_config_path = os.path.join(os_utils.get_path_under_work_dir('config'), 'project.yml')
        FileYamlOperator.__init__(self, project_config_path)

        self.project_name = self.get('project_name')
        self.python_version = self.get('python_version')
        self.github_homepage = self.get('github_homepage')
        self.github_https_repository = self.get('github_https_repository')
        self.github_ssh_repository = self.get('github_ssh_repository')
        self.gitee_https_repository = self.get('gitee_https_repository')
        self.gitee_ssh_repository = self.get('gitee_ssh_repository')
        self.project_git_branch = self.get('project_git_branch')
        self.requirements = self.get('requirements')

        self.screen_standard_width = int(self.get('screen_standard_width'))
        self.screen_standard_height = int(self.get('screen_standard_height'))

        self.qq_link = self.get('qq_link')
        self.quick_start_link = self.get('quick_start_link')  # 链接 - 快速开始
