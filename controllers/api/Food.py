# -*- coding: utf-8 -*-
# 这个文件是处理食物相关API请求的模块
# 主要包含食物列表、搜索、详情等接口

# 导入 Flask 框架中的 request（处理请求数据）、jsonify（返回 JSON 响应）、g（全局上下文，用于存储请求相关数据，如用户信息）
from flask import request, jsonify, g
# 导入 SQLAlchemy 的 or_ 函数，用于构建 SQL 中的 OR 条件
from sqlalchemy import or_

# 从 application 模块导入 db 对象，这是 SQLAlchemy 数据库实例
from application import db
# 从 common.libs.Helper 模块导入 getCurrentDate 函数（尽管在此文件未使用）
from common.libs.Helper import getCurrentDate
# 从 common.libs.UrlManager 模块导入 UrlManager 类，用于生成图片等资源的 URL
from common.libs.UrlManager import UrlManager
# 导入购物车模型
from common.models.member.MemberCart import MemberCart
# 从 web.controllers.api 模块导入 route_api Blueprint，用于注册API路由
from web.controllers.api import route_api
# 导入食物分类模型
from common.models.food.FoodCat import FoodCat
# 导入食物（商品）模型
from common.models.food.Food import Food


@route_api.route("/food/index")  # 定义一个API路由，路径为 /food/index，注册到 route_api Blueprint
def foodIndex():
    """
    食物首页接口
    主要用于获取食物分类列表和首页推荐食物（Banner）列表
    """
    # 初始化响应字典，设置默认成功状态（code: 200），消息（msg: "操作成功"），和空数据字典（data）
    resp = {'code': 200, 'msg': "操作成功", 'data': {}}

    # --- 获取食物分类列表 ---
    # 查询 FoodCat 表中 status 为 1（正常状态）的记录
    # 按 weight 字段倒序排序
    # 获取所有符合条件的记录
    cat_list = FoodCat.query.filter_by(status=1).order_by(FoodCat.weight.desc()).all()
    # 初始化用于存放处理后分类数据的列表
    # 默认添加一个“全部”分类，其ID为0
    data_cat_list = [{
        'id': 0,  # “全部”分类的ID为0
        'name': "全部"  # “全部”分类的名称
    }]
    # 如果查询到了分类列表 (cat_list 不为空)
    if cat_list:
        # 遍历查询结果中的每一个分类项
        for item in cat_list:
            # 构建单个分类的字典数据
            tmp_data = {
                "id": item.id,  # 分类ID
                "name": item.name  # 分类名称
            }
            # 将构建好的分类数据字典添加到结果列表中
            data_cat_list.append(tmp_data)
    # 将处理后的分类列表添加到响应数据的 'cat_list' 字段中
    resp['data']['cat_list'] = data_cat_list

    # --- 获取首页推荐食物列表（Banner） ---
    # 查询 Food 表中 status 为 1（正常状态）的记录
    # 按 total_count（总销量）字段倒序排序
    # 再按 id 字段倒序排序（作为次要排序条件）
    # 限制最多获取 3 条记录
    # 获取所有符合条件的记录列表
    food_list = Food.query.filter_by(status=1) \
        .order_by(Food.total_count.desc(), Food.id.desc()).limit(3).all()
    # 初始化用于存放处理后食物数据的列表
    data_food_list = []
    # 如果查询到了食物列表 (food_list 不为空)
    if food_list:
        # 遍历查询结果中的每一个食物项
        for item in food_list:
            # 构建单个食物的字典数据
            tmp_data = {
                "id": item.id,  # 食物ID
                # 使用 UrlManager 构建食物主图的完整URL
                "pic_url": UrlManager.buildImageUrl(item.main_image)
            }
            # 将构建好的食物数据字典添加到结果列表中
            data_food_list.append(tmp_data)
    # 将处理后的食物列表添加到响应数据的 'banner_list' 字段中
    resp['data']['banner_list'] = data_food_list
    # 将构建好的响应字典转换为 JSON 格式并返回
    return jsonify(resp)


