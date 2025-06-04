# -*- coding: utf-8 -*-
from flask import Blueprint, request, redirect, jsonify

from application import app, db
from common.libs.Helper import ops_render, iPagination, getCurrentDate
from common.libs.UrlManager import UrlManager
from common.models.member.Member import Member

# 创建一个蓝图对象，用于组织和管理会员相关的路由
route_member = Blueprint('member_page', __name__)


# 会员列表页面路由
@route_member.route("/index")
def index():
    """
    会员列表页面
    :return: 渲染后的会员列表页面
    """
    resp_data = {}  # 初始化响应数据字典
    req = request.values  # 获取请求参数

    # 获取当前页码，如果请求中包含 'p' 参数且不为空，则使用该参数的值，否则默认为 1
    page = int(req['p']) if ('p' in req and req['p']) else 1
    query = Member.query  # 创建 Member 模型的查询对象

    # 如果请求中包含 'mix_kw' 参数，则根据昵称模糊搜索会员
    if 'mix_kw' in req:
        # ilike 是不区分大小写的模糊查询
        query = query.filter(Member.nickname.ilike(f"%{req['mix_kw']}%"))

    # 如果请求中包含 'status' 参数且值大于 -1，则根据状态筛选会员
    if 'status' in req and int(req['status']) > -1:
        query = query.filter(Member.status == int(req['status']))

    # 构建分页参数
    page_params = {
        'total': query.count(),  # 总记录数
        'page_size': app.config['PAGE_SIZE'],  # 每页显示的记录数，从 app.config 中获取
        'page': page,  # 当前页码
        'display': app.config['PAGE_DISPLAY'],  # 显示的页码数量，从 app.config 中获取
        'url': request.full_path.replace(f"&p={page}", "")  # 去除分页参数的 URL，用于生成分页链接
    }

    # 创建分页对象
    pages = iPagination(page_params)
    # 计算偏移量，用于数据库查询
    offset = (page - 1) * app.config['PAGE_SIZE']
    # 查询当前页的会员列表，并按照 id 倒序排列
    list = query.order_by(Member.id.desc()).offset(offset).limit(app.config['PAGE_SIZE']).all()

    # 将查询结果和分页对象添加到响应数据中
    resp_data['list'] = list
    resp_data['pages'] = pages
    resp_data['search_con'] = req  # 将搜索条件添加到响应数据中，用于在页面上显示
    resp_data['status_mapping'] = app.config['STATUS_MAPPING']  # 将状态映射添加到响应数据中

    resp_data['current'] = 'index'  # 设置当前页面标识，用于导航栏高亮
    return ops_render("member/index.html", resp_data)  # 渲染会员列表页面


# 会员信息页面路由
@route_member.route("/info")
def info():
    """
    会员信息页面
    :return: 渲染后的会员信息页面
    """
    resp_data = {}  # 初始化响应数据字典
    req = request.args  # 获取请求参数
    id = int(req.get('id', 0))  # 获取会员 id，如果不存在则默认为 0
    reback_url = UrlManager.buildUrl("/member/index")  # 构建返回会员列表页面的 URL

    # 如果 id 小于 1，则重定向到会员列表页面
    if id < 1:
        return redirect(reback_url)
    # 根据 id 查询会员信息
    info = Member.query.filter_by(id=id).first()
    # 如果会员信息不存在，则重定向到会员列表页面
    if not info:
        return redirect(reback_url)
    # 将会员信息添加到响应数据中
    resp_data['info'] = info
    resp_data['current'] = 'index'  # 设置当前页面标识，用于导航栏高亮
    return ops_render("member/info.html", resp_data)  # 渲染会员信息页面


