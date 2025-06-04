# -*- coding: utf-8 -*-
import re  # 导入正则表达式模块，用于URL匹配

from flask import request, redirect, g  # 从Flask导入请求对象、重定向函数和全局应用上下文对象

from application import app  # 从自定义的application模块导入Flask app实例
from common.libs.UrlManager import UrlManager  # 导入URL管理工具类
from common.libs.user.UserService import UserService  # 导入用户服务类，用于生成认证码等
from common.libs.LogService import LogService  # 导入日志服务类，用于记录访问日志
from common.models.User import User  # 导入用户数据模型


@app.before_request  # 定义一个请求预处理钩子函数，在每个请求处理之前执行
def before_request():
    """
    在每个请求处理之前执行的函数，主要用于后台管理员的身份认证和访问控制。
    """
    # 从应用配置中获取不需要进行任何处理（包括日志记录和登录检查）的URL列表
    ignore_urls = app.config['IGNORE_URLS']
    # 从应用配置中获取不需要进行登录检查的URL列表（但可能仍需记录日志）
    ignore_check_login_urls = app.config['IGNORE_CHECK_LOGIN_URLS']
    # 获取当前请求的路径，例如 "/user/login"
    path = request.path

    # 编译一个正则表达式模式，用于匹配 `ignore_check_login_urls` 中的任何一个URL
    # f'|'.join(...) 会将列表中的URL用'|'（或操作符）连接起来，形成一个大的正则表达式
    pattern = re.compile(f'|'.join(ignore_check_login_urls))
    # 如果当前请求的路径匹配到 `ignore_check_login_urls` 中的任何一个URL
    if pattern.match(path):
        return  # 直接返回，不进行后续的登录检查和日志记录等操作

    # 如果当前请求的路径包含 "/api"，说明是API接口请求（通常给小程序或其他客户端使用）
    # 此拦截器主要针对后台管理界面，API请求有其自身的认证拦截器（通常在另一个文件中或判断条件中）
    if "/api" in path:
        return  # 直接返回，不处理API请求

    # 调用 check_login 函数检查用户是否已登录（通过Cookie）
    user_info = check_login()
    # 初始化Flask的全局应用上下文对象 g 中的 current_user 为 None
    g.current_user = None
    # 如果 check_login 返回了有效的用户信息对象
    if user_info:
        # 将用户信息存储到 g.current_user 中，以便在后续的视图函数或模板中使用
        g.current_user = user_info
        # 记录一条信息日志，表明用户信息已设置
        app.logger.info(
            f"Interceptor: g.current_user set to: {g.current_user}, UID: {g.current_user.uid if hasattr(g.current_user, 'uid') else 'No UID'}")
    else:
        # 如果未登录，也记录一条信息日志
        app.logger.info("Interceptor: user_info is None, g.current_user not set.")

    # 调用日志服务记录本次访问日志
    # 注意：LogService.addAccessLog() 内部会判断 g.current_user 是否存在来记录用户ID
    LogService.addAccessLog()

    # 编译一个正则表达式模式，用于匹配 `ignore_urls` 中的任何一个URL
    pattern = re.compile(f'|'.join(ignore_urls))
    # 如果当前请求的路径匹配到 `ignore_urls` 中的任何一个URL
    if pattern.match(path):
        return  # 直接返回，不进行后续的登录检查（但日志已经记录了）

    # 如果执行到这里，说明当前路径既不在 `ignore_check_login_urls` 中，也不在 `ignore_urls` 中
    # 并且用户未登录 (`user_info` 为 False 或 None)
    if not user_info:
        # 重定向到登录页面
        return redirect(UrlManager.buildUrl("/user/login"))

    # 如果用户已登录，且路径不被忽略，则正常继续处理请求
    return


'''
判断用户是否已经登录
'''
def check_login():
    """
    检查当前请求的用户（后台管理员）是否已经登录。
    通过验证存储在Cookie中的认证信息来实现。
    Returns:
        User: 如果用户已登录且有效，则返回User对象。
        False: 如果用户未登录或认证失败，则返回False。
    """
    # 获取请求中的所有Cookie
    cookies = request.cookies
    # 从Cookie中获取名为 AUTH_COOKIE_NAME (在app.config中定义) 的认证Cookie值
    auth_cookie = cookies[app.config['AUTH_COOKIE_NAME']] if app.config['AUTH_COOKIE_NAME'] in cookies else None
    # 记录获取到的认证Cookie值（用于调试）
    app.logger.info(auth_cookie)
    # 如果认证Cookie不存在
    if auth_cookie is None:
        return False  # 用户未登录

    # 认证Cookie的值通常由 "认证码#用户ID" 组成，用 "#" 分隔
    auth_info = auth_cookie.split("#")
    # 如果分隔后的部分不等于2，说明Cookie格式不正确
    if len(auth_info) != 2:
        return False  # 认证信息格式错误

    try:
        # 从分隔后的第二部分获取用户ID，并查询数据库获取用户信息
        # 使用 .first() 获取第一条匹配的记录或None
        user_info = User.query.filter_by(uid=auth_info[1]).first()
    except Exception:
        # 如果数据库查询过程中发生异常
        return False  # 查询失败

    # 如果根据用户ID未找到对应的用户信息
    if user_info is None:
        return False  # 用户不存在

    # 验证Cookie中的认证码是否与根据用户信息重新生成的认证码一致
    # UserService.geneAuthCode(user_info) 会基于用户信息（通常包含盐值、密码等）生成一个动态认证码
    if auth_info[0] != UserService.geneAuthCode(user_info):
        return False  # 认证码不匹配，可能Cookie被篡改或已过期（取决于geneAuthCode的实现）

    # 检查用户状态是否为正常状态（例如，1代表正常）
    if user_info.status != 1:
        return False  # 用户状态异常（如被禁用）

    # 所有检查通过，返回用户信息对象，表示用户已成功登录
    return user_info