;
// 画图通用组件，虽然估计很难统一，但是总要走出第一步了
var charts_ops = {
    /**
     * 设置 Highcharts 的全局默认配置
     * 这个函数会覆盖 Highcharts.setOptions()，定义图表的基础样式
     */
    setOption:function(){
        Highcharts.setOptions({
            chart: {
                // 图表整体配置，可以进一步配置背景色、边框等
            },
            exporting: {
                enabled: false // 禁用导出功能，默认是启用的，会在图表右上角显示导出按钮
            },
            legend: {
                //enabled:false // 是否显示图例，默认为 true
            },
            credits:{
                enabled:false // 禁用版权信息，默认是启用的，会在图表右下角显示 Highcharts 的链接
            },
            colors:['#24CBE5', '#50B432', '#ED561B', '#DDDF00',
                '#058DC7', '#64E572', '#FF9655', '#FFF263', '#6AF9C4','#E93EFF'], // 定义图表颜色，循环使用
            title: '', // 图表标题，这里设置为空，可以在具体图表中单独设置
            xAxis: {
                tickWidth:0, // 刻度线宽度，设置为 0 表示不显示刻度线
                lineWidth: 0, // x 轴线宽度，设置为 0 表示不显示 x 轴线
                gridLineColor: '#eee', // 网格线颜色
                //gridLineWidth: 1, // 网格线宽度
                crosshair: {
                    width: 1, // 鼠标悬浮时的交叉线宽度
                    color: '#ebebeb' // 鼠标悬浮时的交叉线颜色
                }
            },
            yAxis: {
                gridLineColor: '#eee', // 网格线颜色
                gridLineWidth: 1, // 网格线宽度
                title: '' // y 轴标题，这里设置为空，可以在具体图表中单独设置
            },
            plotOptions: {
                column: {
                    pointPadding: 0.2, // 柱子之间的间距
                    pointWidth: 20, // 柱子宽度
                    borderWidth: 0 // 柱子边框宽度，设置为 0 表示不显示边框
                },
                series: {
                    marker: {
                        enabled: false // 是否显示数据点标记，设置为 false 表示不显示
                    },
                },
                line: {
                    lineWidth: 2, // 折线宽度
                    states: {
                        hover: {
                            lineWidth: 2 // 鼠标悬浮时的折线宽度
                        }
                    }
                }
            },
            tooltip: {
                backgroundColor: '#404750', // 提示框背景色
                borderWidth: 0, // 提示框边框宽度
                shadow: false, // 提示框阴影
                headerFormat: '', // 提示框头部格式，这里设置为空，表示不显示头部
                footerFormat: '', // 提示框底部格式，这里设置为空，表示不显示底部
                shared: true, // 是否共享提示框，当鼠标悬浮在多个数据点上时，是否显示所有数据点的提示信息
                useHTML: true, // 是否使用 HTML 格式化提示框内容
                style: {
                    color: '#fff', // 提示框文字颜色
                    padding: '5px' // 提示框内边距
                }
            },
            lang: {
                noData: "暂无数据" // 无数据时显示的文字
            },
            noData: {
                style: {
                    fontWeight: 'bold', // 无数据时文字粗细
                    fontSize: '15px', // 无数据时文字大小
                    color: '#303030' // 无数据时文字颜色
                }
            }
        });
    },

    /**
     * 画直线（折线图）
     * @param {object} target  图表容器的 jQuery 对象
     * @param {object} data  图表数据，包含 categories (x 轴分类) 和 series (数据系列)
     * @returns {object}  Highcharts 图表对象
     */
    drawLine:function( target ,data ){//画直线
        var chart =  target.highcharts({
            chart: {
                type: 'spline' // 图表类型为 spline (平滑曲线)
            },
            xAxis: {
                categories: data.categories // x 轴分类数据
            },
            series: data.series, // 数据系列
            legend: {
                enabled:true, // 是否显示图例
                align: 'right', // 图例水平对齐方式
                verticalAlign: 'top', // 图例垂直对齐方式
                x: 0, // 图例水平偏移量
                y: -15 // 图例垂直偏移量
            }
        });
        return chart; // 返回 Highcharts 图表对象，方便后续操作
    }
};