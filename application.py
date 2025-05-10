# -*- coding: utf-8 -*-

# application.py
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from common.libs.UrlManager import UrlManager


class Application(Flask):
    def __init__(self, import_name, template_folder=None, root_path=None):
        super(Application, self).__init__(import_name, template_folder=template_folder, root_path=root_path,
                                          static_folder=None)
        self.config.from_pyfile('config/base_setting.py')
        ops_config = os.environ.get("ops_config")  # 安全地获取环境变量
        if ops_config:
            try:
                self.config.from_pyfile(f"config/{ops_config}_setting.py")
            except FileNotFoundError:
                print(f"Error: Config file config/{ops_config}_setting.py not found.")
        else:
            print("Warning: ops_config environment variable not set. Using base settings.")
        db.init_app(self)


db = SQLAlchemy()
app = Application(__name__, template_folder=os.getcwd() + "/web/templates/", root_path=os.getcwd())

'''
函数模板
'''
app.add_template_global(UrlManager.buildStaticUrl, "buildStaticUrl")
app.add_template_global(UrlManager.buildUrl, "buildUrl")
app.add_template_global(UrlManager.buildImageUrl, "buildImageUrl")
