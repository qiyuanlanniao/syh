# -*- coding: utf-8 -*-
import datetime
import hashlib
import json
import time
import uuid
from xml.etree import ElementTree as ET

import requests

from application import app, db
from common.libs.Helper import getCurrentDate
from common.models.pay.OauthAccessToken import OauthAccessToken


class WeChatService:
    def __init__(self, merchant_key=None):
        self.merchant_key = merchant_key
        pass

    # def create_sign(self, pay_data):
    #     '''
    #     生产签名
    #     :param pay_data:
    #     :return:
    #     '''
    #     stringA = "&".join(["{0}-{1}".format(k, pay_data.get(k)) for k in sorted(pay_data)])
    #     stringSignTemp = "{0}&key={1}".format(stringA, self.merchant_key)
    #     sign = hashlib.md5(stringSignTemp.encode("utf-8")).hexdigest()
    #     return sign.upper()

    import hashlib

    def create_sign(self, pay_data):
        '''
        生成微信支付签名 (APIv2 MD5)
        :param pay_data: 参与签名的数据字典
        :return: 大写的签名字符串
        '''
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

        # **为了调试，建议在这里打印出 stringSignTemp**
        # app.logger.info(f"String to sign: {stringSignTemp}")

        # 5. MD5 加密并转大写
        m = hashlib.md5()
        m.update(stringSignTemp.encode('utf-8'))  # 确保使用 UTF-8 编码
        sign = m.hexdigest().upper()

        return sign

    def get_pay_info(self, pay_data=None):
        '''
        获取支付信息
        :param pay_data: 统一下单接口所需的字典数据
        :return: 成功时返回小程序支付所需的字典，失败时返回包含错误信息的字典
        '''
        if pay_data is None:
            return {'success': False, 'msg': '支付数据为空'}

        try:
            # 1. 生成请求签名
            sign = self.create_sign(pay_data)
            pay_data['sign'] = sign
            xml_data = self.dict_to_xml(pay_data)

            # --- 在这里添加日志输出 ---
            app.logger.info(f"准备发送给微信支付统一下单的数据字典: {pay_data}")
            app.logger.info(f"准备发送给微信支付统一下单的XML数据: {xml_data}")

            headers = {'Content-Type': 'application/xml'}
            # **纠正：使用正确的 HTTPS 统一下单接口 URL**
            url = "https://api.mch.weixin.qq.com/pay/unifiedorder"

            # 2. 发送请求
            r = requests.post(url=url, data=xml_data.encode('utf-8'), headers=headers, timeout=10)  # 增加超时设置
            r.encoding = "utf-8"

            # 3. 记录原始响应日志（方便调试）
            app.logger.info(f"WeChat Pay UnifiedOrder Response Status: {r.status_code}")
            app.logger.info(f"WeChat Pay UnifiedOrder Response Body: {r.text}")

            # 4. 检查 HTTP 状态码
            if r.status_code != 200:
                return {'success': False, 'msg': f'支付接口请求失败，HTTP状态码: {r.status_code}'}

            # 5. 解析 XML 响应
            response_data = self.xml_to_dict(r.text)

            # 6. 检查微信支付的业务结果
            return_code = response_data.get('return_code')  # 通信结果
            result_code = response_data.get('result_code')  # 业务结果
            return_msg = response_data.get('return_msg', '')  # 通信错误信息
            err_code = response_data.get('err_code', '')  # 业务错误码
            err_code_des = response_data.get('err_code_des', '')  # 业务错误描述

            if return_code != 'SUCCESS' or result_code != 'SUCCESS':
                # 支付接口返回失败，记录详细错误信息
                error_msg = f"微信支付统一下单失败 - 通信结果: {return_code} ({return_msg}), 业务结果: {result_code} ({err_code}: {err_code_des})"
                app.logger.error(error_msg)
                return {'success': False, 'msg': error_msg}

            # 7. 业务结果成功，获取 prepay_id
            prepay_id = response_data.get('prepay_id')
            if not prepay_id:  # 再次检查 prepay_id 是否获取成功
                error_msg = f"微信支付统一下单成功但未返回prepay_id，请检查配置或请求参数。原始响应: {r.text}"
                app.logger.error(error_msg)
                return {'success': False, 'msg': error_msg}

            # 8. 生成小程序端支付所需的签名数据
            # **纠正：timeStamp 应该使用当前时间戳**
            current_timestamp = str(int(time.time()))

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
            # 但这里为了与之前的代码结构一致，先保留原样，你可能需要根据小程序SDK的要求调整
            frontend_pay_info = {
                'timeStamp': current_timestamp,  # 纠正后的时间戳
                'nonceStr': pay_data.get('nonce_str'),
                'package': f'prepay_id={prepay_id}',
                'signType': 'MD5',
                'paySign': pay_sign,
                'prepay_id': prepay_id,  # 虽然 package 里有，但单独返回也行
                # 可能还需要 appId 字段，取决于你的前端SDK需求
                'notify_url': pay_data.get('notify_url')
            }

            return {'success': True, 'msg': '获取支付信息成功', 'data': frontend_pay_info}

        except requests.exceptions.RequestException as e:
            # 捕获请求库异常，如网络问题、超时等
            error_msg = f"请求微信支付接口异常: {e}"
            app.logger.error(error_msg)
            return {'success': False, 'msg': error_msg}
        except Exception as e:
            # 捕获其他未知异常
            app.logger.error(f"处理微信支付信息时发生未知错误: {e}")
            return {'success': False, 'msg': f"处理微信支付信息时发生未知错误: {e}"}


    def dict_to_xml(self, dict_data):
        xml = ["<xml>"]
        for k, v in dict_data.items():
            # 将值转换为字符串，以防它是数字或其他类型
            v_str = str(v)
            # 判断是否需要使用 CDATA 包裹（通常字符串需要）
            # 对于统一下单接口，大多数字段都是字符串，total_fee是数字
            # 为了简化，可以判断是否是字符串类型
            if isinstance(v, str):
                # 字符串使用 CDATA 包裹
                xml.append(f"<{k}><![CDATA[{v_str}]]></{k}>")
            else:
                # 数字等不使用 CDATA
                xml.append(f"<{k}>{v_str}</{k}>")

        xml.append("</xml>")
        # 返回 UTF-8 编码的 XML 字符串
        return "".join(xml)

    def xml_to_dict(self, xml_data):
        xml_dict = {}
        root = ET.fromstring(xml_data)
        for child in root:
            xml_dict[child.tag] = child.text

        return xml_dict

    def get_nonce_str(self):
        return str(uuid.uuid4()).replace("-", "")

    def getAccessToken(self):
        token = None
        token_info = OauthAccessToken.query.filter(OauthAccessToken.expired_time >= getCurrentDate()).first()
        if token_info:
            token = token_info.access_token
            return token

        config_mina = app.config['MINA_APP']
        url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={0}&secret={1}" \
            .format(config_mina['appid'], config_mina['app_secret'])

        r = requests.get(url=url)
        if r.status_code != 200 or not r.text:
            return token

        data = json.loads(r.text)
        now = datetime.datetime.now()
        date = now + datetime.timedelta(seconds=data['expires_in'] - 200)
        model_token = OauthAccessToken()
        model_token.access_token = data['access_token']
        model_token.expired_time = date.strftime("%Y-%m-%d %H:%M:%S")
        model_token.created_time = getCurrentDate()
        db.session.add(model_token)
        db.session.commit()

        return data['access_token']
