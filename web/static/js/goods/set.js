// goods/set.js
;

/**
 * 清理消息，用于安全地显示在 alert 弹窗中。
 * 替换 HTML 敏感字符，并将换行符替换为 <br> (如果弹窗支持HTML) 或空格。
 * @param {string} message 要清理的消息
 * @returns {string} 清理后的消息
 */
function sanitizeForAlert(message) {
    if (typeof message !== 'string') {
        message = String(message); // 确保是字符串
    }
    // 基础的HTML标签替换，防止注入简单标签
    message = message.replace(/</g, "<").replace(/>/g, ">");
    // 将换行符替换为 <br>。如果 common_ops.alert 不支持HTML，可以替换为空格或移除。
    message = message.replace(/\n/g, "<br>");
    // 对于 ' 和 "，通常现代弹窗库能处理，但如果遇到问题可以取消下面行的注释进行转义。
    // message = message.replace(/'/g, "'").replace(/"/g, """);
    return message;
}

var upload = {
    /**
     * 上传失败的回调函数
     * @param {string} msg 错误信息
     */
    error: function (msg) {
        // 在调用 common_ops.alert 之前清理消息
        common_ops.alert(sanitizeForAlert(msg));
    },
    /**
     * 上传成功的回调函数
     * @param {string} file_key  上传成功后服务器返回的文件key，用于构建文件URL
     */
    success: function (file_key) {
        if (!file_key) {
            upload.error("上传成功，但未能获取到图片信息。请重试。"); // 使用 upload.error
            return;
        }
        var html = '<img src="' + common_ops.buildPicUrl(file_key) + '"/>'
            + '<span class="fa fa-times-circle del del_image" data="' + file_key + '"></span>';

        var $picEach = $(".upload_pic_wrap .pic-each");
        if ($picEach.length > 0) {
            $picEach.html(html);
        } else {
            $(".upload_pic_wrap").append('<span class="pic-each">' + html + '</span>');
        }
        goods_set_ops.delete_img(); // 重新绑定删除图片事件
    }
};

