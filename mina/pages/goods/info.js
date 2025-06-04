// 获取应用实例
var app = getApp();
// 引入 wxParse 模块，用于解析 HTML 文本
var WxParse = require('../../wxParse/wxParse.js');
// 引入 utils 模块，包含一些工具函数
var utils = require('../../utils/util.js');

Page({
    data: {
        autoplay: true, // 是否自动播放轮播图
        interval: 3000, // 轮播图切换时间间隔，单位毫秒
        duration: 1000, // 轮播图滑动动画时长，单位毫秒
        swiperCurrent: 0, // 当前轮播图的索引
        hideShopPopup: true, // 是否隐藏商品规格选择弹出框，true 表示隐藏
        buyNumber: 1, // 购买数量，默认为 1
        buyNumMin: 1, // 最小购买数量，默认为 1
        buyNumMax: 1, // 最大购买数量，初始化为 1，在获取商品信息时更新
        canSubmit: false, // 选中规格后是否允许加入购物车，默认为 false
        shopCarInfo: {}, // 购物车信息，目前未使用
        shopType: "addShopCar",// 购物类型，"addShopCar" 表示加入购物车，"tobuy" 表示立即购买，默认为加入购物车
        id: 0, // 商品 ID，在 onLoad 中获取
        shopCarNum: 4, // 购物车商品数量，初始值，在获取商品信息时更新
        commentCount: 2 // 评论总数，初始值，在获取评论信息时更新
    },
    /**
     * 生命周期函数--监听页面加载
     * @param {object} e 包含页面跳转参数的对象
     */
    onLoad: function (e) {
        var that = this;
        // 设置商品 ID，从页面跳转参数中获取
        that.setData({
            id: e.id
        });
        // 设置评论列表数据，这里是模拟数据，实际应从服务器获取
        that.setData({
            commentList: [
                {
                    "score": "好评", // 评价等级
                    "date": "2025-03-11 10:20:00", // 评价日期
                    "content": "非常好", // 评价内容
                    "user": {
                        "avatar_url": "/images/more/logo.png", // 用户头像 URL
                        "nick": "angellee 🐰 🐒" // 用户昵称
                    }
                },
                {
                    "score": "好评", // 评价等级
                    "date": "2025-05-11 10:20:00", // 评价日期
                    "content": "非常好", // 评价内容
                    "user": {
                        "avatar_url": "/images/more/logo.png", // 用户头像 URL
                        "nick": "angellee 🐰 🐒" // 用户昵称
                    }
                }
            ]
        });
    },
    /**
     * 生命周期函数--监听页面显示
     */
    onShow: function () {
        // 获取商品信息
        this.getInfo();
        // 获取商品评论
        this.getComments();
    },
    /**
     * 跳转到购物车页面
     */
    goShopCar: function () {
        wx.reLaunch({
            url: "/pages/cart/index" // 购物车页面路径
        });
    },
    /**
     * 设置购物类型为加入购物车，并打开规格选择弹出框
     */
    toAddShopCar: function () {
        this.setData({
            shopType: "addShopCar" // 设置购物类型为加入购物车
        });
        this.bindGuiGeTap(); // 打开规格选择弹出框
    },
    /**
     * 设置购物类型为立即购买，并打开规格选择弹出框
     */
    tobuy: function () {
        this.setData({
            shopType: "tobuy" // 设置购物类型为立即购买
        });
        this.bindGuiGeTap(); // 打开规格选择弹出框
    },
    /**
     * 加入购物车
     */
    addShopCar: function () {
        var that = this;
        // 构造请求数据
        var data = {
            "id": this.data.info.id, // 商品 ID
            "number": this.data.buyNumber // 购买数量
        };
        // 发起加入购物车请求
        wx.request({
            url: app.buildUrl("/cart/set"), // 加入购物车接口 URL
            header: app.getRequestHeader(), // 请求头，包含用户登录态信息
            method: 'POST', // 请求方法为 POST
            data: data, // 请求数据
            success: function (res) {
                var resp = res.data; // 获取服务器响应数据
                app.alert({"content": resp.msg}); // 显示提示信息
                that.setData({
                    hideShopPopup: true // 隐藏规格选择弹出框
                });
                // 加入购物车成功后返回购物车页面
                wx.navigateBack({
                  delta: 1, // 返回上一页
                });
            }
        });
    },
    /**
     * 立即购买
     */
    buyNow: function () {
        // 构造订单数据
        var data = {
            goods: [
                {
                    "id": this.data.info.id, // 商品 ID
                    "price": this.data.info.price, // 商品价格
                    "number": this.data.buyNumber // 购买数量
                }
            ]
        };
        this.setData({
            hideShopPopup: true // 隐藏规格选择弹出框
        });
        // 跳转到订单确认页面
        wx.navigateTo({
            url: "/pages/order/index?data=" + JSON.stringify(data) // 订单确认页面路径，并将订单数据作为参数传递
        });
    },
    /**
     * 规格选择弹出框
     */
    bindGuiGeTap: function () {
        this.setData({
            hideShopPopup: false // 显示规格选择弹出框
        });
    },
    /**
     * 规格选择弹出框隐藏
     */
    closePopupTap: function () {
        this.setData({
            hideShopPopup: true // 隐藏规格选择弹出框
        })
    },
    /**
     * 减少购买数量
     */
    numJianTap: function () {
        // 如果购买数量小于等于最小购买数量，则不减少
        if (this.data.buyNumber <= this.data.buyNumMin) {
            return;
        }
        var currentNum = this.data.buyNumber; // 获取当前购买数量
        currentNum--; // 减少购买数量
        this.setData({
            buyNumber: currentNum // 更新购买数量
        });
    },
    /**
     * 增加购买数量
     */
    numJiaTap: function () {
        // 如果购买数量大于等于最大购买数量，则不增加
        if (this.data.buyNumber >= this.data.buyNumMax) {
            return;
        }
        var currentNum = this.data.buyNumber; // 获取当前购买数量
        currentNum++; // 增加购买数量
        this.setData({
            buyNumber: currentNum // 更新购买数量
        });
    },
    /**
     * 轮播图切换事件处理函数
     * @param {object} e 包含事件信息的对象
     */
    swiperchange: function (e) {
        this.setData({
            swiperCurrent: e.detail.current // 更新当前轮播图的索引
        })
    },
    /**
     * 获取商品信息
     */
    getInfo: function () {
        var that = this;
        // 发起获取商品信息请求
        wx.request({
            url: app.buildUrl("/goods/info"), // 商品信息接口 URL
            header: app.getRequestHeader(), // 请求头，包含用户登录态信息
            data: {
                id: that.data.id // 商品 ID
            },
            success: function (res) {
                var resp = res.data; // 获取服务器响应数据
                // 如果服务器返回错误码，则显示提示信息并跳转到商品列表页面
                if (resp.code != 200) {
                    app.alert({"content": resp.msg}); // 显示提示信息
                    wx.navigateTo({
                        url: "/pages/goods/index" // 商品列表页面路径
                    });
                    return;
                }

                // 更新商品信息
                that.setData({
                    info: resp.data.info, // 商品信息
                    buyNumMax: resp.data.info.stock, // 最大购买数量，从商品库存中获取
                    shopCarNum: resp.data.cart_number // 购物车商品数量，从服务器获取
                });

                // 使用 wxParse 解析商品描述 HTML 文本
                WxParse.wxParse('article', 'html', resp.data.info.summary, that, 5);
            }
        });
    },
    /**
     * 获取商品评论
     */
    getComments: function () {
        var that = this;
        // 发起获取商品评论请求
        wx.request({
            url: app.buildUrl("/goods/comments"), // 商品评论接口 URL
            header: app.getRequestHeader(), // 请求头，包含用户登录态信息
            data: {
                id: that.data.id // 商品 ID
            },
            success: function (res) {
                var resp = res.data; // 获取服务器响应数据
                // 如果服务器返回错误码，则显示提示信息
                if (resp.code != 200) {
                    app.alert({"content": resp.msg}); // 显示提示信息
                    return;
                }

                // 更新评论列表和评论总数
                that.setData({
                    commentList: resp.data.list, // 评论列表
                    commentCount: resp.data.count, // 评论总数
                });
            }
        });
    },
    /**
     * 用户点击右上角分享
     */
    onShareAppMessage: function () {
        console.log("[DEBUG] onShareAppMessage 被调用了");
        var that = this;
        // 发起分享记录请求
            wx.request({
                url: app.buildUrl("/member/share"), // 分享记录接口 URL
                header: app.getRequestHeader(), // 请求头，包含用户登录态信息
                method: 'POST', // 请求方法为 POST
                data: {url: utils.getCurrentPageUrlWithArgs()}, // 请求数据，包含当前页面 URL
                success: function (res) {
                    console.log("[DEBUG] 分享记录成功:", res); // 调试
                },
                fail: function (err) {
                    console.error("[DEBUG] 分享记录失败:", err); // 调试
                }
            });
        // 返回分享信息
        return {
            title: that.data.info.name, // 分享标题，使用商品名称
            path: '/pages/goods/info?id=' + that.data.info.id // 分享路径，包含商品 ID
        };
    }
})
;