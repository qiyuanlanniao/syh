// 获取全局应用程序实例对象
var app = getApp();

// 定义页面
Page({
    // 页面数据，用于数据绑定
    data: {
        // 评论列表数据，初始值为一个包含两个对象的数组
        list: [
            {
                // 日期
                date: "2018-07-01 22:30:23",
                // 订单号
                order_number: "20180701223023001",
                // 评论内容
                content: "记得周六发货",
            },
            {
                // 日期
                date: "2018-07-01 22:30:23",
                // 订单号
                order_number: "20180701223023001",
                // 评论内容
                content: "记得周六发货",
            }
        ]
    },

    // 页面加载时执行
    onLoad: function (options) {
        // 生命周期函数--监听页面加载
        // options: 页面跳转带来的参数
        // 这里通常用于获取页面跳转时传递过来的参数，例如：options.id
    },

    // 页面显示时执行
    onShow: function () {
        // 生命周期函数--监听页面显示
        // 在页面显示时调用getCommentList函数，用于获取评论列表数据
        this.getCommentList();
    },

    // 获取评论列表函数
    getCommentList: function () {
        // 保存当前页面实例的引用，用于在回调函数中访问this
        var that = this;

        // 发起网络请求
        wx.request({
            // 请求的URL，通过app实例的buildUrl方法生成，拼接了相对路径
            url: app.buildUrl("/my/comment/list"),
            // 请求头，通过app实例的getRequestHeader方法获取
            header: app.getRequestHeader(),
            // 请求成功的回调函数
            success: function (res) {
                // 获取响应数据
                var resp = res.data;

                // 判断响应状态码是否为200，如果不是，则弹出错误提示框
                if (resp.code != 200) {
                    // 调用app实例的alert方法，弹出错误提示框
                    app.alert({"content": resp.msg});
                    // 结束当前函数执行
                    return;
                }

                // 请求成功，更新页面数据中的list
                that.setData({
                    // 将服务器返回的评论列表数据赋值给页面data中的list
                    list: resp.data.list
                });

            }
        });
    }
});