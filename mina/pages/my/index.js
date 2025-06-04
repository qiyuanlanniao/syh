// 获取应用实例，app 变量可以访问全局的app.js中定义的内容，例如全局数据、函数等
var app = getApp();

// Page是微信小程序页面构造器，用于注册小程序页面。
Page({
    // data是页面初始化数据，页面渲染时会读取这些数据。
    data: {},

    // onLoad是页面加载函数，一个页面只会调用一次。
    // 可以在这里获取页面参数，进行初始化操作。
    onLoad() {
        // 页面加载时执行，目前为空
    },

    // onShow是页面显示/切入前台时触发。
    // 可以进行一些数据更新，或者恢复页面状态等操作。
    onShow() {
        // 页面显示时，调用 getInfo 函数获取用户信息
        this.getInfo();
    },

    // getInfo 函数用于通过网络请求获取用户信息
    getInfo: function() {
        // 保存 this 到 that 变量，避免在 wx.request 回调函数中 this 指向改变
        var that = this;

        // wx.request 是微信小程序提供的发起网络请求的 API
        wx.request({
            // url是请求地址，使用 app.buildUrl 构建完整的请求 URL，拼接上 "/member/info" 接口
            url: app.buildUrl("/member/info"),

            // header是请求头，使用 app.getRequestHeader() 获取请求头，例如包含token
            header: app.getRequestHeader(),

            // success 是请求成功的回调函数
            success: function(res) {
                // 从响应中获取数据
                var resp = res.data;

                // 判断服务器返回的状态码是否为 200 (表示成功)
                if (resp.code != 200) {
                    // 如果状态码不是 200，表示请求失败，调用 app.alert 显示错误信息
                    app.alert({"content": resp.msg});

                    // 提前返回，阻止后续代码执行
                    return;
                }

                // 请求成功，将获取到的用户信息设置到页面的 data 中，用于页面渲染
                that.setData({
                    // resp.data.info 包含了用户信息
                    user_info: resp.data.info
                });
            }
        });
    }
});