# 会员设置页面路由
@route_member.route("/set", methods=['GET', 'POST'])
def set():
    """
    会员设置页面
    :return: GET 请求：渲染后的会员设置页面；POST 请求：JSON 响应，包含操作结果
    """
    if request.method == 'GET':  # 如果是 GET 请求
        resp_data = {}  # 初始化响应数据字典
        req = request.args  # 获取请求参数
        id = int(req.get('id', 0))  # 获取会员 id，如果不存在则默认为 0
        reback_url = UrlManager.buildUrl('/member/index')  # 构建返回会员列表页面的 URL
        # 如果 id 小于 1，则重定向到会员列表页面
        if id < 1:
            return redirect(reback_url)

        # 根据 id 查询会员信息
        info = Member.query.filter_by(id=id).first()
        # 如果会员信息不存在，则重定向到会员列表页面
        if not info:
            return redirect(reback_url)

        # 如果会员状态不是 1 (正常)，则重定向到会员列表页面
        if info.status != 1:
            return redirect(reback_url)

        # 将会员信息添加到响应数据中
        resp_data['info'] = info
        resp_data['current'] = 'index'  # 设置当前页面标识，用于导航栏高亮
        return ops_render("member/set.html", resp_data)  # 渲染会员设置页面

    # 如果是 POST 请求
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}  # 初始化 JSON 响应数据
    req = request.values  # 获取请求参数
    id = req['id'] if 'id' in req else 0  # 获取会员 id，如果不存在则默认为 0
    nickname = req['nickname'] if 'nickname' in req else ''  # 获取会员昵称，如果不存在则默认为空字符串

    # 校验昵称是否为空
    if nickname is None or len(nickname) < 1:
        resp['code'] = -1  # 设置错误码
        resp['msg'] = '请输入规范的姓名！'  # 设置错误消息
        return jsonify(resp)  # 返回 JSON 响应

    # 根据 id 查询会员信息
    member_info = Member.query.filter_by(id=id).first()
    # 如果会员信息不存在，则返回错误响应
    if not member_info:
        resp['code'] = -1  # 设置错误码
        resp['msg'] = '指定的会员不存在！'  # 设置错误消息
        return jsonify(resp)  # 返回 JSON 响应

    # 更新会员昵称和更新时间
    member_info.nickname = nickname
    member_info.updated_time = getCurrentDate()
    db.session.add(member_info)  # 将会员信息添加到数据库会话
    db.session.commit()  # 提交数据库会话，保存更改
    return jsonify(resp)  # 返回 JSON 响应


# 会员评论页面路由
@route_member.route("/comment")
def comment():
    """
    会员评论页面
    :return: 渲染后的会员评论页面
    """
    return ops_render("member/comment.html")  # 渲染会员评论页面


# 会员操作路由 (删除/恢复)
@route_member.route('/ops', methods=['POST'])
def ops():
    """
    会员操作 (删除/恢复)
    :return: JSON 响应，包含操作结果
    """
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}  # 初始化 JSON 响应数据
    req = request.values  # 获取请求参数

    id = req['id'] if 'id' in req else 0  # 获取会员 id，如果不存在则默认为 0
    act = req['act'] if 'act' in req else ''  # 获取操作类型 (remove/recover)，如果不存在则默认为空字符串

    # 校验 id 是否为空
    if not id:
        resp['code'] = -1  # 设置错误码
        resp['msg'] = '请选择要操作的账号'  # 设置错误消息
        return jsonify(resp)  # 返回 JSON 响应

    # 校验操作类型是否合法
    if act not in ['remove', 'recover']:
        resp['code'] = -1  # 设置错误码
        resp['msg'] = '操作有误，请重试'  # 设置错误消息
        return jsonify(resp)  # 返回 JSON 响应

    # 根据 id 查询会员信息
    member_info = Member.query.filter_by(id=id).first()
    # 如果会员信息不存在，则返回错误响应
    if not member_info:
        resp['code'] = -1  # 设置错误码
        resp['msg'] = '指定会员不存在'  # 设置错误消息
        return jsonify(resp)  # 返回 JSON 响应

    # 根据操作类型更新会员状态
    if act == 'remove':
        member_info.status = 0  # 设置为删除状态
    elif act == 'recover':
        member_info.status = 1  # 设置为正常状态

    # 更新会员更新时间
    member_info.updated_time = getCurrentDate()
    db.session.add(member_info)  # 将会员信息添加到数据库会话
    db.session.commit()  # 提交数据库会话，保存更改

    return jsonify(resp)  # 返回 JSON 响应