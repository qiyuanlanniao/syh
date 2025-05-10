# -*- coding: utf-8 -*-
import decimal
import json

from flask import request, g, jsonify

from application import app, db
from common.libs.Helper import getCurrentDate
from common.libs.UrlManager import UrlManager
from common.libs.member.CartService import CartService
from common.libs.pay.PayService import PayService
from common.libs.pay.WeChatService import WeChatService
from common.models.food.Food import Food
from common.models.member.MemberAddress import MemberAddress
from common.models.member.OauthMemberBind import OauthMemberBind
from common.models.pay.PayOrder import PayOrder
from common.models.pay.PayOrderItem import PayOrderItem
from web.controllers.api import route_api


@route_api.route("/order/info", methods=["POST"])
def orderInfo():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    params_goods = req['goods'] if 'goods' in req else None
    member_info = g.member_info
    params_goods_list = []
    if params_goods:
        params_goods_list = json.loads(params_goods)

    food_dic = {}
    for item in params_goods_list:
        food_dic[item['id']] = item['number']

    food_ids = food_dic.keys()
    food_list = Food.query.filter(Food.id.in_(food_ids)).all()
    data_food_list = []
    yun_price = pay_price = decimal.Decimal(0.00)
    if food_list:
        for item in food_list:
            tmp_data = {
                'id': item.id,
                'name': item.name,
                'price': str(item.price),
                'pic_url': UrlManager.buildImageUrl(item.main_image),
                'number': food_dic[item.id]
            }
            pay_price = pay_price + item.price * int(food_dic[item.id])
            data_food_list.append(tmp_data)

    # 获取地址
    address_info = MemberAddress.query.filter_by(is_default=1, member_id=member_info.id, status=1).first()
    default_address = ''
    if address_info:
        default_address = {
            "id": address_info.id,
            "name": address_info.nickname,
            "mobile": address_info.mobile,
            "address": "%s%s%s%s" % (
                address_info.province_str, address_info.city_str, address_info.area_str, address_info.address)
        }
    resp['data']['food_list'] = data_food_list
    resp['data']['pay_price'] = str(pay_price)
    resp['data']['yun_price'] = str(yun_price)
    resp['data']['total_price'] = str(pay_price + yun_price)
    resp['data']['default_address'] = default_address
    return jsonify(resp)


@route_api.route("/my/order/info", methods=["POST"])
def myOrderInfo():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    member_info = g.member_info

    if not member_info:
         resp['code'] = -1
         resp['msg'] = '请先登录！'
         return jsonify(resp)

    order_sn = req.get('order_sn')

    if not order_sn:
        resp['code'] = -1
        resp['msg'] = '缺少订单号参数'
        return jsonify(resp)

    # 根据 order_sn 和用户ID查询订单 (注意 PayOrder 是你的 Order 模型)
    order_info = PayOrder.query.filter_by(order_sn=order_sn, member_id=member_info.id).first()

    if not order_info:
        resp['code'] = -1
        resp['msg'] = '订单不存在或无权查看'
        return jsonify(resp)

    # --- 获取订单详情数据 ---

    # 1. 订单商品列表
    # 修改这一行：将 order_id 改为 pay_order_id
    order_items = PayOrderItem.query.filter_by(pay_order_id=order_info.id).all()

    goods_list = []
    # ... (后续根据 order_items 列表查询 Food 信息并构建 goods_list 的代码，保持不变)
    food_ids = [item.food_id for item in order_items]
    food_map = {food.id: food for food in Food.query.filter(Food.id.in_(food_ids)).all()}

    for item in order_items:
        food = food_map.get(item.food_id)
        if food:
            tmp_data = {
                'id': food.id,
                'name': food.name,
                'price': str(item.price), # 使用订单项中的价格
                'pic_url': UrlManager.buildImageUrl(food.main_image),
                'unit': item.quantity
            }
            goods_list.append(tmp_data)

    # ... (获取地址、状态、截止时间等其他逻辑，保持不变)
    address_info = MemberAddress.query.filter_by(id=order_info.express_address_id, member_id=member_info.id, status=1).first()

    order_address = {}
    if address_info:
         order_address = {
             "id": address_info.id,
             "nickname": address_info.nickname,
             "mobile": address_info.mobile,
             "address": "%s%s%s%s" % (
                 address_info.province_str, address_info.city_str, address_info.area_str, address_info.address)
         }

    status_desc = order_info.status_desc # 假设 PayOrder 模型有 status_desc
    deadline = ''
    if order_info.status == -8: # 假设 -8 是待付款状态
         if hasattr(order_info, 'pay_deadline') and order_info.pay_deadline:
              deadline = order_info.pay_deadline.strftime('%Y-%m-%d %H:%M:%S')


    # 组织最终返回的 info 结构
    info = {
        'status': order_info.pay_status, # 使用 pay_status
        'status_desc': status_desc,
        'deadline': deadline,
        'address': order_address,
        'goods': goods_list, # 将商品列表放在 goods 键下
        'pay_price': str(order_info.pay_price),
        'yun_price': str(order_info.yun_price),
        'total_price': str(order_info.total_price),
        'order_sn': order_info.order_sn
    }

    resp['data']['info'] = info # 将所有订单详情数据放在 data.info 键下

    return jsonify(resp)

