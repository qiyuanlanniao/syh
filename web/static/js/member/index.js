;
var member_index_ops = {
    // 初始化函数
    init: function () {
        // 绑定事件
        this.eventBind();
    },
    // 事件绑定函数
    eventBind: function () {
        var that = this; // 保存当前对象的引用，避免在事件处理函数中this指向改变

        // 搜索按钮点击事件
        $(".wrap_search .search").click(function () {
            // 提交表单，执行搜索
            $(".wrap_search").submit();
        });

        // 删除按钮点击事件
        $(".remove").click(function () {
            // 调用ops函数，执行删除操作
            // $(this).attr("data") 获取data属性的值，传递给ops函数作为id
            that.ops("remove", $(this).attr("data"));
        });

        // 恢复按钮点击事件
        $(".recover").click(function () {
            // 调用ops函数，执行恢复操作
            // $(this).attr("data") 获取data属性的值，传递给ops函数作为id
            that.ops("recover", $(this).attr("data"));
        });
    },

    // 操作函数 (删除/恢复)
    ops: function (act, id) {
        // act: 操作类型 ("remove" 删除, "recover" 恢复)
        // id:  操作对象的ID

        // 定义回调函数，用于confirm弹窗确认后的操作
        var callback = {
            'ok': function () {
                // 用户点击了 "确定" 按钮

                // 发送 AJAX 请求到服务器
                $.ajax({
                    url: common_ops.buildUrl("/member/ops"), // 构建URL，指向member/ops接口
                    type: "POST", // 请求类型为 POST
                    data: {
                        act: act,  // 操作类型 (删除/恢复)
                        id: id     // 操作对象的ID
                    },
                    dataType: "json", // 预期服务器返回的数据类型为 JSON
                    success: function (res) {
                        // 请求成功后的回调函数
                        var callback = null; // 初始化回调函数为空

                        // 判断服务器返回的状态码
                        if (res.code == 200) {
                            // 操作成功 (状态码为 200)

                            // 定义回调函数，用于在提示信息显示后刷新页面
                            callback = function () {
                                // 刷新当前页面
                                window.location.href = window.location.href;
                            }
                        }

                        // 显示提示信息 (使用 common_ops.alert 函数，该函数封装了弹窗逻辑)
                        // res.msg 是服务器返回的提示信息
                        // callback 是操作完成后的回调函数 (刷新页面)
                        common_ops.alert(res.msg, callback);
                    }
                });
            },
            'cancel': null // 用户点击了 "取消" 按钮，回调函数为空
        };

        // 显示确认弹窗 (使用 common_ops.confirm 函数，该函数封装了确认弹窗逻辑)
        // 提示信息根据操作类型动态生成
        // callback 是确认后的回调函数
        common_ops.confirm("确定" + (act == "remove" ? "删除" : "恢复") + "?", callback);
    }
};

// 文档加载完成后执行
$(document).ready(function () {
    // 初始化 member_index_ops 对象
    member_index_ops.init();
});