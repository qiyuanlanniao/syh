# -*- coding: utf-8 -*-
from decimal import Decimal

from flask import Blueprint, request, jsonify, redirect
from sqlalchemy import or_

from application import db, app
from common.libs.Helper import ops_render, getCurrentDate, iPagination, getDictFilterField
from common.libs.UrlManager import UrlManager
from common.libs.goods.GoodsService import GoodsService
from common.models.User import User
from common.models.goods.Goods import Goods
from common.models.goods.GoodsCat import GoodsCat
from common.models.goods.GoodsSaleChangeLog import GoodsSaleChangeLog
from common.models.goods.GoodsStockChangeLog import GoodsStockChangeLog

# 创建一个蓝图，用于组织和管理商品相关的路由
route_goods = Blueprint('goods_page', __name__)


# 商品列表页面的路由
@route_goods.route("/index")
def index():
    """
    商品列表页面
    :return: 渲染后的商品列表页面
    """
    resp_data = {}  # 用于存储返回给前端的数据
    req = request.values  # 获取请求参数

    # 获取当前页码，如果请求参数中没有'p'或者'p'为空，则默认为第1页
    page = int(req['p']) if ('p' in req and req['p']) else 1

    # 构建查询对象，默认查询所有商品
    query = Goods.query

    # 搜索功能：如果请求参数中有'mix_kw'，则根据关键词模糊匹配商品名称或标签
    if 'mix_kw' in req:
        # 使用or_条件，只要商品名称或标签包含关键词就符合条件
        rule = or_(Goods.name.ilike("%{0}%".format(req['mix_kw'])), Goods.tags.ilike("%{0}%".format(req['mix_kw'])))
        query = query.filter(rule)  # 添加过滤条件

    # 状态过滤：如果请求参数中有'status'，并且状态值大于-1，则根据状态过滤商品
    if 'status' in req and int(req['status']) > -1:
        query = query.filter(Goods.status == int(req['status']))  # 添加过滤条件

    # 分类过滤：如果请求参数中有'cat_id'，并且分类ID大于0，则根据分类过滤商品
    if 'cat_id' in req and int(req['cat_id']) > 0:
        query = query.filter(Goods.cat_id == int(req['cat_id']))  # 添加过滤条件

    # 分页参数
    page_params = {
        'total': query.count(),  # 总记录数
        'page_size': app.config['PAGE_SIZE'],  # 每页显示的记录数，从配置中获取
        'page': page,  # 当前页码
        'display': app.config['PAGE_DISPLAY'],  # 显示的分页按钮数量，从配置中获取
        'url': request.full_path.replace("&p={}".format(page), "")  # 分页URL，移除当前页码参数
    }
    # 创建分页对象
    pages = iPagination(page_params)

    # 计算偏移量，用于数据库查询
    offset = (page - 1) * app.config['PAGE_SIZE']

    # 查询当前页的商品列表，按照ID倒序排列
    list = query.order_by(Goods.id.desc()).offset(offset).limit(app.config['PAGE_SIZE']).all()

    # 获取所有商品分类，并构建ID到分类名称的映射关系
    cat_mapping = getDictFilterField(GoodsCat, GoodsCat.id, "id", [])

    # 组织返回给前端的数据
    resp_data['list'] = list  # 商品列表
    resp_data['pages'] = pages  # 分页对象
    resp_data['search_con'] = req  # 搜索条件
    resp_data['status_mapping'] = app.config['STATUS_MAPPING']  # 状态映射，从配置中获取
    resp_data['cat_mapping'] = cat_mapping  # 分类映射
    resp_data['current'] = 'index'  # 当前页面标识

    # 渲染模板并返回
    return ops_render("goods/index.html", resp_data)


