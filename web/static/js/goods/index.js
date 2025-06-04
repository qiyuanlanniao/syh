;
var goods_index_ops = {
    /**
     * 初始化函数，页面加载完成后执行。
     * 作用：绑定页面上的事件。
     */
    init: function () {
        this.eventBind(); // 调用事件绑定函数
    },

    /**
     * 事件绑定函数。
     * 作用：绑定删除、恢复和搜索按钮的点击事件。
     */
    eventBind: function () {
        var that = this; // 将当前对象（goods_index_ops）赋值给that，以便在回调函数中使用

        /**
         * 删除按钮的点击事件处理函数。
         * 作用：调用ops函数执行删除操作。
         */
        $(".remove").click(function () {
            that.ops("remove", $(this).attr("data")) // 调用ops函数，传入操作类型 "remove" 和 goods 的 id
        });

        /**
         * 恢复按钮的点击事件处理函数。
         * 作用：调用ops函数执行恢复操作。
         */
        $(".recover").click(function () {
            that.ops("recover", $(this).attr("data")) // 调用ops函数，传入操作类型 "recover" 和 goods 的 id
        });

        /**
         * 搜索按钮的点击事件处理函数。
         * 作用：提交搜索表单。
         */
        $(".wrap_search .search").click(function () {
            $(".wrap_search").submit(); // 提交 class 为 "wrap_search" 的表单
        })
    },

    /**
     * 操作函数，执行删除或恢复操作。
     * @param {string} act 操作类型，可以是 "remove"（删除） 或 "recover"（恢复）。
     * @param {string} id  要操作的 goods 的 id。
     */
    ops: function (act, id) {
        /**
         * 定义回调函数，用于 confirm 弹窗。
         */
        var callback = {
            /**
             * 点击 "确定" 按钮后的回调函数。
             * 作用：发送 AJAX 请求到服务器执行删除或恢复操作。
             */
            'ok': function () {
                $.ajax({
                    url: common_ops.buildUrl("/goods/ops"), // 构建 URL，指向处理删除/恢复操作的接口
                    type: 'POST', // 使用 POST 请求
                    data: {
                        act: act, // 操作类型
                        id: id // goods 的 id
                    },
                    dataType: 'json', // 期望服务器返回 JSON 格式的数据
                    success: function (res) { // AJAX 请求成功后的回调函数
                        var callback = null;
                        if (res.code == 200) { // 如果服务器返回的状态码是 200（成功）
                            callback = function () {
                                window.location.href = window.location.href; // 刷新当前页面
                            }
                        }
                        common_ops.alert(res.msg, callback) // 显示服务器返回的消息，并执行回调函数（如果存在）
                    }
                })
            },
            /**
             * 点击 "取消" 按钮后的回调函数。
             * 作用：不执行任何操作。
             */
            'cancel': null
        }
        /**
         * 调用 common_ops.confirm 函数显示确认弹窗。
         * 根据 act 的值显示不同的提示信息。
         * 并传入回调函数。
         */
        common_ops.confirm((act == "remove") ? "确定删除？" : "确定恢复？", callback)
    }
};

/**
 * 页面加载完成后执行的函数。
 * 作用：初始化 goods_index_ops 对象。
 */
$(document).ready(function () {
    goods_index_ops.init(); // 调用 goods_index_ops 的 init 函数，开始事件绑定和页面初始化
});