# -*- coding: utf-8 -*-
import os  # 导入os模块，用于处理文件和目录

from flask import Flask  # 导入Flask类，用于创建Web应用程序
from flask_sqlalchemy import SQLAlchemy  # 导入SQLAlchemy类，用于数据库操作

from common.libs.UrlManager import UrlManager  # 导入UrlManager类，用于URL构建

class Application(Flask):
    """
    自定义 Flask 应用程序类，继承自 Flask
    用于配置应用程序，包括加载配置文件和初始化数据库。
    """
    def __init__(self, import_name, template_folder=None, root_path=None):
        """
        构造函数

        Args:
            import_name:  应用程序的模块名。通常为 __name__。
            template_folder:  模板文件夹的路径。如果为 None，则使用默认路径。
            root_path:  应用程序的根路径。如果为 None，则自动检测。
        """
        super(Application, self).__init__(import_name, template_folder=template_folder, root_path=root_path,
                                          static_folder=None) # 调用父类的构造函数，static_folder设置为None，防止默认的static目录干扰
        self.config.from_pyfile('config/base_setting.py') # 从 'config/base_setting.py' 文件加载配置
        ops_config = os.environ.get("ops_config")  # 安全地获取名为 "ops_config" 的环境变量。用于指定不同环境的配置。
        if ops_config: # 如果 "ops_config" 环境变量存在
            try:
                self.config.from_pyfile(f"config/{ops_config}_setting.py") # 从指定的环境配置文件加载配置
            except FileNotFoundError:
                print(f"Error: Config file config/{ops_config}_setting.py not found.") # 如果配置文件未找到，则打印错误消息
        else:
            print("Warning: ops_config environment variable not set. Using base settings.") # 如果 "ops_config" 环境变量不存在，则打印警告消息，并使用基础配置
        db.init_app(self) # 初始化数据库连接，将Flask应用实例传递给SQLAlchemy

# 创建 SQLAlchemy 数据库连接实例
db = SQLAlchemy()

# 创建 Application 实例，传入模块名和模板文件夹路径
app = Application(__name__, template_folder=os.getcwd() + "/web/templates/", root_path=os.getcwd())

'''
函数模板
在模板中使用这些函数，可以动态生成 URL，避免硬编码。
'''
app.add_template_global(UrlManager.buildStaticUrl, "buildStaticUrl") # 将 buildStaticUrl 函数添加到模板全局变量中，命名为 "buildStaticUrl"
app.add_template_global(UrlManager.buildUrl, "buildUrl") # 将 buildUrl 函数添加到模板全局变量中，命名为 "buildUrl"
app.add_template_global(UrlManager.buildImageUrl, "buildImageUrl") # 将 buildImageUrl 函数添加到模板全局变量中，命名为 "buildImageUrl"