# 商品详情页面的路由
@route_goods.route("/info")
def info():
    """
    商品详情页面
    :return: 渲染后的商品详情页面
    """
    resp_data = {}  # 用于存储返回给前端的数据
    req = request.args  # 获取请求参数

    # 获取商品ID，如果请求参数中没有'id'，则默认为0
    id = int(req.get("id", 0))

    # 构建返回列表页面的URL
    reback_url = UrlManager.buildUrl("/goods/index")

    # 如果ID小于1，则重定向到列表页面
    if id < 1:
        return redirect(reback_url)

    # 根据ID查询商品信息
    info = Goods.query.filter_by(id=id).first()

    # 如果商品不存在，则重定向到列表页面
    if not info:
        return redirect(reback_url)

    # 查询商品的库存变更记录，按照ID倒序排列
    stock_change_list = GoodsStockChangeLog.query.filter(GoodsStockChangeLog.goods_id == id) \
        .order_by(GoodsStockChangeLog.id.desc()).all()

    # 查询销售历史数据
    sale_change_list = GoodsSaleChangeLog.query.filter(GoodsSaleChangeLog.goods_id == id) \
        .order_by(GoodsSaleChangeLog.created_time.desc()).all()

    # 获取所有涉及的会员ID
    member_ids = [log.member_id for log in sale_change_list]
    unique_member_ids = list(set(member_ids)) # 去重

    # 查询会员信息，构建 member_id 到 nickname 的映射
    member_mapping = {}
    if unique_member_ids:
        # 假设 User.uid 是会员的 ID，User.nickname 是会员的名称
        members = User.query.filter(User.uid.in_(unique_member_ids)).all()
        member_mapping = {member.uid: member.nickname for member in members}

    # 格式化销售历史数据，以便在模板中使用
    processed_sale_list = []
    for log in sale_change_list:
        processed_sale_list.append({
            'member_name': member_mapping.get(log.member_id, '未知会员'), # 如果找不到会员，则显示“未知会员”
            'quantity': log.quantity,
            'price': log.price,
            'order_status': '已完成' # GoodsSaleChangeLog 模型中没有订单状态，这里假设为“已完成”，你可以根据实际业务逻辑修改
        })
    # --- END 新增：查询销售历史数据 ---

    # 组织返回给前端的数据
    resp_data['info'] = info  # 商品信息
    resp_data['stock_change_list'] = stock_change_list  # 库存变更记录
    resp_data['sale_change_list'] = processed_sale_list  # <--- 新增: 销售历史记录
    resp_data['current'] = 'index'  # 当前页面标识

    # 渲染模板并返回
    return ops_render("goods/info.html", resp_data)


# 商品编辑/添加的路由
@route_goods.route("/set", methods=["GET", "POST"])
def goods_set():
    """
    商品编辑/添加页面
    :return: GET: 渲染后的商品编辑/添加页面; POST: JSON格式的响应
    """
    if request.method == "GET":
        # GET请求，显示编辑/添加页面
        resp_data = {}  # 用于存储返回给前端的数据
        req = request.args  # 获取请求参数

        # 获取商品ID，如果请求参数中没有'id'，则默认为0
        id = int(req.get('id', 0))

        # 根据ID查询商品信息
        info = Goods.query.filter_by(id=id).first()

        # 如果商品存在且状态不为1，则重定向到列表页面
        if info and info.status != 1:
            return redirect(UrlManager.buildUrl("/goods/index"))

        # 获取所有商品分类
        cat_list = GoodsCat.query.all()

        # 组织返回给前端的数据
        resp_data['info'] = info  # 商品信息
        resp_data['cat_list'] = cat_list  # 商品分类列表
        resp_data['current'] = 'index'  # 当前页面标识

        # 渲染模板并返回
        return ops_render("goods/set.html", resp_data)

    # POST请求，处理编辑/添加操作
    resp = {'code': 200, 'msg': '操作成功！', 'data': {}}  # 响应数据

    req = request.values  # 获取请求参数

    # 获取请求参数
    id = int(req['id']) if 'id' in req and req['id'] else 0  # 商品ID
    cat_id = int(req['cat_id']) if 'cat_id' in req else 0  # 分类ID
    name = req['name'] if 'name' in req else ''  # 商品名称
    price = req['price'] if 'price' in req else ''  # 商品价格
    main_image = req['main_image'] if 'main_image' in req else ''  # 封面图片
    summary = req['summary'] if 'summary' in req else ''  # 商品描述
    stock = int(req['stock']) if 'stock' in req else ''  # 库存
    tags = req['tags'] if 'tags' in req else ''  # 标签

    # 将价格转换为Decimal类型，并保留两位小数
    price = Decimal(price).quantize(Decimal('0.00'))

    # 验证参数
    if cat_id < 1:
        resp['code'] = -1
        resp['msg'] = '请选择分类'
        return jsonify(resp)

    if name is None or len(name) < 1:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的名称'
        return jsonify(resp)

    if price <= 0:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的售货价格'
        return jsonify(resp)

    if main_image is None or len(main_image) < 3:
        resp['code'] = -1
        resp['msg'] = '请上传封面图'
        return jsonify(resp)

    if summary is None or len(summary) < 3:
        resp['code'] = -1
        resp['msg'] = '请输入图片描述，不能少于10个字符'
        return jsonify(resp)

    if stock < 1:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的库存量'
        return jsonify(resp)

    if tags is None or len(tags) < 1:
        resp['code'] = -1
        resp['msg'] = '请输入商品，便于搜索'
        return jsonify(resp)

    # 根据ID查询商品信息
    goods_info = Goods.query.filter_by(id=id).first()

    # 记录修改前的库存
    before_stock = 0
    if goods_info:
        # 如果商品存在，则更新商品信息
        model_goods = goods_info
        before_stock = model_goods.stock  # 记录修改前的库存
    else:
        # 如果商品不存在，则创建新的商品对象
        model_goods = Goods()
        model_goods.status = 1  # 默认状态为1
        model_goods.created_time = getCurrentDate()  # 创建时间

    # 更新商品信息
    model_goods.cat_id = cat_id  # 分类ID
    model_goods.name = name  # 商品名称
    model_goods.price = price  # 商品价格
    model_goods.main_image = main_image  # 封面图片
    model_goods.summary = summary  # 商品描述
    model_goods.stock = stock  # 库存
    model_goods.tags = tags  # 标签
    model_goods.updated_time = getCurrentDate()  # 更新时间

    # 添加到数据库会话
    db.session.add(model_goods)

    # 提交数据库更改
    ret = db.session.commit()

    # 记录库存变更日志
    GoodsService.setStockChangeLog(model_goods.id, int(stock) - int(before_stock), "后台修改")

    #  创建库存变更日志对象
    model_stock_change = GoodsStockChangeLog()
    model_stock_change.goods_id = model_goods.id
    model_stock_change.unit = int(stock) - int(before_stock)  # 变更数量
    model_stock_change.total_stock = stock  # 总库存
    model_stock_change.note = ''  # 备注
    model_stock_change.created_time = getCurrentDate()  # 创建时间

    # 添加到数据库会话
    db.session.add(model_stock_change)

    # 提交数据库更改
    db.session.commit()

    # 返回JSON响应
    return jsonify(resp)