@route_api.route("/food/search")  # 定义食物搜索接口路由
def foodSearch():
    """
    食物搜索接口
    支持按分类ID（cat_id）、关键词（mix_kw）搜索，支持分页（p）
    """
    # 初始化响应字典
    resp = {'code': 200, 'msg': "操作成功", 'data': {}}
    # 获取请求参数，request.values 会合并 GET 和 POST 参数
    req = request.values
    # 从请求参数中获取 cat_id，如果不存在则默认为0，并转换为整数
    cat_id = int(req['cat_id']) if 'cat_id' in req else 0
    # 从请求参数中获取 mix_kw，如果不存在则默认为空字符串
    mix_kw = str(req['mix_kw']) if 'mix_kw' in req else ''
    # 从请求参数中获取页码 p，如果不存在则默认为1，并转换为整数
    p = int(req['p']) if 'p' in req else 1
    # 确保页码 p 不小于 1
    if p < 1:
        p = 1

    # 初始化数据库查询对象，首先过滤出 status 为 1 的食物
    query = Food.query.filter_by(status=1)

    page_size = 10  # 定义每页的食物数量
    offset = (p - 1) * page_size  # 计算查询的偏移量（从第几条记录开始取）

    # 如果 cat_id 大于 0，则根据分类ID进一步过滤查询结果
    if cat_id > 0:
        query = query.filter(Food.cat_id == cat_id)

    # 如果存在搜索关键词 mix_kw
    if mix_kw:
        # 构建搜索规则：使用 SQLAlchemy 的 or_ 函数构建 OR 条件
        # Food.name.ilike("%{0}%".format(mix_kw)) 表示食物名称 name 包含关键词 mix_kw（不区分大小写）
        # Food.tags.ilike("%{0}%".format(mix_kw)) 表示食物标签 tags 包含关键词 mix_kw（不区分大小写）
        rule = or_(Food.name.ilike("%{0}%".format(mix_kw)), Food.tags.ilike("%{0}%".format(mix_kw)))
        # 将搜索规则添加到查询中
        query = query.filter(rule)

    # 执行查询：
    # 按 total_count 倒序排序
    # 再按 id 倒序排序
    # 应用计算出的偏移量 offset
    # 限制查询结果的数量为 page_size
    # 获取所有符合条件的记录列表
    food_list = query.order_by(Food.total_count.desc(), Food.id.desc()).offset(offset).limit(page_size).all()
    # 初始化用于存放处理后食物数据的列表
    data_food_list = []
    # 如果查询到了食物列表
    if food_list:
        # 遍历查询结果
        for item in food_list:
            # 构建单个食物的字典数据
            tmp_data = {
                'id': item.id,  # 食物ID
                'name': item.name,  # 食物名称
                'price': str(item.price),  # 食物价格（转换为字符串）
                'mix_price': str(item.price),  # 混合价格（这里和价格一样，转换为字符串，可能用于前端显示或兼容旧接口）
                # 使用 UrlManager 构建食物主图的完整URL
                'pic_url': UrlManager.buildImageUrl(item.main_image)
            }
            # 将构建好的食物数据字典添加到结果列表中
            data_food_list.append(tmp_data)

    # 将处理后的食物列表添加到响应数据的 'list' 字段中
    resp['data']['list'] = data_food_list
    # 判断是否还有更多数据：
    # 如果当前页获取到的食物数量小于每页数量 page_size，说明这是最后一页或结果不足一页，则 has_more 为 0
    # 否则，说明可能还有下一页数据，则 has_more 为 1
    resp['data']['has_more'] = 0 if len(data_food_list) < page_size else 1
    # 将构建好的响应字典转换为 JSON 格式并返回
    return jsonify(resp)


@route_api.route("/food/info")  # 定义食物详情接口路由
def foodInfo():
    """
    食物详情接口
    根据食物ID（id）获取详细信息，并获取当前用户的购物车商品总数
    """
    # 初始化响应字典
    resp = {'code': 200, 'msg': "操作成功", 'data': {}}
    # 获取请求参数
    req = request.values
    # 从请求参数中获取食物ID id，如果不存在则默认为0，并转换为整数
    id = int(req['id']) if 'id' in req else 0

    # 根据食物ID查询 Food 表中的记录
    # .first() 获取第一条匹配的记录或 None
    food_info = Food.query.filter_by(id=id).first()
    # 检查查询结果：如果 food_info 不存在（找不到该ID的食物）或者 food_info 的 status 不为 1（食物已下架）
    if not food_info or not food_info.status:
        # 设置错误码为 -1 和错误消息为 "商品已下架~"
        resp['code'] = -1
        resp['msg'] = "商品已下架~"
        # 返回错误响应
        return jsonify(resp)

    # 从 Flask 全局上下文 g 中获取当前登录会员的信息
    # member_info 通常是在登录验证的 before_request 钩子中设置的
    member_info = g.member_info
    cart_number = 0  # 初始化购物车商品总数为0
    # 如果会员信息存在（即用户已登录）
    if member_info:
        # 查询 MemberCart 表，过滤出当前会员（member_id 等于 member_info.id）的购物车记录
        # .count() 计算符合条件的记录数量
        cart_number = MemberCart.query.filter_by(member_id=member_info.id).count()

    # 构建食物详情数据字典
    resp['data']['info'] = {
        'id': food_info.id,  # 食物ID
        'name': food_info.name,  # 食物名称
        'summary': food_info.summary,  # 食物摘要/描述
        'comment_count': food_info.comment_count,  # 评论数量
        # 使用 UrlManager 构建主图的完整URL
        'main_image': UrlManager.buildImageUrl(food_info.main_image),
        'price': str(food_info.price),  # 价格（转换为字符串）
        'stock': food_info.stock,  # 库存
        # 图片列表，这里只包含了主图，可能用于详情页轮播等
        'pics': [UrlManager.buildImageUrl(food_info.main_image)]
    }
    # 将购物车商品总数添加到响应数据的 'cart_number' 字段中
    resp['data']['cart_number'] = cart_number
    # 将构建好的响应字典转换为 JSON 格式并返回
    return jsonify(resp)