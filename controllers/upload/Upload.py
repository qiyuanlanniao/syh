# -*- coding: utf-8 -*-
import json
import re

from flask import Blueprint, request, jsonify

from application import app
from common.libs.UploadService import UploadService
from common.libs.UrlManager import UrlManager
from common.models.Image import Image

route_upload = Blueprint("upload_page", __name__)


@route_upload.route("/ueditor", methods=['GET', 'POST'])
def ueditor():
    req = request.values
    action = req['action'] if 'action' in req else ''

    if action == 'config':
        root_path = app.root_path
        config_path = f"{root_path}/web/static/plugins/ueditor/upload_config.json"
        with open(config_path, 'r', encoding='UTF-8') as fp:
            try:
                config_data = json.loads(re.sub('/\*.*\*/', '', fp.read()))
            except:
                config_data = {}
        return jsonify(config_data)

    if action == "uploadimage":
        return uploadImage()

    if action == 'listimage':
        return listImage()

    return 'upload'


@route_upload.route('/pic', methods=['GET', 'POST'])
def uploadPic():
    file_target = request.files
    up_file = file_target['pic'] if 'pic' in file_target else None
    callback_target = 'window.parent.upload'
    if up_file is None:
        return f"<script type='text/javascript'>{callback_target}.error('{'上传失败'}')</script>"

    ret = UploadService.uploadByFile(up_file)
    if ret['code'] != 200:
        return "<script type='text/javascript'>{0}.error('{1}')</script>".format(callback_target,
                                                                                 "上传失败：" + ret['msg'])

    return f"<script type='text/javascript'>{callback_target}.success('{ret['data']['file_key']}')</script>"


def uploadImage():
    resp = {'state': 'SUCCESS', 'url': '', 'title': '', 'original': ''}
    file_target = request.files
    up_file = file_target['upfile'] if 'upfile' in file_target else None
    if up_file is None:
        resp['state'] = '上传失败'
        return jsonify(resp)

    ret = UploadService.uploadByFile(up_file)
    if ret['code'] != 200:
        resp['state'] = '上传失败：' + ret['msg']
        return jsonify(resp)

    resp['url'] = UrlManager.buildImageUrl(ret['data']['file_key'])

    return jsonify(resp)


def listImage():
    resp = {'state': 'SUCCESS', 'list': [], 'start': 0, 'total': 0}
    req = request.values

    start = int(req['start']) if 'start' in req else 0
    page_size = int(req['size']) if 'size' in req else 20

    query = Image.query

    if start > 0:
        query = query.filter(Image.id < start)

    list = query.order_by(Image.id.desc()).limit(page_size).all()
    images = []
    if list:
        for item in list:
            images.append({'url': UrlManager.buildImageUrl(item.file_key)})
            start = item.id

    resp['list'] = images
    resp['start'] = start
    resp['total'] = len(images)
    return jsonify(resp)
