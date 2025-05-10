# -*- coding: utf-8 -*-
import datetime
import json
import requests

from sqlalchemy import func

from application import app, db
from common.libs.Helper import getCurrentDate
from common.libs.pay.WeChatService import WeChatService
from common.models.food.Food import Food
from common.models.food.FoodSaleChangeLog import FoodSaleChangeLog
from common.models.member.OauthMemberBind import OauthMemberBind
from common.models.pay.PayOrder import PayOrder
from common.models.pay.PayOrderItem import PayOrderItem
from common.models.queue.QueueList import QueueList

'''
python manager.py runjob -m queue/index
'''


class JobTask():
    def __init__(self):
        pass

    def run(self, params):
        list = QueueList.query.filter_by(status=-1) \
            .order_by(QueueList.id.asc()).limit(1).all()
        for item in list:
            if item.queue_name == "pay":
                self.handlePay(item)

            item.status = 1
            item.updated_time = getCurrentDate()
            db.session.add(item)
            db.session.commit()

    def handlePay(self, item):
        data = json.loads(item.data)
        if 'member_id' not in data or 'pay_order_id' not in data:
            return False

        oauth_bind_info = OauthMemberBind.query.filter_by(member_id=data['member_id']).first()
        if not oauth_bind_info:
            return False

        pay_order_info = PayOrder.query.filter_by(id=data['pay_order_id']).first()
        if not pay_order_info:
            return False

        # 更新销售总量
        pay_order_items = PayOrderItem.query.filter_by(pay_order_id=pay_order_info.id).all()
        notice_content = []
        if pay_order_items:
            date_from = datetime.datetime.now().strftime("%Y-%m-01 00:00:00")
            date_to = datetime.datetime.now().strftime("%Y-%m-31 23:59:59")
            for item in pay_order_items:
                tmp_food_info = Food.query.filter_by(id=item.food_id).first()
                if not tmp_food_info:
                    continue

                notice_content.append("%s %s份" % (tmp_food_info.name, item.quantity))

                # 当月数量
                tmp_month_count = db.session.query(func.sum(FoodSaleChangeLog.quantity)) \
                    .filter(FoodSaleChangeLog.food_id == item.food_id) \
                    .filter(FoodSaleChangeLog.created_time >= date_from,
                            FoodSaleChangeLog.created_time <= date_to) \
                    .scalar()

                # 如果查询结果是 None (表示没有找到符合条件的记录)，则总数量为 0
                tmp_month_count = tmp_month_count if tmp_month_count is not None else 0
                tmp_food_info.total_count += item.quantity  # 注意这里应该是加上当前订单的 quantity，而不是 +1
                tmp_food_info.month_count = tmp_month_count if tmp_month_count is not None else 0  # 更新当月数量
                db.session.add(tmp_food_info)
                db.session.commit()  # 将 commit 移到循环外部，批量提交更高效

        keyword1_val = pay_order_info.note if pay_order_info.note else '无'
        keyword2_val = "、".join(notice_content)
        keyword3_val = str(pay_order_info.total_price)
        keyword4_val = str(pay_order_info.order_number)
        # keyword5_val = ""
        # if pay_order_info.express_info:
        #     express_info = json.loads(pay_order_info.express_info)
        #     keyword5_val = str(express_info['address'])
        keyword5_val = str(pay_order_info.pay_time)

        # 发送模板消息
        target_wechat = WeChatService()
        access_token = target_wechat.getAccessToken()
        headers = {'Content-Type': 'application/json'}
        url = f"https://api.weixin.qq.com/cgi-bin/message/wxopen/template/send?access_token={access_token}"
        params = {
            "touser": oauth_bind_info.openid,
            "template_id": "dDImnvTa8WPgpgooqGyq2gJT61Y23H2Sk7TA7aZ-3U0",
            "page": "pages/my/order_list",
            "form_id": pay_order_info.prepay_id,
            "data": {
                "keyword1": {
                    "value": keyword1_val
                },
                "keyword2": {
                    "value": keyword2_val
                },
                "keyword3": {
                    "value": keyword3_val
                },
                "keyword4": {
                    "value": keyword4_val
                },
                "keyword5": {
                    "value": keyword5_val
                }
            }
        }

        r = requests.post(url=url, data=json.dumps(params).encode('utf-8'), headers=headers)
        r.encoding = "utf-8"
        app.logger.info(r.text)
        return True
