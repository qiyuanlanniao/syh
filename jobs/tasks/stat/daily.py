# -*- coding: utf-8 -*-

import random  # 导入random模块，用于生成随机数

from sqlalchemy import func  # 导入sqlalchemy的func模块，用于执行数据库函数如sum

from application import app, db  # 从application模块导入app和db对象，通常app是Flask应用实例，db是SQLAlchemy数据库实例
from common.libs.Helper import getFormatDate, getCurrentDate  # 从common.libs.Helper模块导入getFormatDate和getCurrentDate函数，用于格式化日期
from common.models.goods.GoodsSaleChangeLog import GoodsSaleChangeLog  # 导入GoodsSaleChangeLog模型类，表示商品销售变更日志
from common.models.goods.WxShareHistory import WxShareHistory  # 导入WxShareHistory模型类，表示微信分享历史
from common.models.member.Member import Member  # 导入Member模型类，表示会员信息
from common.models.pay.PayOrder import PayOrder  # 导入PayOrder模型类，表示支付订单信息
from common.models.stat.StatDailyGoods import StatDailyGoods  # 导入StatDailyGoods模型类，表示每日商品统计
from common.models.stat.StatDailyMember import StatDailyMember  # 导入StatDailyMember模型类，表示每日会员统计
from common.models.stat.StatDailySite import StatDailySite  # 导入StatDailySite模型类，表示每日站点统计

'''
python manager.py runjob -m stat/daily -a member|goods|site|test -p 2025-04-19

该代码段的用途：
用于执行每日统计任务，可以统计会员、商品、站点的数据。
通过命令行参数指定统计类型和日期。

-m stat/daily：指定运行的任务模块为stat/daily。
-a member|goods|site|test：指定要执行的动作，可以是member（会员统计）、goods（商品统计）、site（站点统计）或test（测试）。
-p 2025-04-19：指定统计的日期，格式为YYYY-MM-DD。
'''


