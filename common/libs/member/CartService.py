# -*- coding: utf-8 -*-
from application import db  # 导入数据库连接对象，通常在 application.py 中定义
from common.libs.Helper import getCurrentDate  # 导入辅助函数，用于获取当前日期和时间
from common.models.member.MemberCart import MemberCart  # 导入会员购物车模型类

class CartService:
    """
    购物车服务类，提供对购物车数据的操作，例如删除购物车商品、设置购物车商品数量等。
    """

    @staticmethod
    def deleteItem(member_id=0, items=None):
        """
        根据会员ID和商品列表，从购物车中删除指定的商品。

        :param member_id: 会员ID，用于确定哪个会员的购物车。如果小于1，则认为无效。
        :param items: 商品列表，是一个包含要删除的商品信息的列表，每个商品信息应该包含 'id' 键，表示商品ID。如果为空，则认为无效。
        :return: True 删除成功，False 删除失败（通常是由于参数无效）。
        """
        if member_id < 1 or not items:
            return False  # 如果会员ID无效或商品列表为空，则返回 False，表示删除失败

        for item in items:
            # 遍历商品列表，根据商品ID和会员ID，从购物车表中删除对应的记录
            MemberCart.query.filter_by(goods_id=item['id'], member_id=member_id).delete()

        db.session.commit()  # 提交数据库更改，将删除操作持久化到数据库
        return True  # 返回 True，表示删除成功

    @staticmethod
    def setItems(member_id=0, goods_id=0, number=0):
        """
        设置购物车中指定商品的数量。如果商品已存在于购物车，则更新数量；如果商品不存在，则添加到购物车。

        :param member_id: 会员ID，用于确定哪个会员的购物车。如果小于1，则认为无效。
        :param goods_id: 商品ID，用于确定哪个商品。如果小于1，则认为无效。
        :param number: 商品数量，如果小于1，则认为无效。
        :return: True 设置成功，False 设置失败（通常是由于参数无效）。
        """
        if member_id < 1 or goods_id < 1 or number < 1:
            return False  # 如果会员ID、商品ID或数量无效，则返回 False，表示设置失败

        # 查询购物车中是否已存在该商品
        cart_info = MemberCart.query.filter_by(goods_id=goods_id, member_id=member_id).first()

        if cart_info:
            # 如果购物车中已存在该商品，则更新现有的购物车记录
            model_cart = cart_info
        else:
            # 如果购物车中不存在该商品，则创建新购物车记录
            model_cart = MemberCart()
            model_cart.member_id = member_id  # 设置会员ID
            model_cart.created_time = getCurrentDate()  # 设置创建时间

        model_cart.goods_id = goods_id  # 设置商品ID
        model_cart.quantity = number  # 设置商品数量
        model_cart.updated_time = getCurrentDate()  # 设置更新时间

        db.session.add(model_cart)  # 将购物车记录添加到数据库会话中
        db.session.commit()  # 提交数据库更改，将操作持久化到数据库
        return True  # 返回 True，表示设置成功