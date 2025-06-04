# -*- coding: utf-8 -*-
import datetime

from flask import Blueprint, request

from application import app  # 导入Flask应用实例
from common.libs.Helper import getFormatDate, iPagination, getDictFilterField, selectFilterObj  # 导入自定义辅助函数
from common.libs.Helper import ops_render  # 导入渲染函数
from common.models.goods.Goods import Goods  # 导入商品模型
from common.models.member.Member import Member  # 导入会员模型
from common.models.stat.StatDailyGoods import StatDailyGoods  # 导入每日商品统计模型
from common.models.stat.StatDailyMember import StatDailyMember  # 导入每日会员统计模型
from common.models.stat.StatDailySite import StatDailySite  # 导入每日站点统计模型

route_stat = Blueprint('stat_page', __name__)  # 创建一个蓝图，用于组织统计相关的路由


@route_stat.route("/index")
def index():
    """
    站点统计首页
    :return: 渲染后的HTML页面
    """
    now = datetime.datetime.now()  # 获取当前时间
    date_before_30days = now + datetime.timedelta(days=-30)  # 计算30天前的日期
    default_date_from = getFormatDate(date=date_before_30days, format="%Y-%m-%d")  # 格式化30天前的日期为YYYY-MM-DD
    default_date_to = getFormatDate(date=now, format="%Y-%m-%d")  # 格式化当前日期为YYYY-MM-DD

    resp_data = {}  # 初始化响应数据字典
    req = request.values  # 获取请求参数
    page = int(req['p']) if ('p' in req and req['p']) else 1  # 获取当前页码，如果请求参数中没有'p'或者'p'为空，则默认为1
    date_from = req['date_from'] if 'date_from' in req else default_date_from  # 获取起始日期，如果请求参数中没有'date_from'，则使用默认的30天前的日期
    date_to = req['date_to'] if 'date_to' in req else default_date_to  # 获取结束日期，如果请求参数中没有'date_to'，则使用默认的当前日期

    # 构建查询，筛选指定日期范围内的每日站点统计数据
    query = StatDailySite.query.filter(StatDailySite.date >= date_from) \
        .filter(StatDailySite.date <= date_to)

    # 构建分页参数
    page_params = {
        'total': query.count(),  # 总记录数
        'page_size': app.config['PAGE_SIZE'],  # 每页显示的记录数，从应用配置中获取
        'page': page,  # 当前页码
        'display': app.config['PAGE_DISPLAY'],  # 显示的页码数量，从应用配置中获取
        'url': request.full_path.replace("&p={}".format(page), "")  # 构建分页URL，移除当前页码参数
    }

    pages = iPagination(page_params)  # 创建分页对象
    offset = (page - 1) * app.config['PAGE_SIZE']  # 计算偏移量

    # 查询指定范围的数据，并按id降序排列
    list = query.order_by(StatDailySite.id.desc()).offset(offset).limit(app.config['PAGE_SIZE']).all()

    resp_data['list'] = list  # 将查询结果添加到响应数据中
    resp_data['pages'] = pages  # 将分页对象添加到响应数据中
    resp_data['current'] = 'index'  # 设置当前页面标识为'index'
    resp_data['search_con'] = {  # 将搜索条件添加到响应数据中
        'date_from': date_from,
        'date_to': date_to
    }
    return ops_render("stat/index.html", resp_data)  # 渲染模板并返回响应


