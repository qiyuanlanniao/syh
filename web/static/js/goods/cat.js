;
var goods_cat_ops = {
    // 初始化函数
    init: function () {
        // 绑定事件
        this.eventBind();
    },
    // 事件绑定函数
    eventBind: function () {
        // 保存this的引用，避免在回调函数中this指向错误
        var that = this;

        // 监听搜索表单中status下拉框的change事件
        $(".wrap_search select[name=status]").change(function () {
            // 提交搜索表单
            $(".wrap_search").submit();
        });

        // 监听删除按钮的点击事件
        $(".remove").click(function () {
            // 调用ops函数，执行删除操作
            // 获取data属性中存储的id值，传递给ops函数
            that.ops("remove", $(this).attr("data"));
        });

        // 监听恢复按钮的点击事件
        $(".recover").click(function () {
            // 调用ops函数，执行恢复操作
            // 获取data属性中存储的id值，传递给ops函数
            that.ops("recover", $(this).attr("data"));
        });
    },
    // 操作函数，执行删除或恢复操作
    ops: function (act, id) {
        // 定义回调函数，用于confirm弹窗
        var callback = {
            // 点击确定按钮后的回调函数
            'ok': function () {
                // 发送ajax请求
                $.ajax({
                    // 请求的url地址，使用common_ops.buildUrl构建
                    url: common_ops.buildUrl("/goods/cat-ops"),
                    // 请求类型为POST
                    type: 'POST',
                    // 请求参数
                    data: {
                        // 操作类型：remove或recover
                        act: act,
                        // 数据id
                        id: id
                    },
                    // 返回数据类型为json
                    dataType: 'json',
                    // 请求成功后的回调函数
                    success: function (res) {
                        // 定义一个回调函数，用于alert弹窗
                        var callback = null;
                        // 如果请求成功，状态码为200
                        if (res.code == 200) {
                            // 定义一个回调函数，用于刷新页面
                            callback = function () {
                                // 刷新当前页面
                                window.location.href = window.location.href;
                            }
                        }
                        // 显示alert弹窗，提示信息和回调函数
                        common_ops.alert(res.msg, callback);
                    }
                })

            },
            // 点击取消按钮后的回调函数，这里设置为null，表示不执行任何操作
            'cancel': null
        };
        // 显示confirm弹窗，提示用户是否确定删除或恢复
        // 根据act的值，显示不同的提示信息
        common_ops.confirm((act == "remove" ? "确定删除吗？" : "确定恢复吗？"), callback);
    }
};


// 文档加载完成后执行
$(document).ready(function () {
    // 调用goods_cat_ops的init函数，进行初始化
    goods_cat_ops.init()
});