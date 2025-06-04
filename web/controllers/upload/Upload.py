# -*- coding: utf-8 -*-
import json # 导入json模块，用于处理JSON数据格式
import re # 导入re模块，用于正则表达式操作，例如从配置文件中移除注释

from flask import Blueprint, request, jsonify # 从Flask框架中导入蓝图(Blueprint)用于模块化应用，request对象用于处理客户端请求，jsonify函数用于将Python字典转换为JSON响应

from application import app  # 从当前应用的包中导入Flask应用实例app。确保 app 已经初始化并配置了 logger
from common.libs.UploadService import UploadService # 导入自定义的上传服务模块，封装了文件上传的具体逻辑
from common.libs.UrlManager import UrlManager # 导入自定义的URL管理模块，用于生成静态资源（如图片）的访问URL
from common.models.Image import Image # 导入Image模型，通常用于与数据库中的图片信息表进行交互

# 创建一个名为 "upload_page" 的Flask蓝图。
# 蓝图用于组织和管理一组相关的路由，使应用结构更清晰。
route_upload = Blueprint("upload_page", __name__)


# 定义一个路由，路径为 "/ueditor"，支持GET和POST请求方法。
# 此路由专门处理UEditor编辑器的后端交互。
@route_upload.route("/ueditor", methods=['GET', 'POST'])
def ueditor():
    """
    处理UEditor编辑器的配置获取、图片上传和已上传图片列表的请求。

    :return: 根据请求参数 'action' 的不同，返回不同的JSON响应：
             - 'config': 返回UEditor的配置文件内容。
             - 'uploadimage': 处理图片上传并返回上传结果。
             - 'listimage': 返回服务器上已存储的图片列表。
    """
    # 获取请求中的所有参数（包括GET查询参数和POST表单数据）
    req = request.values
    # 从请求参数中获取 'action' 的值，如果不存在则默认为空字符串。
    # 'action' 用于区分UEditor的不同操作请求（如：获取配置、上传图片、列出图片）。
    action = req.get('action', '')

    # 如果action是 'config'，表示UEditor请求获取配置文件
    if action == 'config':
        # 获取Flask应用的根目录路径
        root_path = app.root_path
        # 导入os模块，用于操作系统相关功能，如路径拼接
        import os
        # 使用os.path.join构造配置文件的绝对路径，这种方式更具跨平台兼容性。
        # 配置文件路径：{应用根目录}/web/static/plugins/ueditor/upload_config.json
        config_path = os.path.join(root_path, "web", "static", "plugins", "ueditor", "upload_config.json")
        try:
            # 以只读模式('r')和UTF-8打开配置文件
            with open(config_path, 'r', encoding='UTF-8') as fp:
                # 读取文件内容，并使用正则表达式移除非标准的JSON注释（/* ... */）。
                # re.DOTALL 使得 '.' 可以匹配包括换行符在内的任意字符。
                # 然后将处理后的字符串解析为Python字典。
                # 注意：对于复杂的注释或JSONC格式，考虑使用更健壮的JSONC解析库。
                config_data = json.loads(re.sub(r"/\*.*?\*/", "", fp.read(), flags=re.DOTALL))
        except FileNotFoundError:
            # 捕获文件未找到异常，记录错误日志并返回404响应
            app.logger.error(f"UEditor 配置文件未找到: {config_path}")
            return jsonify({"error": "Config file not found"}), 404 # HTTP 404 Not Found
        except json.JSONDecodeError as e:
            # 捕获JSON解析错误异常，记录错误日志并返回500响应
            app.logger.error(f"解析UEditor配置JSON时出错: {e}")
            return jsonify({"error": "Invalid config JSON"}), 500 # HTTP 500 Internal Server Error
        except Exception as e:
            # 捕获其他读取配置时可能发生的未知异常，记录错误日志
            app.logger.error(f"读取UEditor配置时出错: {e}")
            config_data = {}  # 提供一个空的配置字典作为回退，或者返回错误响应
            # return jsonify({"error": "Error reading config"}), 500 # 也可以选择返回错误
        # 将配置字典转换为JSON格式并返回给UEditor
        return jsonify(config_data)

    # 如果action是 'uploadimage'，表示UEditor请求上传图片
    if action == "uploadimage":
        # 调用专门处理UEditor图片上传的函数 ueditor_upload_image
        return ueditor_upload_image()

    # 如果action是 'listimage'，表示UEditor请求获取已上传的图片列表
    if action == 'listimage':
        # 调用专门处理UEditor图片列表的函数 ueditor_list_image
        return ueditor_list_image()

    # 如果 'action' 不是以上任何一个已知的值
    app.logger.warn(f"UEditor 未知 action: {action}")
    # 返回一个包含错误信息的JSON响应和400状态码 (Bad Request)
    return jsonify({"error": "Unknown action"}), 400


