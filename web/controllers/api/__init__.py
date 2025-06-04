# -*- coding: utf-8 -*-
from flask import Blueprint

# 创建一个名为 'api_page' 的 Blueprint 对象。
# Blueprint 是一种组织一组相关视图和其他代码的方式。
# __name__ 是 Flask 的标准用法，它将自动设置为模块的名称，
# 在这里是包含该 Blueprint 定义的文件名。
route_api = Blueprint('api_page', __name__)

# 导入 API 控制器模块。这些模块包含了实际处理 API 请求的函数。
# 每一个模块都对应一个业务领域，例如会员、商品、购物车等。
# 这样做的目的是为了组织和管理不同的 API 接口，提高代码的可维护性。

# 导入会员 API 控制器
from web.controllers.api.Member import *
# 导入商品 API 控制器
from web.controllers.api.Goods import *
# 导入购物车 API 控制器
from web.controllers.api.Cart import *
# 导入订单 API 控制器
from web.controllers.api.Order import *
# 导入个人中心 API 控制器
from web.controllers.api.My import *
# 导入地址 API 控制器
from web.controllers.api.Address import *


# 定义一个路由规则，将根路径 "/" 映射到 index() 函数。
# 当用户访问 API 的根路径时，例如 "/api/", 将会执行 index() 函数。
@route_api.route("/")
def index():
    #  返回一个字符串，表示 API 的版本信息。
    #  这通常用作 API 的欢迎信息，告知用户 API 已经启动并运行。
    return "Mina api V1.0~~"