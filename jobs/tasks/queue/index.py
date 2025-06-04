# -*- coding: utf-8 -*-
import datetime
import json
import requests

from sqlalchemy import func

from application import app, db
from common.libs.Helper import getCurrentDate
from common.libs.pay.WeChatService import WeChatService
from common.models.goods.Goods import Goods
from common.models.goods.GoodsSaleChangeLog import GoodsSaleChangeLog
from common.models.member.OauthMemberBind import OauthMemberBind
from common.models.pay.PayOrder import PayOrder
from common.models.pay.PayOrderItem import PayOrderItem
from common.models.queue.QueueList import QueueList

'''
任务队列的执行脚本。  
使用方法：python manager.py runjob -m queue/index
这个脚本主要负责从队列中取出任务并执行，目前只实现了处理支付相关的任务。
'''


class JobTask():
    def __init__(self):
        pass

    def run(self, params):
        """
        任务执行入口函数。
        该函数从队列中获取一个待处理的任务，并根据任务类型进行处理。
        :param params: 任务参数 (目前未使用)
        :return: None
        """
        # 从 QueueList 表中获取一个 status 为 -1 (待处理) 的任务，并按照 id 升序排序
        list = QueueList.query.filter_by(status=-1) \
            .order_by(QueueList.id.asc()).limit(1).all()

        # 遍历获取到的任务列表（实际上只有一个任务）
        for item in list:
            # 根据任务名 (queue_name) 判断任务类型
            if item.queue_name == "pay":
                # 如果是支付相关的任务，则调用 handlePay 函数进行处理
                self.handlePay(item)

            # 更新任务状态为 1 (已处理)
            item.status = 1
            # 更新任务的 updated_time 为当前时间
            item.updated_time = getCurrentDate()
            # 将更新后的任务信息添加到数据库会话中
            db.session.add(item)
            # 提交数据库会话，将更改保存到数据库
            db.session.commit()

    def handlePay(self, item):
        """
        处理支付相关的任务。
        该函数从任务数据中获取 member_id 和 pay_order_id，
        然后查询相关信息并更新销售总量，最后发送微信模板消息。
        :param item: 队列中的任务项 (QueueList 对象)
        :return: True if the task was processed successfully, False otherwise.
        """
        # 从任务数据 (JSON 字符串) 中解析出数据
        data = json.loads(item.data)

        # 检查数据中是否包含 member_id 和 pay_order_id，如果缺少则返回 False
        if 'member_id' not in data or 'pay_order_id' not in data:
            return False

        # 根据 member_id 查询 OauthMemberBind 表，获取用户绑定信息
        oauth_bind_info = OauthMemberBind.query.filter_by(member_id=data['member_id']).first()
        # 如果用户未绑定 OAuth 信息，则返回 False
        if not oauth_bind_info:
            return False

        # 根据 pay_order_id 查询 PayOrder 表，获取订单信息
        pay_order_info = PayOrder.query.filter_by(id=data['pay_order_id']).first()
        # 如果订单不存在，则返回 False
        if not pay_order_info:
            return False

        # 更新销售总量
        # 根据 pay_order_id 查询 PayOrderItem 表，获取订单中的商品信息
        pay_order_items = PayOrderItem.query.filter_by(pay_order_id=pay_order_info.id).all()
        notice_content = []
        # 如果订单中有商品
        if pay_order_items:
            # 获取当前月份的起始和结束时间
            date_from = datetime.datetime.now().strftime("%Y-%m-01 00:00:00")
            date_to = datetime.datetime.now().strftime("%Y-%m-31 23:59:59")
            # 遍历订单中的每个商品
            for item in pay_order_items:
                # 根据 goods_id 查询 Goods 表，获取商品信息
                tmp_goods_info = Goods.query.filter_by(id=item.goods_id).first()
                # 如果商品不存在，则跳过
                if not tmp_goods_info:
                    continue

                # 构建微信消息的商品名称和数量
                notice_content.append("%s %s份" % (tmp_goods_info.name, item.quantity))

                # 统计当月该商品的销量
                tmp_month_count = db.session.query(func.sum(GoodsSaleChangeLog.quantity)) \
                    .filter(GoodsSaleChangeLog.goods_id == item.goods_id) \
                    .filter(GoodsSaleChangeLog.created_time >= date_from,
                            GoodsSaleChangeLog.created_time <= date_to) \
                    .scalar()

                # 如果查询结果是 None (表示没有找到符合条件的记录)，则总数量为 0
                tmp_month_count = tmp_month_count if tmp_month_count is not None else 0
                # 更新商品的总销量
                tmp_goods_info.total_count += item.quantity  # 注意这里应该是加上当前订单的 quantity
                tmp_goods_info.month_count = tmp_month_count if tmp_month_count is not None else 0  # 更新当月数量

                # 将更新后的商品信息添加到数据库会话中
                db.session.add(tmp_goods_info)

            # 将 commit 移到循环外部，批量提交更高效
            db.session.commit()

        # 准备微信模板消息的数据
        keyword1_val = pay_order_info.note if pay_order_info.note else '无'  # 订单备注，如果没有则显示 "无"
        keyword2_val = "、".join(notice_content)  # 商品名称和数量，用 "、" 连接
        keyword3_val = str(pay_order_info.total_price)  # 订单总价
        keyword4_val = str(pay_order_info.order_number)  # 订单号
        # keyword5_val = ""
        # if pay_order_info.express_info:
        #     express_info = json.loads(pay_order_info.express_info)
        #     keyword5_val = str(express_info['address'])
        keyword5_val = str(pay_order_info.pay_time)  # 支付时间

        # 发送模板消息
        target_wechat = WeChatService()  # 创建 WeChatService 对象
        access_token = target_wechat.getAccessToken()  # 获取 Access Token
        headers = {'Content-Type': 'application/json'}  # 设置请求头
        url = f"https://api.weixin.qq.com/cgi-bin/message/wxopen/template/send?access_token={access_token}"  # 模板消息 API 地址

        # 构建请求参数
        params = {
            "touser": oauth_bind_info.openid,  # 接收者 OpenID
            "template_id": "dDImnvTa8WPgpgooqGyq2gJT61Y23H2Sk7TA7aZ-3U0",  # 模板 ID
            "page": "pages/my/order_list",  # 点击模板消息后跳转的页面
            "form_id": pay_order_info.prepay_id,  # 表单 ID (用于发送模板消息)
            "data": {
                "keyword1": {
                    "value": keyword1_val  # 订单备注
                },
                "keyword2": {
                    "value": keyword2_val  # 商品信息
                },
                "keyword3": {
                    "value": keyword3_val  # 订单金额
                },
                "keyword4": {
                    "value": keyword4_val  # 订单编号
                },
                "keyword5": {
                    "value": keyword5_val  # 支付时间
                }
            }
        }

        # 发送 POST 请求
        r = requests.post(url=url, data=json.dumps(params).encode('utf-8'), headers=headers)
        r.encoding = "utf-8"  # 设置编码
        app.logger.info(r.text)  # 记录响应信息
        return True  # 返回 True，表示任务处理成功