# -*- coding: utf-8 -*-
import datetime

from flask import Blueprint

from common.libs.Helper import getFormatDate  # 导入自定义的日期格式化函数
from common.libs.Helper import ops_render  # 导入自定义的渲染函数，用于渲染模板
from common.models.stat.StatDailySite import StatDailySite  # 导入每日网站统计数据模型

# 第一个参数 'index_page' 是 Blueprint 的名称，第二个参数 __name__ 是模块的名称。
route_index = Blueprint('index_page', __name__)


# 定义一个路由，当用户访问根路径 "/" 时，会执行 index 函数。
@route_index.route("/")
def index():
    # 初始化响应数据，用于存储从数据库查询到的统计数据。
    resp_data = {
        'data': {
            'finance': {  # 财务数据
                'today': 0,  # 今日支付金额
                'month': 0  # 本月支付金额
            },
            'member': {  # 会员数据
                'today_new': 0,  # 今日新增会员数
                'month_new': 0,  # 本月新增会员数
                'total': 0  # 总会员数
            },
            'order': {  # 订单数据
                'today': 0,  # 今日订单数
                'month': 0  # 本月订单数
            },
            'shared': {  # 分享数据
                'today': 0,  # 今日分享数
                'month': 0  # 本月分享数
            },
        }
    }

    # 获取当前日期和时间
    now = datetime.datetime.now()
    # 计算30天前的日期
    date_before_30days = now + datetime.timedelta(days=-30)
    # 将30天前的日期格式化为 "YYYY-MM-DD" 格式
    date_from = getFormatDate(date=date_before_30days, format="%Y-%m-%d")
    # 将当前日期格式化为 "YYYY-MM-DD" 格式
    date_to = getFormatDate(date=now, format="%Y-%m-%d")

    # 从 StatDailySite 模型中查询指定日期范围内的数据，并按照 id 升序排列。
    # all() 表示获取所有查询结果。
    list = StatDailySite.query.filter(StatDailySite.date >= date_from) \
        .filter(StatDailySite.date <= date_to).order_by(StatDailySite.id.asc()) \
        .all()
    data = resp_data['data']  # 获取响应数据中的 data 部分

    # 如果查询结果不为空，则遍历结果集，并更新 resp_data 中的数据。
    if list:

        for item in list:
            data['finance']['month'] += item.total_pay_money  # 累加本月支付金额
            data['member']['month_new'] += item.total_new_member_count  # 累加本月新增会员数
            data['member']['total'] = item.total_member_count  # 更新总会员数
            data['order']['month'] += item.total_order_count  # 累加本月订单数
            data['shared']['month'] += item.total_shared_count  # 累加本月分享数
            # 判断当前日期是否为今天
            if getFormatDate(date=item.date, format="%Y-%m-%d") == date_to:
                data['finance']['today'] = item.total_pay_money  # 设置今日支付金额
                data['member']['today_new'] = item.total_new_member_count  # 设置今日新增会员数
                data['order']['today'] = item.total_order_count  # 设置今日订单数
                data['shared']['today'] = item.total_shared_count  # 设置今日分享数

    # ops_render 函数负责将数据渲染到 HTML 模板中，并返回一个 HTTP 响应。
    return ops_render("index/index.html", resp_data)