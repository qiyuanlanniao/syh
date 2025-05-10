# -*- coding: utf-8 -*-
import os
import stat
import uuid

from werkzeug.utils import secure_filename

from application import app, db
from common.libs.Helper import getCurrentDate
from common.models.Image import Image


class UploadService():
    @staticmethod
    def uploadByFile(file):
        config_upload = app.config['UPLOAD']
        resp = {'code': 200, 'msg': '操作成功', 'data': {}}
        ext = secure_filename(file.filename)

        if ext not in config_upload['ext']:
            resp['code'] = -1
            resp['msg'] = '不允许的扩展类型文件！'

        root_path = app.root_path + config_upload['prefix_path']
        file_dir = getCurrentDate('%Y%m%d')
        save_dir = root_path + file_dir
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
            os.chmod(save_dir, stat.S_IRWXU | stat.S_IRGRP | stat.S_IRWXO)

        file_name = str(uuid.uuid4()).replace('-', '') + '.' + ext
        file.save(f'{save_dir}/{file_name}')

        model_iamge = Image()
        model_iamge.file_key = file_dir + '/' + file_name
        model_iamge.created_time = getCurrentDate()
        db.session.add(model_iamge)
        db.session.commit()

        resp['data'] = {
            'file_key': model_iamge.file_key
        }

        return resp
