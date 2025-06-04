# -*- coding: utf-8 -*-
from flask import Blueprint, request, redirect, jsonify
from sqlalchemy import or_, desc

from application import app, db
from common.libs.Helper import ops_render, iPagination, getCurrentDate
from common.libs.UrlManager import UrlManager
from common.libs.user.UserService import UserService
from common.models.User import User
from common.models.log.AppAccessLog import AppAccessLog

# 创建一个名为 'account_page' 的蓝图，用于组织和管理与账户相关的路由
route_account = Blueprint('account_page', __name__)


# 定义账户列表页面的路由
@route_account.route("/index")
def index():
    """
    账户列表页面，展示账户信息，支持搜索和分页。
    """
    resp_data = {}  # 用于存储返回给模板的数据
    req = request.values  # 获取请求参数

    # 获取当前页码，如果请求参数中没有 'p' 或者 'p' 为空，则默认为第一页
    page = int(req['p']) if ('p' in req and req['p']) else 1

    # 构建查询对象，默认查询所有用户
    query = User.query

    # 如果请求参数中包含 'mix_kw'，则进行模糊搜索，可以搜索昵称或手机号
    if 'mix_kw' in req:
        rule = or_(User.nickname.ilike("%{0}%".format(req['mix_kw'])), User.mobile.ilike("%{0}%".format(req['mix_kw'])))
        query = query.filter(rule)

    # 如果请求参数中包含 'status'，则根据状态进行过滤
    if 'status' in req and int(req['status']) > -1:
        query = query.filter(User.status == int(req['status']))

    # 构建分页参数
    page_params = {
        'total': query.count(),  # 总记录数
        'page_size': app.config['PAGE_SIZE'],  # 每页显示的记录数，从配置文件中获取
        'page': page,  # 当前页码
        'display': app.config['PAGE_DISPLAY'],  # 显示的分页按钮数量，从配置文件中获取
        'url': request.full_path.replace("&p={}".format(page), "")  # 分页链接，移除当前页码参数
    }

    # 创建分页对象
    pages = iPagination(page_params)

    # 计算查询的 offset 和 limit
    offset = (page - 1) * app.config['PAGE_SIZE']
    limit = app.config['PAGE_SIZE'] * page

    # 查询用户列表，按照 uid 降序排序
    list = query.order_by(User.uid.desc()).all()[offset:limit]

    # 将数据存储到 resp_data 中
    resp_data['list'] = list
    resp_data['pages'] = pages
    resp_data['search_con'] = req  # 保存搜索条件，用于在页面上显示
    resp_data['status_mapping'] = app.config['STATUS_MAPPING']  # 状态映射，用于在页面上显示状态名称

    # 渲染模板并返回
    return ops_render("account/index.html", resp_data)


# 定义账户信息页面的路由
@route_account.route("/info")
def info():
    """
    账户信息页面，展示账户的详细信息和访问日志，支持分页。
    """
    resp_data = {}  # 用于存储返回给模板的数据
    req = request.args  # 使用 request.args 获取 GET 参数
    uid = int(req.get('id', 0))  # 获取用户ID，默认为0

    # 获取访问记录的分页参数，统一使用 'p' (因为你的 common/pagenation.html 用的是 'p')
    log_page = int(req.get('p', 1))  # 默认为第1页

    # 构建返回URL
    reback_url = UrlManager.buildUrl("/account/index")
    # 如果用户ID小于1，则重定向到账户列表页面
    if uid < 1:
        return redirect(reback_url)

    # 根据用户ID查询用户信息
    user_info = User.query.filter(User.uid == uid).first()
    # 如果用户信息不存在，则重定向到账户列表页面
    if not user_info:
        return redirect(reback_url)

    # ---- 访问记录分页逻辑 ----
    query_access_log = AppAccessLog.query.filter_by(uid=user_info.uid)

    log_page_size = app.config.get('LOG_PAGE_SIZE', 10)

    # 构建分页URL，模仿 index() 的方式
    # 1. 获取当前请求的完整路径，但移除 'p' 参数（如果存在）
    # 确保所有其他参数（如 'id'）都保留
    current_url_without_page_param = request.full_path
    if f"&p={log_page}" in current_url_without_page_param:
        current_url_without_page_param = current_url_without_page_param.replace(f"&p={log_page}", "")
    elif f"?p={log_page}" in current_url_without_page_param:  # 如果 p 是第一个参数
        current_url_without_page_param = current_url_without_page_param.replace(f"?p={log_page}", "?")
        if current_url_without_page_param.endswith("?"):  # 如果替换后只剩 '?'，说明没有其他参数
            current_url_without_page_param = request.path  # 只用基础路径
        # 如果替换后 '?' 后面还有内容，例如 "?id=1"，则不需要额外处理，但这种情况较少，通常id在p之前

    # 如果 current_url_without_page_param 中没有问号，说明 id 等参数是通过路径传递的（不太可能）
    # 或者 p 是唯一的查询参数。更稳妥的做法是基于 request.path 和必要的固定参数 (id) 来构建。

    # 一个更健壮的 URL 构建方式，确保 id 参数总是存在，并移除 p 参数
    base_url_for_pagination = f"{request.path}?id={uid}"
    # 如果还有其他非分页的固定参数，也应该加到 base_url_for_pagination 中

    log_page_params = {
        'total': query_access_log.count(),
        'page_size': log_page_size,
        'page': log_page,
        'display': app.config.get('PAGE_DISPLAY', 5),
        'url': base_url_for_pagination  # 使用这个基础URL给iPagination
    }

    log_pages_data = iPagination(log_page_params)

    log_offset = (log_page - 1) * log_page_size
    access_logs = query_access_log.order_by(desc(AppAccessLog.created_time)) \
                                    .offset(log_offset) \
                                    .limit(log_page_size) \
                                    .all()
    # ---- 访问记录分页逻辑结束 ----
    app.logger.info(f"Status Mapping being used: {app.config.get('STATUS_MAPPING')}")
    resp_data['info'] = user_info
    resp_data['access_logs'] = access_logs
    resp_data['access_log_pages'] = log_pages_data
    resp_data['status_mapping'] = app.config.get('STATUS_MAPPING', {})

    # 为了让模板中的分页控件知道当前是哪个页面（如果分页控件需要区分），
    # 或者为了在搜索/筛选时能够正确保持分页，可以传递当前的请求参数
    resp_data['search_con'] = req.to_dict()  # 将请求参数传递给模板，方便后续构建链接

    # 渲染模板并返回
    return ops_render("account/info.html", resp_data)


