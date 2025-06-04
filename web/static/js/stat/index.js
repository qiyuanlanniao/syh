;
var stat_index_ops = {
    // 初始化函数
    init:function(){
        // 绑定事件
        this.eventBind();
        // 绘制图表
        this.drawChart();
        // 初始化日期时间选择器组件
        this.datetimepickerComponent();
    },
    // 事件绑定函数
    eventBind:function(){
        // 找到搜索表单包裹器中的搜索按钮，并绑定点击事件
        $("#search_form_wrap .search").click( function(){
            // 点击搜索按钮时，提交搜索表单
            $("#search_form_wrap").submit();
        });
    },
    // 日期时间选择器组件初始化函数
    datetimepickerComponent:function(){
        // 保存this的引用，以便在回调函数中使用
        var that = this;
        // 设置日期时间选择器的语言为中文
        $.datetimepicker.setLocale('zh');
        // 定义日期时间选择器的参数
        params = {
            // 禁用滚动输入
            scrollInput: false,
            // 禁用滚动月份
            scrollMonth: false,
            // 禁用滚动时间
            scrollTime: false,
            // 设置一周的第一天为星期一
            dayOfWeekStart: 1,
            // 设置语言为中文
            lang: 'zh',
            // 显示回到今天的按钮
            todayButton: true,
            // 默认选中今天
            defaultSelect: true,
            // 默认日期为今天
            defaultDate: new Date().Format('yyyy-MM-dd'),
            // 格式化显示日期为 YYYY-MM-DD
            format: 'Y-m-d',
            // 禁用时间选择器
            timepicker: false
        };
        // 初始化开始日期选择器
        $('#search_form_wrap input[name=date_from]').datetimepicker(params);
        // 初始化结束日期选择器
        $('#search_form_wrap input[name=date_to]').datetimepicker(params);

    },
    // 绘制图表函数
    drawChart:function(){
        // 设置图表选项（调用 charts_ops 对象的 setOption 方法）
        charts_ops.setOption();
        // 发送 AJAX 请求获取图表数据
        $.ajax({
            // 请求的 URL，通过 common_ops.buildUrl 构建，指向 /chart/finance 接口
            url:common_ops.buildUrl("/chart/finance"),
            // 设置数据类型为 JSON
            dataType:'json',
            // 请求成功后的回调函数
            success:function( res ){
                // 调用 charts_ops 对象的 drawLine 方法，绘制折线图
                // 参数：
                //   - $('#container')：图表容器的 jQuery 对象
                //   - res.data：从服务器返回的数据
                charts_ops.drawLine( $('#container'),res.data )
            }
        });
    }
};

// 文档加载完毕后执行的函数
$(document).ready( function(){
    // 调用 stat_index_ops 对象的 init 方法，初始化统计首页
    stat_index_ops.init();
});