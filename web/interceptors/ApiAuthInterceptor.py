# -*- coding: utf-8 -*-
import re  # 导入正则表达式模块

from flask import request, g, jsonify  # 导入flask框架的相关模块，request用于处理请求，g用于存储全局变量，jsonify用于返回json数据

from application import app  # 导入application模块中的app对象，通常是flask的app实例
from common.libs.LogService import LogService  # 导入自定义的日志服务模块
from common.libs.member.MemberService import MemberService  # 导入自定义的会员服务模块
from common.models.member.Member import Member  # 导入会员模型

'''
api认证
'''


@app.before_request
def before_request():
    """
    API请求预处理函数，在每个API请求之前执行。
    进行用户登录状态校验和访问日志记录。
    """
    api_ignore_urls = app.config['API_IGNORE_URLS']  # 从app的配置中获取API_IGNORE_URLS，通常是无需登录验证的URL列表
    path = request.path  # 获取请求的路径

    # 如果请求路径不包含"/api"，则直接返回，不进行后续处理
    if "/api" not in path:
        return

    member_info = check_member_login()  # 调用check_member_login函数检查用户是否已登录，如果登录则返回用户信息
    g.member_info = None  # 初始化g.member_info为None，用于存储当前登录用户的信息
    if member_info:
        g.member_info = member_info  # 如果用户已登录，则将用户信息存储到g.member_info中，供后续请求使用

    # 加入访问日志
    LogService.addAccessLog()  # 调用LogService.addAccessLog()记录访问日志

    # 构建一个正则表达式，用于匹配无需登录验证的URL
    pattern = re.compile('%s' % "|".join(api_ignore_urls))  #  将API_IGNORE_URLS列表用"|"连接成字符串，作为正则表达式的模式
    if pattern.match(path):
        return  # 如果请求的路径匹配无需登录验证的URL，则直接返回，不进行后续处理

    # 如果用户未登录，则返回错误信息
    if not member_info:
        resp = {'code': -1, 'msg': '未登录~', 'data': {}}  # 构建一个包含错误信息的字典
        return jsonify(resp)  # 将字典转换为json格式并返回
    return  # 如果用户已登录，则继续执行后续请求


def check_member_login():
    """
    判断用户是否已经登陆，通过Authorization header中的token进行验证。
    """
    auth_cookie = request.headers.get("Authorization")  # 从请求头中获取Authorization信息，通常包含token
    if auth_cookie is None:
        return False  # 如果Authorization header不存在，则认为用户未登录，返回False

    auth_info = auth_cookie.split("#")  # 将Authorization信息按照"#"分割成两部分，通常是auth_code#member_id
    if len(auth_info) != 2:
        return False  # 如果分割后的长度不为2，则认为Authorization信息格式错误，返回False
    try:
        member_info = Member.query.filter_by(id=auth_info[1]).first()  # 从数据库中查询用户ID为auth_info[1]的会员信息
    except Exception:
        return False  # 查询数据库发生异常，则认为验证失败，返回False
    if member_info is None:
        return False  # 如果数据库中不存在该用户，则认为用户不存在，返回False

    # 验证Authorization信息中的auth_code是否正确
    if auth_info[0] != MemberService.geneAuthCode(member_info):
        return False  # 如果auth_code不匹配，则认为验证失败，返回False

    # 验证用户状态是否正常
    if member_info.status != 1:
        return False  # 如果用户状态不为1（通常表示正常），则认为用户被禁用，返回False

    return member_info  # 如果所有验证都通过，则认为用户已登录，返回用户信息