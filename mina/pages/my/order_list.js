var app = getApp(); // 获取全局应用程序实例
Page({
    data: {
        order_list:[], // 订单列表数据，默认为空数组
        statusType: ["待付款", "待发货", "待确认", "待评价", "已完成","已关闭"], // 订单状态类型列表，用于tab栏显示
        status:[ "-8","-7","-6","-5","1","0" ], // 与statusType对应的后台订单状态值，用于请求数据
        currentType: 0, // 当前选中的订单状态类型，默认为0，即待付款
        tabClass: ["", "", "", "", "", ""] // tab栏样式类名，用于控制tab栏的选中状态
    },
    /**
     * 点击tab栏切换订单状态
     * @param e 事件对象，包含点击的tab栏的index
     */
    statusTap: function (e) {
        var curType = e.currentTarget.dataset.index; // 获取点击的tab栏的index
        this.setData({
            currentType: curType // 更新当前选中的订单状态类型
        });
        this.getPayOrder(); // 重新获取订单列表数据
    },

    /**
     * 查看订单详情
     * @param e 事件对象，包含订单id
     */
    orderDetail: function (e) {
        wx.navigateTo({
            url: "/pages/my/order_info?order_sn=" + e.currentTarget.dataset.id // 跳转到订单详情页面，并传递订单id
        })
    },

    /**
     * 生命周期函数--监听页面加载
     * @param options 页面参数
     */
    onLoad: function (options) {
        // 生命周期函数--监听页面加载
    },

    /**
     * 生命周期函数--监听页面显示
     * 每次显示页面时，重新获取订单列表数据
     */
    onShow: function () {
        this.getPayOrder(); // 获取订单列表数据
    },

    /**
     * 取消订单
     * @param e 事件对象，包含订单id
     */
    orderCancel:function( e ){
        this.orderOps( e.currentTarget.dataset.id,"cancel","确定取消订单？" ); // 调用订单操作函数，执行取消订单操作
    },

    /**
     * 获取订单列表数据
     */
    getPayOrder:function(){
        var that = this; // 保存this指针，以便在wx.request中使用
        wx.request({
            url: app.buildUrl("/my/order"), // 请求订单列表接口
            header: app.getRequestHeader(), // 设置请求头
            data: {
                status: that.data.status[ that.data.currentType ] // 传递订单状态参数，根据当前选中的订单状态类型获取对应的状态值
            },
            success: function (res) { // 请求成功的回调函数
                var resp = res.data; // 获取返回的数据
                if (resp.code != 200) { // 如果返回的code不为200，表示请求失败
                    app.alert({"content": resp.msg}); // 弹出错误提示
                    return; // 结束函数执行
                }

                that.setData({
                   order_list:resp.data.pay_order_list // 更新订单列表数据
                });
            }
        });
    },

    /**
     * 支付订单
     * @param e 事件对象，包含订单id
     */
    toPay:function( e ){
        var that = this; // 保存this指针，以便在wx.request中使用
        wx.request({
            url: app.buildUrl("/order/pay"), // 请求支付接口
            header: app.getRequestHeader(), // 设置请求头
            method: 'POST', // 设置请求方法为POST
            data: {
                order_sn: e.currentTarget.dataset.id // 传递订单id参数
            },
            success: function (res) { // 请求成功回调函数
                var resp = res.data; // 获取返回的数据
                if (resp.code != 200) { // 如果返回的code不为200，表示请求失败
                    app.alert({"content": resp.msg}); // 弹出错误提示
                    return; // 结束函数执行
                }
                var pay_info = resp.data.pay_info; // 获取支付信息
                wx.requestPayment({ // 调用微信支付接口
                    'timeStamp': pay_info.timeStamp, // 时间戳
                    'nonceStr': pay_info.nonceStr, // 随机字符串
                    'package': pay_info.package, // 订单详情扩展字符串
                    'signType': 'MD5', // 签名算法
                    'paySign': pay_info.paySign, // 签名
                    'success': function (res) { // 支付成功的回调函数
                        app.alert({"content": "支付成功"}); // 弹出支付成功的提示
                        that.getPayOrder(); // 重新获取订单列表数据，刷新订单状态
                    },
                    'fail': function (res) { // 支付失败的回调函数
                        app.alert({"content": "支付失败"}); // 弹出支付失败的提示
                    }
                });
            }
        });
    },

    /**
     * 确认收货
     * @param e 事件对象，包含订单id
     */
    orderConfirm:function( e ){
        this.orderOps( e.currentTarget.dataset.id,"confirm","确定收到？" ); // 调用订单操作函数，执行确认收货操作
    },

    /**
     * 去评价
     * @param e 事件对象，包含订单id
     */
    orderComment:function( e ){
        wx.navigateTo({
            url: "/pages/my/comment?order_sn=" + e.currentTarget.dataset.id // 跳转到评价页面，并传递订单id
        });
    },

    /**
     * 订单操作（取消订单、确认收货等）
     * @param order_sn 订单id
     * @param act 操作类型（cancel、confirm等）
     * @param msg 提示信息
     */
    orderOps:function(order_sn,act,msg){
        var that = this; // 保存this指针，以便在回调函数中使用
        var params = {
            "content":msg, // 设置提示信息
            "cb_confirm":function(){ // 设置确认按钮的回调函数
                wx.request({
                    url: app.buildUrl("/order/ops"), // 请求订单操作接口
                    header: app.getRequestHeader(), // 设置请求头
                    method: 'POST', // 设置请求方法为POST
                    data: {
                        order_sn: order_sn, // 传递订单id参数
                        act:act // 传递操作类型参数
                    },
                    success: function (res) { // 请求成功的回调函数
                        var resp = res.data; // 获取返回的数据
                        app.alert({"content": resp.msg}); // 弹出提示信息
                        if ( resp.code == 200) { // 如果返回的code为200，表示操作成功
                            that.getPayOrder(); // 重新获取订单列表数据，刷新订单状态
                        }
                    }
                });
            }
        };
        app.tip( params ); // 调用全局提示函数，弹出确认对话框
    }
});