# @route_api.route("/order/create", methods=['POST'])
# def orderCreate():
#     resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
#     req = request.values
#     type = req['type'] if 'type' in req else ''
#     note = req['note'] if 'note' in req else ''
#     express_address_id = int(req['express_address_id']) if 'express_address_id' in req and req[
#         'express_address_id'] else 0
#     params_goods = req['goods'] if 'goods' in req else None
#
#     items = []
#     if params_goods:
#         items = json.loads(params_goods)
#
#     if len(items) < 1:
#         resp['code'] = -1
#         resp['msg'] = '下单失败：没有选择商品~~'
#         return jsonify(resp)
#
#     address_info = MemberAddress.query.filter_by(id=express_address_id).first()
#     if not address_info or not address_info.status:
#         resp['code'] = -1
#         resp['msg'] = "下单失败：快递地址不对~~"
#         return jsonify(resp)
#
#     member_info = g.member_info
#     target = PayService()
#     params = {
#         "note": note,
#         'express_address_id': address_info.id,
#         'express_info': {
#             'mobile': address_info.mobile,
#             'nickname': address_info.nickname,
#             "address": "%s%s%s%s" % (
#                 address_info.province_str, address_info.city_str, address_info.area_str, address_info.address)
#         }
#     }
#     resp = target.createOrder(member_info.id, items, params)
#     # 如果是来源购物车的，下单成功将下单的商品去掉
#     if resp['code'] == 200 and type == "cart":
#         CartService.deleteItem(member_info.id, items)
#
#     return jsonify(resp)
@route_api.route("/order/create", methods=['POST'])
def orderCreate():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values # request.values 可以获取 form 或 query string 参数

    # 1. 检查用户登录
    member_info = g.member_info # 假设 g 中已设置 member_info
    if not member_info:
         resp['code'] = -1
         resp['msg'] = '请先登录！'
         app.logger.warning("Order creation failed: User not logged in.")
         return jsonify(resp)

    # 2. 获取并验证参数 (使用 .get 方法避免 KeyError)
    order_type = req.get('type', '') # 避免与内置函数 type 冲突，改名 order_type
    note = req.get('note', '')

    # 获取 express_address_id，并尝试转换为 int
    express_address_id_str = req.get('express_address_id', '0') # 默认给 '0' 避免 int("") 报错
    try:
        express_address_id = int(express_address_id_str)
        if express_address_id <= 0: # 简单校验 ID 大于 0
             resp['code'] = -1
             resp['msg'] = "下单失败：请选择收货地址~~" # 更友好的提示
             app.logger.warning(f"Order creation failed for member_id {member_info.id}: Invalid express_address_id {express_address_id_str}.")
             return jsonify(resp)
    except (ValueError, TypeError):
        resp['code'] = -1
        resp['msg'] = "下单失败：快递地址参数格式错误~~"
        app.logger.error(f"Order creation failed for member_id {member_info.id}: express_address_id not an integer: {express_address_id_str}")
        return jsonify(resp)


    params_goods_str = req.get('goods')

    items = []
    if not params_goods_str:
        resp['code'] = -1
        resp['msg'] = '下单失败：缺少商品信息~~'
        app.logger.warning(f"Order creation failed for member_id {member_info.id}: Missing goods parameter.")
        return jsonify(resp)

    try:
        # 解析 JSON 字符串为 Python 列表/字典
        items = json.loads(params_goods_str)
        # 确保 items 是一个非空列表
        if not items or not isinstance(items, list) or len(items) < 1:
             resp['code'] = -1
             resp['msg'] = '下单失败：没有选择有效商品~~'
             app.logger.warning(f"Order creation failed for member_id {member_info.id}: Empty or invalid items list: {items}.")
             return jsonify(resp)
        # 可以进一步校验 items 列表中每个元素是否包含 'id' 和 'number'
        for item in items:
             if not isinstance(item, dict) or 'id' not in item or 'number' not in item:
                  resp['code'] = -1
                  resp['msg'] = '下单失败：商品信息格式错误~~'
                  app.logger.error(f"Order creation failed for member_id {member_info.id}: Invalid item structure in goods list: {items}.")
                  return jsonify(resp)

    except json.JSONDecodeError:
         resp['code'] = -1
         resp['msg'] = '下单失败：商品信息格式错误~~'
         app.logger.error(f"Order creation failed for member_id {member_info.id}: Invalid goods JSON: {params_goods_str}")
         return jsonify(resp)


    # 3. 验证地址信息 (确保地址存在、属于当前用户且状态有效)
    # 这里查询MemberAddress时，增加 member_id 和 status=1 的过滤，更安全
    address_info = MemberAddress.query.filter_by(id=express_address_id, member_id=member_info.id, status=1).first()
    if not address_info:
        resp['code'] = -1
        resp['msg'] = "下单失败：快递地址不对或已失效~~"
        app.logger.warning(f"Order creation failed for member_id {member_info.id}: Address ID {express_address_id} not found or invalid.")
        return jsonify(resp)

    # 4. 准备参数并调用服务层
    # 将获取和验证后的信息传递给 PayService
    service_params = {
        "note": note,
        'express_address_id': address_info.id, # 传递地址 ID
        # PayService 内部应该根据这个 ID 自己去查询地址详情来填充 PayOrder 的 express_info 字段
        # 或者如果你的 PayOrder 表结构包含 express_info 字段，可以在 PayService 里构建
        # 如果 PayService 只需要 ID，express_info block 在这里就不需要构建了
        # 假设 PayService 需要 address_info 对象来保存 express_info 到 PayOrder 表
        'address_info': address_info # 可以直接传递 address_info 对象给服务层
    }
    app.logger.info(f"Calling PayService.createOrder for member {member_info.id} with {len(items)} items, params: {service_params}")

    # 5. 调用 PayService 创建订单
    # PayService().createOrder 方法应该完成：
    # - 验证商品库存等
    # - 计算最终价格
    # - 生成订单号 (order_sn)
    # - 创建 PayOrder 记录，并设置 member_id, total/pay/yun_price, order_sn, status=-8 (待支付)
    # - ** !!! 保存 express_address_id 到 PayOrder 记录 !!! **
    # - ** !!! 计算支付截止时间 (pay_deadline) 并保存到 PayOrder 记录 !!! **
    # - ** !!! 将 address_info 中的详细信息保存到 PayOrder 的 express_info 字段 !!! **
    # - 创建 PayOrderItem 记录，并关联到 PayOrder
    # - 数据库事务管理 (提交/回滚)
    # - 返回结果字典 (包含 code, msg, data, data['order_sn'] 等)

    target = PayService() # 实例化 PayService
    resp = target.createOrder(member_info.id, items, service_params)

    app.logger.info(f"PayService.createOrder returned: {resp}")


    # 6. 处理购物车清理 (如果订单创建成功且来自购物车)
    # 使用 .get() 获取 code 避免 KeyError
    if resp.get('code') == 200 and order_type == "cart":
        # CartService.deleteItem 可能需要一个列表，包含要删除的 food_id
        items_to_delete_from_cart = [{"id": item.get('id')} for item in items if item.get('id')]
        if items_to_delete_from_cart:
             try:
                CartService.deleteItem(member_info.id, items_to_delete_from_cart)
                app.logger.info(f"Removed {len(items_to_delete_from_cart)} items from cart for member {member_info.id}.")
             except Exception as cart_err:
                # 购物车删除失败不影响订单创建，只记录日志
                app.logger.error(f"Failed to delete cart items after order creation for member {member_info.id}: {cart_err}", exc_info=True)


    # 7. 返回结果给前端
    return jsonify(resp)

