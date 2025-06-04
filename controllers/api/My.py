# -*- coding: utf-8 -*-
from flask import g, jsonify, request

from common.libs.Helper import selectFilterObj, getDictFilterField
from common.libs.UrlManager import UrlManager
from common.models.goods.Goods import Goods
from common.models.member.MemberComments import MemberComments
from common.models.pay.PayOrder import PayOrder
from common.models.pay.PayOrderItem import PayOrderItem
from web.controllers.api import route_api


@route_api.route("/my/order")
def myOrderLlist():
    """
    获取我的订单列表API接口
    :return: JSON格式的响应，包含订单列表信息
    """
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    member_info = g.member_info  # 从全局变量g中获取会员信息，g是由Flask提供的上下文变量，用于在请求处理过程中传递数据

    req = request.values  # 从请求中获取参数，request.values包含GET和POST请求的参数

    status = int(req['status']) if 'status' in req else 0  # 获取订单状态，如果请求中包含status参数则使用，否则默认为0

    query = PayOrder.query.filter_by(member_id=member_info.id)  # 查询当前会员的订单，PayOrder是订单模型

    # 根据不同的订单状态进行筛选
    if status == -8:  # 等待付款
        query = query.filter(PayOrder.status == -8)
    elif status == -7:  # 代发货
        query = query.filter(PayOrder.status == 1, PayOrder.express_status == -7, PayOrder.comment_status == 0)
    elif status == -6:  # 待确认
        query = query.filter(PayOrder.status == 1, PayOrder.express_status == -6, PayOrder.comment_status == 0)
    elif status == -5:  # 待评价
        query = query.filter(PayOrder.status == 1, PayOrder.express_status == 1, PayOrder.comment_status == 0)
    elif status == -1:  # 已完成
        query = query.filter(PayOrder.status == 1, PayOrder.express_status == -1, PayOrder.comment_status == 1)
    else:  # 全部订单
        query = query.filter(PayOrder.status == 0)

    pay_order_list = query.order_by(PayOrder.id.desc()).all()  # 查询符合条件的订单列表，并按照订单ID降序排列
    data_pay_order_list = []  # 用于存储格式化后的订单数据

    if pay_order_list:
        pay_order_ids = selectFilterObj(pay_order_list, 'id')  # 提取订单列表中的订单ID
        pay_order_item_list = PayOrderItem.query.filter(PayOrderItem.pay_order_id.in_(pay_order_ids)).all()  # 查询订单中的商品信息，PayOrderItem是订单商品模型
        goods_ids = selectFilterObj(pay_order_item_list, "goods_id")  # 提取订单商品列表中的商品ID
        goods_map = getDictFilterField(Goods, Goods.id, "id", goods_ids)  # 根据商品ID查询商品信息，Goods是商品模型
        pay_order_item_map = {}  # 用于存储订单商品信息，key为订单ID，value为商品列表
        if pay_order_item_list:
            for item in pay_order_item_list:
                if item.pay_order_id not in pay_order_item_map:
                    pay_order_item_map[item.pay_order_id] = []

                tmp_goods_info = goods_map[item.goods_id]  # 获取商品信息
                pay_order_item_map[item.pay_order_id].append({  # 将商品信息添加到订单商品列表中
                    "id": item.id,
                    "goods_id": item.goods_id,
                    "quantity": item.quantity,
                    "price": str(item.price),
                    "pic_url": UrlManager.buildImageUrl(tmp_goods_info.main_image),  # 构建商品图片URL
                    "name": tmp_goods_info.name
                })
        for item in pay_order_list:  # 遍历订单列表
            tmp_data = {  # 格式化订单数据
                "status": item.pay_status,
                "status_desc": item.status_desc,
                "date": item.created_time.strftime("%Y-%m-%d %H:%M:%S"),  # 格式化订单创建时间
                "order_number": item.order_number,
                "order_sn": item.order_sn,
                "note": item.note,
                "total_price": str(item.total_price),
                "goods_list": pay_order_item_map[item.id]  # 获取订单中的商品列表
            }
            data_pay_order_list.append(tmp_data)  # 将格式化后的订单数据添加到订单列表中
    resp['data']['pay_order_list'] = data_pay_order_list  # 将订单列表添加到响应数据中

    return jsonify(resp)  # 返回JSON格式的响应