class JobTask():
    """
    JobTask 类，用于执行统计任务。
    """

    def __init__(self):
        """
        初始化方法，目前为空。
        """
        pass

    def run(self, params):
        """
        运行任务的入口方法。

        Args:
            params (dict): 包含任务参数的字典，例如：
                {
                    'act': 'member',  # 动作类型，如 'member', 'goods', 'site', 'test'
                    'param': ['2025-04-19']  # 参数列表，通常是日期
                }
        """
        act = params['act'] if 'act' in params else ''  # 获取动作类型，如果不存在则默认为空字符串
        date = params['param'][0] if params['param'] and len(params['param']) else getFormatDate(
            format="%Y-%m-%d")  # 获取日期参数，如果不存在则使用当前日期
        if not act:  # 如果没有指定动作类型，则直接返回
            return

        date_from = date + " 00:00:00"  # 构造起始日期时间字符串
        date_to = date + " 23:59:59"  # 构造结束日期时间字符串
        func_params = {  # 构造包含动作类型和日期信息的字典
            'act': act,
            'date': date,
            'date_from': date_from,
            'date_to': date_to
        }
        with app.app_context():  # 激活应用程序上下文，确保可以访问Flask应用配置和数据库连接
            if act == "member":  # 如果动作类型是会员统计
                self.statMember(func_params)  # 调用会员统计方法
            elif act == "goods":  # 如果动作类型是商品统计
                self.statGoods(func_params)  # 调用商品统计方法
            elif act == "site":  # 如果动作类型是站点统计
                self.statSite(func_params)  # 调用站点统计方法
            elif act == "test":  # 如果动作类型是测试
                self.test()  # 调用测试方法

        app.logger.info("it's over~~")  # 记录任务完成的日志信息
        return

    '''
    会员统计
    '''

    def statMember(self, params):
        """
        会员统计方法。

        Args:
            params (dict): 包含统计参数的字典，包括：
                'act': 动作类型 (string)
                'date': 统计日期 (string)
                'date_from': 起始日期时间 (string)
                'date_to': 结束日期时间 (string)
        """
        act = params['act']  # 获取动作类型
        date = params['date']  # 获取统计日期
        date_from = params['date_from']  # 获取起始日期时间
        date_to = params['date_to']  # 获取结束日期时间
        app.logger.info(f"act:{act},from:{date_from},to:{date_to}")  # 记录日志信息

        member_list = Member.query.all()  # 查询所有会员信息
        if not member_list:  # 如果没有会员信息，则记录日志并返回
            app.logger.info("no member list")
            return

        for member_info in member_list:  # 遍历每个会员
            tmp_stat_member = StatDailyMember.query.filter_by(date=date,
                                                                member_id=member_info.id).first()  # 查询该会员当日的统计信息
            if tmp_stat_member:  # 如果存在该会员当日的统计信息，则更新该信息
                tmp_model_stat_member = tmp_stat_member
            else:  # 如果不存在该会员当日的统计信息，则创建新的统计信息
                tmp_model_stat_member = StatDailyMember()
                tmp_model_stat_member.date = date
                tmp_model_stat_member.member_id = member_info.id
                tmp_model_stat_member.created_time = getCurrentDate()

            tmp_stat_pay = db.session.query(func.sum(PayOrder.total_price).label("total_pay_money")) \
                .filter(PayOrder.member_id == member_info.id, PayOrder.status == 1) \
                .filter(PayOrder.created_time >= date_from, PayOrder.created_time <= date_to).first()  # 统计该会员在指定日期范围内的总支付金额

            tmp_stat_share_count = WxShareHistory.query.filter(PayOrder.member_id == member_info.id) \
                .filter(PayOrder.created_time >= date_from, PayOrder.created_time <= date_to).count()  # 统计该会员在指定日期范围内的分享次数

            tmp_model_stat_member.total_shared_count = tmp_stat_share_count  # 设置总分享次数
            tmp_model_stat_member.total_pay_money = tmp_stat_pay[0] if tmp_stat_pay[0] else 0.00  # 设置总支付金额
            '''
            为了测试效果模拟数据
            '''
            tmp_model_stat_member.total_shared_count = random.randint(50, 100)  # 模拟总分享次数
            tmp_model_stat_member.total_pay_money = random.randint(1000, 1010)  # 模拟总支付金额
            tmp_model_stat_member.updated_time = getCurrentDate()  # 更新更新时间
            db.session.add(tmp_model_stat_member)  # 添加或更新会员统计信息
            db.session.commit()  # 提交数据库事务

        return

    '''
    Goods统计
    '''

    def statGoods(self, params):
        """
        商品统计方法。

        Args:
            params (dict): 包含统计参数的字典，包括：
                'act': 动作类型 (string)
                'date': 统计日期 (string)
                'date_from': 起始日期时间 (string)
                'date_to': 结束日期时间 (string)
        """
        act = params['act']  # 获取动作类型
        date = params['date']  # 获取统计日期
        date_from = params['date_from']  # 获取起始日期时间
        date_to = params['date_to']  # 获取结束日期时间
        app.logger.info(f"act:{act},from:{date_from},to:{date_to}")  # 记录日志信息

        stat_goods_list = db.session.query(GoodsSaleChangeLog.goods_id,  # 查询商品销售变更日志的goods_id
                                          func.sum(GoodsSaleChangeLog.quantity).label("total_count"),  # 统计总数量
                                          func.sum(GoodsSaleChangeLog.price).label("total_pay_money")) \
            .filter(GoodsSaleChangeLog.created_time >= date_from, GoodsSaleChangeLog.created_time <= date_to) \
            .group_by(GoodsSaleChangeLog.goods_id).all()  # 按goods_id分组，统计每个商品的总数量和总支付金额

        if not stat_goods_list:  # 如果没有数据，则记录日志并返回
            app.logger.info("no data")
            return

        for item in stat_goods_list:  # 遍历每个商品的统计信息
            tmp_goods_id = item[0]  # 获取商品ID
            tmp_stat_goods = StatDailyGoods.query.filter_by(date=date,
                                                            goods_id=tmp_goods_id).first()  # 查询该商品当日的统计信息
            if tmp_stat_goods:  # 如果存在该商品当日的统计信息，则更新该信息
                tmp_model_stat_goods = tmp_stat_goods
            else:  # 如果不存在该商品当日的统计信息，则创建新的统计信息
                tmp_model_stat_goods = StatDailyGoods()
                tmp_model_stat_goods.date = date
                tmp_model_stat_goods.goods_id = tmp_goods_id
                tmp_model_stat_goods.created_time = getCurrentDate()

            tmp_model_stat_goods.total_count = item[1]  # 设置总数量
            tmp_model_stat_goods.total_pay_money = item[2]  # 设置总支付金额
            tmp_model_stat_goods.updated_time = getCurrentDate()  # 更新更新时间

            '''
            为了测试效果模拟数据
            '''
            tmp_model_stat_goods.total_count = random.randint(50, 100)  # 模拟总数量
            tmp_model_stat_goods.total_pay_money = random.randint(1000, 1010)  # 模拟总支付金额

            # db.session.add(tmp_model_stat_goods)
            # db.session.commit()
            try:
                db.session.add(tmp_model_stat_goods)  # 添加或更新商品统计信息
                db.session.commit()  # 提交数据库事务
            except Exception as e:  # 捕获异常，防止因数据问题导致程序崩溃
                db.session.rollback()  # 回滚事务
                app.logger.error(f"Error saving data: {e}")  # 记录错误日志

        return

    '''
    site统计
    '''

    def statSite(self, params):
        """
        站点统计方法。

        Args:
            params (dict): 包含统计参数的字典，包括：
                'act': 动作类型 (string)
                'date': 统计日期 (string)
                'date_from': 起始日期时间 (string)
                'date_to': 结束日期时间 (string)
        """
        act = params['act']  # 获取动作类型
        date = params['date']  # 获取统计日期
        date_from = params['date_from']  # 获取起始日期时间
        date_to = params['date_to']  # 获取结束日期时间
        app.logger.info(f"act:{act},from:{date_from},to:{date_to}")  # 记录日志信息

        stat_pay = db.session.query(func.sum(PayOrder.total_price).label("total_pay_money")) \
            .filter(PayOrder.status == 1) \
            .filter(PayOrder.created_time >= date_from, PayOrder.created_time <= date_to).first()  # 统计指定日期范围内的总支付金额

        stat_member_count = Member.query.count()  # 统计会员总数
        stat_new_member_count = Member.query.filter(Member.created_time >= date_from,
                                                    Member.created_time <= date_to).count()  # 统计指定日期范围内的新增会员数

        stat_order_count = PayOrder.query.filter_by(status=1) \
            .filter(PayOrder.created_time >= date_from, PayOrder.created_time <= date_to) \
            .count()  # 统计指定日期范围内的订单总数

        stat_share_count = WxShareHistory.query.filter(WxShareHistory.created_time >= date_from
                                                       , WxShareHistory.created_time <= date_to).count()  # 统计指定日期范围内的分享总数

        tmp_stat_site = StatDailySite.query.filter_by(date=date).first()  # 查询当日的站点统计信息
        if tmp_stat_site:  # 如果存在当日的站点统计信息，则更新该信息
            tmp_model_stat_site = tmp_stat_site
        else:  # 如果不存在当日的站点统计信息，则创建新的统计信息
            tmp_model_stat_site = StatDailySite()
            tmp_model_stat_site.date = date
            tmp_model_stat_site.created_time = getCurrentDate()

        tmp_model_stat_site.total_pay_money = stat_pay[0] if stat_pay[0] else 0.00  # 设置总支付金额
        tmp_model_stat_site.total_new_member_count = stat_new_member_count  # 设置新增会员数
        tmp_model_stat_site.total_member_count = stat_member_count  # 设置会员总数
        tmp_model_stat_site.total_order_count = stat_order_count  # 设置订单总数
        tmp_model_stat_site.total_shared_count = stat_share_count  # 设置分享总数
        tmp_model_stat_site.updated_time = getCurrentDate()  # 更新更新时间
        '''
        为了测试效果模拟数据
        '''
        tmp_model_stat_site.total_pay_money = random.randint(1000, 1010)  # 模拟总支付金额
        tmp_model_stat_site.total_new_member_count = random.randint(50, 100)  # 模拟新增会员数
        tmp_model_stat_site.total_member_count += tmp_model_stat_site.total_new_member_count  # 模拟会员总数
        tmp_model_stat_site.total_order_count = random.randint(900, 1000)  # 模拟订单总数
        tmp_model_stat_site.total_shared_count = random.randint(1000, 2000)  # 模拟分享总数
        db.session.add(tmp_model_stat_site)  # 添加或更新站点统计信息
        db.session.commit()  # 提交数据库事务

    def test(self):
        """
        测试方法，用于生成测试数据并进行统计。
        """
        import datetime  # 导入datetime模块，用于处理日期和时间
        from common.libs.Helper import getFormatDate  # 从common.libs.Helper模块导入getFormatDate函数，用于格式化日期
        now = datetime.datetime.now()  # 获取当前时间
        for i in reversed(range(1, 30)):  # 循环30天，从昨天开始到一个月前
            date_before = now + datetime.timedelta(days=-i)  # 计算指定日期
            date = getFormatDate(date=date_before, format="%Y-%m-%d")  # 格式化日期
            tmp_params = {  # 构造参数字典
                'act': 'test',
                'date': date,
                'date_from': date + " 00:00:00",
                'date_to': date + " 23:59:59"
            }
            self.testGoods(date)  # 生成测试商品销售数据
            self.statGoods(tmp_params)  # 统计商品数据
            self.statMember(tmp_params)  # 统计会员数据
            self.statSite(tmp_params)  # 统计站点数据

    def testGoods(self, date):
        """
        生成测试商品销售数据。

        Args:
            date (string): 日期，格式为YYYY-MM-DD。
        """
        from common.models.goods.Goods import Goods  # 导入Goods模型类，表示商品信息
        list = Goods.query.all()  # 查询所有商品信息
        if list:  # 如果存在商品信息
            for item in list:  # 遍历每个商品
                model = GoodsSaleChangeLog()  # 创建商品销售变更日志模型
                model.goods_id = item.id  # 设置商品ID
                model.quantity = random.randint(1, 10)  # 随机生成销售数量
                model.price = model.quantity * item.price  # 计算销售价格
                model.member_id = 1  # 设置会员ID
                model.created_time = date + " " + getFormatDate(format="%H:%M:%S")  # 设置创建时间
                db.session.add(model)  # 添加商品销售变更日志
                db.session.commit()  # 提交数据库事务