@route_api.route("/order/pay", methods=["POST"])
def orderPay():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    member_info = g.member_info
    req = request.values
    order_sn = req['order_sn'] if 'order_sn' in req else ''
    pay_order_info = PayOrder.query.filter_by(order_sn=order_sn, member_id=member_info.id).first()
    if not pay_order_info:
        resp['code'] = -1
        resp['msg'] = "订单不存在或不属于当前用户~~" # 提示信息更具体
        return jsonify(resp)

    # 检查订单状态，避免重复支付或处理已取消的订单
    # 假设 -8 是待支付状态，你需要根据你的status定义来调整
    if pay_order_info.status != -8:
         resp['code'] = -1
         resp['msg'] = "订单状态异常，请勿重复支付或订单已失效~~"
         return jsonify(resp)

    oauth_bind_info = OauthMemberBind.query.filter_by(member_id=member_info.id).first()
    if not oauth_bind_info:
        resp['code'] = -1
        resp['msg'] = "系统繁忙，请稍后再试~~(用户信息绑定异常)" # 提示信息更具体
        return jsonify(resp)

    config_mina = app.config['MINA_APP']
    ngrok_domain = app.config['APP']['ngrok_domain']
    # 确保 callback_url 配置正确
    # notify_url = app.config['APP']['domain'] + config_mina['callback_url'] if config_mina.get('callback_url') else None
    notify_url = f"{ngrok_domain}{config_mina['callback_url']}"
    # --- 在这里添加日志输出 ---
    app.logger.info(f"计算得到的支付回调地址 notify_url: {notify_url}")

    # 检查 notify_url 是否为空
    if not notify_url:
        resp['code'] = -1
        resp['msg'] = "系统配置错误，回调地址未设置~~"
        app.logger.error("系统配置错误，回调地址未设置或为空。")  # 增加日志
        return jsonify(resp)

    target_wechat = WeChatService(merchant_key=config_mina['paykey'])

    data = {
        'appid': config_mina['appid'],
        'mch_id': config_mina['mch_id'],
        'nonce_str': target_wechat.get_nonce_str(),
        'body': '订单支付',
        'out_trade_no': pay_order_info.order_sn,
        'total_fee': int(pay_order_info.pay_price * 100),  # 使用 pay_price 并转成分
        'notify_url': notify_url,
        'trade_type': "JSAPI",
        'openid': oauth_bind_info.openid
    }

    # --- 在这里添加日志输出 ---
    app.logger.info(f"准备传递给 WeChatService.get_pay_info 的 data 字典: {data}")
    # --------------------------

    # **修改：调用新的 get_pay_info 方法并检查返回结构**
    pay_result = target_wechat.get_pay_info(pay_data=data)

    if not pay_result or not pay_result.get('success'):
        # 获取支付信息失败，直接返回错误信息
        resp['code'] = -1
        resp['msg'] = pay_result.get('msg', '获取支付信息失败，请稍后再试~~')
        # get_pay_info 内部已经记录了详细日志，这里可以不用重复记录特定错误
        return jsonify(resp)

    # 获取支付信息成功
    frontend_pay_info = pay_result.get('data')  # 获取给前端的支付数据
    prepay_id = frontend_pay_info.get('prepay_id')  # 从返回数据中获取 prepay_id

    # 保存 prepay_id 到数据库
    pay_order_info.prepay_id = prepay_id  # 现在这里确保 prepay_id 是从成功的接口返回的
    # pay_order_info.status = -7 # 更新订单状态为已发起支付请求等（根据你的状态定义）

    try:
        db.session.add(pay_order_info)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        resp['code'] = -1
        resp['msg'] = "订单信息保存失败，请稍后再试~~"
        app.logger.error(f"Database commit failed for order_sn: {order_sn}, error: {e}")
        return jsonify(resp)

    # 返回前端支付信息
    resp['data']['pay_info'] = frontend_pay_info  # 将获取到的前端支付数据放入 resp['data']
    resp['msg'] = pay_result.get('msg', '操作成功~')  # 可以使用 get_pay_info 返回的成功消息
    return jsonify(resp)

