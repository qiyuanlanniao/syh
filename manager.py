# -*- coding: utf-8 -*-
import click

from application import app
from jobs.launcher import runjob

import www

# job entrance
app.cli.add_command(runjob)


@click.command()
@click.option("--host", "-h", default="0.0.0.0", help="Hostname to listen on.")
@click.option("--port", "-p", default=None, type=int, help="Port to listen on.")
@click.option("--debug", "-d", is_flag=True, help="Enable debug mode.")
def runserver(host, port, debug):
    """运行 Flask 开发服务器"""
    # 如果未指定端口，使用配置中的端口
    if port is None:
        port = app.config.get('SERVER_PORT', 5000)  # 添加默认值以防配置中没有
    app.debug = debug
    print("Runserver function called...")  # 添加这行
    app.run(host=host, port=port, debug=debug, use_reloader=debug)


app.cli.add_command(runserver)
if __name__ == '__main__':
    try:
        import sys

        sys.exit(app.cli())  # 使用 app.cli() 来调用 click 命令
    except Exception as e:
        import traceback

        traceback.print_exc()
