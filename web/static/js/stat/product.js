;
var stat_product_ops = {
    // 初始化函数
    init:function(){
        // 绑定事件
        this.eventBind();
        // 初始化日期选择器组件
        this.datetimepickerComponent();
    },
    // 事件绑定函数
    eventBind:function(){
        // 绑定搜索按钮的点击事件
        $("#search_form_wrap .search").click( function(){
            // 提交搜索表单
            $("#search_form_wrap").submit();
        });
    },
    // 日期选择器组件初始化函数
    datetimepickerComponent:function() {
        var that = this; // 保存this指针，方便在回调函数中使用
        $.datetimepicker.setLocale('zh'); // 设置日期选择器的语言为中文

        // 日期选择器参数配置
        params = {
            scrollInput: false, // 禁用滚动输入
            scrollMonth: false, // 禁用滚动月份
            scrollTime: false, // 禁用滚动时间
            dayOfWeekStart: 1, // 设置一周的第一天为星期一 (0是周日，1是周一)
            lang: 'zh', // 设置语言为中文
            todayButton: true,// 添加 "回到今天" 按钮
            defaultSelect: true, // 默认选中
            defaultDate: new Date().Format('yyyy-MM-dd'), // 设置默认日期为今天，这里使用了Date对象的扩展方法Format
            format: 'Y-m-d',// 格式化显示日期为 年-月-日
            timepicker: false // 禁用时间选择器
        };

        // 初始化 "开始日期" 日期选择器
        $('#search_form_wrap input[name=date_from]').datetimepicker(params);
        // 初始化 "结束日期" 日期选择器
        $('#search_form_wrap input[name=date_to]').datetimepicker(params);
    }
};

// 页面加载完成后执行
$(document).ready( function(){
    // 调用统计产品操作对象的初始化函数
    stat_product_ops.init();
});