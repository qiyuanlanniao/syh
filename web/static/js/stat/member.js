;
var stat_member_ops = {
    /**
     * 初始化函数，页面加载完成后执行
     */
    init:function(){
        this.eventBind(); // 绑定事件
        this.datetimepickerComponent(); // 初始化日期选择器组件
    },

    /**
     * 事件绑定函数，用于绑定页面元素的事件
     */
    eventBind:function(){
        // 当id为 "search_form_wrap" 下的 class 为 "search" 的元素被点击时
        $("#search_form_wrap .search").click( function(){
            // 提交 id 为 "search_form_wrap" 的表单
            $("#search_form_wrap").submit();
        });
    },

    /**
     * 日期选择器组件初始化函数，用于初始化日期选择器插件
     */
    datetimepickerComponent:function() {
        var that = this; // 保存当前对象this，避免在回调函数中this指向改变
        $.datetimepicker.setLocale('zh'); // 设置日期选择器的语言为中文

        // 配置日期选择器的参数
        params = {
            scrollInput: false,  // 禁止滚动输入
            scrollMonth: false, // 禁止滚动选择月份
            scrollTime: false,  // 禁止滚动选择时间
            dayOfWeekStart: 1,   // 设置一周的第一天为星期一
            lang: 'zh',         // 设置语言为中文
            todayButton: true,   // 显示回到今天的按钮
            defaultSelect: true, // 默认选中
            defaultDate: new Date().Format('yyyy-MM-dd'), // 设置默认日期为今天，并格式化为 yyyy-MM-dd
            format: 'Y-m-d',     // 设置日期格式为 yyyy-MM-dd
            timepicker: false    // 禁用时间选择器
        };

        // 初始化 id 为 "search_form_wrap" 下 name 为 "date_from" 的输入框为日期选择器，并传入参数params
        $('#search_form_wrap input[name=date_from]').datetimepicker(params);

        // 初始化 id 为 "search_form_wrap" 下 name 为 "date_to" 的输入框为日期选择器，并传入参数params
        $('#search_form_wrap input[name=date_to]').datetimepicker(params);
    }
};

/**
 * 页面加载完成后执行的函数
 */
$(document).ready( function(){
    stat_member_ops.init(); // 调用 stat_member_ops 对象的 init 方法
});