# 商品分类列表页面的路由
@route_goods.route("/cat")
def cat():
    """
    商品分类列表页面
    :return: 渲染后的商品分类列表页面
    """
    resp_data = {}  # 用于存储返回给前端的数据
    req = request.values  # 获取请求参数

    # 构建查询对象，默认查询所有商品分类
    query = GoodsCat.query

    # 状态过滤：如果请求参数中有'status'，并且状态值大于-1，则根据状态过滤商品分类
    if 'status' in req and int(req['status']) > -1:
        query = query.filter(GoodsCat.status == int(req['status']))  # 添加过滤条件

    # 查询商品分类列表，按照权重倒序排列，ID倒序排列
    list = query.order_by(GoodsCat.weight.desc(), GoodsCat.id.desc()).all()

    # 组织返回给前端的数据
    resp_data['list'] = list  # 商品分类列表
    resp_data['search_con'] = req  # 搜索条件
    resp_data['status_mapping'] = app.config['STATUS_MAPPING']  # 状态映射，从配置中获取
    resp_data['current'] = 'cat'  # 当前页面标识

    # 渲染模板并返回
    return ops_render("goods/cat.html", resp_data)


# 商品分类编辑/添加页面的路由
@route_goods.route("/cat-set", methods=["GET", "POST"])
def catSet():
    """
    商品分类编辑/添加页面
    :return: GET: 渲染后的商品分类编辑/添加页面; POST: JSON格式的响应
    """
    if request.method == "GET":
        # GET请求，显示编辑/添加页面
        resp_data = {}  # 用于存储返回给前端的数据
        req = request.args  # 获取请求参数

        # 获取商品分类ID，如果请求参数中没有'id'，则默认为0
        id = int(req.get("id", 0))

        # 根据ID查询商品分类信息
        info = None
        if id:
            info = GoodsCat.query.filter_by(id=id).first()

        # 组织返回给前端的数据
        resp_data['info'] = info  # 商品分类信息
        resp_data['current'] = 'cat'  # 当前页面标识

        # 渲染模板并返回
        return ops_render("goods/cat_set.html", resp_data)

    # POST请求，处理编辑/添加操作
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}  # 响应数据
    req = request.values  # 获取请求参数

    # 获取请求参数
    id = req['id'] if 'id' in req else 0  # 商品分类ID
    name = req['name'] if 'name' in req else ''  # 商品分类名称
    weight = int(req['weight']) if ('weight' in req and int(req['weight']) > 0) else 1  # 商品分类权重

    # 验证参数
    if name is None or len(name) < 1:
        resp['code'] = -1
        resp['msg'] = '请输入符合规范的分类名称'
        return jsonify(resp)

    # 根据ID查询商品分类信息
    goods_cat_info = GoodsCat.query.filter_by(id=id).first()
    if goods_cat_info:
        # 如果商品分类存在，则更新商品分类信息
        model_goods_cat = goods_cat_info
    else:
        # 如果商品分类不存在，则创建新的商品分类对象
        model_goods_cat = GoodsCat()
        model_goods_cat.created_time = getCurrentDate()  # 创建时间

    # 更新商品分类信息
    model_goods_cat.name = name  # 商品分类名称
    model_goods_cat.weight = weight  # 商品分类权重
    model_goods_cat.updated_time = getCurrentDate()  # 更新时间

    # 添加到数据库会话
    db.session.add(model_goods_cat)

    # 提交数据库更改
    db.session.commit()

    # 返回JSON响应
    return jsonify(resp)


