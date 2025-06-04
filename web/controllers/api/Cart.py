# -*- coding: utf-8 -*-
import json  # 导入json模块，用于处理JSON数据

from flask import jsonify, request, g  # 导入flask的jsonify, request, g模块

from common.libs.Helper import getDictFilterField, selectFilterObj  # 导入自定义的Helper模块中的函数
from common.libs.UrlManager import UrlManager  # 导入自定义的UrlManager模块
from common.libs.member.CartService import CartService  # 导入自定义的CartService模块
from common.models.goods.Goods import Goods  # 导入Goods模型
from common.models.member.MemberCart import MemberCart  # 导入MemberCart模型
from web.controllers.api import route_api  # 导入api蓝图

# 定义购物车列表接口
@route_api.route('/cart/index')
def cartIndex():
    """
    获取购物车列表
    :return: JSON格式的响应
    """
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}  # 初始化响应数据
    member_info = g.member_info  # 从全局变量g中获取用户信息，g通常用于存储请求上下文相关的数据
    if not member_info:  # 如果用户未登录
        resp['code'] = -1  # 设置错误码
        resp['msg'] = "获取失敗，未登陸"  # 设置错误信息
        return jsonify(resp)  # 返回JSON响应

    # 查询当前用户的购物车列表
    cart_list = MemberCart.query.filter_by(member_id=member_info.id).all()  # 根据用户ID查询购物车记录
    data_cart_list = []  # 初始化用于存储格式化后的购物车数据的列表
    if cart_list:  # 如果购物车列表不为空
        goods_ids = selectFilterObj(cart_list, "goods_id")  # 提取购物车列表中所有商品的ID
        goods_map = getDictFilterField(Goods, Goods.id, "id", goods_ids)  # 根据商品ID查询商品信息，并以字典形式存储，方便后续查找
        for item in cart_list:  # 遍历购物车列表
            tmp_goods_info = goods_map[item.goods_id]  # 根据商品ID从商品信息字典中获取商品信息
            tmp_data = {  # 格式化购物车数据
                'id': item.id,  # 购物车条目ID
                'goods_id': item.goods_id,  # 商品ID
                'number': item.quantity,  # 商品数量
                'name': tmp_goods_info.name,  # 商品名称
                'price': str(tmp_goods_info.price),  # 商品价格，转换为字符串
                'pic_url': UrlManager.buildImageUrl(tmp_goods_info.main_image),  # 商品图片URL
                'active': True  # 是否选中，默认为True
            }
            data_cart_list.append(tmp_data)  # 将格式化后的购物车数据添加到列表中

    resp['data']['list'] = data_cart_list  # 将购物车数据添加到响应数据中
    return jsonify(resp)  # 返回JSON响应


# 定义添加/修改购物车接口
@route_api.route("/cart/set", methods=["POST"])
def setCart():
    """
    添加或修改购物车商品
    :return: JSON格式的响应
    """
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}  # 初始化响应数据
    req = request.values  # 获取POST请求的参数
    goods_id = int(req['id']) if 'id' in req else 0  # 获取商品ID，如果不存在则默认为0
    number = int(req['number']) if 'number' in req else 0  # 获取商品数量，如果不存在则默认为0

    if goods_id < 1 or number < 1:  # 如果商品ID或商品数量小于1
        resp['code'] = -1  # 设置错误码
        resp['msg'] = "添加购物车失败-1"  # 设置错误信息
        return jsonify(resp)  # 返回JSON响应

    member_info = g.member_info  # 从全局变量g中获取用户信息
    if not member_info:  # 如果用户未登录
        resp['code'] = -1  # 设置错误码
        resp['msg'] = "添加购物车失败-2"  # 设置错误信息
        return jsonify(resp)  # 返回JSON响应

    goods_info = Goods.query.filter_by(id=goods_id).first()  # 根据商品ID查询商品信息
    if not goods_info:  # 如果商品不存在
        resp['code'] = -1  # 设置错误码
        resp['msg'] = "添加购物车失败-3"  # 设置错误信息
        return jsonify(resp)  # 返回JSON响应

    if goods_info.stock < number:  # 如果商品库存不足
        resp['code'] = -1  # 设置错误码
        resp['msg'] = "添加购物车失败,库存不足"  # 设置错误信息
        return jsonify(resp)  # 返回JSON响应

    # 调用CartService来添加或修改购物车商品
    ret = CartService.setItems(member_id=member_info.id, goods_id=goods_id, number=number)  # 调用CartService的setItems方法
    if not ret:  # 如果添加或修改失败
        resp['code'] = -1  # 设置错误码
        resp['msg'] = "添加购物车失败-4"  # 设置错误信息
        return jsonify(resp)  # 返回JSON响应

    return jsonify(resp)  # 返回JSON响应


# 定义删除购物车接口
@route_api.route("/cart/del", methods=["POST"])
def delCart():
    """
    删除购物车商品
    :return: JSON格式的响应
    """
    resp = {'code': 200, 'msg': '操作成功', 'data': {}}  # 初始化响应数据
    req = request.values  # 获取POST请求的参数
    params_goods = req['goods'] if 'goods' in req else None  # 获取要删除的商品ID列表

    items = []  # 初始化商品ID列表
    if params_goods:  # 如果存在商品ID列表
        items = json.loads(params_goods)  # 将JSON字符串转换为Python列表
    if not items or len(items) < 1:  # 如果商品ID列表为空
        return jsonify(resp)  # 返回JSON响应

    member_info = g.member_info  # 从全局变量g中获取用户信息
    if not member_info:  # 如果用户未登录
        resp['code'] = -1  # 设置错误码
        resp['msg'] = "删除购物车失败-1~~"  # 设置错误信息
        return jsonify(resp)  # 返回JSON响应

    # 调用CartService来删除购物车商品
    ret = CartService.deleteItem(member_id=member_info.id, items=items)  # 调用CartService的deleteItem方法
    if not ret:  # 如果删除失败
        resp['code'] = -1  # 设置错误码
        resp['msg'] = "删除购物车失败-2~~"  # 设置错误信息
        return jsonify(resp)  # 返回JSON响应

    return jsonify(resp)  # 返回JSON响应