;
var finance_index_ops = {
    // 初始化函数
    init:function(){
        // 调用事件绑定函数
        this.eventBind();
    },
    // 事件绑定函数
    eventBind:function(){
        // 将this赋值给that，解决作用域问题，方便在匿名函数中使用finance_index_ops对象
        var that = this;
        // 监听类名为"wrap_search"的元素下的name属性为"status"的select元素的change事件
        $(".wrap_search select[name=status]").change( function(){
            // 当select元素的值发生改变时，提交类名为"wrap_search"的form表单
            $(".wrap_search").submit();
        });
    }
};

// DOM加载完成后执行的函数
$(document).ready( function(){
    // 调用finance_index_ops对象的init方法，进行初始化
    finance_index_ops.init();
});