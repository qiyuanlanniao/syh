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

        # 1. 获取原始文件名
        original_filename = file.filename
        app.logger.info(f"UploadService: Original filename: {original_filename}")

        # 2. 获取安全的文件名 (防止路径遍历等)
        safe_filename = secure_filename(original_filename)
        app.logger.info(f"UploadService: Secure filename: {safe_filename}")

        # 3. 从安全的文件名中提取扩展名
        if '.' in safe_filename:
            # rsplit('.', 1) 从右边分割一次，获取文件名和扩展名
            # [1] 取扩展名部分
            # .lower() 转换为小写，以便与配置中的小写扩展名列表比较
            ext = safe_filename.rsplit('.', 1)[1].lower()
        else:
            # 如果文件名中没有点，则认为没有扩展名
            ext = ''

        app.logger.info(f"UploadService: Detected extension: '{ext}'")
        app.logger.info(f"UploadService: Allowed extensions: {config_upload['ext']}")

        # 4. 校验扩展名是否在允许的列表中
        if ext not in config_upload['ext']:
            app.logger.error(f"UploadService: Extension '{ext}' is not allowed.")
            resp['code'] = -1
            resp['msg'] = '不允许的扩展类型文件！'
            return resp  # 校验失败，直接返回

        # --- 后续文件保存逻辑 ---
        # 使用原始文件名中的扩展名(ext)来构建新文件名，而不是用处理后的safe_filename作为扩展名
        # （虽然通常 ext 是从 safe_filename 提取的，但明确一下）

        root_path = app.root_path + config_upload['prefix_path']
        # 使用 getCurrentDate('%Y%m%d') 作为日期目录是好的
        file_dir = getCurrentDate('%Y%m%d')
        save_dir = os.path.join(root_path, file_dir)  # 使用 os.path.join 更安全

        if not os.path.exists(save_dir):
            try:
                os.makedirs(save_dir)  # 使用 makedirs 可以创建多级目录
                # 设置权限，注意：os.chmod 在某些系统上可能需要特定权限才能执行
                # 并且在Web服务中，通常由Web服务器用户（如 www-data）来创建，其umask会影响默认权限
                # 确保Web服务器用户对 save_dir 的父目录有写权限
                os.chmod(save_dir, stat.S_IRWXU | stat.S_IRGRP | stat.S_IRWXO)
                app.logger.info(f"UploadService: Created directory {save_dir} with permissions.")
            except Exception as e:
                app.logger.error(f"UploadService: Failed to create directory {save_dir}: {e}")
                resp['code'] = -1
                resp['msg'] = '服务器错误：无法创建上传目录。'
                return resp

        # 使用UUID生成唯一的文件名，并附加正确的扩展名 ext
        # ext 已经是小写了
        new_file_name = str(uuid.uuid4()).replace('-', '') + '.' + ext
        save_path = os.path.join(save_dir, new_file_name)

        try:
            file.save(save_path)
            app.logger.info(f"UploadService: File saved to {save_path}")
        except Exception as e:
            app.logger.error(f"UploadService: Failed to save file {save_path}: {e}")
            resp['code'] = -1
            resp['msg'] = '服务器错误：文件保存失败。'
            return resp

        # --- 保存到数据库的 Image 模型 ---
        model_image = Image()  # 注意变量名是 model_image 而不是 model_iamge
        model_image.file_key = file_dir + '/' + new_file_name  # 存储相对路径
        model_image.created_time = getCurrentDate('%Y-%m-%d %H:%M:%S')  # 确保是datetime或正确格式的字符串

        try:
            db.session.add(model_image)
            db.session.commit()
            app.logger.info(f"UploadService: Image record saved to DB with file_key: {model_image.file_key}")
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"UploadService: Failed to save image record to DB: {e}")
            # 考虑是否需要删除已上传的文件
            if os.path.exists(save_path):
                try:
                    os.remove(save_path)
                    app.logger.info(f"UploadService: Rolled back file save, removed {save_path}")
                except Exception as remove_e:
                    app.logger.error(f"UploadService: Failed to remove file after DB error: {remove_e}")
            resp['code'] = -1
            resp['msg'] = '服务器错误：保存图片信息失败。'
            return resp

        resp['data'] = {
            'file_key': model_image.file_key
        }

        return resp