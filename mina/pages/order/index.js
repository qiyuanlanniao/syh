//获取应用实例
var app = getApp();

Page({
    data: {
        goods_list: [], // 商品列表，存放订单中的商品信息
        default_address: null, // 默认收货地址，包含收货人姓名、电话、地址等信息
        yun_price: "0.00", // 运费
        pay_price: "0.00", // 实际支付金额
        total_price: "0.00", // 商品总价
        params: null, // 页面参数，通常是从其他页面传递过来的商品信息等
        express_address_id:0 //快递地址id
    },
    /**
     * 生命周期函数--监听页面加载
     * e: 页面跳转时传递的参数，可以通过 e.data 获取
     */
    onLoad: function (e) {
        var that = this;
        // 将接收到的参数（JSON字符串）解析为 JavaScript 对象，并存储到 data.params 中
        that.setData({
            params: JSON.parse(e.data)
        });
    },

    /**
     * 生命周期函数--监听页面显示
     * 页面每次显示时都会调用该方法
     */
    onShow: function () {
        var that = this;
        // 获取订单信息，例如商品列表、默认地址、价格等
        this.getOrderInfo();
    },

    /**
     * 创建订单
     * e: 事件对象，包含触发事件的组件信息
     */
    createOrder: function (e) {
        wx.showLoading(); // 显示加载提示框
        var that = this;
        // 构造请求数据
        var data = {
            type: this.data.params.type, // 订单类型，例如立即购买、购物车结算等
            goods: JSON.stringify(this.data.params.goods), // 商品信息，将商品信息对象转换为 JSON 字符串
            express_address_id: that.data.default_address.id // 默认收货地址 ID
        };

        // 发起网络请求
        wx.request({
            url: app.buildUrl("/order/create"), // 订单创建接口 URL
            header: app.getRequestHeader(), // 设置请求头，包含用户认证信息
            method: 'POST', // 设置请求方法为 POST
            data: data, // 设置请求数据
            success: function (res) { // 请求成功的回调函数
                wx.hideLoading(); // 隐藏加载提示框
                var resp = res.data; // 获取服务器返回的数据
                if (resp.code != 200) { // 如果返回的 code 不是 200，表示请求失败
                    app.alert({"content": resp.msg}); // 弹出提示框，显示错误信息
                    return; // 终止函数执行
                }

                // 跳转到订单列表页面
                wx.navigateTo({
                    url: "/pages/my/order_list"
                });
            }
        });

    },

    /**
     * 跳转到地址设置页面
     *  用户可以添加新的收货地址
     */
    addressSet: function () {
        wx.navigateTo({
            url: "/pages/my/addressSet?id=0" // 跳转到地址设置页面，参数 id=0 表示新增地址
        });
    },

    /**
     * 跳转到地址列表页面
     * 用户可以选择已有的收货地址
     */
    selectAddress: function () {
        wx.navigateTo({
            url: "/pages/my/addressList" // 跳转到地址列表页面
        });
    },

    /**
     * 获取订单信息
     * 包括商品列表、默认地址、价格等
     */
    getOrderInfo: function () {
        var that = this;
        // 构造请求数据
        var data = {
            type: this.data.params.type, // 订单类型
            goods: JSON.stringify(this.data.params.goods) // 商品信息
        };

        // 发起网络请求
        wx.request({
            url: app.buildUrl("/order/info"), // 订单信息接口 URL
            header: app.getRequestHeader(), // 设置请求头
            method: 'POST', // 设置请求方法为 POST
            data: data, // 设置请求数据
            success: function (res) { // 请求成功的回调函数
                var resp = res.data; // 获取服务器返回的数据
                if (resp.code != 200) { // 如果返回的 code 不是 200，表示请求失败
                    app.alert({"content": resp.msg}); // 弹出提示框，显示错误信息
                    return; // 终止函数执行
                }

                // 更新 data 中的数据
                that.setData({
                    goods_list: resp.data.goods_list, // 商品列表
                    default_address: resp.data.default_address, // 默认收货地址
                    yun_price: resp.data.yun_price, // 运费
                    pay_price: resp.data.pay_price, // 实际支付金额
                    total_price: resp.data.total_price, // 商品总价
                });

                // 如果存在默认地址，则设置 express_address_id
                if( that.data.default_address ){
                    that.setData({
                         express_address_id: that.data.default_address.id // 设置 express_address_id 为默认地址 ID
                    });
                }
            }
        });
    }

});