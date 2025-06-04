# -*- coding: utf-8 -*-
import datetime

from flask import Blueprint, jsonify

from common.libs.Helper import getFormatDate  # 导入自定义的Helper类，其中包含日期格式化函数
from common.models.stat.StatDailySite import StatDailySite  # 导入每日站点统计模型

# 创建一个名为 'chart_page' 的 Blueprint 对象，用于组织和管理相关的路由
route_chart = Blueprint('chart_page', __name__)


# 定义一个路由，用于获取dashboard数据
@route_chart.route("/dashboard")
def dashboard():
    """
    获取近30天的会员总数和订单总数的统计数据，并返回JSON格式的数据，用于dashboard展示。
    """
    now = datetime.datetime.now()  # 获取当前时间
    date_before_30days = now + datetime.timedelta(days=-30)  # 计算30天前的日期
    date_from = getFormatDate(date=date_before_30days, format="%Y-%m-%d")  # 将30天前的日期格式化为 YYYY-MM-DD 格式的字符串
    date_to = getFormatDate(date=now, format="%Y-%m-%d")  # 将当前日期格式化为 YYYY-MM-DD 格式的字符串

    # 从 StatDailySite 模型中查询日期在 date_from 和 date_to 之间的所有记录，并按照 id 升序排列
    list = StatDailySite.query.filter(StatDailySite.date >= date_from) \
        .filter(StatDailySite.date <= date_to).order_by(StatDailySite.id.asc()) \
        .all()

    resp = {'code': 200, 'msg': '操作成功~~', 'data': {}}  # 初始化返回结果，包含状态码，消息和数据部分
    data = {
        "categories": [],  # 用于存储日期分类
        "series": [  # 用于存储序列数据，这里包含会员总数和订单总数
            {
                "name": "会员总数",  # 序列名称
                "data": []  # 存储会员总数的数据
            },
            {
                "name": "订单总数",  # 序列名称
                "data": []  # 存储订单总数的数据
            },
        ]
    }

    # 如果查询结果不为空
    if list:
        # 遍历查询结果
        for item in list:
            data['categories'].append(getFormatDate(date=item.date, format="%Y-%m-%d"))  # 将日期添加到分类列表中
            data['series'][0]['data'].append(item.total_member_count)  # 将会员总数添加到会员总数序列中
            data['series'][1]['data'].append(item.total_order_count)  # 将订单总数添加到订单总数序列中

    resp['data'] = data  # 将处理后的数据添加到返回结果中
    return jsonify(resp)  # 将返回结果转换为 JSON 格式并返回


# 定义一个路由，用于获取财务数据
@route_chart.route("/finance")
def finance():
    """
    获取近30天的每日营收报表数据，并返回JSON格式的数据，用于财务报表展示。
    """
    now = datetime.datetime.now()  # 获取当前时间
    date_before_30days = now + datetime.timedelta(days=-30)  # 计算30天前的日期
    date_from = getFormatDate(date=date_before_30days, format="%Y-%m-%d")  # 将30天前的日期格式化为 YYYY-MM-DD 格式的字符串
    date_to = getFormatDate(date=now, format="%Y-%m-%d")  # 将当前日期格式化为 YYYY-MM-DD 格式的字符串

    # 从 StatDailySite 模型中查询日期在 date_from 和 date_to 之间的所有记录，并按照 id 升序排列
    list = StatDailySite.query.filter(StatDailySite.date >= date_from) \
        .filter(StatDailySite.date <= date_to).order_by(StatDailySite.id.asc()) \
        .all()

    resp = {'code': 200, 'msg': '操作成功~~', 'data': {}}  # 初始化返回结果，包含状态码，消息和数据部分
    data = {
        "categories": [],  # 用于存储日期分类
        "series": [  # 用于存储序列数据，这里包含日营收报表
            {
                "name": "日营收报表",  # 序列名称
                "data": []  # 存储日营收报表的数据
            }
        ]
    }

    # 如果查询结果不为空
    if list:
        # 遍历查询结果
        for item in list:
            data['categories'].append(getFormatDate(date=item.date, format="%Y-%m-%d"))  # 将日期添加到分类列表中
            data['series'][0]['data'].append(float(item.total_pay_money))  # 将日营收添加到日营收报表序列中, 强制转换成float类型

    resp['data'] = data  # 将处理后的数据添加到返回结果中
    return jsonify(resp)  # 将返回结果转换为 JSON 格式并返回


# 定义一个路由，用于获取分享数据
@route_chart.route("/share")
def share():
    """
    获取近30天的每日分享统计数据，并返回JSON格式的数据，用于分享数据展示。
    """
    now = datetime.datetime.now()  # 获取当前时间
    date_before_30days = now + datetime.timedelta(days=-30)  # 计算30天前的日期
    date_from = getFormatDate(date=date_before_30days, format="%Y-%m-%d")  # 将30天前的日期格式化为 YYYY-MM-DD 格式的字符串
    date_to = getFormatDate(date=now, format="%Y-%m-%d")  # 将当前日期格式化为 YYYY-MM-DD 格式的字符串

    # 从 StatDailySite 模型中查询日期在 date_from 和 date_to 之间的所有记录，并按照 id 升序排列
    list = StatDailySite.query.filter(StatDailySite.date >= date_from) \
        .filter(StatDailySite.date <= date_to).order_by(StatDailySite.id.asc()) \
        .all()

    resp = {'code': 200, 'msg': '操作成功~~', 'data': {}}  # 初始化返回结果，包含状态码，消息和数据部分
    data = {
        "categories": [],  # 用于存储日期分类
        "series": [  # 用于存储序列数据，这里包含日分享数据
            {
                "name": "日分享",  # 序列名称
                "data": []  # 存储日分享数据
            }
        ]
    }

    # 如果查询结果不为空
    if list:
        # 遍历查询结果
        for item in list:
            data['categories'].append(getFormatDate(date=item.date, format="%Y-%m-%d"))  # 将日期添加到分类列表中
            data['series'][0]['data'].append(item.total_shared_count)  # 将日分享数添加到日分享序列中

    resp['data'] = data  # 将处理后的数据添加到返回结果中
    return jsonify(resp)  # 将返回结果转换为 JSON 格式并返回