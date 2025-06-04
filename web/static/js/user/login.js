; // 空语句，通常用于分隔代码块或避免语法错误。可以忽略。

var user_login_ops = {
    // user_login_ops 对象，包含用户登录相关操作

    init: function () {
        // init 方法，初始化函数，页面加载完成后调用
        this.eventBind(); // 调用 eventBind 方法，绑定事件
    },

    eventBind: function () {
        // eventBind 方法，用于绑定页面事件

        $(".login_wrap .do-login").click(function () {
            // 给class为 login_wrap 下的 class为 do-login 的元素（通常是登录按钮）绑定点击事件
            var btn_target = $(this); // 获取当前点击的按钮对象，缓存起来，提高效率。

            if (btn_target.hasClass("disabled")) {
                // 如果按钮已经有 disabled class，说明正在处理中，防止重复提交
                common_ops.alert("正在处理!!请不要重复提交~~"); // 弹出提示框，告知用户不要重复提交
                return; // 阻止后续代码执行，退出事件处理函数
            }

            var login_name = $(".login_wrap input[name=login_name]").val(); // 获取class为 login_wrap 下的 name为 login_name 的 input 元素的值（通常是用户名输入框）
            var login_pwd = $(".login_wrap input[name=login_pwd]").val(); // 获取class为 login_wrap 下的 name为 login_pwd 的 input 元素的值（通常是密码输入框）

            if (login_name == undefined || login_name.length < 1) {
                // 如果用户名为空或未定义
                common_ops.alert("请输入正确的登录用户名~"); // 弹出提示框，提示用户输入用户名
                return; // 阻止后续代码执行，退出事件处理函数
            }
            if (login_pwd == undefined || login_pwd.length < 1) {
                // 如果密码为空或未定义
                common_ops.alert("请输入正确的登录密码~"); // 弹出提示框，提示用户输入密码
                return; // 阻止后续代码执行，退出事件处理函数
            }

            btn_target.addClass("disabled"); // 点击后，给按钮添加 disabled class，防止重复提交

            $.ajax({
                // 使用 jQuery 的 ajax 方法发送异步请求
                url: common_ops.buildUrl("/user/login"), // 请求的 URL，通过 common_ops.buildUrl 方法构建
                type: "POST", // 请求类型，POST 方法
                data: {
                    // 发送的数据
                    login_name: login_name, // 用户名
                    login_pwd: login_pwd // 密码
                },
                dataType: "json", // 返回的数据类型，JSON 格式
                success: function (res) {
                    // 请求成功后的回调函数，res 为服务器返回的数据
                    btn_target.removeClass("disabled"); // 请求完成后，移除按钮的 disabled class，允许再次点击

                    var callback = null; // 定义一个回调函数变量，初始值为 null

                    if (res.code == 200) {
                        // 如果服务器返回的状态码为 200，表示登录成功
                        callback = function () {
                            // 定义一个回调函数，用于登录成功后跳转页面
                            window.location.href = common_ops.buildUrl("/"); // 跳转到首页，通过 common_ops.buildUrl 方法构建 URL
                        }

                    }
                    common_ops.alert(res.msg, callback); // 弹出提示框，显示服务器返回的消息，并传入回调函数
                }
            });

        })
    }
};

$(document).ready(function () {
    // $(document).ready() 函数，文档加载完成后执行
    user_login_ops.init(); // 调用 user_login_ops 的 init 方法，初始化登录操作
});