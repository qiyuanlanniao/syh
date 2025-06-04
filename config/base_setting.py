# -*- coding: utf-8 -*-
SERVER_PORT = 8999
DEBUG = True
SQLALCHEMY_ECHO = False

JSON_AS_ASCII = False  # json数据中文显示正确

AUTH_COOKIE_NAME = ""

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
    "appid": "",
    "app_secret": "",
    "paykey": "",
    "mch_id": "",
    "callback_url": "/api/order/callback"
}

UPLOAD = {
    'ext': ['jpg', 'gif', 'bmp', 'jpeg', 'png'],
    'prefix_path': '/web/static/upload/',
    'prefix_url': '/static/upload/'
}

APP = {
    'domain': '',
    'ngrok_domain': "" # 每次调试都要更改
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
