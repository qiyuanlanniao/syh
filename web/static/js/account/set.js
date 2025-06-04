;
var account_set_ops = {
    // 初始化函数
    init: function () {
        // 绑定事件
        this.eventBind();
    },
    // 事件绑定函数
    eventBind: function () {
        // 监听保存按钮的点击事件
        $(".wrap_account_set .save").click(function () {
            // 获取当前点击的按钮对象
            var btn_target = $(this);

            // 判断按钮是否被禁用，防止重复提交
            if (btn_target.hasClass("disabled")) {
                // 弹出提示信息
                common_ops.alert("正在处理!!请不要重复提交~~");
                // 阻止后续代码执行
                return;
            }

            // 获取昵称输入框对象和值
            var nickname_target = $(".wrap_account_set input[name=nickname]");
            var nickname = nickname_target.val();

            // 获取手机号码输入框对象和值
            var mobile_target = $(".wrap_account_set input[name=mobile]");
            var mobile = mobile_target.val();

            // 获取邮箱输入框对象和值
            var email_target = $(".wrap_account_set input[name=email]");
            var email = email_target.val();

            // 获取登录用户名输入框对象和值
            var login_name_target = $(".wrap_account_set input[name=login_name]");
            var login_name = login_name_target.val();

            // 获取登录密码输入框对象和值
            var login_pwd_target = $(".wrap_account_set input[name=login_pwd]");
            var login_pwd = login_pwd_target.val();

            // 验证昵称是否为空
            if (nickname.length < 1) {
                // 弹出提示信息，并聚焦到昵称输入框
                common_ops.tip("请输入符合规范的姓名~~", nickname_target);
                // 阻止后续代码执行
                return false;
            }

            // 验证手机号码是否为空
            if (mobile.length < 1) {
                // 弹出提示信息，并聚焦到手机号码输入框
                common_ops.tip("请输入符合规范的手机号码~~", mobile_target);
                // 阻止后续代码执行
                return false;
            }

            // 验证邮箱是否为空
            if (email.length < 1) {
                // 弹出提示信息，并聚焦到邮箱输入框
                common_ops.tip("请输入符合规范的邮箱~~", email_target);
                // 阻止后续代码执行
                return false;
            }

            // 验证登录用户名是否为空
            if (login_name.length < 1) {
                // 弹出提示信息，并聚焦到登录用户名输入框
                common_ops.tip("请输入符合规范的登录用户名~~", login_name_target);
                // 阻止后续代码执行
                return false;
            }

            // 验证登录密码长度是否小于6位
            if (login_pwd.length < 6) {
                // 弹出提示信息，并聚焦到登录密码输入框
                common_ops.tip("请输入符合规范的登录密码~~", login_pwd_target);
                // 阻止后续代码执行
                return false;
            }

            // 禁用保存按钮
            btn_target.addClass("disabled");

            // 构造请求参数
            var data = {
                nickname: nickname,
                mobile: mobile,
                email: email,
                login_name: login_name,
                login_pwd: login_pwd,
                id:$(".wrap_account_set input[name=id]").val() // 获取ID值
            }

            // 发起AJAX请求
            $.ajax({
                // 请求URL，使用common_ops.buildUrl()生成
                url: common_ops.buildUrl("/account/set"),
                // 请求类型为POST
                type: "POST",
                // 请求数据
                data: data,
                // 返回数据类型为JSON
                dataType: "json",
                // 请求成功回调函数
                success: function (res) {
                    // 移除保存按钮的禁用状态
                    btn_target.removeClass("disabled");
                    // 定义回调函数，用于处理成功后的跳转
                    var callback = null;
                    // 判断返回码是否为200
                    if (res.code == 200) {
                        // 如果成功，则定义回调函数为跳转到账户列表页面
                        callback = function () {
                            // 使用window.location.href进行页面跳转
                            window.location.href = common_ops.buildUrl("/account/index");
                        }
                    }
                    // 弹出提示信息，并执行回调函数
                    common_ops.alert(res.msg, callback);
                }
            })


        });
    }
};

// 文档加载完成后执行的函数
$(document).ready(function () {
    // 初始化account_set_ops对象
    account_set_ops.init();
})