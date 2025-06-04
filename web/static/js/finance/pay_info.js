;
var finance_pay_info_ops = {
    // 初始化函数
    init: function () {
        // 绑定事件
        this.eventBind();
    },
    // 事件绑定函数
    eventBind: function () {
        // 找到 class 为 express_send 的元素，并绑定点击事件
        $(".express_send").click(function () {
            // 获取当前点击元素上的 data 属性值 (假设 data 属性名为 'data', 存储的是订单ID或者支付记录ID)
            var data_id = $(this).attr("data");

            // 定义一个回调对象，包含 'ok' 和 'cancel' 两个函数
            var callback = {
                // 点击确认按钮后执行的函数
                'ok': function () {
                    // 发起 AJAX 请求
                    $.ajax({
                        // 请求 URL，通过 common_ops.buildUrl 函数构建，指向财务操作接口的 /finance/ops 路径
                        url: common_ops.buildUrl("/finance/ops"),
                        // 请求类型为 POST
                        type: 'POST',
                        // 请求数据
                        data: {
                            // act 参数，指定操作类型为 "express" (发货)
                            act: "express",
                            // id 参数，传递需要操作的数据 ID (支付记录/订单 ID)
                            id: data_id
                        },
                        // 返回数据类型为 JSON
                        dataType: 'json',
                        // AJAX 请求成功后的回调函数
                        success: function (res) {
                            // 定义一个回调函数，用于提示信息后的操作
                            var callback = null;
                            // 判断返回的 code 是否为 200 (假设 200 代表成功)
                            if (res.code == 200) {
                                // 如果成功，定义回调函数，刷新当前页面
                                callback = function () {
                                    // 刷新当前页面
                                    window.location.href = window.location.href;
                                }
                            }
                            // 调用 common_ops.alert 函数，显示返回的提示信息，并执行回调函数
                            common_ops.alert(res.msg, callback);
                        }
                    });
                },
                // 点击取消按钮后执行的函数，这里设置为 null，表示不执行任何操作
                'cancel': null
            };
            // 调用 common_ops.confirm 函数，显示确认对话框，提示用户是否确定已发货，并传入回调对象
            common_ops.confirm("确定已发货了？", callback);
        });
    }
};

// 在文档加载完成后执行以下代码
$(document).ready(function () {
    // 调用 finance_pay_info_ops 对象的 init 函数，初始化操作
    finance_pay_info_ops.init();
});