# 定义账户设置页面的路由
@route_account.route("/set", methods=['GET', 'POST'])
def set():
    """
    账户设置页面，用于创建或编辑账户信息。
    支持 GET 请求显示编辑页面，以及 POST 请求保存账户信息。
    """
    default_pwd = '******'  # 默认密码，用于判断是否修改了密码
    if request.method == 'GET':
        # GET 请求，显示编辑页面
        resp_data = {}
        req = request.args
        uid = int(req.get('id', 0))  # 获取用户ID，默认为0
        info = None
        if uid:
            # 如果有用户ID，则查询用户信息
            info = User.query.filter_by(uid=uid).first()
        resp_data['info'] = info
        return ops_render("account/set.html", resp_data)

    # POST 请求，保存账户信息
    resp = {'code': 200, 'msg': '操作成功~~', 'data': {}}
    req = request.values

    # 获取请求参数
    id = req['id'] if 'id' in req else 0
    nickname = req['nickname'] if 'nickname' in req else ''
    mobile = req['mobile'] if 'mobile' in req else ''
    email = req['email'] if 'email' in req else ''
    login_name = req['login_name'] if 'login_name' in req else ''
    login_pwd = req['login_pwd'] if 'login_pwd' in req else ''

    # 验证参数
    if nickname is None or len(nickname) < 1:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的姓名~~'
        return jsonify(resp)

    if mobile is None or len(mobile) < 1:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的手机号码~~'
        return jsonify(resp)

    if email is None or len(email) < 1:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的邮箱~~'
        return jsonify(resp)

    if login_name is None or len(login_name) < 1:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的登录用户名~~'
        return jsonify(resp)

    if login_pwd is None or len(login_pwd) < 6:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的登录密码~~'
        return jsonify(resp)

    # 验证登录名是否已存在
    has_in = User.query.filter(User.login_name == login_name, User.uid != id).first()
    if has_in:
        resp['code'] = -1
        resp['msg'] = '该登录名已被注册，请换一个试试~~'
        return jsonify(resp)

    # 查询用户信息
    user_info = User.query.filter_by(uid=id).first()
    if user_info:
        # 如果用户存在，则更新用户信息
        model_user = user_info
    else:
        # 如果用户不存在，则创建新用户
        model_user = User()
        model_user.created_time = getCurrentDate()
        model_user.login_salt = UserService.geneSalt().decode('utf-8')  # 生成 salt

    # 更新用户信息
    model_user.nickname = nickname
    model_user.mobile = mobile
    model_user.email = email
    model_user.login_name = login_name
    # 如果密码不等于默认密码，则修改密码
    if login_pwd != default_pwd:
        model_user.login_pwd = UserService.genePwd(login_pwd, model_user.login_salt)  # 生成加密后的密码
    model_user.updated_time = getCurrentDate()

    # 保存到数据库
    db.session.add(model_user)
    db.session.commit()
    return jsonify(resp)


# 定义账户操作页面的路由，例如删除和恢复
@route_account.route("/ops", methods=['POST'])
def ops():
    """
    账户操作接口，用于删除或恢复账户。
    """
    resp = {'code': 200, 'msg': '操作成功~~', 'data': {}}
    req = request.values

    # 获取请求参数
    id = req['id'] if 'id' in req else 0
    act = req['act'] if 'act' in req else ''
    # 验证参数
    if not id:
        resp['code'] = -1
        resp['msg'] = '请选择要操作的账号~~'
        return jsonify(resp)

    if act not in ['remove', 'recover']:
        resp['code'] = -1
        resp['msg'] = '操作有误，请重试~~'
        return jsonify(resp)

    # 查询用户信息
    user_info = User.query.filter_by(uid=id).first()
    if not user_info:
        resp['code'] = -1
        resp['msg'] = '指定账号不存在~~'
        return jsonify(resp)

    # 根据操作类型更新状态
    if act == 'remove':
        user_info.status = 0  # 0表示删除
    elif act == 'recover':
        user_info.status = 1  # 1表示正常

    user_info.updated_time = getCurrentDate()
    # 保存到数据库
    db.session.add(user_info)
    db.session.commit()
    return jsonify(resp)