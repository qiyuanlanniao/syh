var app = getApp(); // 获取全局应用程序实例

Page({
    data: {
        order_sn: null, // 订单号，从其他页面传递过来，初始化为 null，表示尚未获取
        info: null      // 订单详情信息，初始化为 null，表示尚未获取
    },
    /**
     * 生命周期函数--监听页面加载
     * @param {Object} e 页面跳转时传递的参数对象，例如：{order_sn: "some_order_sn"}
     */
    onLoad: function (e) {
        var that = this; // 保存 this 指针，以便在回调函数中使用

        // 1. 从页面参数中获取订单号 (order_sn)
        if (e.order_sn) {
            // 如果参数对象 e 中存在 order_sn 属性，则将其赋值给 data 中的 order_sn
            that.setData({
                order_sn: e.order_sn // 更新 data 中的 order_sn
            });
        } else {
            // 2. 如果没有 order_sn，显示提示信息并返回上一页 (可选)
            //  说明：这种情况通常是用户直接进入了订单详情页，但是没有通过有效的订单列表页或其他页面跳转过来，缺少了关键的订单号参数
            app.alert({"content": "缺少订单号"}); // 显示一个提示框，告知用户缺少订单号
            //  wx.navigateBack() 函数用于返回上一页，可以根据业务需求选择是否需要立即返回
            //  如果需要延迟一段时间后再返回，可以使用 setTimeout 函数
            //  例如：setTimeout(function() { wx.navigateBack(); }, 2000); // 2秒后返回
        }
    },

    /**
     * 生命周期函数--监听页面显示
     * 监听页面显示时执行。
     * 作用：确保用户从其他页面返回时能够刷新订单详情
     */
    onShow: function () {
        // 1. 在页面显示时加载订单详情
        //  说明：为了保证用户从其他页面（例如支付成功页）返回到订单详情页时，能够及时更新订单状态，需要在 onShow 生命周期函数中调用获取订单详情的接口

        // 2. 只有当 order_sn 存在时才去请求订单详情
        if (this.data.order_sn) { // 避免在 order_sn 为 null 或 undefined 时发起请求，导致错误
            this.getPayOrderInfo(); // 调用 getPayOrderInfo 函数获取订单详情
        }
    },

    /**
     * 获取支付订单详情
     * 从后端 API 获取指定订单号的详细信息，并更新 data 中的 info
     */
    getPayOrderInfo: function () {
        var that = this; // 保存 this 指针，以便在回调函数中使用

        // 1. 检查 order_sn 是否已经设置
        //  说明：在发起请求之前，再次检查 order_sn 是否已经正确设置，避免因为某些未知原因导致 order_sn 为空
        if (!that.data.order_sn) {
            console.error("order_sn is not set, cannot fetch order info."); // 在控制台输出错误信息，方便调试
            //  可以添加一个用户可见的错误提示，例如：
            //  wx.showToast({ title: '订单号为空，请重试', icon: 'none' });
            return; // 终止函数执行
        }

        // 2. 发起网络请求，从后端 API 获取订单详情
        wx.request({
            url: app.buildUrl("/my/order/info"), // 后端 API 的 URL，由 app.buildUrl 函数生成，拼接了完整的请求地址
            header: app.getRequestHeader(), // 设置请求头，通常包含用户身份验证信息，例如 token
            method: 'POST', // 指定使用 POST 方法
            data: {
                order_sn: that.data.order_sn // 将 order_sn 作为请求参数传递给后端
            },
            success: function (res) {
                // 3. 请求成功的回调函数
                var resp = res.data; // 获取后端返回的数据

                // 4. 检查后端返回的状态码
                if (resp.code != 200) {
                    //  如果状态码不是 200，表示请求失败，显示错误信息
                    app.alert({"content": resp.msg}); // 显示错误信息
                    // 清空或重置 data.info 以防显示错误信息
                    that.setData({
                        info: null // 清空 info，避免显示错误信息
                    });
                    return; // 终止函数执行
                }

                // 5. 处理后端返回的数据
                //  后端返回的数据通常包含在一个 data 属性中，例如：resp.data.info
                if (resp.data && resp.data.info) {
                    // 如果 resp.data 存在且 resp.data.info 也存在，则将其赋值给 data 中的 info
                    that.setData({
                        info: resp.data.info // 更新 data 中的 info，显示订单详情
                    });
                } else {
                    //  处理 resp.data.info 不存在的情况，可能是后端错误
                    app.alert({"content": "获取订单详情失败：数据结构错误"}); // 显示错误信息，告知用户获取订单详情失败
                     that.setData({
                        info: null // 清空 info，避免显示错误信息
                    });
                }
            },
            fail: function (err) {
                // 6. 请求失败的回调函数
                //  处理请求失败的情况，例如网络错误、服务器错误等
                console.error("请求订单详情接口失败", err); // 在控制台输出错误信息，方便调试
                app.alert({"content": "网络请求失败，请稍后再试"}); // 显示错误信息，告知用户网络请求失败
                 that.setData({
                    info: null // 清空 info，避免显示错误信息
                });
            }
        });
    }
});