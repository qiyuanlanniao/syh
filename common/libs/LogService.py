# common/libs/LogService.py
import json
from flask import request, g
from application import db, app
from common.libs.Helper import getCurrentDate
from common.models.log.AppAccessLog import AppAccessLog
from common.models.log.AppErrorLog import AppErrorLog  # 确保导入 AppErrorLog 模型

"""
日志服务类，提供记录访问日志和错误日志的功能。
"""
class LogService():
    """
    添加访问日志。
    该方法记录用户访问的URL、来源URL、IP地址、请求参数和User-Agent等信息到AppAccessLog表中。
    """
    @staticmethod
    def addAccessLog():
        app.logger.info(f"--- 尝试添加访问日志，URL: {request.url} ---")  # 记录开始尝试添加日志的信息
        # 检查是否存在当前用户，并且用户具有uid属性
        if hasattr(g, 'current_user') and g.current_user and hasattr(g.current_user, 'uid'):
            app.logger.info(f"满足条件: g.current_user.uid = {g.current_user.uid}")  # 记录满足条件的信息
            try:
                target = AppAccessLog()  # 创建 AppAccessLog 对象
                target.uid = g.current_user.uid  # 设置用户ID
                target.target_url = request.url  # 设置目标URL
                # 设置来源URL，如果request.referrer为空，则设置为空字符串
                target.referrer_url = request.referrer if request.referrer is not None else ''

                target.ip = request.remote_addr  # 设置IP地址

                # 尝试将请求参数转换为字典，如果出错则设置为空字典
                try:
                    query_params_dict = request.values.to_dict()
                except Exception:
                    query_params_dict = {}
                target.query_params = json.dumps(query_params_dict)  # 将请求参数转换为JSON字符串

                target.ua = request.headers.get("User-Agent", "")  # 获取 User-Agent，如果不存在则设置为空字符串
                target.created_time = getCurrentDate()  # 设置创建时间（datetime对象）

                db.session.add(target)  # 添加到数据库会话
                db.session.commit()  # 提交到数据库
                app.logger.info(f"成功添加访问日志，用户ID: {g.current_user.uid}, URL: {request.url}")  # 记录成功添加日志的信息
                return True
            except Exception as e:
                # 记录错误信息，包括异常堆栈信息
                app.logger.error(f"添加访问日志时发生错误: {str(e)}", exc_info=True)
                db.session.rollback()  # 回滚数据库事务
                return False
        else:
            # 如果g.current_user不存在，或者g.current_user为None，或者g.current_user没有uid属性，则记录警告信息
            if not hasattr(g, 'current_user'):
                app.logger.warning(f"未添加访问日志，URL: '{request.url}'：g.current_user 未设置。")
            elif not g.current_user:
                app.logger.warning(f"未添加访问日志，URL: '{request.url}'：g.current_user 为 None。")
            elif not hasattr(g.current_user, 'uid'):
                app.logger.warning(
                    f"未添加访问日志，URL: '{request.url}'：g.current_user (类型: {type(g.current_user)}) 没有 'uid' 属性。")
            return False

    """
    添加错误日志。
    该方法记录发生的错误信息、URL、来源URL和请求参数等到AppErrorLog表中。
    """
    @staticmethod
    def addErrorLog(content):
        try:
            target = AppErrorLog()  # 创建 AppErrorLog 对象
            target.target_url = request.url  # 设置目标URL
            # 设置来源URL，如果request.referrer为空，则设置为空字符串
            target.referrer_url = request.referrer if request.referrer is not None else ''  # 处理 None

            # 尝试将请求参数转换为字典，如果出错则设置为空字典
            try:
                query_params_dict = request.values.to_dict()
            except Exception:
                query_params_dict = {}
            target.query_params = json.dumps(query_params_dict)  # 将请求参数转换为JSON字符串

            target.content = content  # 设置错误内容
            target.created_time = getCurrentDate()  # 设置创建时间（datetime对象）

            db.session.add(target)  # 添加到数据库会话
            db.session.commit()  # 提交到数据库
            return True
        except Exception as e:
            # 记录错误信息，包括异常堆栈信息
            app.logger.error(f"添加错误日志时发生错误: {str(e)}", exc_info=True)
            db.session.rollback()  # 回滚数据库事务
            return False