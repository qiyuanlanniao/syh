# -*- coding: utf-8 -*-
# 导入标准库，用于动态导入模块，处理系统相关信息，以及打印错误堆栈
import importlib
import sys
import traceback

# 导入 click 库，用于创建命令行界面
import click

# 导入应用实例，通常在 application.py 中定义
from application import app


@click.command()  # 将函数转化为一个命令行命令
@click.option("-m", "--name", "name", required=True, help="指定job名")  # 定义一个命令行选项 -m 或 --name，用于指定 job 的名称，必须提供
@click.option("-a", "--act", "act", required=False, help="Job动作")  # 定义一个命令行选项 -a 或 --act，用于指定 job 的动作，非必须
@click.option("-p", "--param", "param", multiple=True, required=False, help="业务参数")  # 定义一个命令行选项 -p 或 --param，用于指定业务参数，允许多次指定，非必须
@click.pass_context  # 传递 click 上下文对象到函数
def runjob(ctx, name, act, param):
    """job处理异步消息"""  # 命令的描述信息

    # 格式化模块名
    module_path = name.replace("/", ".")  # 将 job 名称中的斜杠替换为点，用于构建模块路径
    full_module_name = "jobs.tasks." + module_path  # 构建完整的模块名，例如 jobs.tasks.Test 或 jobs.tasks.test.Index

    try:
        # --- 改进的动态导入方式 ---
        job_module = importlib.import_module(full_module_name)  # 动态导入模块，根据完整的模块名导入
        # 获取 JobTask 类
        job_target_class = getattr(job_module, "JobTask")  # 从导入的模块中获取名为 "JobTask" 的类
        # 实例化 JobTask
        target = job_target_class()  # 创建 JobTask 类的实例
        # ------------------------

        ret_params = {
            "name": name,
            "act": act,
            "param": param # param 已经是一个元组，因为 multiple=True
        }

        # --- 添加 Flask 应用上下文 ---
        with app.app_context():
            # 在这个块内，就可以安全地访问需要应用上下文的功能，比如 db.session
            app.logger.info(f"Starting job: {name} with params: {ret_params}")  # 使用 Flask 应用的 logger 记录 job 启动信息
            target.run(ret_params)  # 调用 JobTask 实例的 run 方法，传递参数
            app.logger.info(f"Job {name} finished successfully.")  # 使用 Flask 应用的 logger 记录 job 完成信息
        # --------------------------

    except ImportError:  # 捕获导入错误
        click.echo(f"Error: Could not import job module: {full_module_name}", err=True)  # 打印错误信息到标准错误输出
        click.echo("Please check the -m parameter and the file path in jobs/tasks.", err=True)  # 打印提示信息到标准错误输出
        sys.exit(1)  # 使用非零状态码退出程序，表示发生错误
    except AttributeError:  # 捕获属性错误，例如找不到 JobTask 类
        click.echo(f"Error: Could not find 'JobTask' class in module: {full_module_name}", err=True)  # 打印错误信息到标准错误输出
        click.echo("Please ensure the job file defines a 'JobTask' class.", err=True)  # 打印提示信息到标准错误输出
        sys.exit(1)  # 使用非零状态码退出程序，表示发生错误
    except Exception as e:  # 捕获其他所有异常
        # Catch any other exceptions during job execution
        click.echo(f"An error occurred while running the job: {name}", err=True)  # 打印错误信息到标准错误输出
        traceback.print_exc()  # 打印完整的错误堆栈信息到标准错误输出，方便调试
        sys.exit(1)  # 使用非零状态码退出程序，表示发生错误


def tips():
    tip_msg = '''
        请正确调度Job
        python manage runjob -m Test  (  jobs/tasks/Test.py )
        python manage runjob -m test/Index (  jobs/tasks/test/Index.py )
    '''
    app.logger.info(tip_msg)
    return False