@route_stat.route("/goods")
def goods():
    """
    商品统计页面
    :return: 渲染后的HTML页面
    """
    now = datetime.datetime.now()  # 获取当前时间
    date_before_30days = now + datetime.timedelta(days=-30)  # 计算30天前的日期
    default_date_from = getFormatDate(date=date_before_30days, format="%Y-%m-%d")  # 格式化30天前的日期为YYYY-MM-DD
    default_date_to = getFormatDate(date=now, format="%Y-%m-%d")  # 格式化当前日期为YYYY-MM-DD

    resp_data = {}  # 初始化响应数据字典
    req = request.values  # 获取请求参数
    page = int(req['p']) if ('p' in req and req['p']) else 1  # 获取当前页码，如果请求参数中没有'p'或者'p'为空，则默认为1
    date_from = req['date_from'] if 'date_from' in req else default_date_from  # 获取起始日期，如果请求参数中没有'date_from'，则使用默认的30天前的日期
    date_to = req['date_to'] if 'date_to' in req else default_date_to  # 获取结束日期，如果请求参数中没有'date_to'，则使用默认的当前日期

    # 构建查询，筛选指定日期范围内的每日商品统计数据
    query = StatDailyGoods.query.filter(StatDailyGoods.date >= date_from) \
        .filter(StatDailyGoods.date <= date_to)

    # 构建分页参数
    page_params = {
        'total': query.count(),  # 总记录数
        'page_size': app.config['PAGE_SIZE'],  # 每页显示的记录数，从应用配置中获取
        'page': page,  # 当前页码
        'display': app.config['PAGE_DISPLAY'],  # 显示的页码数量，从应用配置中获取
        'url': request.full_path.replace("&p={}".format(page), "")  # 构建分页URL，移除当前页码参数
    }

    pages = iPagination(page_params)  # 创建分页对象
    offset = (page - 1) * app.config['PAGE_SIZE']  # 计算偏移量

    # 查询指定范围的数据，并按id降序排列
    list = query.order_by(StatDailyGoods.id.desc()).offset(offset).limit(app.config['PAGE_SIZE']).all()
    date_list = []  # 用于存储处理后的数据列表

    if list:
        # 获取商品ID列表，从查询结果中提取goods_id
        goods_map = getDictFilterField(Goods, Goods.id, "id", selectFilterObj(list, "goods_id"))  # 根据商品ID从Goods模型中获取商品信息
        for item in list:  # 遍历查询结果
            tmp_goods_info = goods_map[item.goods_id] if item.goods_id in goods_map else {}  # 根据goods_id从商品信息映射中获取商品信息
            tmp_data = {  # 构建临时数据字典
                "date": item.date,  # 日期
                "total_count": item.total_count,  # 总销量
                "total_pay_money": item.total_pay_money,  # 总支付金额
                'goods_info': tmp_goods_info  # 商品信息
            }
            date_list.append(tmp_data)  # 将临时数据添加到数据列表中

    resp_data['list'] = date_list  # 将处理后的数据列表添加到响应数据中
    resp_data['pages'] = pages  # 将分页对象添加到响应数据中
    resp_data['current'] = 'goods'  # 设置当前页面标识为'goods'
    resp_data['search_con'] = {  # 将搜索条件添加到响应数据中
        'date_from': date_from,
        'date_to': date_to
    }
    return ops_render("stat/goods.html", resp_data)  # 渲染模板并返回响应


@route_stat.route("/member")
def memebr():
    """
    会员统计页面
    :return: 渲染后的HTML页面
    """
    now = datetime.datetime.now()  # 获取当前时间
    date_before_30days = now + datetime.timedelta(days=-30)  # 计算30天前的日期
    default_date_from = getFormatDate(date=date_before_30days, format="%Y-%m-%d")  # 格式化30天前的日期为YYYY-MM-DD
    default_date_to = getFormatDate(date=now, format="%Y-%m-%d")  # 格式化当前日期为YYYY-MM-DD

    resp_data = {}  # 初始化响应数据字典
    req = request.values  # 获取请求参数
    page = int(req['p']) if ('p' in req and req['p']) else 1  # 获取当前页码，如果请求参数中没有'p'或者'p'为空，则默认为1
    date_from = req['date_from'] if 'date_from' in req else default_date_from  # 获取起始日期，如果请求参数中没有'date_from'，则使用默认的30天前的日期
    date_to = req['date_to'] if 'date_to' in req else default_date_to  # 获取结束日期，如果请求参数中没有'date_to'，则使用默认的当前日期

    # 构建查询，筛选指定日期范围内的每日会员统计数据
    query = StatDailyMember.query.filter(StatDailyMember.date >= date_from) \
        .filter(StatDailyMember.date <= date_to)

    # 构建分页参数
    page_params = {
        'total': query.count(),  # 总记录数
        'page_size': app.config['PAGE_SIZE'],  # 每页显示的记录数，从应用配置中获取
        'page': page,  # 当前页码
        'display': app.config['PAGE_DISPLAY'],  # 显示的页码数量，从应用配置中获取
        'url': request.full_path.replace("&p={}".format(page), "")  # 构建分页URL，移除当前页码参数
    }

    pages = iPagination(page_params)  # 创建分页对象
    offset = (page - 1) * app.config['PAGE_SIZE']  # 计算偏移量

    # 查询指定范围的数据，并按id降序排列
    list = query.order_by(StatDailyMember.id.desc()).offset(offset).limit(app.config['PAGE_SIZE']).all()
    date_list = []  # 用于存储处理后的数据列表

    if list:
        # 获取会员ID列表，从查询结果中提取member_id
        member_map = getDictFilterField(Member, Member.id, "id", selectFilterObj(list, "member_id"))  # 根据会员ID从Member模型中获取会员信息
        for item in list:  # 遍历查询结果
            tmp_member_info = member_map[item.member_id] if item.member_id in member_map else {}  # 根据member_id从会员信息映射中获取会员信息
            tmp_data = {  # 构建临时数据字典
                "date": item.date,  # 日期
                "total_pay_money": item.total_pay_money,  # 总支付金额
                "total_shared_count": item.total_shared_count,  # 总分享次数
                'member_info': tmp_member_info  # 会员信息
            }
            date_list.append(tmp_data)  # 将临时数据添加到数据列表中

    resp_data['list'] = date_list  # 将处理后的数据列表添加到响应数据中
    resp_data['pages'] = pages  # 将分页对象添加到响应数据中
    resp_data['current'] = 'member'  # 设置当前页面标识为'member'
    resp_data['search_con'] = {  # 将搜索条件添加到响应数据中
        'date_from': date_from,
        'date_to': date_to
    }
    return ops_render("stat/member.html", resp_data)  # 渲染模板并返回响应


