// index.js
// 获取应用实例
var app = getApp(); // 获取全局应用实例，可以在当前页面中使用 app.globalData 访问全局数据和方法

Page({
  data: {
    indicatorDots: true, // 是否显示轮播图指示点
    autoplay: true, // 是否自动播放轮播图
    interval: 3000, // 轮播图自动切换的时间间隔 (ms)
    duration: 1000, // 轮播图切换的动画时长 (ms)
    loadingHidden: false, // loading 加载提示是否隐藏，初始为 false，表示显示 loading 提示
    swiperCurrent: 0, // 当前轮播图的索引
    categories: [], // 商品分类列表
    activeCategoryId: 0, // 当前选中的商品分类 ID，默认为 0 (全部商品)
    goods: [], // 商品列表数据
    scrollTop: "0", // 页面滚动条距离顶部的距离，用于记录滚动位置
    loadingMoreHidden: true, // "加载更多" 是否隐藏，初始为 true，表示显示 "加载更多"
    searchInput: '', // 搜索框输入的内容
    p: 1, // 当前页码，用于分页加载商品数据，默认为 1
    processing: false // 是否正在请求数据，防止重复请求
  },

  // 页面加载时触发
  onLoad: function () {
    var that = this; // 保存当前页面对象，避免在回调函数中 this 指向改变

    // 设置导航栏标题为全局配置的 shopName
    wx.setNavigationBarTitle({
      title: app.globalData.shopName
    });
  },

  // 页面显示时触发 (每次展示页面都会调用这个方法，解决切换 tab 不刷新的问题)
  onShow: function () {
    this.getBannerAndCat(); // 获取轮播图和商品分类数据
  },

  // 监听页面滚动事件
  scroll: function (e) {
    var that = this,
      scrollTop = that.data.scrollTop; // 获取当前滚动距离

    // 更新页面 data 中的 scrollTop
    that.setData({
      scrollTop: e.detail.scrollTop // 存储当前的滚动位置
    });
  },

  // 轮播图切换事件处理函数
  swiperchange: function (e) {
    this.setData({
      swiperCurrent: e.detail.current // 更新当前轮播图的索引
    });
  },

  // 监听搜索输入框输入事件
  listenerSearchInput: function (e) {
    this.setData({
      searchInput: e.detail.value // 更新搜索框输入的内容
    });
  },

  // 搜索按钮点击事件处理函数
  toSearch: function (e) {
    this.setData({
      p: 1, // 重置页码为 1
      goods: [], // 清空商品列表
      loadingMoreHidden: true // 显示 "加载更多"
    });
    this.getGoodsList(); // 重新获取商品列表
  },

  // 点击轮播图事件处理函数
  tapBanner: function (e) {
    if (e.currentTarget.dataset.id != 0) { // 如果轮播图 ID 不为 0
      wx.navigateTo({
        url: "/pages/goods/info?id=" + e.currentTarget.dataset.id // 跳转到商品详情页面
      });
    }
  },

  // 点击商品列表中的商品事件处理函数
  toDetailsTap: function (e) {
    wx.navigateTo({
      url: "/pages/goods/info?id=" + e.currentTarget.dataset.id // 跳转到商品详情页面
    });
  },

  // 获取轮播图和商品分类数据
  getBannerAndCat: function () {
    var that = this;

    wx.request({
      url: app.buildUrl("/goods/index"), // 请求接口地址
      header: app.getRequestHeader(), // 设置请求头，包含 token 等信息
      success: function (res) {
        var resp = res.data; // 获取接口返回的数据

        if (resp.code != 200) { // 如果接口返回错误码
          app.alert({
            "content": resp.msg
          }); // 显示错误提示
          return; // 结束函数执行
        }

        // 更新页面 data 中的 banners 和 categories
        that.setData({
          banners: resp.data.banner_list, // 轮播图列表
          categories: resp.data.cat_list // 商品分类列表
        });
        that.getGoodsList(); // 获取商品列表数据
      }
    });
  },

  // 点击商品分类事件处理函数
  catClick: function (e) {
    this.setData({
      activeCategoryId: e.currentTarget.id // 更新当前选中的商品分类 ID
    });
    this.setData({
      loadingMoreHidden: true, // 显示 "加载更多"
      p: 1, // 重置页码为 1
      goods: [] // 清空商品列表
    });
    this.getGoodsList(); // 重新获取商品列表
  },

  // 页面触底事件处理函数 (上拉加载更多)
  onReachBottom: function () {
    var that = this;

    // 延迟 500ms 加载，避免频繁请求
    setTimeout(function () {
      that.getGoodsList(); // 获取商品列表数据
    }, 500);
  },

  // 获取商品列表数据
  getGoodsList: function () {
    var that = this;

    // 如果正在请求数据，则直接返回，避免重复请求
    if (that.data.processing) {
      return;
    }

    // 如果没有更多数据了，则直接返回
    if (!that.data.loadingMoreHidden) {
      return;
    }

    that.setData({
      processing: true // 设置正在请求数据标志
    });

    wx.request({
      url: app.buildUrl("/goods/search"), // 请求接口地址
      header: app.getRequestHeader(), // 设置请求头，包含 token 等信息
      data: {
        cat_id: that.data.activeCategoryId, // 商品分类 ID
        mix_kw: that.data.searchInput, // 搜索关键词
        p: that.data.p, // 当前页码
      },
      success: function (res) {
        var resp = res.data; // 获取接口返回的数据

        if (resp.code != 200) { // 如果接口返回错误码
          app.alert({
            "content": resp.msg
          }); // 显示错误提示
          return; // 结束函数执行
        }

        var goods = resp.data.list; // 获取商品列表

        // 更新页面 data 中的 goods, p 和 processing
        that.setData({
          goods: that.data.goods.concat(goods), // 将新获取的商品列表添加到原商品列表
          p: that.data.p + 1, // 页码加 1
          processing: false // 设置请求数据完成标志
        });

        // 如果没有更多数据了
        if (resp.data.has_more == 0) {
          that.setData({
            loadingMoreHidden: false // 隐藏 "加载更多"
          });
        }
      }
    });
  }
});