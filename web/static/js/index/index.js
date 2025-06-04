// static/js/index/index.js

; // 空语句，防止某些情况下代码压缩出现问题

// 定义 dashboard_index_ops 对象，包含仪表盘首页相关的操作
var dashboard_index_ops = {
    // 初始化函数
    init:function(){
        this.drawChart(); // 调用 drawChart 函数，绘制图表
    },
    // 绘制图表函数
    drawChart:function(){

        // 发送 AJAX 请求，获取仪表盘数据
        $.ajax({
            url:common_ops.buildUrl("/chart/dashboard"), // 请求地址，通过 common_ops.buildUrl 构建，指向 /chart/dashboard
            dataType:'json', // 设置数据类型为 JSON
            success:function( res ){ // 请求成功的回调函数，res 为服务器返回的数据
                if(res.code === 200 && res.data){ // 判断返回的 code 是否为 200，以及是否包含 data 数据
                    index_charts_ops.drawLine( $('#member_order'), res.data, 'areaspline' ); // 调用 index_charts_ops.drawLine 函数绘制图表
                    // 参数：
                    //   $('#member_order')：图表渲染的目标 DOM 元素，选择器为 #member_order
                    //   res.data：图表数据
                    //   'areaspline'：图表类型，设置为 areaspline，即区域样条图，使视觉冲击力更强

                } else { // 如果返回的 code 不是 200 或者没有 data 数据
                    $('#member_order').html('<div style="text-align: center; padding-top: 50px; color: var(--light-blue-text);">暂无营收/订单数据</div>'); // 在 #member_order 元素中显示提示信息
                    console.error("Failed to load dashboard chart data:", res.msg); // 在控制台输出错误信息，方便调试
                }
            },
            error: function(xhr, status, error) { // 请求失败的回调函数
                $('#member_order').html('<div style="text-align: center; padding-top: 50px; color: var(--light-blue-text);">加载数据失败</div>'); // 在 #member_order 元素中显示提示信息
                console.error("AJAX error loading dashboard chart:", status, error); // 在控制台输出错误信息，方便调试
            }
        });

        // 发送 AJAX 请求，获取财务数据
        $.ajax({
            url:common_ops.buildUrl("/chart/finance"), // 请求地址，通过 common_ops.buildUrl 构建，指向 /chart/finance
            dataType:'json', // 设置数据类型为 JSON
            success:function( res ){ // 请求成功的回调函数，res 为服务器返回的数据
                 if(res.code === 200 && res.data){ // 判断返回的 code 是否为 200，以及是否包含 data 数据
                    index_charts_ops.drawLine( $('#finance'), res.data, 'spline' ); // 调用 index_charts_ops.drawLine 函数绘制图表
                    // 参数：
                    //   $('#finance')：图表渲染的目标 DOM 元素，选择器为 #finance
                    //   res.data：图表数据
                    //   'spline'：图表类型，设置为 spline，即样条图，保持财务数据图表的简洁性

                 } else { // 如果返回的 code 不是 200 或者没有 data 数据
                    $('#finance').html('<div style="text-align: center; padding-top: 50px; color: var(--light-blue-text);">暂无财务数据</div>'); // 在 #finance 元素中显示提示信息
                    console.error("Failed to load finance chart data:", res.msg); // 在控制台输出错误信息，方便调试
                 }
            },
            error: function(xhr, status, error) { // 请求失败的回调函数
                $('#finance').html('<div style="text-align: center; padding-top: 50px; color: var(--light-blue-text);">加载数据失败</div>'); // 在 #finance 元素中显示提示信息
                console.error("AJAX error loading finance chart:", status, error); // 在控制台输出错误信息，方便调试
            }
        });
    }
};

// 文档加载完成后执行
$(document).ready( function(){
    dashboard_index_ops.init(); // 调用 dashboard_index_ops.init 函数，初始化仪表盘首页
});