# -*- coding: utf-8 -*-
import time

import application


class UrlManager(object):
    """
    Url管理器，用于构建各种类型的URL，例如静态资源URL、图片URL等。
    """

    @staticmethod
    def buildUrl(path):
        """
        构建基础URL。这个方法目前直接返回传入的路径。
        """
        return path

    @staticmethod
    def buildStaticUrl(path):
        """
        构建静态资源URL，例如CSS、JavaScript文件。
        为了解决浏览器缓存问题，会在URL中添加版本号。
        版本号的生成方式取决于是否配置了RELEASE_VERSION：
            - 如果配置了RELEASE_VERSION，则使用该值作为版本号。
            - 如果没有配置，则使用当前时间戳作为版本号。

        Args:
            path (str): 静态资源文件的路径（例如：/css/style.css）。

        Returns:
            str: 构建后的静态资源URL，例如：/static/css/style.css?ver=1678886400 或 /static/css/style.css?ver=1.0.0
        """
        release_version = application.app.config.get('RELEASE_VERSION') # 从应用配置中获取 RELEASE_VERSION 的值
        ver = f"{int(time.time())}" if not release_version else release_version # 根据是否配置了 RELEASE_VERSION 决定版本号
        path = "/static" + path + "?ver=" + ver # 构建带有版本号的路径
        return UrlManager.buildUrl(path) # 调用 buildUrl 方法构建最终的URL

    @staticmethod
    def buildImageUrl(path):
        """
        构建图片URL。
        图片URL的构建方式为： APP配置中的domain + UPLOAD配置中的prefix_url + 图片路径。

        Args:
            path (str): 图片文件路径（例如：/images/example.jpg）。

        Returns:
            str: 构建后的图片URL，例如：http://example.com/upload/images/example.jpg
        """
        app_config = application.app.config['APP'] # 从应用配置中获取 APP 配置
        url = app_config['domain'] + application.app.config['UPLOAD']['prefix_url'] + path # 根据配置和路径构建图片URL
        return url