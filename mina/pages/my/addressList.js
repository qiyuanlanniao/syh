// 获取应用实例
var app = getApp(); // 获取全局唯一的 App 实例

Page({
    data: {}, //  页面的初始数据，通常是一个 JSON 对象

    /**
     * 生命周期函数--监听页面显示
     * onShow 在页面展示时触发，每次打开页面都会调用一次。
     * 可以在这里做一些数据刷新或者初始化工作。
     */
    onShow: function () {
        var that = this; //  保存 `this` 指针，避免在回调函数中 `this` 指向问题
        this.getList(); //  调用 `getList` 方法，获取地址列表
    },

    /**
     *  事件处理函数--选中地址设置为默认地址
     *  @param {Object} e - 事件对象，包含触发事件的组件信息
     */
    selectTap: function (e) {
        var that = this; //  保存 `this` 指针
        wx.request({
            url: app.buildUrl("/my/address/ops"), //  构建请求 URL，`app.buildUrl` 可能是 app.js 中定义的，用于拼接完整的 API 地址
            header: app.getRequestHeader(), //  设置请求头，一般包含用户身份验证信息
            method: 'POST', //  设置请求方法为 POST
            data: {
                id: e.currentTarget.dataset.id, //  获取被点击的地址 ID，`e.currentTarget.dataset.id` 从 `wxml` 页面中传递过来
                act: 'default' //  设置操作类型为 "default"，表示设置为默认地址
            },
            success: function (res) { //  请求成功回调函数
                var resp = res.data; //  获取响应数据
                if (resp.code != 200) { //  如果响应码不是 200，表示请求失败
                    app.alert({"content": resp.msg}); //  调用 `app.alert` 显示错误信息，`app.alert` 可能是 app.js 中定义的，用于显示弹窗提示
                    return; //  终止函数执行
                }
                that.setData({ //  更新页面数据，`setData` 会触发页面重新渲染
                    list: resp.data.list //  更新地址列表
                });
            }
        });
        wx.navigateBack({}); //  返回上一页，设置空对象作为参数，表示不传递任何参数
    },

    /**
     *  事件处理函数--跳转到地址编辑页面
     *  @param {Object} e - 事件对象，包含触发事件的组件信息
     */
    addressSet: function (e) {
        wx.navigateTo({ //  跳转到指定页面
            url: "/pages/my/addressSet?id=" + e.currentTarget.dataset.id //  构建目标页面的 URL，包含地址 ID 作为参数
        })
    },

    /**
     *  获取地址列表
     */
    getList: function () {
        var that = this; //  保存 `this` 指针
        wx.request({
            url: app.buildUrl("/my/address/index"), //  构建请求 URL，获取地址列表
            header: app.getRequestHeader(), //  设置请求头
            success: function (res) { //  请求成功的回调函数
                var resp = res.data; //  获取响应数据
                if (resp.code != 200) { //  如果响应码不是 200，表示请求失败
                    app.alert({"content": resp.msg}); //  显示错误信息
                    return; //  终止函数执行
                }
                that.setData({ //  更新页面数据
                    list: resp.data.list //  更新地址列表
                });
            }
        });
    }
});