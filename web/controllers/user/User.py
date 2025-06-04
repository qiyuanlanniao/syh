# -*- coding: utf-8 -*- 表示文件编码为 UTF-8，支持中文注释和字符串

import json
# 导入 json 模块，用于处理 JSON 数据

from flask import Blueprint, request, jsonify, make_response, redirect, g
# 从 flask 框架中导入所需模块：
# Blueprint: 用于组织路由的蓝图对象
# request: 请求对象，用于获取请求参数、方法等
# jsonify: 将 Python 字典/列表转换为 JSON 响应
# make_response: 创建响应对象，常用于设置 cookie 或 headers
# redirect: 创建重定向响应
# g: 全局对象，用于在请求期间存储数据，这里用于存储当前用户信息

from application import app, db
# 从 application 包导入 app 实例 (Flask 应用核心) 和 db (SQLAlchemy 数据库实例)

from common.libs.Helper import ops_render
# 从 common.libs.Helper 模块导入自定义的模板渲染函数 ops_render

from common.libs.UrlManager import UrlManager
# 从 common.libs.UrlManager 模块导入自定义的 URL 管理器，用于构建 URL

from common.libs.user.UserService import UserService
# 从 common.libs.user.UserService 模块导入用户服务类，处理用户相关的业务逻辑（如密码加密、生成认证码等）

from common.models.User import User
# 从 common.models.User 模块导入 User 模型类，对应数据库中的用户表

# 创建一个名为 'user_page' 的蓝图对象，URL 前缀默认为空，可以在注册蓝图时指定
route_user = Blueprint('user_page', __name__)


# 定义用户登录路由，支持 GET 和 POST 方法
@route_user.route("/login", methods=['GET', 'POST'])
def login():
    # 如果是 GET 请求，渲染登录页面
    if request.method == 'GET':
        # 调用自定义的 ops_render 函数渲染 'user/login.html' 模板
        return ops_render('user/login.html')

    # 如果是 POST 请求，处理登录逻辑
    # 初始化响应字典，默认成功状态
    resp = {'code': 200, 'msg': '登录成功', 'data': {}}

    # 获取请求参数，request.values 包含 GET 和 POST 的参数
    req = request.values
    # 获取登录用户名，如果参数不存在则设置为空字符串
    login_name = req['login_name'] if 'login_name' in req else ''
    # 获取登录密码，如果参数不存在则设置为空字符串
    login_pwd = req['login_pwd'] if 'login_pwd' in req else ''

    # 参数有效性校验
    # 检查用户名是否为空或长度小于 1
    if login_name is None or len(login_name) < 1:
        # 设置错误码和错误信息
        resp['code'] = -1
        resp['msg'] = '请输入正确的用户名'
        # 将响应字典转换为 JSON 格式返回
        return jsonify(resp)

    # 检查密码是否为空或长度小于 1
    if login_pwd is None or len(login_pwd) < 1:
        # 设置错误码和错误信息
        resp['code'] = -1
        resp['msg'] = '请输入正确的登录密码'
        # 将响应字典转换为 JSON 格式返回
        return jsonify(resp)

    # 根据用户名查询数据库中的用户信息
    user_info = User.query.filter_by(login_name=login_name).first()
    # 检查是否查询到用户
    if not user_info:
        # 如果用户不存在，返回错误信息
        resp['code'] = -1
        resp['msg'] = '请输入正确的用户名和密码~1' # 这里的~1可能用于区分不同的错误原因
        # 将响应字典转换为 JSON 格式返回
        return jsonify(resp)

    # 验证用户输入的密码是否与数据库中存储的加密密码匹配
    # 调用 UserService.genePwd 函数对用户输入的密码进行加密（通常会用到 salt）
    # 然后与数据库中存储的 user_info.login_pwd 进行比对
    if user_info.login_pwd != UserService.genePwd(login_pwd, user_info.login_salt):
        # 如果密码不匹配，返回错误信息
        resp['code'] = -1
        resp['msg'] = '请输入正确的用户名和密码~2' # 这里的~2可能用于区分不同的错误原因
        # 将响应字典转换为 JSON 格式返回
        return jsonify(resp)

    # 检查用户账号状态，status 为 1 通常表示正常
    if user_info.status != 1:
        # 如果账号状态不是正常，返回禁用信息
        resp['code'] = -1
        resp['msg'] = '账号已被禁用，请联系管理员'
        # 将响应字典转换为 JSON 格式返回
        return jsonify(resp)

    # 登录成功
    # 创建一个 HTTP 响应对象，并将成功的响应字典转换为 JSON 字符串作为响应体
    response = make_response(json.dumps(resp))
    # 设置认证 cookie
    # app.config['AUTH_COOKIE_NAME'] 是在应用配置中定义的 cookie 名称
    # cookie 的值格式通常是 "认证码#用户ID"，认证码由 UserService.geneAuthCode 生成
    # 这个认证码通常用于后续请求的身份验证，可能包含用户信息或签名
    response.set_cookie(app.config['AUTH_COOKIE_NAME'], f"{UserService.geneAuthCode(user_info)}#{user_info.uid}")

    # 返回包含 cookie 的响应对象
    return response


