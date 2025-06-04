;
var goodss_cat_set_ops = {
    /**
     * 初始化函数
     * 在页面加载完成后执行，用于绑定事件等
     */
    init: function () {
        this.eventBind(); // 调用事件绑定函数
    },
    /**
     * 事件绑定函数
     * 用于绑定页面上的事件，例如按钮点击事件等
     */
    eventBind: function () {
        // 绑定 ".wrap_cat_set .save" 元素的点击事件
        $(".wrap_cat_set .save").click(function () {
            var btn_target = $(this); // 获取当前点击的按钮对象

            // 防止重复提交：如果按钮已经被禁用，则提示并返回
            if (btn_target.hasClass("disabled")) {
                common_ops.alert("正在处理，请不要重复提交！"); // 弹出提示框
                return; // 阻止后续代码执行
            }

            // 获取分类名称
            var name_target = $(".wrap_cat_set input[name=name]"); // 获取名称输入框对象
            var name = name_target.val(); // 获取名称输入框的值

            // 获取权重
            var weight_target = $(".wrap_cat_set input[name=weight]"); // 获取权重输入框对象
            var weight = weight_target.val(); // 获取权重输入框的值

            // 表单验证：分类名称不能为空
            if (name.length < 1) {
                common_ops.tip("请输入符合规范的分类名称！", name_target); // 弹出提示框
                return false; // 阻止后续代码执行
            }

            // 表单验证：权重不能为空且必须大于等于1
            if (weight.length < 1 || parseInt(weight) < 1) {
                common_ops.tip("请输入符合规范的权重，并且至少大于1！", weight_target); // 弹出提示框
                return false; // 阻止后续代码执行
            }

            // 禁用按钮，防止重复提交
            btn_target.addClass("disabled");

            // 准备 AJAX 请求的数据
            var data = {
                name: name, // 分类名称
                weight: weight, // 权重
                id: $(".wrap_cat_set input[name=id]").val() // 分类ID (用于更新操作，如果没有则是新增)
            };

            // 发送 AJAX 请求
            $.ajax({
                url: common_ops.buildUrl("/goods/cat-set"), // 请求的 URL (由 common_ops.buildUrl 构建)
                type: 'POST', // 请求类型为 POST
                data: data, // 请求数据
                dataType: 'json', // 期望返回的数据类型为 JSON
                success: function (res) { // 请求成功后的回调函数
                    btn_target.removeClass("disabled"); // 移除按钮的禁用状态

                    var callback = null; // 回调函数，用于处理成功后的跳转
                    if (res.code == 200) { // 如果返回码为 200，表示成功
                        callback = function () {
                            window.location.href = common_ops.buildUrl("/goods/cat"); // 跳转到分类列表页
                        }
                    }
                    common_ops.alert(res.msg, callback); // 弹出提示框，显示返回的消息
                }
            })

        })
    }
};

// 页面加载完成后执行 init 函数
$(document).ready(function () {
    goodss_cat_set_ops.init();
});