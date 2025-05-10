# -*- coding: utf-8 -*-
import decimal
import hashlib
import json
from datetime import datetime, timedelta
from random import randint
from time import time

from application import db, app
from common.libs.Helper import getCurrentDate
from common.libs.food.FoodService import FoodService
from common.libs.queue.QueueService import QueueService
from common.models.food.Food import Food
from common.models.food.FoodSaleChangeLog import FoodSaleChangeLog
from common.models.pay.PayOrder import PayOrder
from common.models.pay.PayOrderCallbackData import PayOrderCallbackData
from common.models.pay.PayOrderItem import PayOrderItem


class PayService():
    def __init__(self):
        pass

    # 改进后的 createOrder 方法
    def createOrder(self, member_id, items=None, params=None):
        resp = {'code': 200, 'msg': '操作成功', 'data': {}}

        if not items or not isinstance(items, list) or len(items) < 1:
             resp['code'] = -1
             resp['msg'] = '商品列表为空'
             # app.logger.warning(f"Create order failed for member {member_id}: items list empty or invalid.")
             return resp

        # 从 params 中获取订单相关参数
        params = params if params is not None else {}
        note = params.get('note', '')
        express_address_id = params.get('express_address_id', 0) # 获取地址ID
        address_info = params.get('address_info') # 获取地址详情对象 (假设接口层已经查好并传递过来)
        # 运费获取，如前所述，建议后端计算更安全
        yun_price_from_params = params.get('yun_price', '0')
        try:
             yun_price = decimal.Decimal(yun_price_from_params)
        except (decimal.InvalidOperation, TypeError):
             yun_price = decimal.Decimal('0.00') # 转换失败则设为0

        # 1. 计算商品总金额并获取商品ID列表 (忽略负价商品，收集有效项)
        pay_price = decimal.Decimal(0.00)
        foods_id = []
        valid_items = [] # 存储有效的订单项数据，用于后续处理和库存检查
        for item in items:
             # 确保 item 是字典且包含必要的键和可转换为 Decimal/int 的值
             if not isinstance(item, dict) or 'id' not in item or 'number' not in item or 'price' not in item:
                  # app.logger.warning(f"Skipping invalid item format: {item}")
                  continue # 跳过格式不正确的项

             try:
                  item_price = decimal.Decimal(str(item['price'])) # 获取前端传的单价，并转换为Decimal
                  item_number = int(item['number']) # 获取数量，并转换为int
             except (decimal.InvalidOperation, ValueError):
                  # app.logger.warning(f"Skipping item with invalid price or number: {item}")
                  continue # 跳过价格或数量格式不正确的项

             if item_price < 0 or item_number <= 0:
                  # app.logger.warning(f"Skipping item with negative price or zero number: {item}")
                  continue # 忽略负价或数量为0的商品

             # PayOrderItem.price 字段存储的是该项的总价格 (单价 * 数量)
             item_total_price = item_price * item_number
             pay_price += item_total_price # 累加商品总金额

             foods_id.append(item['id'])
             valid_items.append({ # 存储用于后续处理的规范化数据
                  'food_id': item['id'], # 使用 food_id 键名更清晰
                  'quantity': item_number,
                  'unit_price': item_price, # 存储单价，方便计算订单项总价
                  'item_total_price': item_total_price, # 计算好的订单项总价
                  'note': item.get('note', '') # 如果订单项有备注
              })

        if not valid_items:
            resp['code'] = -1
            resp['msg'] = '没有选择有效商品进行结算'
            # app.logger.warning(f"Create order failed for member {member_id}: No valid items after processing.")
            return resp

        # 计算最终总价
        total_price = pay_price + yun_price

        # 校验地址是否存在 (接口层已经校验过，这里可以简化或跳过，取决于你希望在哪层处理严格校验)
        if not address_info or not express_address_id or address_info.id != express_address_id:
            resp['code'] = -1
            resp['msg'] = "快递地址信息不匹配或不存在~~"
            # app.logger.error(f"Create order failed for member {member_id}: Address info mismatch. express_address_id from params: {express_address_id}, address_info passed: {address_info}")
            return resp


        try:
             # 2. 在事务中锁定商品，检查库存并更新销量
             # 使用 with_for_update() 在事务中锁定行，防止超卖
             # 根据收集到的 foods_id 批量查询商品
             tmp_food_list = db.session.query(Food).filter(Food.id.in_(foods_id)).with_for_update().all()

             # 构建 Food 映射，方便根据 ID 查找
             tmp_food_mapping = {tmp_item.id: tmp_item for tmp_item in tmp_food_list}

             # 检查查询到的商品数量是否与有效商品项数量一致
             if len(tmp_food_list) != len(valid_items):
                  raise Exception("部分商品信息异常，请刷新后重试") # 如果有商品ID找不到，或者有重复的商品ID导致数量不匹配


             # 遍历有效商品项，检查库存并更新销量
             for item in valid_items:
                  food_id = item['food_id']
                  quantity = item['quantity']

                  target_food = tmp_food_mapping.get(food_id)

                  # 理论上 target_food 应该存在，因为上面检查了数量
                  if not target_food:
                      raise Exception(f"商品 ID {food_id} 未找到，下单失败")

                  # 检查库存是否足够
                  if quantity > target_food.stock:
                      raise Exception(f"商品【{target_food.name}】库存不足，剩余：{target_food.stock}，您购买：{quantity}")

                  # 更新 Food 表库存和销量
                  target_food.stock -= quantity
                  target_food.month_count += quantity
                  target_food.total_count += quantity
                  # ORM 对象修改后会自动被 session 跟踪，不需要 add


             # 3. 创建 PayOrder 记录 (只创建一次)
             model_pay_order = PayOrder()
             model_pay_order.order_sn = self.geneOrderSn()
             model_pay_order.member_id = member_id
             model_pay_order.total_price = total_price # 使用计算出的总价
             model_pay_order.yun_price = yun_price
             model_pay_order.pay_price = pay_price
             model_pay_order.note = note # 保存备注
             model_pay_order.status = -8 # 默认待支付状态
             model_pay_order.express_status = -8 # 快递状态初始也是待支付相关
             model_pay_order.updated_time = getCurrentDate()
             model_pay_order.created_time = getCurrentDate()

             # !!! 关键改进 1: 保存快递地址 ID !!!
             model_pay_order.express_address_id = express_address_id

             # !!! 关键改进 2: 保存快递地址详情 (如果你的 PayOrder 表有 express_info 字段) !!!
             # 根据你的 PayOrder 模型 express_info 字段类型保存
             if address_info: # address_info 是 MemberAddress 对象
                 # 组织 express_info 字段内容，例如保存为 JSON 字符串
                 express_info_data = {
                     'nickname': address_info.nickname,
                     'mobile': address_info.mobile,
                     'address': "%s%s%s%s" % (
                         address_info.province_str, address_info.city_str, address_info.area_str, address_info.address)
                 }
                 # 确保 express_info 字段足够长来存储 JSON 字符串
                 model_pay_order.express_info = json.dumps(express_info_data)
                 # 如果 express_info 是 Text 类型，也可以保存格式化文本
                 # model_pay_order.express_info = f"收件人: {address_info.nickname}, 电话: {address_info.mobile}, 地址: {address_info.province_str}{address_info.city_str}{address_info.area_str}{address_info.address}"
             else:
                  # 理论上接口层已经校验地址存在，这里不应该没有 address_info，但为了健壮性可以设置空值
                  model_pay_order.express_info = '' # 或者 None


             # !!! 关键改进 3: 计算并保存支付截止时间 !!!
             # 假设支付时限是下单后2小时
             # 需要根据实际业务需求调整时限
             payment_deadline = datetime.now() + timedelta(hours=2)  # 例如，从当前时间算起
             model_pay_order.pay_deadline = payment_deadline  # <-- 添加这一行，将计算出的时间赋值给字段

             db.session.add(model_pay_order) # 添加 PayOrder 记录到 session
             db.session.flush() # 刷新 session，以便获取 model_pay_order 的 ID

             # 4. 创建 PayOrderItem 记录 (循环 valid_items)
             for item in valid_items:
                 food_id = item['food_id']
                 quantity = item['quantity']
                 item_unit_price = item['unit_price'] # 单价
                 item_total_price = item['item_total_price'] # 总价
                 item_note = item.get('note', '')

                 # 创建 PayOrderItem 记录
                 tmp_pay_item = PayOrderItem()
                 tmp_pay_item.pay_order_id = model_pay_order.id # 关联到新创建的 PayOrder
                 tmp_pay_item.member_id = member_id
                 tmp_pay_item.quantity = quantity
                 tmp_pay_item.price = item_total_price # !!! PayOrderItem.price 保存该项的总价格 !!!
                 tmp_pay_item.food_id = food_id
                 tmp_pay_item.note = item_note # 如果订单项有备注
                 tmp_pay_item.status = 1 # 订单项状态，假设1为正常
                 tmp_pay_item.updated_time = getCurrentDate()
                 tmp_pay_item.created_time = getCurrentDate()
                 db.session.add(tmp_pay_item) # 添加 PayOrderItem 记录到 session

                 # 记录库存变化日志
                 # FoodService.setStockChangeLog(food_id, -quantity, "在线购买", member_id=member_id) # 传递 member_id 更详细

             # 5. 提交事务
             db.session.commit()

             # 6. 构建并返回成功响应
             resp['data'] = {
                 'id': model_pay_order.id,
                 'order_sn': model_pay_order.order_sn,
                 'total_price': str(model_pay_order.total_price) # 返回订单中保存的总价
             }
             resp['msg'] = '下单成功'

        except Exception as e:
            # 7. 捕获异常，回滚事务，并返回错误信息
            db.session.rollback()
            # print(e) # 避免直接 print 而是使用 logger
            # app.logger.error(f"Failed to create order for member {member_id}: {e}", exc_info=True) # 记录详细错误日志
            resp['code'] = -1
            resp['msg'] = "下单失败，请稍后再试" # 默认错误信息
            # 如果是用户友好的错误（如库存不足），使用捕获到的异常信息
            if "库存不足" in str(e) or "商品信息异常" in str(e):
                 resp['msg'] = str(e)

        return resp

    def geneOrderSn(self):
        m = hashlib.md5()
        sn = None
        while True:
            str = "%s-%s" % (int(round(time() * 1000)), randint(0, 9999999))
            m.update(str.encode("utf-8"))
            sn = m.hexdigest()
            if not PayOrder.query.filter_by(order_sn=sn).first():
                break

        return sn

    def orderSuccess(self, pay_order_id=0, params=None):
        try:
            pay_order_info = PayOrder.query.filter_by(id=pay_order_id).first()
            if not pay_order_info or pay_order_info.status not in [-8, -7]:
                return True

            pay_order_info.pay_sn = params['pay_sn'] if params and 'pay_sn' in params else ''
            pay_order_info.status = 1
            pay_order_info.express_status = -7
            pay_order_info.updated_time = getCurrentDate()
            db.session.add(pay_order_info)
            # 售卖历史
            pay_order_items = PayOrderItem.query.filter_by(pay_order_id=pay_order_id).all()
            for order_item in pay_order_items:
                tmp_model_sale_log = FoodSaleChangeLog()
                tmp_model_sale_log.food_id = order_item.food_id
                tmp_model_sale_log.quantity = order_item.quantity
                tmp_model_sale_log.price = order_item.price
                tmp_model_sale_log.member_id = order_item.member_id
                tmp_model_sale_log.created_time = getCurrentDate()
                db.session.add(tmp_model_sale_log)

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return False

        QueueService.addQueue("pay", {
            "member_id": pay_order_info.member_id,
            "pay_order_id": pay_order_info.id
        })

    def addPayCallbackData(self, pay_order_id=0, type='pay', data=''):
        model_callback = PayOrderCallbackData()
        model_callback.pay_order_id = pay_order_id
        if type == "pay":
            model_callback.pay_data = data
            model_callback.refund_data = ''
        else:
            model_callback.refund_data = data
            model_callback.pay_data = ''

        model_callback.created_time = model_callback.updated_time = getCurrentDate()
        db.session.add(model_callback)
        db.session.commit()
        return True

    def closeOrder(self, pay_order_id=0):
        if pay_order_id < 1:
            return False
        pay_order_info = PayOrder.query.filter_by(id=pay_order_id, status=-8).first()
        if not pay_order_info:
            return False

        pay_order_items = PayOrderItem.query.filter_by(pay_order_id=pay_order_id).all()
        if pay_order_items:
            # 需要归还库存
            for item in pay_order_items:
                tmp_food_info = Food.query.filter_by(id=item.food_id).first()
                if tmp_food_info:
                    tmp_food_info.stock = tmp_food_info.stock + item.quantity
                    tmp_food_info.updated_time = getCurrentDate()
                    db.session.add(tmp_food_info)
                    db.session.commit()
                    FoodService.setStockChangeLog(item.food_id, item.quantity, "订单取消")

        pay_order_info.status = 0
        pay_order_info.updated_time = getCurrentDate()
        db.session.add(pay_order_info)
        db.session.commit()
        return True

