# -*- coding: utf-8 -*-
import datetime  # 导入日期时间模块，用于处理日期和时间
import hashlib  # 导入哈希模块，用于生成MD5签名
import json  # 导入JSON模块，用于处理JSON数据
import time  # 导入时间模块，用于获取当前时间戳
import uuid  # 导入UUID模块，用于生成唯一的随机字符串
from xml.etree import ElementTree as ET  # 导入XML处理模块，用于解析和生成XML数据

import requests  # 导入requests库，用于发送HTTP请求

from application import app, db  # 从application模块导入app和db对象，app是Flask应用实例，db是数据库对象
from common.libs.Helper import getCurrentDate  # 从common.libs.Helper模块导入getCurrentDate函数，用于获取当前日期
from common.models.pay.OauthAccessToken import OauthAccessToken  # 从common.models.pay.OauthAccessToken模块导入OauthAccessToken模型类，用于访问数据库中OAuth访问令牌


class WeChatService:
    """
    微信支付服务类，封装了微信支付相关的操作，如生成签名、获取支付信息等。
    """

    def __init__(self, merchant_key=None):
        """
        构造函数，初始化微信支付服务类。
        :param merchant_key: 微信支付商户密钥，用于生成签名。
        """
        self.merchant_key = merchant_key  # 设置商户密钥

    def create_sign(self, pay_data):
        """
        生成微信支付签名 (APIv2 MD5)
        :param pay_data: 参与签名的数据字典
        :return: 大写的签名字符串
        """
        # 1. 过滤掉值为 None 或空字符串的参数，以及 sign 字段本身
        # 注意：微信支付签名通常只需要非空的业务参数
        filtered_data = {k: str(v) for k, v in pay_data.items() if v is not None and v != '' and k != 'sign'}

        # 2. 参数按 key 进行字典序排序
        sorted_keys = sorted(filtered_data.keys())

        # 3. 拼接字符串 stringA (使用 key=value&key=value 格式)
        # 确保所有参数都使用 str() 转换为字符串再进行拼接
        stringA = '&'.join([f'{key}={filtered_data[key]}' for key in sorted_keys])

        # 4. 拼接商户支付密钥
        stringSignTemp = f'{stringA}&key={self.merchant_key}'

        # 5. MD5 加密并转大写
        m = hashlib.md5()  # 创建MD5对象
        m.update(stringSignTemp.encode('utf-8'))  # 使用UTF-8编码更新MD5对象
        sign = m.hexdigest().upper()  # 获取MD5哈希值的十六进制表示，并转换为大写

        return sign  # 返回签名

    def get_pay_info(self, pay_data=None):
        """
        获取支付信息
        :param pay_data: 统一下单接口所需的字典数据
        :return: 成功时返回小程序支付所需的字典，失败时返回包含错误信息的字典
        """
        if pay_data is None:  # 检查pay_data是否为空
            return {'success': False, 'msg': '支付数据为空'}  # 返回错误信息

        try:
            # 1. 生成请求签名
            sign = self.create_sign(pay_data)  # 调用create_sign方法生成签名
            pay_data['sign'] = sign  # 将签名添加到支付数据中
            xml_data = self.dict_to_xml(pay_data)  # 将支付数据转换为XML格式

            # --- 在这里添加日志输出 ---
            app.logger.info(f"准备发送给微信支付统一下单的数据字典: {pay_data}")  # 记录发送的数据字典
            app.logger.info(f"准备发送给微信支付统一下单的XML数据: {xml_data}")  # 记录发送的XML数据

            headers = {'Content-Type': 'application/xml'}  # 设置HTTP请求头，指定Content-Type为application/xml

            url = "https://api.mch.weixin.qq.com/pay/unifiedorder"  # 微信支付统一下单接口URL

            # 2. 发送请求
            r = requests.post(url=url, data=xml_data.encode('utf-8'), headers=headers, timeout=10)  # 发送POST请求，设置超时时间为10秒
            r.encoding = "utf-8"  # 设置响应编码为UTF-8

            # 3. 记录原始响应日志（方便调试）
            app.logger.info(f"WeChat Pay UnifiedOrder Response Status: {r.status_code}")  # 记录HTTP状态码
            app.logger.info(f"WeChat Pay UnifiedOrder Response Body: {r.text}")  # 记录响应体

            # 4. 检查 HTTP 状态码
            if r.status_code != 200:  # 检查HTTP状态码是否为200
                return {'success': False, 'msg': f'支付接口请求失败，HTTP状态码: {r.status_code}'}  # 返回错误信息

            # 5. 解析 XML 响应
            response_data = self.xml_to_dict(r.text)  # 将XML响应转换为字典

            # 6. 检查微信支付的业务结果
            return_code = response_data.get('return_code')  # 通信结果
            result_code = response_data.get('result_code')  # 业务结果
            return_msg = response_data.get('return_msg', '')  # 通信错误信息
            err_code = response_data.get('err_code', '')  # 业务错误码
            err_code_des = response_data.get('err_code_des', '')  # 业务错误描述

            if return_code != 'SUCCESS' or result_code != 'SUCCESS':  # 检查通信结果和业务结果是否都为SUCCESS
                # 支付接口返回失败，记录详细错误信息
                error_msg = f"微信支付统一下单失败 - 通信结果: {return_code} ({return_msg}), 业务结果: {result_code} ({err_code}: {err_code_des})"  # 构建错误信息
                app.logger.error(error_msg)  # 记录错误信息
                return {'success': False, 'msg': error_msg}  # 返回错误信息

            # 7. 业务结果成功，获取 prepay_id
            prepay_id = response_data.get('prepay_id')  # 获取预支付ID
            if not prepay_id:  # 再次检查 prepay_id 是否获取成功
                error_msg = f"微信支付统一下单成功但未返回prepay_id，请检查配置或请求参数。原始响应: {r.text}"  # 构建错误信息
                app.logger.error(error_msg)  # 记录错误信息
                return {'success': False, 'msg': error_msg}  # 返回错误信息

            # 8. 生成小程序端支付所需的签名数据
            current_timestamp = str(int(time.time()))  # 获取当前时间戳（秒级）

            pay_sign_data = {
                'appId': pay_data.get('appid'),  # 小程序 appId
                'timeStamp': current_timestamp,  # 当前时间戳
                'nonceStr': pay_data.get('nonce_str'),  # 随机字符串
                'package': f'prepay_id={prepay_id}',  # 预支付交易会话标识
                'signType': 'MD5'  # 签名算法，与统一下单一致
            }

            # 9. 为小程序支付数据生成签名
            pay_sign = self.create_sign(pay_sign_data)

            # 10. 组装返回给前端的数据
            # 注意：返回给前端的数据字段名首字母大小写需要注意，通常微信小程序支付要求是小驼峰
            # 例如 appId, timeStamp, nonceStr, package, signType, paySign
            frontend_pay_info = {
                'timeStamp': current_timestamp,  # 时间戳
                'nonceStr': pay_data.get('nonce_str'),  # 随机字符串
                'package': f'prepay_id={prepay_id}',  # 预支付交易会话标识
                'signType': 'MD5',  # 签名类型
                'paySign': pay_sign,  # 支付签名
                'prepay_id': prepay_id,  # 预支付ID，虽然 package 里有，但单独返回也行

                'notify_url': pay_data.get('notify_url')  # 回调地址
            }

            return {'success': True, 'msg': '获取支付信息成功', 'data': frontend_pay_info}  # 返回成功信息和支付数据

        except requests.exceptions.RequestException as e:  # 捕获requests库抛出的异常
            # 捕获请求库异常，如网络问题、超时等
            error_msg = f"请求微信支付接口异常: {e}"  # 构建错误信息
            app.logger.error(error_msg)  # 记录错误信息
            return {'success': False, 'msg': error_msg}  # 返回错误信息
        except Exception as e:  # 捕获其他未知异常
            # 捕获其他未知异常
            app.logger.error(f"处理微信支付信息时发生未知错误: {e}")  # 记录错误信息
            return {'success': False, 'msg': f"处理微信支付信息时发生未知错误: {e}"}  # 返回错误信息

    def dict_to_xml(self, dict_data):
        """
        将字典数据转换为XML格式的字符串。
        :param dict_data: 要转换的字典数据。
        :return: XML格式的字符串。
        """
        xml = ["<xml>"]  # 初始化XML字符串列表，添加根节点<xml>
        for k, v in dict_data.items():  # 遍历字典中的键值对
            # 将值转换为字符串，以防它是数字或其他类型
            v_str = str(v)  # 将值转换为字符串
            # 判断是否需要使用 CDATA 包裹（通常字符串需要）
            # 对于统一下单接口，大多数字段都是字符串，total_fee是数字
            # 为了简化，可以判断是否是字符串类型
            if isinstance(v, str):  # 如果值是字符串类型
                # 字符串使用 CDATA 包裹
                xml.append(f"<{k}><![CDATA[{v_str}]]></{k}>")  # 添加带有CDATA包裹的XML元素
            else:  # 如果值不是字符串类型（例如数字）
                # 数字等不使用 CDATA
                xml.append(f"<{k}>{v_str}</{k}>")  # 添加不带CDATA包裹的XML元素

        xml.append("</xml>")  # 添加根节点结束标签</xml>
        # 返回 UTF-8 编码的 XML 字符串
        return "".join(xml)  # 将XML字符串列表连接成一个字符串并返回

    def xml_to_dict(self, xml_data):
        """
        将XML格式的字符串转换为字典。
        :param xml_data: 要转换的XML字符串。
        :return: 转换后的字典。
        """
        xml_dict = {}  # 初始化空字典
        root = ET.fromstring(xml_data)  # 从XML字符串中解析出根元素
        for child in root:  # 遍历根元素的子元素
            xml_dict[child.tag] = child.text  # 将子元素的标签和文本内容添加到字典中

        return xml_dict  # 返回字典

    def get_nonce_str(self):
        """
        生成随机字符串。
        :return: 随机字符串。
        """
        return str(uuid.uuid4()).replace("-", "")  # 生成UUID，替换掉其中的“-”，并转换为字符串

    def getAccessToken(self):
        """
        获取微信AccessToken，如果本地有未过期的AccessToken，则直接返回，否则从微信服务器获取。
        :return: AccessToken字符串。
        """
        token = None  # 初始化token为None
        token_info = OauthAccessToken.query.filter(OauthAccessToken.expired_time >= getCurrentDate()).first()  # 从数据库查询未过期的AccessToken
        if token_info:  # 如果查询到未过期的AccessToken
            token = token_info.access_token  # 从数据库记录中获取AccessToken
            return token  # 返回AccessToken

        config_mina = app.config['MINA_APP']  # 获取小程序配置信息
        url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={0}&secret={1}" \
            .format(config_mina['appid'], config_mina['app_secret'])  # 构建获取AccessToken的URL

        r = requests.get(url=url)  # 发送GET请求获取AccessToken
        if r.status_code != 200 or not r.text:  # 如果请求失败或响应为空
            return token  # 返回None

        data = json.loads(r.text)  # 解析JSON响应
        now = datetime.datetime.now()  # 获取当前时间
        date = now + datetime.timedelta(seconds=data['expires_in'] - 200)  # 计算过期时间，减去200秒作为缓冲
        model_token = OauthAccessToken()  # 创建OauthAccessToken模型实例
        model_token.access_token = data['access_token']  # 设置AccessToken
        model_token.expired_time = date.strftime("%Y-%m-%d %H:%M:%S")  # 设置过期时间
        model_token.created_time = getCurrentDate()  # 设置创建时间
        db.session.add(model_token)  # 将模型实例添加到数据库会话
        db.session.commit()  # 提交数据库会话

        return data['access_token']  # 返回AccessToken