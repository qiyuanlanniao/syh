// pages/activity/index.js
Page({
    data: {
        activities: [
            {
                id: 1,
                mainTitle: "逐浪揽山",
                subTitle: "海岛极限双环赛",
                time: "春季赛",
                image: "/images/activity/spring.jpg", // 确保图片路径正确
                description: "春暖花开，万物复苏，在生机盎然的季节挑战自我！",
                externalLink: "https://www.wjx.cn/vm/OlDwb82.aspx" // <-- 在这里添加
            },
            {
                id: 2,
                mainTitle: "逐浪揽山",
                subTitle: "海岛极限双环赛",
                time: "夏季赛",
                image: "/images/activity/summer.jpg", // 确保图片路径正确
                description: "炎炎夏日，激情似火，在海风的吹拂下突破极限！",
                externalLink: "https://www.wjx.cn/vm/OlDwb82.aspx" // <-- 在这里添加
            },
            {
                id: 3,
                mainTitle: "逐浪揽山",
                subTitle: "海岛极限双环赛",
                time: "秋季赛",
                image: "/images/activity/autumn.jpg", // 确保图片路径正确
                description: "金秋送爽，气候宜人，在诗情画意的海岛尽情驰骋！",
                externalLink: "https://www.wjx.cn/vm/OlDwb82.aspx" // <-- 在这里添加
            },
            {
                id: 4,
                mainTitle: "逐浪揽山",
                subTitle: "海岛极限双环赛",
                time: "冬季赛",
                image: "/images/activity/winter.jpg", // 确保图片路径正确
                description: "冬日暖阳，独特风光，在沉静的海岛感受非凡挑战！",
                externalLink: "https://www.wjx.cn/vm/OlDwb82.aspx" // <-- 在这里添加
            }
        ]
    },

    onLoad: function (options) {
        // 页面加载时的逻辑
    },

    // 假设点击“查看详情”会跳转到某个详情页
    goToDetail: function (e) {
        // 获取点击的活动ID
        const activityId = e.currentTarget.dataset.id;
        // 根据ID找到对应的活动数据，获取其 externalLink
        const activity = this.data.activities.find(item => item.id === activityId);

        if (activity && activity.externalLink) {
            // 编码外部链接，作为参数传递给 webview 页面
            const encodedUrl = encodeURIComponent(activity.externalLink);
            wx.navigateTo({
                url: `/pages/webview/index?url=${encodedUrl}`
            });
        } else {
            console.error("活动链接不存在或未定义");
            // 可以给用户一个提示，例如：
            wx.showToast({
                title: '活动详情加载失败',
                icon: 'none',
                duration: 2000
            });
        }
    }
})