@route_stat.route("/share")
def share():
    """
    分享统计页面
    :return: 渲染后的HTML页面
    """
    now = datetime.datetime.now()  # 获取当前时间
    date_before_30days = now + datetime.timedelta(days=-30)  # 计算30天前的日期
    default_date_from = getFormatDate(date=date_before_30days, format="%Y-%m-%d")  # 格式化30天前的日期为YYYY-MM-DD
    default_date_to = getFormatDate(date=now, format="%Y-%m-%d")  # 格式化当前日期为YYYY-MM-DD

    resp_data = {}  # 初始化响应数据字典
    req = request.values  # 获取请求参数
    page = int(req['p']) if ('p' in req and req['p']) else 1  # 获取当前页码，如果请求参数中没有'p'或者'p'为空，则默认为1
    date_from = req['date_from'] if 'date_from' in req else default_date_from  # 获取起始日期，如果请求参数中没有'date_from'，则使用默认的30天前的日期
    date_to = req['date_to'] if 'date_to' in req else default_date_to  # 获取结束日期，如果请求参数中没有'date_to'，则使用默认的当前日期

    # 构建查询，筛选指定日期范围内的每日站点统计数据
    query = StatDailySite.query.filter(StatDailySite.date >= date_from) \
        .filter(StatDailySite.date <= date_to)

    # 构建分页参数
    page_params = {
        'total': query.count(),  # 总记录数
        'page_size': app.config['PAGE_SIZE'],  # 每页显示的记录数，从应用配置中获取
        'page': page,  # 当前页码
        'display': app.config['PAGE_DISPLAY'],  # 显示的页码数量，从应用配置中获取
        'url': request.full_path.replace("&p={}".format(page), "")  # 构建分页URL，移除当前页码参数
    }

    pages = iPagination(page_params)  # 创建分页对象
    offset = (page - 1) * app.config['PAGE_SIZE']  # 计算偏移量

    # 查询指定范围的数据，并按id降序排列
    list = query.order_by(StatDailySite.id.desc()).offset(offset).limit(app.config['PAGE_SIZE']).all()
    resp_data['list'] = list  # 将查询结果添加到响应数据中
    resp_data['pages'] = pages  # 将分页对象添加到响应数据中
    resp_data['current'] = 'goods'  # 设置当前页面标识为'goods'，这里可能有误，应该是'share'
    resp_data['search_con'] = {  # 将搜索条件添加到响应数据中
        'date_from': date_from,
        'date_to': date_to
    }
    return ops_render("stat/share.html", resp_data)  # 渲染模板并返回响应