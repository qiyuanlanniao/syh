# -*- coding: utf-8 -*-
import bcrypt
import requests

from application import app


class MemberService():
    @staticmethod
    def geneAuthCode(member_info=None):
        # 将用户信息的各个部分组合成一个字符串
        raw_string = f"{member_info.id}-{member_info.salt}-{member_info.status}"

        # 将字符串编码为字节串
        raw_bytes = raw_string.encode("utf-8")
        member_salt = member_info.salt.encode('utf-8')
        hashed_bytes = bcrypt.hashpw(raw_bytes, member_salt)

        # 将字节串解码为字符串
        return hashed_bytes.decode("utf-8")

    @staticmethod
    def geneSalt():
        return bcrypt.gensalt()

    @staticmethod
    def getWeChatOpenId(code):
        url = 'https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}&grant_type=authorization_code'.format(
            app.config['MINA_APP']['appid'], app.config['MINA_APP']['app_secret'], code)
        res = requests.get(url).json()
        openid = None
        if 'openid' in res:
            openid = res['openid']
        return openid

