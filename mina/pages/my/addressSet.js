// 获取应用实例
var commonCityData = require('../../utils/city.js'); // 引入城市数据文件
var app = getApp(); // 获取全局应用实例
Page({
    data: {
        info: [], // 地址信息
        provinces: [], // 省份列表
        citys: [], // 城市列表
        districts: [], // 区域列表
        selProvince: '请选择', // 选中的省份
        selCity: '请选择', // 选中的城市
        selDistrict: '请选择', // 选中的区域
        selProvinceIndex: 0, // 选中的省份索引
        selCityIndex: 0, // 选中的城市索引
        selDistrictIndex: 0 // 选中的区域索引
    },
    onLoad: function (e) {
        // 页面加载时触发
        var that = this; // 保存this指针
        that.setData({
            id: e.id // 获取传递过来的地址ID
        });
        this.initCityData(1); // 初始化省份数据
    },
    onShow: function () {
        // 页面显示时触发
        this.getInfo(); // 获取地址信息
    },
    // 初始化城市数据
    initCityData: function (level, obj) {
        // level: 层级，1-省份，2-城市，3-区域
        // obj:  父级对象，例如：选择省份后，obj为该省份对象
        if (level == 1) {
            // 初始化省份数据
            var pinkArray = []; // 存储省份名称的数组
            for (var i = 0; i < commonCityData.cityData.length; i++) {
                // 遍历城市数据文件中的省份数据
                pinkArray.push(commonCityData.cityData[i].name); // 将省份名称添加到数组中
            }
            this.setData({
                provinces: pinkArray // 设置省份列表
            });
        } else if (level == 2) {
            // 初始化城市数据
            var pinkArray = []; // 存储城市名称的数组
            var dataArray = obj.cityList // 获取该省份下的城市列表
            for (var i = 0; i < dataArray.length; i++) {
                // 遍历城市列表
                pinkArray.push(dataArray[i].name); // 将城市名称添加到数组中
            }
            this.setData({
                citys: pinkArray // 设置城市列表
            });
        } else if (level == 3) {
            // 初始化区域数据
            var pinkArray = []; // 存储区域名称的数组
            var dataArray = obj.districtList // 获取该城市下的区域列表
            for (var i = 0; i < dataArray.length; i++) {
                // 遍历区域列表
                pinkArray.push(dataArray[i].name); // 将区域名称添加到数组中
            }
            this.setData({
                districts: pinkArray // 设置区域列表
            });
        }
    },
    bindPickerProvinceChange: function (event) {
        // 省份选择器改变时触发
        var selIterm = commonCityData.cityData[event.detail.value]; // 获取选中的省份对象
        this.setData({
            selProvince: selIterm.name, // 设置选中的省份名称
            selProvinceIndex: event.detail.value, // 设置选中的省份索引
            selCity: '请选择', // 重置选中的城市
            selCityIndex: 0, // 重置选中的城市索引
            selDistrict: '请选择', // 重置选中的区域
            selDistrictIndex: 0 // 重置选中的区域索引
        });
        this.initCityData(2, selIterm); // 初始化城市数据
    },
    bindPickerCityChange: function (event) {
        // 城市选择器改变时触发
        var selIterm = commonCityData.cityData[this.data.selProvinceIndex].cityList[event.detail.value]; // 获取选中的城市对象
        this.setData({
            selCity: selIterm.name, // 设置选中的城市名称
            selCityIndex: event.detail.value, // 设置选中的城市索引
            selDistrict: '请选择', // 重置选中的区域
            selDistrictIndex: 0 // 重置选中的区域索引
        });
        this.initCityData(3, selIterm); // 初始化区域数据
    },
    bindPickerChange: function (event) {
        // 区域选择器改变时触发
        var selIterm = commonCityData.cityData[this.data.selProvinceIndex].cityList[this.data.selCityIndex].districtList[event.detail.value]; // 获取选中的区域对象
        if (selIterm && selIterm.name && event.detail.value) {
            // 如果选中了有效的区域
            this.setData({
                selDistrict: selIterm.name, // 设置选中的区域名称
                selDistrictIndex: event.detail.value // 设置选中的区域索引
            })
        }
    },
    bindCancel: function () {
        // 取消按钮点击时触发
        wx.navigateBack({}); // 返回上一页
    },
    bindSave: function (e) {
        // 保存按钮点击时触发
        var that = this; // 保存this指针
        var nickname = e.detail.value.nickname; // 获取联系人姓名
        var address = e.detail.value.address; // 获取详细地址
        var mobile = e.detail.value.mobile; // 获取手机号码

        if (nickname == "") {
            // 如果联系人姓名为空
            app.tip({content: '请填写联系人姓名~~'}); // 提示用户
            return // 结束执行
        }
        if (mobile == "") {
            // 如果手机号码为空
            app.tip({content: '请填写手机号码~~'}); // 提示用户
            return // 结束执行
        }
        if (this.data.selProvince == "请选择") {
            // 如果没有选择省份
            app.tip({content: '请选择地区~~'}); // 提示用户
            return // 结束执行
        }
        if (this.data.selCity == "请选择") {
            // 如果没有选择城市
            app.tip({content: '请选择地区~~'}); // 提示用户
            return // 结束执行
        }
        var city_id = commonCityData.cityData[this.data.selProvinceIndex].cityList[this.data.selCityIndex].id; // 获取城市ID
        var district_id; // 区域ID
        if (this.data.selDistrict == "请选择" || !this.data.selDistrict) {
            // 如果没有选择区域
            district_id = ''; // 区域ID为空
        } else {
            // 如果选择了区域
            district_id = commonCityData.cityData[this.data.selProvinceIndex].cityList[this.data.selCityIndex].districtList[this.data.selDistrictIndex].id; // 获取区域ID
        }
        if (address == "") {
            // 如果详细地址为空
            app.tip({content: '请填写详细地址~~'}); // 提示用户
            return // 结束执行
        }

        wx.request({
            url: app.buildUrl("/my/address/set"), // 设置地址的接口URL
            header: app.getRequestHeader(), // 设置请求头
            method: "POST", // 设置请求方法为POST
            data: {
                id: that.data.id, // 地址ID
                province_id: commonCityData.cityData[this.data.selProvinceIndex].id, // 省份ID
                province_str: that.data.selProvince, // 省份名称
                city_id: city_id, // 城市ID
                city_str: that.data.selCity, // 城市名称
                district_id: district_id, // 区域ID
                district_str: that.data.selDistrict, // 区域名称
                nickname: nickname, // 联系人姓名
                address: address, // 详细地址
                mobile: mobile, // 手机号码
            },
            success: function (res) {
                // 请求成功的回调函数
                var resp = res.data; // 获取返回的数据
                if (resp.code != 200) {
                    // 如果返回的code不是200
                    app.alert({"content": resp.msg}); // 弹出错误提示
                    return; // 结束执行
                }
                // 跳转
                wx.navigateBack({}); // 返回上一页
            }
        })
    },
    deleteAddress: function (e) {
        // 删除地址
        var that = this;
        var params = {
            "content": "确定删除？", // 提示内容
            "cb_confirm": function () {
                // 确认删除的回调函数
                wx.request({
                    url: app.buildUrl("/my/address/ops"), // 删除地址的接口URL
                    header: app.getRequestHeader(), // 设置请求头
                    method: 'POST', // 设置请求方法为POST
                    data: {
                        id: that.data.id, // 地址ID
                        act:'del' // 删除操作
                    },
                    success: function (res) {
                        // 请求成功的回调函数
                        var resp = res.data; // 获取返回的数据
                        app.alert({"content": resp.msg}); // 弹出提示信息
                        if (resp.code == 200) {
                            // 如果返回的code是200
                            // 跳转
                            wx.navigateBack({}); // 返回上一页
                        }
                    }
                });
            }
        };
        app.tip(params); // 弹出确认提示框
    },
    getInfo: function () {
        // 获取地址信息
        var that = this;
        if (that.data.id < 1) {
            // 如果地址ID小于1
            return; // 结束执行
        }
        wx.request({
            url: app.buildUrl("/my/address/info"), // 获取地址信息的接口URL
            header: app.getRequestHeader(), // 设置请求头
            data: {
                id: that.data.id // 地址ID
            },
            success: function (res) {
                // 请求成功的回调函数
                var resp = res.data; // 获取返回的数据
                if (resp.code != 200) {
                    // 如果返回的code不是200
                    app.alert({"content": resp.msg}); // 弹出错误提示
                    return; // 结束执行
                }
                var info = resp.data.info; // 获取地址信息
                that.setData({
                    info: info, // 设置地址信息
                    selProvince: info.province_str ? info.province_str : "请选择", // 设置选中的省份
                    selCity: info.city_str ? info.city_str : "请选择", // 设置选中的城市
                    selDistrict: info.area_str ? info.area_str : "请选择" // 设置选中的区域
                });
            }
        });
    }
});