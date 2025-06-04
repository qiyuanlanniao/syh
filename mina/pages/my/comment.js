//获取应用实例
var app = getApp(); // 获取全局应用程序实例

Page({ // 定义一个页面

    data: { // 定义页面数据
        "content": "非常愉快的订餐体验~~", // 评价内容，默认值
        "score": 10, // 评分，默认值10
        "order_sn": "" // 订单编号，初始为空
    },

    /**
     * 生命周期函数--监听页面加载
     * 监听页面加载时触发
     * @param {object} e  包含页面跳转带来的参数
     */
    onLoad: function (e) {
        var that = this; // 保存当前页面实例，避免this指向问题

        // 从页面跳转参数中获取订单编号，并更新到页面数据中
        that.setData({
            order_sn: e.order_sn // 将传入的订单编号赋值给data中的order_sn
        });
    },

    /**
     * 评分改变事件
     * 当评分组件的值改变时触发
     * @param {object} e 事件对象，包含评分组件的值
     */
    scoreChange: function (e) {
        // 更新页面数据中的评分
        this.setData({
            "score": e.detail.value // 将评分组件的值赋值给data中的score
        });
    },

    /**
     * 评价内容输入框失去焦点事件
     * 当评价内容输入框失去焦点时触发
     * @param {object} e 事件对象，包含输入框的值
     */
    contentBlur: function ( e ) {
        app.console( e ); // 调用全局应用程序实例的console方法，用于调试，打印事件对象

        // 更新页面数据中的评价内容
        this.setData({
            content: e.detail.value // 将输入框的值赋值给data中的content
        });
    },

    /**
     * 发表评价事件
     * 当点击发表评价按钮时触发
     */
    doComment: function () {
        var that = this; // 保存当前页面实例，避免this指向问题

        // 发起网络请求
        wx.request({
            url: app.buildUrl("/my/comment/add"), // 请求地址，由全局应用程序实例的buildUrl方法生成
            header: app.getRequestHeader(), // 请求头，由全局应用程序实例的getRequestHeader方法生成，包含用户token等信息
            method: "POST", // 请求方法为POST
            data: { // 请求数据
                "content": that.data.content, // 评价内容，从页面数据中获取
                "score": that.data.score, // 评分，从页面数据中获取
                "order_sn": that.data.order_sn // 订单编号，从页面数据中获取
            },
            success: function (res) { // 请求成功的回调函数
                var resp = res.data; // 获取服务器返回的数据

                // 判断返回码是否为200，如果不是，则弹出错误提示框
                if (resp.code != 200) {
                    app.alert({"content": resp.msg}); // 调用全局应用程序实例的alert方法，弹出提示框，显示错误信息
                    return; // 终止执行
                }

                // 跳转到评价列表页面
                wx.navigateTo({
                    url: "/pages/my/commentList" // 跳转到评价列表页面
                });
            }
        });
    }
});