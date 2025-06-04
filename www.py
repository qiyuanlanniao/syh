# -*- coding: utf-8 -*-

'''
统一拦截器配置

本文件负责引入并注册各种拦截器，对请求进行预处理或后处理。
拦截器通常用于身份验证、权限控制、错误处理、日志记录等。
'''
from web.interceptors.ApiAuthInterceptor import *  # 导入 API 接口的认证拦截器
from web.interceptors.ErrorInterceptor import *  # 导入错误处理拦截器，用于捕获和处理全局异常
from web.interceptors.AuthInterceptor import *  # 导入用户认证拦截器，用于验证用户是否已登录

'''
蓝图功能注册

蓝图是一种组织Flask应用的机制，可以将相关的视图函数和其他代码组织到一起。
每个蓝图都可以定义自己的URL前缀，从而使代码更模块化和易于维护。
本段代码负责注册所有蓝图，并为它们指定相应的URL前缀。
'''
from web.controllers.account.Account import route_account  # 导入账户管理蓝图
from web.controllers.finance.Finance import route_finance  # 导入财务管理蓝图
from web.controllers.goods.Goods import route_goods  # 导入商品管理蓝图
from web.controllers.index import route_index  # 导入首页蓝图
from web.controllers.member.Member import route_member  # 导入会员管理蓝图
from web.controllers.stat.Stat import route_stat  # 导入统计管理蓝图
from web.controllers.static import route_static  # 导入静态资源蓝图，通常用于提供CSS、JavaScript、图片等
from web.controllers.user.User import route_user  # 导入用户管理蓝图
from web.controllers.api import route_api  # 导入 API 接口蓝图
from web.controllers.upload.Upload import route_upload  # 导入上传文件蓝图
from web.controllers.chart import route_chart  # 导入图表展示蓝图

# 注册蓝图，并指定URL前缀
# app 是 Flask 应用实例，这里假定它已经在其他地方创建并初始化
app.register_blueprint(route_index, url_prefix="/")  # 注册首页蓝图，根路径 "/"
app.register_blueprint(route_user, url_prefix="/user")  # 注册用户管理蓝图，URL前缀 "/user"
app.register_blueprint(route_static, url_prefix="/static")  # 注册静态资源蓝图，URL前缀 "/static"
app.register_blueprint(route_account, url_prefix="/account")  # 注册账户管理蓝图，URL前缀 "/account"
app.register_blueprint(route_finance, url_prefix="/finance")  # 注册财务管理蓝图，URL前缀 "/finance"
app.register_blueprint(route_goods, url_prefix="/goods")  # 注册商品管理蓝图，URL前缀 "/goods"
app.register_blueprint(route_member, url_prefix="/member")  # 注册会员管理蓝图，URL前缀 "/member"
app.register_blueprint(route_stat, url_prefix="/stat")  # 注册统计管理蓝图，URL前缀 "/stat"
app.register_blueprint(route_api, url_prefix="/api")  # 注册 API 接口蓝图，URL前缀 "/api"
app.register_blueprint(route_upload, url_prefix="/upload")  # 注册上传文件蓝图，URL前缀 "/upload"
app.register_blueprint(route_chart, url_prefix="/chart")  # 注册图表展示蓝图，URL前缀 "/chart"