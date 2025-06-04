;

/**
 * 平滑地显示菜单
 * 该函数用于在切换菜单状态时，通过淡入淡出的效果来平滑地显示侧边栏菜单。
 * 它会根据body元素的class来判断当前菜单的状态，并采取相应的动画策略。
 */
function SmoothlyMenu() {
    // 如果body没有 'mini-navbar' class (菜单不是最小化状态) 或者 body 有 'body-small' class (屏幕较小)
    if (!$('body').hasClass('mini-navbar') || $('body').hasClass('body-small')) {
        // 为了在最大化菜单时平滑地显示，先隐藏菜单
        $('#side-menu').hide();
        // 使用 setTimeout 来平滑地显示菜单
        setTimeout(
            function () {
                // 淡入效果，持续时间 400 毫秒
                $('#side-menu').fadeIn(400);
            }, 200); // 延迟 200 毫秒执行，给一个过渡时间
    } else if ($('body').hasClass('fixed-sidebar')) { // 如果 body 有 'fixed-sidebar' class (固定侧边栏)
        // 先隐藏菜单
        $('#side-menu').hide();
        // 使用 setTimeout 来平滑地显示菜单
        setTimeout(
            function () {
                // 淡入效果，持续时间 400 毫秒
                $('#side-menu').fadeIn(400);
            }, 100); // 延迟 100 毫秒执行，给一个过渡时间
    } else {
        // 如果不是以上情况，移除 jQuery fadeIn 函数添加的内联样式，重置菜单状态
        // 这样可以避免菜单显示异常
        $('#side-menu').removeAttr('style');
    }
}

/**
 * 修正侧边栏和内容区域的高度
 * 该函数用于确保侧边栏和内容区域（page-wrapper）的高度正确，尤其是在内容较少时，防止页面出现空白。
 * 主要考虑了固定导航栏的情况。
 */
function fix_height() {
    // 计算不包含导航栏的高度
    var heightWithoutNavbar = $("body > #wrapper").height() - 61;
    // 设置侧边栏面板的最小高度
    $(".sidebard-panel").css("min-height", heightWithoutNavbar + "px");

    // 获取导航栏的高度
    var navbarHeigh = $('nav.navbar-default').height();
    // 获取内容区域的高度
    var wrapperHeigh = $('#page-wrapper').height();

    // 如果导航栏高度大于内容区域高度
    if (navbarHeigh > wrapperHeigh) {
        // 设置内容区域的最小高度为导航栏高度
        $('#page-wrapper').css("min-height", navbarHeigh + "px");
    }

    // 如果导航栏高度小于内容区域高度
    if (navbarHeigh < wrapperHeigh) {
        // 设置内容区域的最小高度为窗口高度
        $('#page-wrapper').css("min-height", $(window).height() + "px");
    }

    // 如果body有 'fixed-nav' class (固定导航栏)
    if ($('body').hasClass('fixed-nav')) {
        // 如果导航栏高度大于内容区域高度
        if (navbarHeigh > wrapperHeigh) {
            // 设置内容区域的最小高度为导航栏高度减去一个固定值（通常是导航栏的padding或margin）
            $('#page-wrapper').css("min-height", navbarHeigh - 60 + "px");
        } else {
            // 设置内容区域的最小高度为窗口高度减去一个固定值
            $('#page-wrapper').css("min-height", $(window).height() - 60 + "px");
        }
    }

}

/**
 *  常用操作对象
 *  包含初始化、事件绑定、菜单高亮等常用功能。
 */
