# -*- coding: utf-8 -*-
import time

import application


class UrlManager(object):
    @staticmethod
    def buildUrl(path):
        return path

    @staticmethod
    def buildStaticUrl(path):
        release_version = application.app.config.get('RELEASE_VERSION')
        ver = f"{int(time.time())}" if not release_version else release_version
        path = "/static" + path + "?ver=" + ver
        return UrlManager.buildUrl(path)

    @staticmethod
    def buildImageUrl(path):
        app_config = application.app.config['APP']
        url = app_config['domain'] + application.app.config['UPLOAD']['prefix_url'] + path
        return url
