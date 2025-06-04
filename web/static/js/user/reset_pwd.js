;
/**
 * 修改密码相关操作对象
 */
var mod_pwd_ops = {
    /**
     * 初始化函数
     * 在页面加载完成后执行，用于绑定事件
     */
    init: function () {
        this.eventBind(); // 调用事件绑定函数
    },
    /**
     * 事件绑定函数
     * 用于绑定页面上的各种事件
     */
    eventBind: function () {
        /**
         * “保存”按钮的点击事件处理函数
         */
        $("#save").click(function () {
            var btn_target = $(this); // 获取当前点击的按钮对象

            /**
             *  判断按钮是否处于禁用状态
             *  防止重复提交
             */
            if (btn_target.hasClass("disabled")) {
                common_ops.alert("正在处理!!请不要重复提交~~"); // 弹出提示框
                return; // 终止执行
            }

            /**
             *  获取表单中的原密码和新密码
             */
            var old_password = $("#old_password").val(); // 获取原密码输入框的值
            var new_password = $("#new_password").val(); // 获取新密码输入框的值

            /**
             *  校验原密码是否为空
             */
            if (!old_password) {
                common_ops.alert("请输入原密码~~"); // 弹出提示框
                return false; // 终止执行
            }

            /**
             *  校验新密码是否为空或者长度是否小于6位
             */
            if (!new_password || new_password.length < 6) {
                common_ops.alert("请输入不少于6位的新密码~~"); // 弹出提示框
                return false; // 终止执行
            }

            /**
             *  禁用“保存”按钮，防止重复提交
             */
            btn_target.addClass("disabled"); // 添加 disabled class，禁用按钮

            /**
             *  构造请求数据
             */
            var data = {
                old_password: old_password, // 原密码
                new_password: new_password  // 新密码
            }

            /**
             *  发送 AJAX 请求，修改密码
             */
            $.ajax({
                url: common_ops.buildUrl("/user/reset-pwd"), // 请求 URL，通过 common_ops.buildUrl 函数生成
                type: "POST", // 请求类型为 POST
                data: data, // 请求数据
                dataType: "json", // 返回数据类型为 JSON
                success: function (res) { // 请求成功后的回调函数
                    btn_target.removeClass("disabled"); // 移除 disabled class，启用按钮
                    var callback = null; // 回调函数，用于处理成功后的操作

                    /**
                     *  判断修改密码是否成功
                     */
                    if (res.code == 200) { // 如果返回码为 200，表示修改成功
                        callback = function () { // 定义回调函数
                            window.location.href = window.location.href; // 刷新当前页面
                        }
                    }
                    common_ops.alert(res.msg, callback); // 弹出提示框，显示返回信息，并执行回调函数
                }
            })


        });
    }
};

/**
 *  页面加载完成后执行的函数
 */
$(document).ready(function () {
    mod_pwd_ops.init(); // 调用 mod_pwd_ops 对象的 init 函数，进行初始化操作
})