# 定义一个路由，路径为 '/pic'，仅支持POST请求方法。
# 通常用于AJAX方式上传单张图片，例如商品封面图。
@route_upload.route('/pic', methods=['POST'])
def upload_pic_ajax():
    """
    处理通过AJAX方式上传的图片请求（例如，商品封面图上传）。
    文件通过表单的 'pic' 字段上传。
    :return: 返回JSON格式的响应，包含上传操作的结果。
             成功时: {'code': 200, 'msg': '操作成功', 'data': {'file_key': '...'}}
             失败时: {'code': -1, 'msg': '错误信息', 'data': {}}
    """
    # 从POST请求的 'files' 集合中获取名为 'pic' 的上传文件对象。
    # 'pic' 是前端 FormData 中 append 文件时指定的键名。
    # 使用 .get 获取可以避免在文件未上传时引发 KeyError。
    up_file = request.files.get('pic')

    # 检查是否没有上传文件或者文件名为空
    if up_file is None or up_file.filename == '':
        app.logger.warn("上传 /pic: 请求中没有文件部分或未选择文件。")
        # 返回JSON格式的错误响应，告知前端未选择文件。
        # 'code': -1 表示操作失败。
        return jsonify({'code': -1, 'msg': '未选择上传文件', 'data': {}})

    # 记录参考日志：正在处理文件上传，文件名是什么。
    app.logger.info(f"上传 /pic: 正在处理文件 '{up_file.filename}'")
    # 调用 UploadService 模块的 uploadByFile 方法处理文件上传。
    # 该方法应返回一个字典，例如:
    # 成功: {'code': 200, 'msg': '操作成功', 'data': {'file_key': 'path/to/file.jpg'}}
    # 失败: {'code': -1, 'msg': '错误信息', 'data': {}}
    resp_dict = UploadService.uploadByFile(up_file)

    # 检查上传服务返回的结果码，如果不为200，表示上传失败。
    if resp_dict.get('code') != 200:
        app.logger.error(f"上传 /pic 文件 '{up_file.filename}' 失败: {resp_dict.get('msg')}")
    else:
        # 记录参考日志：上传成功及文件在服务器上存储的键名 (file_key)。
        app.logger.info(
            f"上传 /pic 文件 '{up_file.filename}' 成功, file_key: {resp_dict.get('data', {}).get('file_key')}")

    # 将UploadService返回的字典转换为JSON响应并返回给前端。
    return jsonify(resp_dict)


# 定义一个函数，专门用于处理UEditor编辑器的图片上传请求
def ueditor_upload_image():
    """
    处理UEditor编辑器的图片上传请求。
    UEditor通过名为 'upfile' 的字段上传图片。
    :return: 返回一个JSON格式的响应，符合UEditor对图片上传接口的格式要求:
             {
                 "state": "SUCCESS"|"错误信息",  // 上传状态信息
                 "url": "图片访问地址",           // 上传成功后的图片URL
                 "title": "图片标题",            // 图片标题，通常是原始文件名
                 "original": "原始文件名"        // 原始文件名
             }
    """
    # 初始化UEditor期望的响应字典结构。
    # 'state'表示状态，'url'是图片访问地址，'title'是图片标题，'original'是原始文件名。
    resp = {'state': 'SUCCESS', 'url': '', 'title': '', 'original': ''}
    # 从请求中获取名为 'upfile' 的文件对象，这是UEditor上传图片时默认的文件字段名。
    up_file = request.files.get('upfile')

    # 检查是否没有上传文件或文件名为空
    if up_file is None or up_file.filename == '':
        app.logger.warn("UEditor uploadimage: 请求中没有 upfile 部分或未选择文件。")
        resp['state'] = '未选择上传文件或文件名为空' # 设置响应状态为更具体的错误信息
        return jsonify(resp)

    # 记录参考日志：正在处理UEditor图片上传，文件名是什么。
    app.logger.info(f"UEditor uploadimage: 正在处理文件 '{up_file.filename}'")
    # 调用UploadService处理文件上传
    ret = UploadService.uploadByFile(up_file)

    # 如果上传服务返回码不为200，表示上传失败
    if ret.get('code') != 200:
        app.logger.error(f"UEditor uploadimage 文件 '{up_file.filename}' 失败: {ret.get('msg')}")
        # 从上传服务的返回结果中获取错误信息，并设置到响应的 'state' 字段。
        # 如果ret中没有'msg'，则提供一个默认的错误信息。
        resp['state'] = ret.get('msg', '上传失败，未知错误')
    else:
        # 上传成功
        app.logger.info(
            f"UEditor uploadimage 文件 '{up_file.filename}' 成功, file_key: {ret.get('data', {}).get('file_key')}")
        # 使用UrlManager根据上传服务返回的文件键名 (file_key) 构建图片的完整访问URL
        resp['url'] = UrlManager.buildImageUrl(ret['data']['file_key'])
        # 设置图片标题为原始文件名。
        resp['title'] = up_file.filename
        # 设置原始文件名为上传时的文件名
        resp['original'] = up_file.filename

    # 返回JSON格式的响应给UEditor
    return jsonify(resp)


