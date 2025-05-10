# -*- coding: utf-8 -*-
import importlib
import sys
import traceback

import click

from application import app


@click.command()
@click.option("-m", "--name", "name", required=True, help="指定job名")
@click.option("-a", "--act", "act", required=False, help="Job动作")
@click.option("-p", "--param", "param", multiple=True, required=False, help="业务参数")
@click.pass_context
def runjob(ctx, name, act, param):
    """job处理异步消息"""

    # 格式化模块名
    module_path = name.replace("/", ".")
    full_module_name = "jobs.tasks." + module_path

    try:
        # --- 改进的动态导入方式 ---
        job_module = importlib.import_module(full_module_name)
        # 获取 JobTask 类
        job_target_class = getattr(job_module, "JobTask")
        # 实例化 JobTask
        target = job_target_class()
        # ------------------------

        ret_params = {
            "name": name,
            "act": act,
            "param": param # 'param' is already a tuple due to multiple=True
        }

        # --- 添加 Flask 应用上下文 ---
        with app.app_context():
            # 在这个块内，就可以安全地访问需要应用上下文的功能，比如 db.session
            app.logger.info(f"Starting job: {name} with params: {ret_params}")
            target.run(ret_params)
            app.logger.info(f"Job {name} finished successfully.")
        # --------------------------

    except ImportError:
        click.echo(f"Error: Could not import job module: {full_module_name}", err=True)
        click.echo("Please check the -m parameter and the file path in jobs/tasks.", err=True)
        sys.exit(1) # Exit with a non-zero status to indicate failure
    except AttributeError:
        click.echo(f"Error: Could not find 'JobTask' class in module: {full_module_name}", err=True)
        click.echo("Please ensure the job file defines a 'JobTask' class.", err=True)
        sys.exit(1) # Exit with a non-zero status to indicate failure
    except Exception as e:
        # Catch any other exceptions during job execution
        click.echo(f"An error occurred while running the job: {name}", err=True)
        traceback.print_exc() # Print the full traceback
        sys.exit(1) # Exit with a non-zero status to indicate failure


def tips():
    tip_msg = '''
        请正确调度Job
        python manage runjob -m Test  (  jobs/tasks/Test.py )
        python manage runjob -m test/Index (  jobs/tasks/test/Index.py )
    '''
    app.logger.info(tip_msg)
    return False

