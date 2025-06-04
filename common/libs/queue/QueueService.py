# -*- coding: utf-8 -*-
import json  # 导入 json 模块，用于将数据序列化成 JSON 字符串
from application import db
from common.libs.Helper import getCurrentDate  # 从 common.libs.Helper 模块导入 getCurrentDate 函数，用于获取当前日期和时间
from common.models.queue.QueueList import QueueList  # 从 common.models.queue.QueueList 模块导入 QueueList 类，这个类代表队列数据表模型

class QueueService():
    """
    队列服务类，提供与队列相关的操作，例如添加队列任务。
    """

    @staticmethod
    def addQueue(queue_name, data = None):
        """
        添加队列任务。

        Args:
            queue_name (str): 队列名称，用于标识不同的队列。
            data (dict, optional): 队列数据，需要序列化为 JSON 字符串存储。默认为 None。

        Returns:
            bool: True 表示添加成功。
        """

        # 创建 QueueList 模型实例
        model_queue = QueueList()

        # 设置队列名称
        model_queue.queue_name = queue_name

        # 如果有数据，则将数据序列化为 JSON 字符串并存储
        if data:
            model_queue.data = json.dumps(data)  # 使用 json.dumps() 将 Python 字典转换为 JSON 字符串

        # 设置创建时间和更新时间为当前时间
        model_queue.created_time = model_queue.updated_time = getCurrentDate()

        # 将模型添加到数据库会话中
        db.session.add(model_queue)

        # 提交数据库会话，将更改保存到数据库
        db.session.commit()

        # 返回 True 表示添加成功
        return True