# -*- coding: utf-8 -*-
from application import app  # 从 application 模块导入 app 实例
from flask import Blueprint, send_from_directory  # 导入 Blueprint 用于创建可插拔的视图函数集合， send_from_directory 用于发送静态文件


route_static = Blueprint('static', __name__)


# 定义一个路由规则，该规则匹配任何以 "/" 开头的 URL，并将后面的路径作为 filename 参数传递给 index 函数。
# <path:filename> 表示匹配任意路径，包括多个目录。
@route_static.route("/<path:filename>")
def index(filename):
    """
    处理静态文件请求的视图函数。

    Args:
        filename (str): 请求的静态文件名，包括可能的目录结构。

    Returns:
        Response: 从指定目录发送的静态文件。
    """
    # 使用 app.logger.info 记录 filename，这有助于调试和跟踪。
    # app.logger 是 Flask 应用的日志记录器，用于输出各种级别的日志信息。
    app.logger.info(filename)

    # 使用 send_from_directory 函数从指定的目录发送静态文件。
    # app.root_path 获取 Flask 应用的根目录。
    # app.root_path + "/web/static/" 构建了静态文件所在的完整路径。
    # filename 是用户请求的文件名。
    # send_from_directory 函数会自动处理文件的 MIME 类型，并设置正确的 HTTP 响应头。
    return send_from_directory(app.root_path + "/web/static/", filename)