# 定义一个函数，专门用于处理UEditor编辑器的图片列表请求
def ueditor_list_image():
    """
    处理UEditor编辑器的图片列表请求（"图片在线管理"功能）。
    UEditor会传递 'start' (起始索引) 和 'size' (每页数量) 参数。
    :return: 返回一个JSON格式的响应，符合UEditor对图片列表接口的格式要求:
             {
                 "state": "SUCCESS"|"错误信息", // 获取状态信息
                 "list": [{"url": "图片1访问地址"}, {"url": "图片2访问地址"}, ...], // 图片URL列表
                 "start": new_start_index,    // 本次列表的结束位置，也是下次请求的起始位置
                 "total": total_image_count   // 图片总数
             }
    """
    # 初始化UEditor期望的图片列表响应字典结构。
    # 'list'是图片URL列表，'start'是下一次请求的起始索引，'total'是图片总数。
    resp = {'state': 'SUCCESS', 'list': [], 'start': 0, 'total': 0}
    # 获取请求参数
    req = request.values

    try:
        # 尝试将请求中的 'start' (起始索引) 和 'size' (每页数量) 参数转换为整数。
        # UEditor 第一次请求时 'start' 通常为 0。
        start = int(req.get('start', 0))
        # UEditor 默认每页请求20张图片。
        page_size = int(req.get('size', 20))
    except ValueError:
        # 如果 'start' 或 'size' 参数无法转换为整数，则视为无效参数。
        app.logger.warn("UEditor listimage: 无效的 start 或 size 参数。")
        resp['state'] = '无效的分页参数'
        return jsonify(resp)

    # 获取Image模型的查询对象，用于后续的数据库查询
    query = Image.query

    # 将 'start' 参数理解为分页查询的偏移量 (offset)。
    # 这更符合UEditor在请求图片列表时的典型行为：
    # 第一次请求: start=0, size=20
    # 第二次请求: start=20, size=20 (表示跳过前20张)
    offset = start

    try:
        # 查询数据库中图片总数
        total_count = query.count()
        # 执行分页查询：按图片ID降序排列 (最新的图片在前面)，
        # 跳过 'offset' 条记录，然后获取 'page_size' 条记录。
        image_list = query.order_by(Image.id.desc()).offset(offset).limit(page_size).all()
    except Exception as e:
        # 捕获数据库查询时可能发生的异常
        app.logger.error(f"UEditor listimage: 数据库查询错误: {e}")
        resp['state'] = '数据库查询错误'
        return jsonify(resp)

    # 初始化一个空列表，用于存放处理后的图片信息（UEditor仅需要图片的URL）
    images_data = []

    # 如果查询到了图片记录
    if image_list:
        # 遍历查询结果中的每一张图片对象
        for item in image_list:
            # 为每张图片构建可访问的URL，并将其包装成UEditor期望的字典格式添加到 'images_data' 列表中
            images_data.append({'url': UrlManager.buildImageUrl(item.file_key)})

    # 设置响应中的图片列表
    resp['list'] = images_data
    # 设置下一次请求的 'start' 值。UEditor期望的是下一次拉取的起始索引，
    # 即当前偏移量 + 当前返回的图片数量。
    resp['start'] = offset + len(images_data)
    # 设置图片总数。UEditor用此值来判断是否还有更多图片可加载。
    resp['total'] = total_count

    # 记录参考日志：本次列表请求的参数、返回的图片数量以及数据库中的总图片数。
    app.logger.info(
        f"UEditor listimage: start={offset}, size={page_size}, 返回数量={len(images_data)}, 数据库总数={total_count}")
    # 返回JSON格式的响应给UEditor
    return jsonify(resp)