# 定义用户资料编辑路由，支持 GET 和 POST 方法
@route_user.route("/edit", methods=['GET', 'POST'])
def edit():
    # 如果是 GET 请求，渲染编辑资料页面
    if request.method == 'GET':
        # 调用 ops_render 渲染 'user/edit.html' 模板，并传递 {'current': 'edit'} 参数（可能用于导航栏高亮）
        return ops_render("user/edit.html", {'current': 'edit'})

    # 如果是 POST 请求，处理资料编辑逻辑
    # 初始化响应字典，默认成功状态
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    # 获取请求参数
    req = request.values
    # 获取昵称和邮箱参数
    nickname = req['nickname'] if 'nickname' in req else ''
    email = req['email'] if 'email' in req else ''

    # 校验昵称参数
    if nickname is None or len(nickname) < 1:
        # 设置错误码和错误信息
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的姓名~'
        # 返回 JSON 响应
        return jsonify(resp)

    # 校验邮箱参数
    if email is None or len(email) < 1:
        # 设置错误码和错误信息
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的邮箱~'
        # 返回 JSON 响应
        return jsonify(resp)

    # 从全局对象 g 中获取当前登录用户信息
    # 注意：这里依赖于一个前置处理器@app.before_request
    # 在请求处理前已经根据 cookie 验证了用户身份并将用户信息存储在 g.current_user 中
    user_info = g.current_user
    # 更新用户信息
    user_info.nickname = nickname
    user_info.email = email
    # 将更新后的用户信息添加到数据库会话
    db.session.add(user_info)
    # 提交数据库更改
    db.session.commit()
    # 返回 JSON 响应
    return jsonify(resp)


# 定义用户密码重置路由，支持 GET 和 POST 方法
@route_user.route("/reset-pwd", methods=['GET', 'POST'])
def resetPwd():
    # 如果是 GET 请求，渲染重置密码页面
    if request.method == 'GET':
        # 调用 ops_render 渲染 'user/reset_pwd.html' 模板，并传递 {'current': 'reset-pwd'} 参数
        return ops_render("user/reset_pwd.html", {'current': 'reset-pwd'})

    # 如果是 POST 请求，处理密码重置逻辑
    # 初始化响应字典，默认成功状态
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}
    # 获取请求参数
    req = request.values

    # 获取原密码和新密码参数
    old_password = req['old_password'] if 'old_password' in req else ''
    new_password = req['new_password'] if 'new_password' in req else ''

    # 校验原密码，检查是否为空或长度小于 6
    if old_password is None or len(old_password) < 6:
        # 设置错误码和错误信息
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的原密码~'
        # 返回 JSON 响应
        return jsonify(resp)

    # 校验新密码，检查是否为空或长度小于 6
    if new_password is None or len(new_password) < 6:
        # 设置错误码和错误信息
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的新密码~'
        # 返回 JSON 响应
        return jsonify(resp)

    # 检查新密码是否与原密码相同
    if new_password == old_password:
        # 设置错误码和错误信息
        resp['code'] = -1
        resp['msg'] = '新密码不能和原密码相同~'
        # 返回 JSON 响应
        return jsonify(resp)

    # 从全局对象 g 中获取当前登录用户信息
    user_info = g.current_user
    # 使用新密码和用户的 salt 生成新的加密密码
    user_info.login_pwd = UserService.genePwd(new_password, user_info.login_salt)

    # 将更新后的用户信息添加到数据库会话
    db.session.add(user_info)
    # 提交数据库更改
    db.session.commit()

    # 密码修改成功后，通常需要更新或重新设置认证 cookie
    # 这是为了使用新的用户状态（比如密码修改时间）或者防止旧的认证信息被继续使用
    # 创建一个 HTTP 响应对象，并将成功响应字典转换为 JSON 字符串作为响应体
    response = make_response(json.dumps(resp))
    # 重新生成认证码并设置新的 cookie
    response.set_cookie(app.config['AUTH_COOKIE_NAME'], f"{UserService.geneAuthCode(user_info)}#{user_info.uid}")

    # 返回包含新 cookie 的响应对象
    return response


# 定义用户登出路由
@route_user.route("/logout")
def logout():
    # 创建一个重定向到登录页面的响应对象
    # UrlManager.buildUrl 用于构建应用内部的 URL，这里构建 /user/login 的 URL
    response = make_response(redirect(UrlManager.buildUrl("/user/login")))
    # 删除认证 cookie
    # app.config['AUTH_COOKIE_NAME'] 是之前设置的 cookie 名称
    response.delete_cookie(app.config['AUTH_COOKIE_NAME'])
    # 返回响应对象，浏览器会根据响应进行重定向并删除 cookie
    return response