# 商品分类操作（删除/恢复）的路由
@route_goods.route("/cat-ops", methods=["POST"])
def catOps():
    """
    商品分类操作（删除/恢复）
    :return: JSON格式的响应
    """
    resp = {'code': 200, 'msg': '操作成功!', 'data': {}}  # 响应数据
    req = request.values  # 获取请求参数

    # 获取请求参数
    id = req['id'] if 'id' in req else 0  # 商品分类ID
    act = req['act'] if 'act' in req else ''  # 操作类型（remove/recover）

    # 验证参数
    if not id:
        resp['code'] = -1
        resp['msg'] = "请选择要操作的分类！"
        return jsonify(resp)

    if act not in ['remove', 'recover']:
        resp['code'] = -1
        resp['msg'] = "操作有误，请重试！"
        return jsonify(resp)

    # 根据ID查询商品分类信息
    goods_cat_info = GoodsCat.query.filter_by(id=id).first()
    if not goods_cat_info:
        resp['code'] = -1
        resp['msg'] = "指定分类不存在！"
        return jsonify(resp)

    # 执行操作
    if act == 'remove':
        goods_cat_info.status = 0  # 设置状态为0（删除）
    elif act == 'recover':
        goods_cat_info.status = 1  # 设置状态为1（恢复）

    # 更新更新时间
    goods_cat_info.update_time = getCurrentDate()

    # 添加到数据库会话
    db.session.add(goods_cat_info)

    # 提交数据库更改
    db.session.commit()

    # 返回JSON响应
    return jsonify(resp)


# 商品操作（删除/恢复）的路由
@route_goods.route("/ops", methods=["POST"])
def ops():
    """
    商品操作（删除/恢复）
    :return: JSON格式的响应
    """
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}  # 响应数据
    req = request.values  # 获取请求参数

    # 获取请求参数
    id = req['id'] if 'id' in req else 0  # 商品ID
    act = req['act'] if 'act' in req else ''  # 操作类型（remove/recover）

    # 验证参数
    if not id:
        resp['code'] = -1
        resp['msg'] = "操作有误，请重试"
        return jsonify(resp)

    if act not in ['remove', 'recover']:
        resp['code'] = -1
        resp['msg'] = "操作有误，请重试"
        return jsonify(resp)

    # 根据ID查询商品信息
    goods_info = Goods.query.filter_by(id=id).first()
    if not goods_info:
        resp['code'] = -1
        resp['msg'] = "指定商品不存在"
        return jsonify(resp)

    # 执行操作
    if act == 'remove':
        goods_info.status = 0  # 设置状态为0（删除）
    elif act == 'recover':
        goods_info.status = 1  # 设置状态为1（恢复）

    # 更新更新时间
    goods_info.updated_time = getCurrentDate()

    # 添加到数据库会话
    db.session.add(goods_info)

    # 提交数据库更改
    db.session.commit()

    # 返回JSON响应
    return jsonify(resp)