var common_ops = {
    /**
     *  初始化函数
     *  调用事件绑定和设置菜单高亮函数。
     */
    init: function () {
        this.eventBind();
        this.setMenuIconHighLight();
    },
    /**
     *  事件绑定函数
     *  绑定菜单最小化按钮的点击事件和窗口的加载、调整大小、滚动事件。
     */
    eventBind: function () {
        // 菜单最小化按钮的点击事件
        $('.navbar-minimalize').click(function () {
            // 切换body的 'mini-navbar' class，用于控制菜单的显示状态
            $("body").toggleClass("mini-navbar");
            // 平滑地显示菜单
            SmoothlyMenu();
        });

        // 窗口加载、调整大小、滚动事件
        $(window).bind("load resize scroll", function () {
            // 如果body没有 'body-small' class (非小屏幕)
            if (!$("body").hasClass('body-small')) {
                // 修正侧边栏和内容区域的高度
                fix_height();
            }
        });
    },
    /**
     *  设置菜单图标高亮函数
     *  根据当前URL路径高亮对应的菜单项。
     */
    setMenuIconHighLight: function () {
        // 如果侧边栏菜单没有菜单项，则直接返回
        if ($("#side-menu li").size() < 1) {
            return;
        }

        // 获取当前URL路径
        var pathname = window.location.pathname;
        // 默认的导航名称
        var nav_name = "default";

        // 根据URL路径判断当前所属的模块，并设置对应的导航名称
        if (pathname.indexOf("/account") > -1) {
            nav_name = "account";
        }

        if (pathname.indexOf("/goods") > -1) {
            nav_name = "goods";
        }

        if (pathname.indexOf("/member") > -1) {
            nav_name = "member";
        }

        if (pathname.indexOf("/finance") > -1) {
            nav_name = "finance";
        }

        if (pathname.indexOf("/qrcode") > -1) {
            nav_name = "market";
        }

        if (pathname.indexOf("/stat") > -1) {
            nav_name = "stat";
        }

        // 如果没有匹配的导航名称，则直接返回
        if (nav_name == null) {
            return;
        }

        // 给当前导航名称对应的菜单项添加 'active' class，实现高亮效果
        $("#side-menu li." + nav_name).addClass("active");
    },
    /**
     *  弹出提示框
     *  @param {string} msg - 提示消息
     *  @param {function} cb - 回调函数，点击确定后执行
     */
    alert: function (msg, cb) {
        // 使用layer插件弹出提示框
        layer.alert(msg, {
            yes: function (index) {
                // 如果回调函数存在，则执行回调函数
                if (typeof cb == "function") {
                    cb();
                }
                // 关闭提示框
                layer.close(index);
            }
        });
    },
    /**
     *  弹出确认框
     *  @param {string} msg - 提示消息
     *  @param {object} callback - 回调函数，包含确定和取消的回调函数
     */
    confirm: function (msg, callback) {
        // 如果没有传递回调函数，则使用默认的空对象
        callback = (callback != undefined) ? callback : {'ok': null, 'cancel': null};
        // 使用layer插件弹出确认框
        layer.confirm(msg, {
            btn: ['确定', '取消'] //按钮
        }, function (index) {
            //确定事件
            // 如果确定回调函数存在，则执行确定回调函数
            if (typeof callback.ok == "function") {
                callback.ok();
            }
            // 关闭确认框
            layer.close(index);
        }, function (index) {
            //取消事件
            // 如果取消回调函数存在，则执行取消回调函数
            if (typeof callback.cancel == "function") {
                callback.cancel();
            }
            // 关闭确认框
            layer.close(index);
        });
    },
    /**
     *  显示提示信息
     *  @param {string} msg - 提示消息
     *  @param {object} target - 目标元素，提示信息将显示在该元素附近
     */
    tip: function (msg, target) {
        // 使用layer插件在目标元素附近显示提示信息
        layer.tips(msg, target, {
            tips: [3, '#e5004f'] // 提示信息的位置和颜色
        });
        // 滚动页面到目标元素的位置
        $('html, body').animate({
            scrollTop: target.offset().top - 10
        }, 100);
    },
    /**
     *  构建URL
     *  @param {string} path - URL路径
     *  @param {object} params - URL参数
     *  @return {string} - 构建后的URL
     */
    buildUrl: function (path, params) {
        var url = "" + path;
        var _paramUrl = "";
        // 如果有参数
        if (params) {
            // 将参数对象转换为URL参数字符串
            _paramUrl = Object.keys(params).map(function (key) {
                return [encodeURIComponent(key), encodeURIComponent(params[key])].join('=');
            }).join('&');

            _paramUrl = "?" + _paramUrl;
        }
        // 返回完整的URL
        return url + _paramUrl;
    },
    /**
     *  构建图片URL
     *  @param {string} img_key - 图片Key
     *  @return {string} - 构建后的图片URL
     */
    buildPicUrl: function (img_key) {
        // 获取域名和图片URL前缀
        var domain = $(".hidden_layout_wrap input[name='domain']").val();
        var prefix_url = $(".hidden_layout_wrap input[name='prefix_url']").val();
        // 返回完整的图片URL
        return domain + prefix_url + img_key;
    }
};

// 文档加载完成后的事件
$(document).ready(function () {
    // 初始化 common_ops 对象
    common_ops.init();
});

// 对Date的扩展，将 Date 转化为指定格式的String
// 月(M)、日(d)、小时(h)、分(m)、秒(s)、季度(q) 可以用 1-2 个占位符，
// 年(y)可以用 1-4 个占位符，毫秒(S)只能用 1 个占位符(是 1-3 位的数字)
// 例子：
// (new Date()).Format("yyyy-MM-dd hh:mm:ss.S") ==> 2006-07-02 08:09:04.423
// (new Date()).Format("yyyy-M-d h:m:s.S")      ==> 2006-7-2 8:9:4.18
/**
 * Date对象的格式化方法
 * @param {string} fmt - 格式字符串
 * @return {string} - 格式化后的日期字符串
 */
Date.prototype.Format = function (fmt) { //author: meizz
    var o = {
        "M+": this.getMonth() + 1,                 //月份
        "d+": this.getDate(),                    //日
        "h+": this.getHours(),                   //小时
        "m+": this.getMinutes(),                 //分
        "s+": this.getSeconds(),                 //秒
        "q+": Math.floor((this.getMonth() + 3) / 3), //季度
        "S": this.getMilliseconds()             //毫秒
    };
    // 如果格式字符串包含年份
    if (/(y+)/.test(fmt))
        // 替换年份
        fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
    // 循环替换其他占位符
    for (var k in o)
        // 如果格式字符串包含当前占位符
        if (new RegExp("(" + k + ")").test(fmt))
            // 替换占位符
            fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
    // 返回格式化后的日期字符串
    return fmt;
};