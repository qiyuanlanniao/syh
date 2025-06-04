//app.js
App({
    // 小程序启动时触发的事件
    onLaunch: function () {
        // 这里可以执行一些初始化操作，例如获取用户信息、检查登录状态等
    },
    // 全局数据，可以在小程序的所有页面中使用
    globalData: {
        userInfo: null, // 用户信息
        version: "1.0", // 小程序版本号
        shopName: "山屿海", // 店铺名称
        //sdomain:"http://192.168.0.119:8999/api", // 备用的API域名，已注释掉
        domain:"http://192.168.43.25:8999/api" // API域名
    },
    /**
     * 封装的提示框函数，显示带有确定和取消按钮的模态框
     * @param {object} params - 参数对象
     * @param {string} params.title - 提示框标题，默认为"雪碧提示您"
     * @param {string} params.content - 提示框内容，默认为空字符串
     * @param {function} params.cb_confirm - 点击确定按钮的回调函数，可选
     * @param {function} params.cb_cancel - 点击取消按钮的回调函数，可选
     */
    tip:function( params ){
        var that = this; // 保存this引用，以便在回调函数中使用
        var title = params.hasOwnProperty('title')?params['title']:'雪碧提示您'; // 获取标题，如果params中没有title属性，则使用默认值
        var content = params.hasOwnProperty('content')?params['content']:''; // 获取内容，如果params中没有content属性，则使用默认值

        // --- 新增/修改的参数处理 ---
        var showCancel = params.hasOwnProperty('showCancel') ? params['showCancel'] : true; // 默认显示取消按钮
        var confirmText = params.hasOwnProperty('confirmText') ? params['confirmText'] : '确定'; // 默认确认按钮文本为“确定”
        var cancelText = params.hasOwnProperty('cancelText') ? params['cancelText'] : '取消'; // 默认取消按钮文本为“取消”
        // --- 新增/修改的参数处理结束 ---

        wx.showModal({ // 显示模态框
            title: title, // 设置标题
            content: content, // 设置内容
            // --- 将新的参数传递给 wx.showModal ---
            showCancel: showCancel,
            confirmText: confirmText,
            cancelText: cancelText,
            // --- 传递结束 ---
            success: function(res) { // 模态框显示成功后的回调函数
                if ( res.confirm ) {//点击确定按钮
                    if( params.hasOwnProperty('cb_confirm') && typeof( params.cb_confirm ) == "function" ){ // 如果存在cb_confirm回调函数，并且类型为function
                        params.cb_confirm(); // 执行回调函数
                    }
                }else if( res.cancel ){//点击取消按钮 (增加else if确保只有在点击取消时才触发)
                    if( params.hasOwnProperty('cb_cancel') && typeof( params.cb_cancel ) == "function" ){ // 如果存在cb_cancel回调函数，并且类型为function
                        params.cb_cancel(); // 执行回调函数
                    }
                }
                // --- 新增：将 wx.showModal 的 success 回调结果传递给 params.success ---
                // 这允许外部调用者直接处理 wx.showModal 的 success 返回的 res 对象
                if (params.hasOwnProperty('success') && typeof(params.success) == "function") {
                    params.success(res);
                }
                // --- 新增结束 ---
            }
        })
    },
    /**
     * 封装的提示框函数，显示带有确定按钮的模态框
     * @param {object} params - 参数对象
     * @param {string} params.title - 提示框标题，默认为"雪碧提示您"
     * @param {string} params.content - 提示框内容，默认为空字符串
     * @param {function} params.cb_confirm - 点击确定按钮的回调函数，可选
     */
    alert:function( params ){
        var title = params.hasOwnProperty('title')?params['title']:'雪碧提示您'; // 获取标题，如果params中没有title属性，则使用默认值
        var content = params.hasOwnProperty('content')?params['content']:''; // 获取内容，如果params中没有content属性，则使用默认值
        wx.showModal({ // 显示模态框
            title: title, // 设置标题
            content: content, // 设置内容
            showCancel:false, // 不显示取消按钮，只显示确定按钮
            success: function(res) { // 模态框显示成功后的回调函数
                if (res.confirm) {//用户点击确定
                    if( params.hasOwnProperty('cb_confirm') && typeof( params.cb_confirm ) == "function" ){ // 如果存在cb_confirm回调函数，并且类型为function
                        params.cb_confirm(); // 执行回调函数
                    }
                }else{ // 虽然没有取消按钮，这里还是保留了else分支，以防未来扩展需求
                    if( params.hasOwnProperty('cb_cancel') && typeof( params.cb_cancel ) == "function" ){
                        params.cb_cancel();
                    }
                }
            }
        })
    },
    /**
     * 封装的console.log函数，方便统一管理日志输出
     * @param {any} msg - 要输出的信息
     */
    console:function( msg ){
        console.log( msg); // 直接调用console.log输出信息
    },
    /**
     * 获取请求头信息，包含Content-Type和Authorization（Token）
     * @returns {object} - 请求头对象
     */
    getRequestHeader:function(){
        return {
            'content-type': 'application/x-www-form-urlencoded', // 设置Content-Type为application/x-www-form-urlencoded，适用于表单提交
            'Authorization': this.getCache( "token" ) // 从缓存中获取Token，并添加到Authorization头中
        }
    },
    /**
     * 构建完整的URL地址，包括域名、路径和参数
     * @param {string} path - API路径，例如"/user/login"
     * @param {object} params - 请求参数，例如{ username: "test", password: "password" }
     * @returns {string} - 完整的URL地址
     */
    buildUrl:function( path,params ){
        var url = this.globalData.domain + path; // 将域名和路径拼接起来
        var _paramUrl = ""; // 用于存储参数字符串
        if(  params ){ // 如果有参数
            _paramUrl = Object.keys( params ).map( function( k ){ // 将参数对象转换为数组，并使用map函数进行处理
                return [ encodeURIComponent( k ),encodeURIComponent( params[ k ] ) ].join("="); // 对key和value进行URL编码，然后拼接成"key=value"的格式
            }).join("&"); // 将所有的"key=value"拼接成"key1=value1&key2=value2"的格式
            _paramUrl = "?" + _paramUrl; // 在参数字符串前面加上"?"
        }
        return url + _paramUrl; // 将URL和参数字符串拼接起来，返回完整的URL地址
    },
    /**
     * 从缓存中获取数据
     * @param {string} key - 缓存Key
     * @returns {any} - 缓存Value，如果Key不存在，则返回undefined
     */
    getCache:function( key ){
        var value = undefined; // 初始化返回值
        try {
            value = wx.getStorageSync( key ); // 从缓存中获取数据
        } catch (e) {
            // 忽略异常，避免程序崩溃
        }
        return value; // 返回缓存Value
    },
    /**
     * 将数据存储到缓存中
     * @param {string} key - 缓存Key
     * @param {any} value - 缓存Value
     */
    setCache:function(key,value){
        wx.setStorage({ // 将数据存储到缓存中
            key:key, // 设置缓存Key
            data:value // 设置缓存Value
        });
    }
});