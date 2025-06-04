// pages/webview/index.js
Page({
  data: {
    webViewUrl: 'https://www.wjx.cn/vm/OlDwb82.aspx'
  },

  onLoad: function (options) {
    if (options.url) {
      // 接收传递过来的 URL，并进行解码，因为URL中可能包含特殊字符
      this.setData({
        webViewUrl: decodeURIComponent(options.url)
      });
    }
    // 可选：设置页面的导航栏标题，通常是加载的网页标题，或者一个通用标题
    // wx.setNavigationBarTitle({
    //   title: '活动详情'
    // });
  },
})