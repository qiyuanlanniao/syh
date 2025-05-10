# -*- coding: utf-8 -*-
SERVER_PORT = 8999
DEBUG = True
SQLALCHEMY_ECHO = False

JSON_AS_ASCII = False  # json数据中文显示正确

AUTH_COOKIE_NAME = "mooc_food"

# 过滤url
IGNORE_URLS = [
    "^/user/login"
]

IGNORE_CHECK_LOGIN_URLS = [
    "^/static",
    "^/favicon.ico"
]

API_IGNORE_URLS = [
    "^/api"
]

PAGE_SIZE = 50
PAGE_DISPLAY = 10

STATUS_MAPPING = {
    "1": "正常",
    "0": "已删除"
}

MINA_APP = {
    # "app_id": "wx9fa4464ca9da2086",
    "appid": "wx64f3ca472d535f45",
    # "app_secret": "08413cc5e6f4f7fb58f773d94e06425e",
    "app_secret": "87780bea75efdec73060db5ca584d727",
    "paykey": "b71db6f9098623fed71d57e311b35734",
    "mch_id": "1715360269",
    "callback_url": "/api/order/callback"
}

UPLOAD = {
    'ext': ['jpg', 'gif', 'bmp', 'jpeg', 'png'],
    'prefix_path': '/web/static/upload/',
    'prefix_url': '/static/upload/'
}

APP = {
    'domain': 'http://192.168.43.25:8999',
    'ngrok_domain': "https://9b38-123-147-245-156.ngrok-free.app"
}

PAY_STATUS_MAPPING = {
    "1": "已支付",
    "-8": "待支付",
    "0": "已关闭"
}

PAY_STATUS_DISPLAY_MAPPING = {
    "0": "订单关闭",
    "1": "支付成功",
    "-8": "待支付",
    "-7": "待发货",
    "-6": "待确认",
    "-5": "待评价"
}
