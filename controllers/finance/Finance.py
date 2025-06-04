# -*- coding: utf-8 -*-
import json  # 导入 json 模块，用于处理 JSON 数据

from flask import Blueprint, request, redirect, jsonify  # 导入 Flask 相关的模块
from sqlalchemy import func  # 导入 SQLAlchemy 的 func 模块，用于执行数据库函数

from application import app, db  # 导入 application 模块中的 app 和 db 对象
from common.libs.Helper import iPagination, selectFilterObj, getDictListFilterField, getDictFilterField, getCurrentDate  # 导入自定义的 Helper 函数
from common.libs.Helper import ops_render  # 导入自定义的渲染函数
from common.libs.UrlManager import UrlManager  # 导入自定义的 UrlManager 类
from common.models.goods.Goods import Goods  # 导入 Goods 模型类
from common.models.member.Member import Member  # 导入 Member 模型类
from common.models.pay.PayOrder import PayOrder  # 导入 PayOrder 模型类
from common.models.pay.PayOrderItem import PayOrderItem  # 导入 PayOrderItem 模型类

route_finance = Blueprint('finance_page', __name__)  # 创建一个名为 finance_page 的蓝图

# 财务首页
@route_finance.route("/index")
def index():
    """
    财务首页视图函数
    """
    resp_data = {}  # 初始化返回数据字典
    req = request.values  # 获取请求参数
    page = int(req['p']) if ('p' in req and req['p']) else 1  # 获取当前页码，如果没有则默认为 1

    query = PayOrder.query  # 创建 PayOrder 查询对象

    if 'status' in req and int(req['status']) >= -8:  # 如果请求参数中包含 status 且值大于等于 -8
        query = query.filter(PayOrder.status == int(req['status']))  # 根据状态过滤查询结果

    # 分页参数
    page_params = {
        'total': query.count(),  # 总记录数
        'page_size': app.config['PAGE_SIZE'],  # 每页显示数量
        'page': page,  # 当前页码
        'display': app.config['PAGE_DISPLAY'],  # 显示的页码数量
        'url': request.full_path.replace("&p={}".format(page), "")  # URL，用于生成分页链接
    }

    pages = iPagination(page_params)  # 创建分页对象
    offset = (page - 1) * app.config['PAGE_SIZE']  # 计算偏移量
    pay_list = query.order_by(PayOrder.id.desc()).offset(offset).limit(app.config['PAGE_SIZE']).all()  # 查询当前页的支付订单数据
    data_list = []  # 初始化数据列表
    if pay_list:  # 如果有支付订单数据
        pay_order_ids = selectFilterObj(pay_list, "id")  # 获取支付订单 ID 列表
        pay_order_items_map = getDictListFilterField(PayOrderItem, PayOrderItem.pay_order_id, "pay_order_id",
                                                     pay_order_ids)  # 获取支付订单项的字典，以 pay_order_id 为键

        goods_mapping = {}  # 初始化商品字典
        if pay_order_items_map:  # 如果有支付订单项数据
            goods_ids = []  # 初始化商品 ID 列表
            for item in pay_order_items_map:  # 遍历支付订单项字典
                tmp_goods_ids = selectFilterObj(pay_order_items_map[item], "goods_id")  # 获取当前支付订单项中的商品 ID 列表
                tmp_goods_ids = {}.fromkeys(tmp_goods_ids).keys()  # 去重商品 ID 列表
                goods_ids = goods_ids + list(tmp_goods_ids)  # 将商品 ID 添加到总的商品 ID 列表中

            # goods_ids里面会有重复的，要去重
            goods_mapping = getDictFilterField(Goods, Goods.id, "id", goods_ids)  # 获取商品的字典，以商品 ID 为键

        for item in pay_list:  # 遍历支付订单数据
            tmp_data = {
                "id": item.id,  # 订单 ID
                "status_desc": item.status_desc,  # 订单状态描述
                "order_number": item.order_number,  # 订单号
                "price": item.total_price,  # 订单总价
                "pay_time": item.pay_time,  # 支付时间
                "created_time": item.created_time.strftime("%Y%m%d%H%M%S")  # 创建时间，格式化为字符串
            }
            tmp_goodss = []  # 初始化商品列表
            tmp_order_items = pay_order_items_map[item.id]  # 获取当前订单的订单项列表
            for tmp_order_item in tmp_order_items:  # 遍历订单项列表
                tmp_goods_info = goods_mapping[tmp_order_item.goods_id]  # 获取商品信息
                tmp_goodss.append({
                    'name': tmp_goods_info.name,  # 商品名称
                    'quantity': tmp_order_item.quantity  # 商品数量
                })

            tmp_data['goodss'] = tmp_goodss  # 将商品列表添加到订单数据中
            data_list.append(tmp_data)  # 将订单数据添加到数据列表中

    resp_data['list'] = data_list  # 将数据列表添加到返回数据中
    resp_data['pages'] = pages  # 将分页对象添加到返回数据中
    resp_data['search_con'] = req  # 将搜索条件添加到返回数据中
    resp_data['pay_status_mapping'] = app.config['PAY_STATUS_MAPPING']  # 将支付状态映射添加到返回数据中
    resp_data['current'] = 'index'  # 设置当前页面标识

    return ops_render("finance/index.html", resp_data)  # 渲染模板并返回

