//index.js
var app = getApp(); // 获取全局应用程序实例，方便调用全局方法和数据

Page({
    data: {
        // list: 购物车商品列表，初始为空
        // saveHidden: 是否隐藏“完成”按钮，初始为true（隐藏）
        // totalPrice: 总价，初始为0.00
        // allSelect: 是否全选，初始为true
        // noSelect: 是否没有选择任何商品，初始为false
    },
    onLoad: function () {
        // 页面加载时执行，目前为空，可以进行一些初始化操作
    },
    onShow:function(){
        // 页面显示时执行，每次进入页面都会触发
        this.getCartList(); // 调用getCartList方法，获取购物车列表数据
    },
    //每项前面的选中框
    selectTap: function (e) {
        // 点击购物车商品前的选择框时触发
        var index = e.currentTarget.dataset.index; // 获取当前点击的商品在列表中的索引，通过data-index传递
        var list = this.data.list; // 获取购物车商品列表
        if (index !== "" && index != null) { // 确保索引有效
            list[ parseInt(index) ].active = !list[ parseInt(index) ].active; // 将对应索引的商品的选中状态取反
            this.setPageData(this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list); // 更新页面数据，包括隐藏状态、总价、全选状态、未选状态和商品列表
        }
    },
    //计算是否全选了
    allSelect: function () {
        // 计算当前是否所有商品都被选中
        var list = this.data.list; // 获取购物车商品列表
        var allSelect = false; // 初始假设没有全选
        for (var i = 0; i < list.length; i++) { // 遍历商品列表
            var curItem = list[i]; // 获取当前商品
            if (curItem.active) { // 如果当前商品被选中
                allSelect = true; // 标记为已选中
            } else { // 如果当前商品未被选中
                allSelect = false; // 标记为未选中
                break; // 只要有一个未选中，就跳出循环，因为没有全选
            }
        }
        return allSelect; // 返回全选状态
    },
    //计算是否都没有选
    noSelect: function () {
        // 计算当前是否没有任何商品被选中
        var list = this.data.list; // 获取购物车商品列表
        var noSelect = 0; // 记录未选中的商品数量，初始为0
        for (var i = 0; i < list.length; i++) { // 遍历商品列表
            var curItem = list[i]; // 获取当前商品
            if (!curItem.active) { // 如果当前商品未被选中
                noSelect++; // 未选中商品数量加1
            }
        }
        if (noSelect == list.length) { // 如果未选中商品数量等于商品总数
            return true; // 返回true，表示没有任何商品被选中
        } else {
            return false; // 返回false，表示有商品被选中
        }
    },
    //全选和全部选按钮
    bindAllSelect: function () {
        // 点击全选/取消全选按钮时触发
        var currentAllSelect = this.data.allSelect; // 获取当前的全选状态
        var list = this.data.list; // 获取购物车商品列表
        for (var i = 0; i < list.length; i++) { // 遍历商品列表
            list[i].active = !currentAllSelect; // 将所有商品的选中状态设置为当前全选状态的取反
        }
        this.setPageData(this.getSaveHide(), this.totalPrice(), !currentAllSelect, this.noSelect(), list); // 更新页面数据，包括隐藏状态、总价、全选状态、未选状态和商品列表
    },
    //加数量
    jiaBtnTap: function (e) {
        // 点击增加商品数量按钮时触发
        var that = this; // 保存this的引用
        var index = e.currentTarget.dataset.index; // 获取当前点击的商品在列表中的索引
        var list = that.data.list; // 获取购物车商品列表
        list[parseInt(index)].number++; // 增加对应索引的商品的数量
        that.setPageData(that.getSaveHide(), that.totalPrice(), that.allSelect(), that.noSelect(), list); // 更新页面数据
        this.setCart( list[parseInt(index)].goods_id,list[parseInt(index)].number ); // 调用setCart方法，更新服务器购物车数据
    },
    //减数量
    jianBtnTap: function (e) {
        // 点击减少商品数量按钮时触发
        var index = e.currentTarget.dataset.index; // 获取当前点击的商品在列表中的索引
        var list = this.data.list; // 获取购物车商品列表
        if (list[parseInt(index)].number > 1) { // 如果商品数量大于1
            list[parseInt(index)].number--; // 减少对应索引的商品的数量
            this.setPageData(this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list); // 更新页面数据
            this.setCart( list[parseInt(index)].goods_id,list[parseInt(index)].number ); // 调用setCart方法，更新服务器购物车数据
        }
    },
    //编辑默认全不选
    editTap: function () {
        // 点击编辑按钮时触发
        var list = this.data.list; // 获取购物车商品列表
        for (var i = 0; i < list.length; i++) { // 遍历商品列表
            var curItem = list[i]; // 获取当前商品
            curItem.active = false; // 将所有商品的选中状态设置为false（未选中）
        }
        this.setPageData(!this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list); // 更新页面数据，切换编辑/完成状态，并更新其他相关数据
    },
    //选中完成默认全选
    saveTap: function () {
        // 点击完成按钮时触发
        var list = this.data.list; // 获取购物车商品列表
        for (var i = 0; i < list.length; i++) { // 遍历商品列表
            var curItem = list[i]; // 获取当前商品
            curItem.active = true; // 将所有商品的选中状态设置为true（选中）
        }
        this.setPageData(!this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list); // 更新页面数据，切换编辑/完成状态，并更新其他相关数据
    },
    getSaveHide: function () {
        // 获取当前“完成”按钮的隐藏状态
        return this.data.saveHidden; // 返回saveHidden属性的值
    },
    totalPrice: function () {
        // 计算购物车中选中的商品的总价
        var list = this.data.list; // 获取购物车商品列表
        var totalPrice = 0.00; // 初始化总价为0.00
        for (var i = 0; i < list.length; i++) { // 遍历商品列表
            if ( !list[i].active) { // 如果当前商品未被选中
                continue; // 跳过当前循环，处理下一个商品
            }
            totalPrice = totalPrice + parseFloat( list[i].price ) * list[i].number; // 将当前商品的价格乘以数量加到总价中
        }
        return totalPrice; // 返回计算出的总价
    },
    setPageData: function (saveHidden, total, allSelect, noSelect, list) {
        // 更新页面数据
        this.setData({ // 使用setData方法更新数据
            list: list, // 更新购物车商品列表
            saveHidden: saveHidden, // 更新“完成”按钮的隐藏状态
            totalPrice: total, // 更新总价
            allSelect: allSelect, // 更新全选状态
            noSelect: noSelect, // 更新未选状态
        });
    },
    //去结算
    toPayOrder: function () {
        // 点击“去结算”按钮时触发
        var data = { // 创建一个数据对象，用于传递到订单页面
            type:"cart", // 标记为购物车类型
            goods: [] // 初始化商品数组
        };

        var list = this.data.list; // 获取购物车商品列表
        for (var i = 0; i < list.length; i++) { // 遍历商品列表
            if ( !list[i].active) { // 如果当前商品未被选中
                continue; // 跳过当前循环，处理下一个商品
            }
            data['goods'].push({ // 将选中的商品信息添加到商品数组中
                "id": list[i].goods_id, // 商品ID
                "price": list[i].price, // 商品价格
                "number": list[i].number // 商品数量
            });
        }

        wx.navigateTo({ // 跳转到订单页面
            url: "/pages/order/index?data=" + JSON.stringify(data) // 将数据对象转换为JSON字符串，作为参数传递
        });
    },
    //如果没有显示去逛逛按钮事件
    toIndexPage: function () {
        // 如果购物车为空，点击“去逛逛”按钮时触发
        wx.switchTab({ // 切换到商品列表页面
            url: "/pages/goods/index" // 商品列表页面路径
        });
    },
    //选中删除的数据
    deleteSelected: function () {
        // 点击删除选中的商品按钮时触发
        var list = this.data.list; // 获取购物车商品列表
        var goods = []; // 创建一个数组，用于存储需要删除的商品的ID
        list = list.filter(function ( item ) { // 使用filter方法过滤掉选中的商品
            if( item.active ){ // 如果商品被选中
                goods.push( { // 将商品ID添加到需要删除的商品数组中
                    "id":item.goods_id
                } )
            }

            return !item.active; // 返回false，表示该商品将被从列表中移除
        });

        this.setPageData( this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list); // 更新页面数据
        //发送请求到后台删除数据
        wx.request({ // 发送请求到后台删除商品
            url: app.buildUrl("/cart/del"), // 删除购物车商品的API地址
            header: app.getRequestHeader(), // 获取请求头
            method: 'POST', // 使用POST方法
            data: { // 请求数据
                goods: JSON.stringify( goods ) // 需要删除的商品ID数组，转换为JSON字符串
            },
            success: function (res) { // 请求成功的回调函数
            }
        });
    },
    getCartList: function () {
        // 获取购物车列表数据
        var that = this; // 保存this的引用
        wx.request({ // 发送请求到后台获取购物车列表
            url: app.buildUrl("/cart/index"), // 获取购物车列表的API地址
            header: app.getRequestHeader(), // 获取请求头
            success: function (res) { // 请求成功的回调函数
                var resp = res.data; // 获取响应数据
                if (resp.code != 200) { // 如果响应码不是200，表示出错
                    app.alert({"content": resp.msg}); // 显示错误信息
                    return; // 停止执行
                }
                that.setData({ // 更新页面数据
                    list:resp.data.list, // 更新购物车商品列表
                    saveHidden: true, // 隐藏“完成”按钮
                    totalPrice: 0.00, // 重置总价
                    allSelect: true, // 默认全选
                    noSelect: false // 默认有选择商品
                });

                that.setPageData(that.getSaveHide(), that.totalPrice(), that.allSelect(), that.noSelect(), that.data.list); // 再次更新页面数据，确保所有数据都正确显示
            }
        });
    },
    setCart:function( goods_id, number ){
        // 设置购物车商品数量
        var that = this; // 保存this的引用
        var data = { // 创建一个数据对象，用于传递到后台
            "id": goods_id, // 商品ID
            "number": number // 商品数量
        };
        wx.request({ // 发送请求到后台更新购物车商品数量
            url: app.buildUrl("/cart/set"), // 更新购物车商品数量的API地址
            header: app.getRequestHeader(), // 获取请求头
            method: 'POST', // 使用POST方法
            data: data, // 请求数据
            success: function (res) { // 请求成功的回调函数
            }
        });
    }
});