// 获取全局应用程序实例
var app = getApp();

// 定义页面对象
Page({
    // 页面的初始数据
    data: {
        // 页面加载提示信息
        remind: '加载中',
        // 手机倾斜角度
        angle: 0,
        // 用户信息
        userInfo: {},
        // 是否已经注册的标志，true 表示已注册，false 表示未注册
        regFlag: true
    },
    // 跳转到首页
    goToIndex: function () {
        // 使用 wx.switchTab 切换到指定 tabBar 页面
        wx.switchTab({
            // 目标页面路径
            url: '/pages/goods/index',
        });
    },
    // 页面加载时执行
    onLoad: function () {
        // 设置导航栏标题为全局数据中的店铺名称
        wx.setNavigationBarTitle({
            title: app.globalData.shopName
        });
        // 检查用户登录状态
        this.checkLogin();
    },
    // 页面显示时执行
    onShow: function () {

    },
    // 页面初次渲染完成时执行
    onReady: function () {
        var that = this;
        // 设置一个定时器，1秒后清除加载提示信息
        setTimeout(function () {
            that.setData({
                remind: ''
            });
        }, 1000);
        // 监听手机加速度数据变化
        wx.onAccelerometerChange(function (res) {
            // 根据加速度数据计算倾斜角度，限制在 -14 到 14 度之间
            var angle = -(res.x * 30).toFixed(1);
            if (angle > 14) {
                angle = 14;
            } else if (angle < -14) {
                angle = -14;
            }
            // 如果角度发生变化，则更新 data 中的 angle 值
            if (that.data.angle !== angle) {
                that.setData({
                    angle: angle
                });
            }
        });
    },
    // 检查用户登录状态
    checkLogin: function () {
        var that = this;
        // 调用微信登录接口获取用户 code
        wx.login({
            success: function (res) {
                // 如果获取 code 失败，弹出提示信息
                if (!res.code) {
                    app.alert({'content': '登录失败，请再次点击~~'});
                    return;
                }
                // 调用后端接口检查用户是否已经注册
                wx.request({
                    // 接口 URL，由 app.buildUrl 方法生成
                    url: app.buildUrl('/member/check-reg'),
                    // 设置请求头，由 app.getRequestHeader 方法生成
                    header: app.getRequestHeader(),
                    // 请求方法为 POST
                    method: 'POST',
                    // 传递用户 code 到后端
                    data: {code: res.code},
                    // 请求成功回调函数
                    success: function (res) {
                        // 如果后端返回 code 不是 200，表示用户未注册
                        if (res.data.code != 200) {
                            // 设置 regFlag 为 false，表示未注册
                            that.setData({
                                regFlag: false
                            });
                            return;
                        }

                        // 将 token 存储到缓存中
                        app.setCache("token", res.data.data.token);
                        //that.goToIndex(); //检查登录成功后是否跳转首页，注释掉表示不跳转
                    }
                });
            }
        });
    },
    // 用户登录函数
    login: function (e) {
        var that = this;
        // 如果用户拒绝授权，弹出提示信息
        if (!e.detail.userInfo) {
            app.alert({'content': '登录失败，请再次点击~~'});
            return;
        }

        // 获取用户信息
        var data = e.detail.userInfo;
        // 调用微信登录接口获取用户 code
        wx.login({
            success: function (res) {
                // 如果获取 code 失败，弹出提示信息
                if (!res.code) {
                    app.alert({'content': '登录失败，请再次点击~~'});
                    return;
                }
                // 将 code 添加到用户信息中
                data['code'] = res.code;
                // 调用后端接口进行登录
                wx.request({
                    // 接口 URL，由 app.buildUrl 方法生成
                    url: app.buildUrl('/member/login'),
                    // 设置请求头，由 app.getRequestHeader 方法生成
                    header: app.getRequestHeader(),
                    // 请求方法为 POST
                    method: 'POST',
                    // 传递用户信息到后端
                    data: data,
                    // 请求成功的回调函数
                    success: function (res) {
                        // 如果后端返回 code 不是 200，弹出提示信息
                        if (res.data.code != 200) {
                            app.alert({'content': res.data.msg});
                            return;
                        }
                        // 将 token 存储到缓存中
                        app.setCache("token", res.data.data.token);
                        // 登录成功后跳转到首页
                        that.goToIndex();
                    }
                });
            }
        });
    }
});