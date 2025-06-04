# -*- coding: utf-8 -*-
import click  # 导入 click 库，用于创建命令行界面

from application import app  # 从 application 模块导入 app 对象 (Flask 实例)
from jobs.launcher import runjob  # 从 jobs.launcher 模块导入 runjob 函数 (用于启动后台任务)

import www  # 导入 www 模块，通常包含 Web 相关的代码 (例如路由，视图函数)

# job entrance
# 将 runjob 函数注册为 app 的一个命令行子命令
# 这样可以通过命令行运行 runjob 函数
app.cli.add_command(runjob)


@click.command()  # 使用 click.command() 装饰器将 runserver 函数转换为一个 click 命令
@click.option("--host", "-h", default="0.0.0.0", help="Hostname to listen on.")  # 定义 host 选项，默认值为 "0.0.0.0"
@click.option("--port", "-p", default=None, type=int, help="Port to listen on.")  # 定义 port 选项，类型为 int，默认值为 None
@click.option("--debug", "-d", is_flag=True, help="Enable debug mode.")  # 定义 debug 选项，是一个标志，默认值为 False
def runserver(host, port, debug):
    """运行 Flask 开发服务器"""
    # 如果未指定端口，使用配置中的端口
    if port is None:
        port = app.config.get('SERVER_PORT', 5000)  # 从 Flask 应用配置中获取 SERVER_PORT，如果没有则使用 5000 作为默认值
    app.debug = debug  # 设置 Flask 应用的 debug 模式
    print("Runserver function called...")  # 添加这行，用于调试，显示 runserver 函数已被调用
    app.run(host=host, port=port, debug=debug, use_reloader=debug)  # 启动 Flask 开发服务器，并传入 host, port, debug 和 use_reloader 参数


# 将 runserver 函数注册为 app 的一个命令行子命令
# 这样可以通过命令行运行 runserver 函数
app.cli.add_command(runserver)

# 只有当该文件作为主程序运行时，才会执行以下代码
if __name__ == '__main__':
    try:
        import sys  # 导入 sys 模块，用于访问系统相关的参数和函数

        sys.exit(app.cli())  # 调用 app.cli() 来执行 click 命令，并使用 sys.exit() 来返回命令的退出码
    except Exception as e:  # 捕获所有异常
        import traceback  # 导入 traceback 模块，用于打印异常的堆栈信息

        traceback.print_exc()  # 打印异常的堆栈信息，方便调试