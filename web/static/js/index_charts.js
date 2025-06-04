// static/js/index_charts.js
;
//  定义一个对象 index_charts_ops，用于管理首页图表的配置和绘制。
var index_charts_ops = {
    // setOption 函数：用于设置 Highcharts 的全局默认配置。
    setOption:function(){
        // 调用 Highcharts.setOptions 方法，设置全局配置。
        Highcharts.setOptions({
            // chart 属性：定义图表的基本外观。
            chart: {
                backgroundColor: 'transparent', // 将图表背景设置为透明。
                style: {
                    fontFamily: 'Arial, sans-serif', // 设置字体为 Arial 或 sans-serif。
                    color: '#A0D0E8' // 设置图表默认文本颜色为淡蓝色。
                },
                // Add subtle chart border (optional)
                // borderColor: 'rgba(160, 208, 232, 0.1)',  // 可选：添加细微的图表边框，使用淡蓝色。
                // borderWidth: 1, // 边框宽度为 1 像素。
                borderRadius: 8 // 将图表圆角半径设置为 8 像素，与容器的圆角半径匹配。
            },
            // exporting 属性：配置导出功能。
            exporting: {
                enabled: false // 禁用导出按钮。
            },
            // legend 属性：配置图例。
            legend: {
                enabled: true, // 启用图例。
                align: 'right', // 将图例对齐到右侧。
                verticalAlign: 'top', // 将图例垂直对齐到顶部。
                x: 0, // 图例的水平偏移量。
                y: -15, // 图例的垂直偏移量，向上移动 15 像素。
                itemStyle: {
                    color: '#A0D0E8', // 设置图例文本颜色为淡蓝色。
                    fontSize: '13px' // 设置图例字体大小为 13 像素。
                },
                itemHoverStyle: {
                    color: '#FFFFFF' // 设置图例鼠标悬停时的文本颜色为白色。
                }
            },
            // credits 属性：配置版权信息。
            credits:{
                enabled:false // 禁用 Highcharts 的版权信息。
            },
            // Define a custom blue color palette
            // 定义一个自定义的蓝色调色板，用于图表颜色。
            colors:[
                '#87CEFA', // 天蓝色（主色）。
                '#A0D0E8', // 淡蓝色。
                '#FFFFFF', // 白色（用于对比或第二个系列）。
                '#50B432', // 谨慎使用，用于在需要时进行对比。
                '#ED561B',
                '#058DC7',
                '#64E572',
                '#FF9655',
                '#FFF263',
                '#6AF9C4'
            ],
            // title 属性：配置图表标题。
            title: {
                text: '', // 通过 HTML 处理标题，此处不设置。
                style: {
                    color: '#FFFFFF', // 设置标题颜色为白色。
                    fontSize: '18px' // 设置标题字体大小为 18 像素。
                }
            },
            // xAxis 属性：配置 X 轴。
            xAxis: {
                tickWidth: 0, // 移除刻度。
                lineWidth: 1, // 设置轴线宽度为 1 像素。
                lineColor: 'rgba(160, 208, 232, 0.2)', // 设置轴线颜色为淡蓝色，透明度为 0.2。
                gridLineColor: 'rgba(160, 208, 232, 0.1)', // 设置网格线颜色为淡蓝色，透明度为 0.1。
                gridLineWidth: 1, // 设置网格线宽度为 1 像素。
                crosshair: {
                    width: 1, // 设置十字线宽度为 1 像素。
                    color: '#87CEFA', // 设置十字线颜色为天蓝色。
                    dashStyle: 'dash' // 设置十字线样式为虚线。
                },
                labels: {
                    style: {
                        color: '#A0D0E8', // 设置轴标签颜色为淡蓝色。
                        fontSize: '12px' // 设置轴标签字体大小为 12 像素。
                    }
                }
            },
            // yAxis 属性：配置 Y 轴。
            yAxis: {
                gridLineColor: 'rgba(160, 208, 232, 0.1)', // 设置网格线颜色为淡蓝色，透明度为 0.1。
                gridLineWidth: 1, // 设置网格线宽度为 1 像素。
                title: {
                     text: '', // 默认情况下移除 Y 轴标题。
                     style: {
                          color: '#FFFFFF'
                     }
                },
                labels: {
                    style: {
                        color: '#A0D0E8', // 设置轴标签颜色为淡蓝色。
                        fontSize: '12px' // 设置轴标签字体大小为 12 像素。
                    }
                }
            },
            // plotOptions 属性：配置绘图选项，影响数据系列的显示方式。
            plotOptions: {
                // series 属性：配置所有数据系列的通用选项。
                series: {
                    marker: {
                        enabled: false, // 默认情况下隐藏数据点标记。
                        radius: 5, // 设置标记半径为 5 像素。
                        lineColor: '#FFFFFF', // 设置标记边框颜色为白色。
                        lineWidth: 2, // 设置标记边框宽度为 2 像素。
                        symbol: 'circle', // 使用圆形作为标记符号。
                        states: {
                            hover: {
                                enabled: true, // 鼠标悬停时显示标记。
                                radius: 7 // 鼠标悬停时，标记半径增大到 7 像素。
                            }
                        }
                    },
                    states: {
                        hover: {
                            lineWidthPlus: 0, // 鼠标悬停时，防止线条变粗。
                            halo: { // 添加微妙的光晕效果。
                                size: 15, // 光晕大小。
                                attributes: {
                                    fill: Highcharts.color('#87CEFA').brighten(0.5).setOpacity(0.3).get() // 天蓝色，提亮 0.5 倍，透明度为 0.3。
                                }
                            }
                        }
                    },
                    animation: { // 添加明显的动画效果。
                       duration: 1800, // 动画持续时间为 1.8 秒。
                       easing: 'easeOutQuint' // 使用更戏剧性的缓动函数。
                    },
                    shadow: true // 为系列添加微妙的阴影。
                },
                // line 属性：配置折线图的特定选项。
                 line: {
                    lineWidth: 3, // 设置折线宽度为 3 像素。
                    // Optional: Add data labels on hover or always for炫技
                    // dataLabels: { enabled: true, style: { color: '#FFFFFF' } }
                 },
                 // spline 属性：配置样条曲线图的特定选项。
                 spline: { // 使用样条曲线，如原始代码。
                    lineWidth: 3, // 设置样条曲线宽度为 3 像素。
                     // Make it an area spline for more visual impact (optional)
                     fillOpacity: 0.2, // 添加半透明填充。
                     threshold: null // 区域图需要将阈值设置为 null，才能显示负值区域。
                 }
            },
            // tooltip 属性：配置提示框。
            tooltip: {
                backgroundColor: 'rgba(26, 63, 97, 0.9)', // 设置提示框背景颜色为深蓝色，透明度为 0.9。
                borderColor: 'rgba(135, 206, 250, 0.4)', // 设置提示框边框颜色为淡蓝色，透明度为 0.4。
                borderWidth: 1, // 设置提示框边框宽度为 1 像素。
                borderRadius: 8, // 设置提示框圆角半径为 8 像素，与容器的圆角半径匹配。
                shadow: true, // 为提示框添加阴影。
                headerFormat: '<span style="font-size: 12px; color: #87CEFA; font-weight: bold;">{point.key}</span><br/>', // 设置提示框头部格式，显示 X 轴值，颜色为天蓝色，加粗。
                pointFormat: '<span style="color:{point.color}">\u25CF</span> <span style="color:#FFFFFF;">{series.name}</span>: <b>{point.y}</b><br/>', // 设置提示框数据点格式，显示系列名称和 Y 轴值，系列名称颜色为白色，Y 轴值加粗。
                footerFormat: '', // 设置提示框尾部格式为空。
                shared: true, // 设置提示框为共享模式，鼠标悬停时显示所有系列的数据。
                useHTML: false, // 不使用 HTML 格式化提示框内容。
                style: {
                    color: '#FFFFFF', // 设置提示框文本颜色为白色。
                    padding: '10px', // 设置提示框内边距为 10 像素。
                    fontSize: '13px', // 设置提示框字体大小为 13 像素。
                    lineHeight: '18px' // 设置提示框行高为 18 像素，增加间距。
                }
            },
            // lang 属性：配置语言设置。
            lang: {
                noData: "暂无数据" // 设置没有数据时显示的文本。
            },
            // noData 属性：配置没有数据时的显示样式。
            noData: {
                style: {
                    fontWeight: 'bold', // 设置字体为粗体。
                    fontSize: '20px', // 设置字体大小为 20 像素。
                    color: '#A0D0E8' // 设置颜色为淡蓝色。
                }
            }
        });
    },
    // drawLine 函数：用于绘制折线图或样条曲线图。
    drawLine:function( target ,data, type = 'spline' ){ // Added type parameter
        // target: 要绘制图表的 HTML 元素的选择器。
        // data: 包含图表数据，包括 X 轴类别和数据系列。
        // type: 图表类型，默认为 'spline' (样条曲线)，可以设置为 'line'（折线）或者 'areaspline'(区域样条曲线)

        // 调用 jQuery Highcharts 插件，绘制图表。
        var chart =  target.highcharts({
            // chart 属性：配置图表的基本外观。
            chart: {
                type: type // 使用指定的类型 (spline 或者 areaspline)。
            },
            // xAxis 属性：配置 X 轴。
            xAxis: {
                categories: data.categories // 设置 X 轴类别为数据中的类别。
            },
            // series 属性：配置数据系列。
            series: data.series, // 设置数据系列为数据中的系列。
            // 可以在此处添加特定的图表选项，覆盖全局 setOption 中的设置。
        });
        // 返回图表对象。
        return chart;
    }
};

// 在脚本加载时立即设置全局选项。
index_charts_ops.setOption();