# @route_api.route("/my/order/info")
# def myOrderInfo():
# 	resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
# 	member_info = g.member_info
# 	req = request.values
# 	order_sn = req['order_sn'] if 'order_sn' in req else ''
# 	pay_order_info = PayOrder.query.filter_by( member_id=member_info.id ,order_sn = order_sn).first()
# 	if not pay_order_info:
# 		resp['code'] = -1
# 		resp['msg'] = "系统繁忙，请稍后再试~~"
# 		return jsonify(resp)
#
# 	express_info = {}
# 	if pay_order_info.express_info:
# 		express_info = json.loads( pay_order_info.express_info )
#
# 	tmp_deadline = pay_order_info.created_time + datetime.timedelta(minutes=30)
# 	info = {
# 		"order_sn":pay_order_info.order_sn,
# 		"status":pay_order_info.pay_status,
# 		"status_desc":pay_order_info.status_desc,
# 		"pay_price":str( pay_order_info.pay_price),
# 		"yun_price":str( pay_order_info.yun_price),
# 		"total_price":str( pay_order_info.total_price),
# 		"address":express_info,
# 		"goods": [],
# 		"deadline":tmp_deadline.strftime("%Y-%m-%d %H:%M")
# 	}
#
# 	pay_order_items = PayOrderItem.query.filter_by( pay_order_id = pay_order_info.id  ).all()
# 	if pay_order_items:
# 		goods_ids = selectFilterObj( pay_order_items , "goods_id")
# 		goods_map = getDictFilterField(Goods, Goods.id, "id", goods_ids)
# 		for item in pay_order_items:
# 			tmp_goods_info = goods_map[item.goods_id]
# 			tmp_data = {
# 				"name": tmp_goods_info.name,
# 				"price": str( item.price ),
# 				"unit": item.quantity,
# 				"pic_url": UrlManager.buildImageUrl( tmp_goods_info.main_image ),
# 			}
# 			info['goods'].append( tmp_data )
# 	resp['data']['info'] = info
# 	return jsonify(resp)
#
#
# @route_api.route("/my/comment/add",methods = [ "POST" ])
# def myCommentAdd():
# 	resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
# 	member_info = g.member_info
# 	req = request.values
# 	order_sn = req['order_sn'] if 'order_sn' in req else ''
# 	score = req['score'] if 'score' in req else 10
# 	content = req['content'] if 'content' in req else ''
#
# 	pay_order_info = PayOrder.query.filter_by( member_id=member_info.id ,order_sn = order_sn).first()
# 	if not pay_order_info:
# 		resp['code'] = -1
# 		resp['msg'] = "系统繁忙，请稍后再试~~"
# 		return jsonify(resp)
#
# 	if pay_order_info.comment_status:
# 		resp['code'] = -1
# 		resp['msg'] = "已经评价过了~~"
# 		return jsonify(resp)
#
# 	pay_order_items = PayOrderItem.query.filter_by( pay_order_id = pay_order_info.id ).all()
# 	goods_ids = selectFilterObj( pay_order_items,"goods_id" )
# 	tmp_goods_ids_str = '_'.join(str(s) for s in goods_ids if s not in [None])
# 	model_comment = MemberComments()
# 	model_comment.goods_ids = "_%s_"%tmp_goods_ids_str
# 	model_comment.member_id = member_info.id
# 	model_comment.pay_order_id = pay_order_info.id
# 	model_comment.score = score
# 	model_comment.content = content
# 	db.session.add( model_comment )
#
# 	pay_order_info.comment_status = 1
# 	pay_order_info.updated_time = getCurrentDate()
# 	db.session.add( pay_order_info )
#
# 	db.session.commit()
# 	return jsonify(resp)

@route_api.route("/my/comment/list")
def myCommentList():
    """
    获取我的评论列表API接口
    :return: JSON格式的响应，包含评论列表信息
    """
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    member_info = g.member_info  # 从全局变量g中获取会员信息
    comment_list = MemberComments.query.filter_by(member_id=member_info.id) \
        .order_by(MemberComments.id.desc()).all()  # 查询当前会员的评论列表，MemberComments是评论模型，并按照评论ID降序排列
    data_comment_list = []  # 用于存储格式化后的评论数据
    if comment_list:
        pay_order_ids = selectFilterObj(comment_list, "pay_order_id")  # 提取评论列表中的订单ID
        pay_order_map = getDictFilterField(PayOrder, PayOrder.id, "id", pay_order_ids)  # 根据订单ID查询订单信息，PayOrder是订单模型
        for item in comment_list:  # 遍历评论列表
            tmp_pay_order_info = pay_order_map[item.pay_order_id]  # 获取订单信息
            tmp_data = {  # 格式化评论数据
                "date": item.created_time.strftime("%Y-%m-%d %H:%M:%S"),  # 格式化评论创建时间
                "content": item.content,
                "order_number": tmp_pay_order_info.order_number  # 获取订单编号
            }
            data_comment_list.append(tmp_data)  # 将格式化后的评论数据添加到评论列表中
    resp['data']['list'] = data_comment_list  # 将评论列表添加到响应数据中
    return jsonify(resp)  # 返回JSON格式的响应