@route_api.route('/order/callback', methods=['GET', 'POST'])
def orderCallback():
    """
    <xml><appid><![CDATA[wx64f3ca472d535f45]]></appid>
    <bank_type><![CDATA[OTHERS]]></bank_type>
    <cash_fee><![CDATA[1]]></cash_fee>
    <fee_type><![CDATA[CNY]]></fee_type>
    <is_subscribe><![CDATA[N]]></is_subscribe>
    <mch_id><![CDATA[1715360269]]></mch_id>
    <nonce_str><![CDATA[be8c4fb26fac4606afca82a3af61b973]]></nonce_str>
    <openid><![CDATA[oMDmr7az-nQ3A5NvlXTHSgs8p-nk]]></openid>
    <out_trade_no><![CDATA[92a1482fcbebd695a705c5ee09e33232]]></out_trade_no>
    <result_code><![CDATA[SUCCESS]]></result_code>
    <return_code><![CDATA[SUCCESS]]></return_code>
    <sign><![CDATA[5A99FE791DC122D008FE7D482B5C1D92]]></sign>
    <time_end><![CDATA[20250426110129]]></time_end>
    <total_fee>1</total_fee>
    <trade_type><![CDATA[JSAPI]]></trade_type>
    <transaction_id><![CDATA[4200002693202504262337101840]]></transaction_id>
    </xml>
    :return:
    """
    result_data = {
        'return_code': 'SUCCESS',
        'return_msg': 'OK',
    }
    header = {'Content-Type': 'application/xml'}
    config_mina = app.config['MINA_APP']
    target_wechat = WeChatService(merchant_key=config_mina['paykey'])
    callback_data = target_wechat.xml_to_dict(request.data)
    app.logger.info(callback_data)
    sign = callback_data['sign']
    callback_data.pop('sign')
    gene_sign = target_wechat.create_sign(callback_data)
    app.logger.info(gene_sign)
    if sign != gene_sign:
        result_data['result_code'] = result_data['result_msg'] = 'FAIL'
        return target_wechat.dict_to_xml(result_data), header
    order_sn = callback_data['out_trade_no']
    pay_order_info = PayOrder.query.filter_by(order_sn=order_sn).first()
    if not pay_order_info:
        result_data['result_code'] = result_data['result_msg'] = 'FAIL'
        return target_wechat.dict_to_xml(result_data), header

    if int(pay_order_info.total_price * 100) != int(callback_data['total_fee']):
        result_data['result_code'] = result_data['result_msg'] = 'FAIL'
        return target_wechat.dict_to_xml(result_data), header

    if pay_order_info.status == 1:
        return target_wechat.dict_to_xml(result_data), header

    target_pay = PayService()
    target_pay.orderSuccess(pay_order_id=pay_order_info.id, params={'pay_sn': callback_data['transaction_id']})
    # 讲微信回调的结果放入记录表
    target_pay.addPayCallbackData(pay_order_id=pay_order_info.id, data=request.data)
    return target_wechat.dict_to_xml(result_data), header


@route_api.route("/order/ops", methods=["POST"])
def orderOps():
    resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
    req = request.values
    member_info = g.member_info
    order_sn = req['order_sn'] if 'order_sn' in req else ''
    act = req['act'] if 'act' in req else ''
    pay_order_info = PayOrder.query.filter_by(order_sn=order_sn, member_id=member_info.id).first()
    if not pay_order_info:
        resp['code'] = -1
        resp['msg'] = "系统繁忙，请稍后再试~~"
        return jsonify(resp)

    if act == "cancel":
        target_pay = PayService()
        ret = target_pay.closeOrder(pay_order_id=pay_order_info.id)
        if not ret:
            resp['code'] = -1
            resp['msg'] = "系统繁忙，请稍后再试~~"
            return jsonify(resp)
    elif act == "confirm":
        pay_order_info.express_status = 1
        pay_order_info.updated_time = getCurrentDate()
        db.session.add(pay_order_info)
        db.session.commit()

    return jsonify(resp)
