var app = getApp();
Page({
    data: {
        order_sn: null, // 初始化为 null
        info: null      // 初始化为 null 或 {}
    },
    onLoad: function (e) {
        var that = this;
        // 从页面参数获取 order_sn 并保存到 data
        if (e.order_sn) {
            that.setData({
                order_sn: e.order_sn
            });
        } else {
             // 如果没有 order_sn，可以给出提示或返回上一页
             app.alert({"content": "缺少订单号"});
             // setTimeout(function() { wx.navigateBack(); }, 2000); // 示例：2秒后返回
        }
    },
    onShow: function () {
        // 在页面显示时加载订单详情，确保用户从其他页面返回也能刷新
        if (this.data.order_sn) { // 只有当 order_sn 存在时才去请求
             this.getPayOrderInfo();
        }
    },
    getPayOrderInfo:function(){
        var that = this;
        // 检查 order_sn 是否已经设置
        if (!that.data.order_sn) {
             console.error("order_sn is not set, cannot fetch order info.");
             // 可以添加一个用户可见的错误提示
             return;
        }

        wx.request({
            url: app.buildUrl("/my/order/info"), // 确保这里的路径和后端修改后的匹配
            header: app.getRequestHeader(),
            method: 'POST', // <-- 重点：增加这一行，指定使用 POST 方法
            data: {
                order_sn: that.data.order_sn // 传递 order_sn
            },
            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({"content": resp.msg});
                    // 清空或重置 data.info 以防显示错误信息
                    that.setData({
                        info: null
                    });
                    return;
                }

                // 后端返回的数据在 resp.data.info
                if (resp.data && resp.data.info) {
                    that.setData({
                       info: resp.data.info
                    });
                } else {
                    // 处理 resp.data.info 不存在的情况，可能是后端错误
                    app.alert({"content": "获取订单详情失败：数据结构错误"});
                     that.setData({
                        info: null
                    });
                }
            },
            fail: function(err) {
                // 处理请求失败
                console.error("请求订单详情接口失败", err);
                app.alert({"content": "网络请求失败，请稍后再试"});
                 that.setData({
                    info: null
                });
            }
        });
    }
});