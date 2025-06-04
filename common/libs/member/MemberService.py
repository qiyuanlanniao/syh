# -*- coding: utf-8 -*-
import bcrypt  # 导入bcrypt库，用于密码哈希和加盐
import requests  # 导入requests库，用于发送HTTP请求

from application import app  # 从application模块导入app对象，通常是Flask应用实例


class MemberService():
    """
    会员服务类，提供会员相关的业务逻辑，例如生成认证码、生成盐值、获取微信OpenID等。
    """

    @staticmethod
    def geneAuthCode(member_info=None):
        """
        生成认证码。

        Args:
            member_info (object, optional): 会员信息对象，包含id、salt、status等属性. Defaults to None.

        Returns:
            str: 生成的认证码字符串。
        """
        # 将用户信息的各个部分组合成一个字符串，用于生成认证码的原始字符串
        raw_string = f"{member_info.id}-{member_info.salt}-{member_info.status}"

        # 将字符串编码为字节串，以便进行哈希运算
        raw_bytes = raw_string.encode("utf-8")
        member_salt = member_info.salt.encode('utf-8') # 获取会员的盐值，并编码为字节串
        hashed_bytes = bcrypt.hashpw(raw_bytes, member_salt) # 使用bcrypt库的hashpw函数进行哈希运算，将原始字节串与盐值结合生成哈希值

        # 将字节串解码为字符串，以便存储和传输
        return hashed_bytes.decode("utf-8")

    @staticmethod
    def geneSalt():
        """
        生成盐值。

        Returns:
            bytes: 生成的盐值字节串。
        """
        return bcrypt.gensalt()  # 使用bcrypt库的gensalt函数生成一个随机的盐值

    @staticmethod
    def getWeChatOpenId(code):
        """
        通过微信code获取微信OpenID。

        Args:
            code (str): 微信授权返回的code。

        Returns:
            str: 微信OpenID，如果获取失败则返回None。
        """
        # 构建微信接口URL，其中包含appid、app_secret、code和grant_type等参数
        url = 'https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}&grant_type=authorization_code'.format(
            app.config['MINA_APP']['appid'], app.config['MINA_APP']['app_secret'], code) # 从app.config中获取小程序的相关配置信息

        # 发送GET请求到微信接口，并解析返回的JSON数据
        res = requests.get(url).json()

        # 提取OpenID，如果存在则返回，否则返回None
        openid = None
        if 'openid' in res:
            openid = res['openid']
        return openid