var goods_set_ops = {
    /**
     * 初始化函数，页面加载时执行
     */
    init: function () {
        this.ue = null;
        this.eventBind();
        this.initEditor();
        this.delete_img(); // 初始化时也绑定一次，针对已存在的图片
    },
    /**
     * 事件绑定函数，用于绑定页面元素的事件
     */
    eventBind: function () {
        var that = this;

        // 当上传图片的文件选择框发生变化时，使用 AJAX 提交上传
        $("#goodsPicUploadInput").change(function () {
            var file_input = this;
            if (file_input.files.length < 1) {
                return; // 没有选择文件
            }

            var file = file_input.files[0];

            // 客户端文件验证
            var allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif'];
            if (allowedTypes.indexOf(file.type) === -1) {
                upload.error("不支持的文件类型。请上传 PNG, JPG, JPEG, 或 GIF 图片。");
                $(file_input).val(''); // 清空文件输入框
                return;
            }
            var maxSizeMB = 5; // 例如: 5MB 大小限制
            if (file.size > maxSizeMB * 1024 * 1024) {
                upload.error("文件过大，请上传小于 " + maxSizeMB + "MB 的图片。");
                $(file_input).val(''); // 清空文件输入框
                return;
            }

            var formData = new FormData();
            formData.append('pic', file); // 'pic' 必须与服务器端点期望的名称匹配

            var upload_url = $(".upload_pic_wrap").attr("action"); // 从表单的 action 属性获取 URL

            // 可在此处显示加载指示器，例如：
            // common_ops.alert("图片上传中...", null, {time: 0}); // time:0 表示不自动关闭

            $.ajax({
                url: upload_url,
                type: 'POST',
                data: formData,
                processData: false,  // 告诉 jQuery 不要处理数据
                contentType: false,  // 告诉 jQuery 不要设置 contentType
                dataType: 'json',    // 期望服务器返回 JSON 响应
                success: function (res) {
                    $(file_input).val(''); // 上传成功或失败后都清空文件输入框
                    // layer.closeAll('dialog'); // 如果用了上面的加载指示器，在这里关闭
                    if (res && res.code == 200 && res.data && res.data.file_key) {
                        upload.success(res.data.file_key);
                    } else {
                        upload.error(res.msg || "上传失败，请检查文件或联系管理员。");
                    }
                },
                error: function (xhr, status, error) {
                    $(file_input).val(''); // 清空文件输入框
                    // layer.closeAll('dialog'); // 如果用了上面的加载指示器，在这里关闭

                    var errorMsg = "上传出错了：";
                    var serverResponse = "";

                    if (xhr.responseJSON && xhr.responseJSON.msg) { // 服务器返回了JSON，且有msg字段
                        serverResponse = xhr.responseJSON.msg;
                    } else if (xhr.responseText) { // 服务器返回了非JSON文本 (可能是HTML错误页)
                        // 尝试从HTML中提取一些信息，或者只显示部分文本避免过长
                        // 这是一个非常基础的尝试，可能需要根据实际返回的HTML调整
                        var contentType = xhr.getResponseHeader("content-type");
                        if (contentType && contentType.indexOf("application/json") !== -1) {
                            // Content-Type 是 JSON 但解析失败 (xhr.responseJSON 为空)
                            serverResponse = "服务器返回无效JSON响应。内容：" + xhr.responseText.substring(0, 200) + "...";
                        } else if (contentType && contentType.indexOf("text/html") !== -1){
                            var titleMatch = xhr.responseText.match(/<title>(.*?)<\/title>/i);
                            if (titleMatch && titleMatch[1]) {
                                serverResponse = "服务器错误页面: " + titleMatch[1];
                            } else {
                                serverResponse = "服务器返回HTML错误，内容截取：" + xhr.responseText.substring(0, 200).replace(/<[^>]+>/g, '') + "...";
                            }
                        } else {
                             serverResponse = "服务器响应内容截取：" + xhr.responseText.substring(0,200) + "...";
                        }
                    } else { // 其他网络错误
                        serverResponse = status + " " + error;
                    }
                    errorMsg += serverResponse;
                    upload.error(errorMsg);
                }
            });
        });

        // 初始化分类选择框
        $(".wrap_goods_set select[name=cat_id]").select2({
            language: 'zh-CN',
            width: '100%'
        });

        // 初始化标签输入框
        $(".wrap_goods_set input[name=tags]").tagsInput({
            // 'defaultText':'添加标签', // tagsInput 插件的默认文本
            'height':'40px',
            'width':'100%', // 根据需要调整
            'interactive':true,
            // onAddTag 和 onRemoveTag 保持原样，如有需要可添加逻辑
            onAddTag: function (tag) {
            },
            onRemoveTag: function (tag) {
            }
        });

        // 点击保存按钮时触发的事件
        $(".wrap_goods_set .save").click(function () {
            var btn_target = $(this);
            if (btn_target.hasClass('disabled')) {
                common_ops.alert("正在处理，请不要重复提交");
                return;
            }

            // 获取表单数据
            var cat_id_target = $(".wrap_goods_set select[name=cat_id]");
            var cat_id = cat_id_target.val();

            var name_target = $(".wrap_goods_set input[name=name]");
            var name = name_target.val();

            var price_target = $(".wrap_goods_set input[name=price]");
            var price = price_target.val();

            var summary = $.trim(that.ue.getContent());

            var stock_target = $(".wrap_goods_set input[name=stock]");
            var stock = stock_target.val();

            var tags_target = $(".wrap_goods_set input[name=tags]");
            var tags = $.trim(tags_target.val()); // tagsInput插件会自动更新这个input的值

            // 前端验证
            if (parseInt(cat_id) < 1) {
                common_ops.tip("请选择分类~~", cat_id_target);
                return;
            }
            if (name.length < 1) {
                common_ops.tip("请输入符合规范的名称~~", name_target);
                return;
            }
            if (!price || parseFloat(price) <= 0) {
                common_ops.tip("请输入符合规范的售卖价格~~", price_target);
                return;
            }

            // 获取图片的文件key
            var main_image_key = "";
            var $del_image_span = $(".wrap_goods_set .pic-each .del_image");
            if ($del_image_span.length > 0) {
                main_image_key = $del_image_span.attr("data");
            }

            if (!main_image_key) {
                common_ops.alert("请上传封面图~~");
                return;
            }
            if (summary.length < 10) {
                // common_ops.tip 对于富文本编辑器可能不太好定位，用 alert 更直接
                common_ops.alert("请输入描述，并不能少于10个字符~~");
                return;
            }
            if (!stock || parseInt(stock) < 0) { // 库存可以是0，但不能是负数或非数字
                common_ops.tip("请输入符合规范的库存量~~", stock_target);
                return;
            }
            if (tags.length < 1) {
                common_ops.tip("请输入标签，便于搜索~~", tags_target);
                return;
            }

            btn_target.addClass("disabled");

            var data = {
                cat_id: cat_id,
                name: name,
                price: price,
                main_image: main_image_key,
                summary: summary,
                stock: stock,
                tags: tags,
                id: $(".wrap_goods_set input[name=id]").val()
            };

            $.ajax({
                url: common_ops.buildUrl("/goods/set"),
                type: 'POST',
                data: data,
                dataType: 'json',
                success: function (res) {
                    btn_target.removeClass("disabled");
                    var callback = null;
                    if (res.code == 200) {
                        callback = function () {
                            window.location.href = common_ops.buildUrl("/goods/index");
                        };
                    }
                    // 这里的 res.msg 也可能需要 sanitize，但通常业务操作成功/失败信息是可控的
                    common_ops.alert(res.msg, callback);
                },
                error: function (xhr, status, error) { // 保存操作的AJAX错误处理
                    btn_target.removeClass("disabled");
                    var errorMsg = "保存失败：";
                    var serverResponse = "";
                     if(xhr.responseJSON && xhr.responseJSON.msg){
                        serverResponse = xhr.responseJSON.msg;
                    } else if (xhr.responseText) {
                        serverResponse = "服务器响应异常，请稍后重试。(" + xhr.status + ")";
                    } else {
                        serverResponse = status + " " + error;
                    }
                    errorMsg += serverResponse;
                    common_ops.alert(sanitizeForAlert(errorMsg)); // 使用 sanitize
                }
            });
        });
    },
    /**
     * 初始化UEditor编辑器
     */
    initEditor: function () {
        var that = this;
        try {
            that.ue = UE.getEditor('editor', {
                toolbars: [ // 自定义工具栏，根据需要调整
                    ['fullscreen', 'source', '|', 'undo', 'redo', '|',
                     'bold', 'italic', 'underline', 'fontborder', 'strikethrough', 'superscript', 'subscript', 'removeformat', 'formatmatch', 'autotypeset', 'blockquote', 'pasteplain', '|', 'forecolor', 'backcolor', 'insertorderedlist', 'insertunorderedlist', 'selectall', 'cleardoc', '|',
                     'rowspacingtop', 'rowspacingbottom', 'lineheight', '|',
                     'customstyle', 'paragraph', 'fontfamily', 'fontsize', '|',
                     'directionalityltr', 'directionalityrtl', 'indent', '|',
                     'justifyleft', 'justifycenter', 'justifyright', 'justifyjustify', '|', 'touppercase', 'tolowercase', '|',
                     'link', 'unlink', 'anchor', '|', 'imagenone', 'imageleft', 'imageright', 'imagecenter', '|',
                     'simpleupload', /*'insertimage',*/ 'emotion', /*'scrawl',*/ 'insertvideo', 'music', 'attachment', 'map', /*'gmap',*/ 'insertframe', /*'insertcode',*/ 'webapp', 'pagebreak', 'template', 'background', '|',
                     'horizontal', 'date', 'time', 'spechars', /*'snapscreen', 'wordimage',*/ '|',
                     'inserttable', 'deletetable', 'insertparagraphbeforetable', 'insertrow', 'deleterow', 'insertcol', 'deletecol', 'mergecells', 'mergeright', 'mergedown', 'splittocells', 'splittorows', 'splittocols', /*'charts',*/ '|',
                     'print', 'preview', 'searchreplace', 'drafts', 'help']
                ],
                enableAutoSave: true,
                saveInterval: 60000,
                elementPathEnabled: false,
                initialFrameHeight: 300, // 初始高度
                zIndex: 4,
                serverUrl: common_ops.buildUrl('/upload/ueditor') // UEditor自身的图片上传等服务器接口
            });
        } catch (e) {
            console.error("UEditor 初始化失败:", e);
            upload.error("编辑器加载失败，请刷新页面重试。");
        }
    },
    /**
     * 删除图片函数
     */
    delete_img: function () {
        $(".wrap_goods_set .del_image").off("click").on("click", function () { // 使用 .off().on() 避免重复绑定
            $(this).parent(".pic-each").remove(); // 移除整个 .pic-each 容器
        });
    }
};

$(document).ready(function () {
    goods_set_ops.init();
});