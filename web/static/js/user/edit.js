;
var user_edit_ops = {
    // 初始化函数
    init: function () {
        // 调用事件绑定函数
        this.eventBind();
    },
    // 事件绑定函数
    eventBind: function () {
        // 监听 class 为 "user_edit_wrap .save" 的元素的点击事件（保存按钮）
        $(".user_edit_wrap .save").click(function () {
            // 获取当前点击的按钮对象
            var btn_target = $(this);

            // 判断按钮是否处于禁用状态 (避免重复提交)
            if (btn_target.hasClass("disabled")) {
                // 如果是禁用状态，弹出提示信息
                common_ops.alert("正在处理!!请不要重复提交~~");
                // 停止后续操作
                return;
            }

            // 获取昵称输入框对象
            var nickname_target = $(".user_edit_wrap input[name=nickname]");
            // 获取昵称输入框的值
            var nickname = nickname_target.val();

            // 获取邮箱输入框对象
            var email_target = $(".user_edit_wrap input[name=email]");
            // 获取邮箱输入框的值
            var email = email_target.val();

            // 验证昵称是否为空或者长度小于2
            if (!nickname || nickname.length < 2) {
                // 如果昵称不符合规范，弹出提示信息并聚焦到昵称输入框
                common_ops.tip("请输入符合规范的姓名~~", nickname_target);
                // 停止后续操作
                return false;
            }

            // 验证邮箱是否为空或者长度小于2
            if (!email || email.length < 2) {
                // 如果邮箱不符合规范，弹出提示信息并聚焦到邮箱输入框
                common_ops.tip("请输入符合规范的邮箱~~", email_target);
                // 停止后续操作
                return false;
            }

            // 禁用按钮，防止重复提交
            btn_target.addClass("disabled");

            // 构造要提交的数据对象
            var data = {
                nickname: nickname,
                email: email
            }

            // 发送 AJAX 请求
            $.ajax({
                // 请求地址，由 common_ops.buildUrl 函数生成
                url: common_ops.buildUrl("/user/edit"),
                // 请求类型为 POST
                type: "POST",
                // 请求数据
                data: data,
                // 返回数据类型为 JSON
                dataType: "json",
                // 请求成功后的回调函数
                success: function (res) {
                    // 移除按钮的禁用状态
                    btn_target.removeClass("disabled");
                    // 定义回调函数变量
                    var callback = null;
                    // 判断请求是否成功 (code == 200 表示成功)
                    if (res.code == 200) {
                        // 如果成功，定义一个回调函数，用于刷新当前页面
                        callback = function () {
                            // 刷新当前页面
                            window.location.href = window.location.href;
                        }
                    }
                    // 弹出提示信息，并执行回调函数
                    common_ops.alert(res.msg, callback);
                }
            })


        });
    }
};

// DOM 加载完成后执行
$(document).ready(function () {
    // 调用 user_edit_ops 的初始化函数
    user_edit_ops.init();
})