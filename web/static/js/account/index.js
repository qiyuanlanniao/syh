; // 分号，通常用于防止多个JavaScript文件合并时可能出现的语法错误。

var account_index_ops = {
    // 初始化函数，页面加载完成后会执行
    init: function () {
        this.eventBind(); // 调用事件绑定函数
    },

    // 事件绑定函数，用于绑定页面元素的点击事件
    eventBind: function () {
        var that = this; // 将当前对象(account_index_ops)赋值给that，以便在回调函数中使用

        // 搜索按钮点击事件
        $(".wrap_search .search").click(function () {
            $(".wrap_search").submit(); // 提交搜索表单
        });

        // 删除按钮点击事件
        $(".remove").click(function () {
            // 调用ops函数，执行删除操作，并传入要删除的ID
            that.ops("remove", $(this).attr("data")); // $(this).attr("data") 获取当前点击的元素data属性的值，通常是ID
        });

        // 恢复按钮点击事件
        $(".recover").click(function () {
            // 调用ops函数，执行恢复操作，并传入要恢复的ID
            that.ops("recover", $(this).attr("data")); // $(this).attr("data") 获取当前点击的元素data属性的值，通常是ID
        });
    },

    // 执行操作的函数，用于删除或恢复账户
    ops: function (act, id) {
        // act: 操作类型，"remove"表示删除，"recover"表示恢复
        // id: 要操作的账户ID

        var callback = {
            // 确认对话框的回调函数
            'ok': function () {
                // 点击确认按钮后执行的函数

                // 发送Ajax请求到服务器
                $.ajax({
                    url: common_ops.buildUrl("/account/ops"), // 请求的URL，使用common_ops.buildUrl构建
                    type: "POST", // 请求类型为POST
                    data: { // 请求数据
                        act: act, // 操作类型
                        id: id // 账户ID
                    },
                    dataType: "json", // 期望服务器返回的数据类型为JSON
                    success: function (res) {
                        // 请求成功后的回调函数
                        var callback = null; // 定义回调函数，初始值为null

                        if (res.code == 200) {
                            // 如果服务器返回的状态码为200，表示操作成功
                            callback = function () {
                                // 定义刷新页面的回调函数
                                window.location.href = window.location.href; // 刷新当前页面
                            }
                        }
                        // 显示提示信息，使用common_ops.alert函数
                        common_ops.alert(res.msg, callback); // res.msg是服务器返回的消息，callback是操作完成后的回调函数
                    }
                });
            },
            'cancel': null // 点击取消按钮后执行的函数，这里设为null表示不做任何操作
        };

        // 显示确认对话框，使用common_ops.confirm函数
        common_ops.confirm("确定" + (act == "remove" ? "删除" : "恢复") + "?", callback);
        // "确定" + (act == "remove" ? "删除" : "恢复") + "?"  构建确认消息，根据操作类型显示不同的文本
        // callback: 确认对话框的回调函数，包含ok和cancel两个函数
    }
};

// 页面加载完成后执行的函数
$(document).ready(function () {
    account_index_ops.init(); // 调用account_index_ops的初始化函数
});