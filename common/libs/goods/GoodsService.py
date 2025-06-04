# -*- coding: utf-8 -*-
from application import db  # 导入 application.py 中定义的数据库对象 db
from common.libs.Helper import getCurrentDate  # 导入自定义的辅助函数 getCurrentDate，用于获取当前日期
from common.models.goods.Goods import Goods  # 导入 Goods 模型类，用于操作 goods 表
from common.models.goods.GoodsStockChangeLog import GoodsStockChangeLog  # 导入 GoodsStockChangeLog 模型类，用于操作 goods_stock_change_log 表


class GoodsService:
    """
    GoodsService 类，提供与商品相关的业务逻辑方法。
    """

    @staticmethod
    def setStockChangeLog(goods_id=0, quantity=0, note=''):
        """
        记录商品库存变更日志。

        Args:
            goods_id (int): 商品 ID，必须大于 0。
            quantity (int): 变更数量，必须大于 0。表示本次入库或出库的数量。
            note (str): 备注信息，可选。例如，可以记录操作原因、操作人等。

        Returns:
            bool: True 表示记录成功，False 表示记录失败。
        """

        # 参数校验，确保 goods_id 和 quantity 的有效性。
        if goods_id < 1 or quantity < 1:
            return False  # goods_id 或 quantity 无效，返回 False

        # 查询食品信息，确保 goods_id 对应的食品存在。
        goods_info = Goods.query.filter_by(id=goods_id).first()
        if not goods_info:
            return False  # goods_id 对应的食品不存在，返回 False

        # 创建 GoodsStockChangeLog 对象，并设置相关属性。
        model_stock_change = GoodsStockChangeLog()  # 实例化 GoodsStockChangeLog 模型

        model_stock_change.goods_id = goods_id  # 设置食品 ID
        model_stock_change.unit = quantity  # 设置变更数量
        model_stock_change.total_stock = goods_info.stock  # 设置变更前的总库存量，从Goods表中读取当前库存
        model_stock_change.note = note  # 设置备注信息
        model_stock_change.created_time = getCurrentDate()  # 设置创建时间

        # 将 GoodsStockChangeLog 对象添加到数据库会话，并提交更改。
        db.session.add(model_stock_change)  # 将对象添加到数据库会话
        db.session.commit()  # 提交数据库会话，将更改保存到数据库

        return True  # 记录成功，返回 True