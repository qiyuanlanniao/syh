# -*- coding: utf-8 -*-
from common.models.pay.PayOrder import  PayOrder  # 导入支付订单模型
from common.libs.Helper import getFormatDate # 导入 Helper 类中的 getFormatDate 函数，用于格式化日期
from common.libs.pay.PayService import PayService # 导入支付服务类
import datetime # 导入 datetime 模块，用于处理日期和时间
from application import app,db # 导入 application 模块中的 app 和 db 对象，app 是 Flask 应用实例，db 是 SQLAlchemy 数据库实例
'''
python manager.py runjob -m pay/index
这段注释说明了如何运行这个任务。
通过执行 `python manager.py runjob -m pay/index` 命令来调用 `pay/index` 模块下的 JobTask 类的 run 方法。
manager.py 是 Flask 应用的入口脚本，runjob 命令用于执行特定的后台任务。
'''

class JobTask():
	"""
	定时关闭未支付订单的任务类
	"""
	def __init__(self):
		"""
		初始化方法
		"""
		pass # 目前没有需要初始化的内容

	def run(self,params):
		"""
		任务执行方法
		:param params:  从命令行传递过来的参数，这里未使用
		"""
		now = datetime.datetime.now() # 获取当前时间
		date_before_30min = now + datetime.timedelta( minutes = -30 ) # 计算 30 分钟之前的时间
		# 查询状态为 -8 (待支付) 并且创建时间早于 30 分钟之前的订单
		list = PayOrder.query.filter_by( status = -8 ).\
			filter( PayOrder.created_time <= getFormatDate( date = date_before_30min ) ).all()
		# PayOrder.query: 从数据库查询 PayOrder 表
		# .filter_by( status = -8 ):  过滤状态为 -8 的订单，-8 通常代表待支付状态
		# .filter( PayOrder.created_time <= getFormatDate( date = date_before_30min ) ): 过滤创建时间早于 30 分钟之前的订单
		# .all(): 获取所有符合条件的订单列表

		if not list:
			app.logger.info("no data~~") # 如果没有找到符合条件的订单，记录日志信息
			return # 结束任务执行

		pay_target = PayService() # 创建 PayService 类的实例，用于处理支付相关的操作
		for item in list: # 遍历符合条件的订单列表
			pay_target.closeOrder( pay_order_id = item.id ) # 调用 PayService 类的 closeOrder 方法关闭订单
		# pay_order_id = item.id：指定要关闭的订单的 ID

		app.logger.info("it's over~~") # 记录任务完成的日志信息