# 支付信息详情
@route_finance.route("/pay-info")
def info():
    """
    支付信息详情视图函数
    """
    resp_data = {}  # 初始化返回数据字典
    req = request.values  # 获取请求参数
    id = int(req['id']) if 'id' in req else 0  # 获取订单 ID，如果没有则默认为 0

    reback_url = UrlManager.buildUrl("/finance/index")  # 构建返回 URL

    if id < 1:  # 如果订单 ID 小于 1
        return redirect(reback_url)  # 重定向到返回 URL

    pay_order_info = PayOrder.query.filter_by(id=id).first()  # 查询支付订单信息
    if not pay_order_info:  # 如果没有支付订单信息
        return redirect(reback_url)  # 重定向到返回 URL

    member_info = Member.query.filter_by(id=pay_order_info.member_id).first()  # 查询会员信息
    if not member_info:  # 如果没有会员信息
        return redirect(reback_url)  # 重定向到返回 URL

    order_item_list = PayOrderItem.query.filter_by(pay_order_id=pay_order_info.id).all()  # 查询订单项列表
    data_order_item_list = []  # 初始化订单项数据列表
    if order_item_list:  # 如果有订单项数据
        goods_map = getDictFilterField(Goods, Goods.id, "id", selectFilterObj(order_item_list, "goods_id"))  # 获取商品字典，以商品 ID 为键
        for item in order_item_list:  # 遍历订单项列表
            tmp_goods_info = goods_map[item.goods_id]  # 获取商品信息
            tmp_data = {
                "quantity": item.quantity,  # 商品数量
                "price": item.price,  # 商品价格
                "name": tmp_goods_info.name  # 商品名称
            }
            data_order_item_list.append(tmp_data)  # 将订单项数据添加到订单项数据列表中

    address_info = {}  # 初始化地址信息字典
    if pay_order_info.express_info:  # 如果有快递信息
        address_info = json.loads(pay_order_info.express_info)  # 将快递信息解析为 JSON 对象

    resp_data['pay_order_info'] = pay_order_info  # 将支付订单信息添加到返回数据中
    resp_data['pay_order_items'] = data_order_item_list  # 将订单项数据列表添加到返回数据中
    resp_data['member_info'] = member_info  # 将会员信息添加到返回数据中
    resp_data['address_info'] = address_info  # 将地址信息添加到返回数据中
    resp_data['current'] = 'index'  # 设置当前页面标识
    return ops_render("finance/pay_info.html", resp_data)  # 渲染模板并返回

# 财务统计
@route_finance.route("/account")
def account():
    """
    财务统计视图函数
    """
    resp_data = {}  # 初始化返回数据字典
    req = request.values  # 获取请求参数
    page = int(req['p']) if ('p' in req and req['p']) else 1  # 获取当前页码，如果没有则默认为 1
    query = PayOrder.query.filter_by(status=1)  # 创建 PayOrder 查询对象，过滤状态为 1 的订单

    # 分页参数
    page_params = {
        'total': query.count(),  # 总记录数
        'page_size': app.config['PAGE_SIZE'],  # 每页显示数量
        'page': page,  # 当前页码
        'display': app.config['PAGE_DISPLAY'],  # 显示的页码数量
        'url': request.full_path.replace("&p={}".format(page), "")  # URL，用于生成分页链接
    }

    pages = iPagination(page_params)  # 创建分页对象
    offset = (page - 1) * app.config['PAGE_SIZE']  # 计算偏移量
    list = query.order_by(PayOrder.id.desc()).offset(offset).limit(app.config['PAGE_SIZE']).all()  # 查询当前页的支付订单数据

    # 使用 db.session.query 查询统计信息
    stat_info = db.session.query(func.sum(PayOrder.total_price).label("total")) \
        .filter(PayOrder.status == 1).first()

    total_money = stat_info[0] if stat_info and stat_info[0] else 0.00  # 获取总金额，如果没有则默认为 0.00

    app.logger.info(stat_info)  # 记录统计信息

    resp_data['list'] = list  # 将数据列表添加到返回数据中
    resp_data['pages'] = pages  # 将分页对象添加到返回数据中
    resp_data['total_money'] = total_money  # 将总金额添加到返回数据中
    resp_data['current'] = 'account'  # 设置当前页面标识
    return ops_render("finance/account.html", resp_data)  # 渲染模板并返回

# 订单操作
@route_finance.route("/ops", methods=["POST"])
def orderOps():
    """
    订单操作视图函数
    """
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}  # 初始化返回数据字典
    req = request.values  # 获取请求参数
    id = req['id'] if 'id' in req else 0  # 获取订单 ID，如果没有则默认为 0
    act = req['act'] if 'act' in req else ''  # 获取操作类型，如果没有则默认为空
    pay_order_info = PayOrder.query.filter_by(id=id).first()  # 查询支付订单信息
    if not pay_order_info:  # 如果没有支付订单信息
        resp['code'] = -1  # 设置错误码
        resp['msg'] = "系统繁忙。请稍后再试~~"  # 设置错误信息
        return jsonify(resp)  # 返回 JSON 数据

    if act == "express":  # 如果操作类型为 express
        pay_order_info.express_status = -6  # 设置快递状态为 -6
        pay_order_info.updated_time = getCurrentDate()  # 更新更新时间
        db.session.add(pay_order_info)  # 添加到数据库会话
        db.session.commit()  # 提交数据库会话

    return jsonify(resp)  # 返回 JSON 数据