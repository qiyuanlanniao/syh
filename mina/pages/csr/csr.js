// pages/csr/csr.js
// 获取小程序全局应用实例
const app = getApp();
// 定义用于本地缓存Bandit算法相关数据的键名
const CACHE_BANDIT_DATA_KEY = "csr_bandit_data";

// --- 导入本地商品数据 ---
// 确保同目录下存在 products_data.js 文件，并且该文件导出了一个名为 products 的对象
const PRODUCTS_DATA = require('../../utils/products_data.js'); // <-- 在此导入数据

// --- 前端常量定义 ---
const GAODE_API_KEY = ""; //
const CITY_CODE = ""; //

// 可提供的饮品列表，按温度分为热饮、冷饮和中性饮品
const AVAILABLE_DRINKS = {
    "hot": ["热可可", "奶茶", "咖啡", "姜茶"],       // 适合低温天气
    "cold": ["冰镇果汁", "冷泡茶", "冰咖啡", "椰汁", "汽水"], // 适合高温天气
    "neutral": ["常温矿泉水", "花草茶"]             // 适合中等温度天气
};

const learningRate = 0.1;

// 不适合划船的天气条件列表
const unsuitableWeatherConditionsForRowing = [
    // 降水类 (根据您的 includes 条件判断)
    "阵雨", "雷阵雨", "雷阵雨并伴有冰雹", "小雨", "中雨", "大雨", "暴雨", "大暴雨", "特大暴雨",
    "强阵雨", "强雷阵雨", "极端降雨", "毛毛雨/细雨", "雨", "小雨-中雨", "中雨-大雨",
    "大雨-暴雨", "暴雨-大暴雨", "大暴雨-特大暴雨", "雨雪天气", "雨夹雪", "阵雨夹雪", "冻雨",
    // 降雪类 (根据您的 includes 条件判断)
    "雪", "阵雪", "小雪", "中雪", "大雪", "暴雪", "小雪-中雪", "中雪-大雪", "大雪-暴雪",
    // 强风类
    "有风", "强风/劲风", "疾风", "大风", "烈风", "风暴", "狂爆风", "飓风", "龙卷风",
    // 低能见度类
    "霾", "中度霾", "重度霾", "严重霾", "浮尘", "扬沙", "沙尘暴", "强沙尘暴",
    "雾", "浓雾", "强浓雾", "轻雾", "大雾", "特强浓雾",
];


Page({
    // 页面的初始数据
    data: {
        messages: [], // 聊天消息列表，用于展示对话内容
        scrollToView: '', // 滚动到视图的元素ID，用于控制聊天记录滚动到底部
        showTagInput: false, // 是否显示标签输入框
        products: PRODUCTS_DATA, // 从products_data.js导入的商品数据
        availableTags: [], // 从商品数据中提取的所有可用标签列表
        tagToProductsIndex: null, // 标签到商品名称列表的映射，用于快速查找包含特定标签的商品
        Q: {}, // Bandit算法中的Q值 (Action-Value)，存储每个商品的预期回报的估计
        N: {}, // Bandit算法中的N值，存储每个商品（臂）被选择（拉动）的次数
        likedTags: [], // 用户选择的偏好标签列表
        recommendedProductsAll: [], // 所有历史推荐过的商品名称列表 (用于避免短期内重复推荐相同的商品)
        recommendationCycleCount: 0, // 当前推荐轮次计数，用于Epsilon-greedy策略中的epsilon衰减
        shoppingCart: [], // 购物车，存储用户选择的商品对象，每个对象包含 {id, name}

        initialEpsilon: 0.5, // Epsilon-greedy策略的初始探索率 (epsilon)
        epsilonDecayRate: 0.005, // Epsilon-greedy策略的探索率衰减率
        minEpsilon: 0.05, // Epsilon-greedy策略的最小探索率
        topN: 3, // 每次推荐的商品数量

        tagSimilarityThreshold: 0.5, // 标签相似度阈值，用于在用户输入无效标签时推荐相似的有效标签
        maxSuggestedTags: 3, // 当用户输入无效标签时，最多建议的相似标签数量
        currentTagInput: '', // 当前标签输入框中的文本内容
        availableTagsSample: '', // 可用标签的示例字符串，用于在输入框下方提示用户
        currentRecommendationsForFeedback: [], // <--- 新增：存储当前展示的推荐商品列表，用于反馈
        hasInteractedWithCurrentRecommendations: false, // <--- 新增：标记当前批次推荐是否已被用户交互 (加入心仪商品)
    },

    /**
     * 生命周期函数--监听页面加载
     * 当页面加载时被调用，通常用于初始化数据、加载资源等。
     */
    onLoad: function () {
        // 添加系统欢迎消息
        this.addMessage('system', '汪！欢迎来到山屿海营地，我是营地的拉布拉多——"雪碧"！由我为您提供推荐服务。');
        // 添加狗狗图片消息
        this.addMessage('system', '', {type: 'image', content: '../../images/dog.png'});
        // 加载本地存储的Bandit算法数据 (Q值和N值)
        this.loadBanditData();
        // 处理导入的商品数据，提取标签、构建索引等
        this.processProductsData();
        // 异步获取天气信息和推荐饮品，并处理可能发生的错误
        this.getWeatherAndDrinks().catch(() => {
            console.warn("Weather/Drinks failed, proceeding."); // 在控制台记录警告，但程序继续执行
        });
    },

    /**
     * 生命周期函数--监听页面初次渲染完成
     * 当页面初次渲染完成后被调用，此时视图层已经准备好，可以进行界面操作。
     */
    onReady: function () {
        // 将聊天界面滚动到底部，确保最新消息可见
        this.scrollToBottom();
    },

    /**
     * 生命周期函数--监听页面显示
     * 当页面显示或从后台切回前台时被调用。
     */
    onShow: function () {
        // 每次页面显示时都尝试滚动到底部，以防有新消息或页面重新进入
        this.scrollToBottom();
    },

    /**
     * 生命周期函数--监听页面卸载
     * 当页面卸载（如关闭或跳转到其他非tabBar页面）时被调用。
     */
    onUnload: function () {
        // 在页面卸载前保存当前的Bandit数据到本地缓存
        this.saveBanditData();
    },

    /**
     * 向消息列表添加新消息，并自动滚动到底部。
     * @param {string} type - 消息类型 ('system', 'user')
     * @param {string} text - 消息文本内容
     * @param {Object|null} data - 附加数据，可选，例如图片、天气、推荐等特定类型的消息内容
     */
    addMessage: function (type, text, data = null) {
        // 创建新消息对象，包含类型、文本、附加数据和时间戳（用作唯一key）
        const newMessage = {type, text, data, timestamp: Date.now()};
        // 更新页面的messages数据，将新消息追加到列表末尾
        // 使用回调函数确保在setData完成后执行滚动操作
        this.setData({messages: [...this.data.messages, newMessage]}, () => this.scrollToBottom());
    },

    /**
     * 将聊天界面滚动到底部，使最新消息可见。
     */
    scrollToBottom: function () {
        // 使用setTimeout确保滚动操作在DOM更新之后执行，避免找不到元素
        setTimeout(() => {
            if (this.data.messages.length > 0) {
                // 如果有消息，则滚动到最后一条消息的位置
                // `msg-${timestamp}` 是对应消息wxml元素的id
                this.setData({scrollToView: `msg-${this.data.messages[this.data.messages.length - 1].timestamp}`});
            } else {
                // 如果没有消息，理论上不需要滚动，但可以设置一个通用的底部锚点（如果存在）
                this.setData({scrollToView: 'bottom'}); // 假设有一个id为'bottom'的元素作为底部锚点
            }
        }, 100); // 延迟100毫秒
    },

    /**
     * 处理导入的商品数据：提取可用标签、构建标签到商品的索引、初始化Bandit数据。
     */
    processProductsData: function () {
        const products = this.data.products; // 获取商品数据
        // 检查商品数据是否有效
        if (!products || Object.keys(products).length === 0) {
            console.warn("Imported products data is empty."); // 控制台警告
            this.addMessage('system', '商品数据为空，无法提供商品推荐服务。'); // 提示用户
            this.setData({showTagInput: false}); // 隐藏标签输入框
            this.initializeBanditData({}); // 使用空商品数据初始化Bandit（实际上会清空）
            this.setData({tagToProductsIndex: null}); // 清空标签索引
            return; // 提前退出
        }

        // 从商品数据中提取所有唯一的可用标签
        const availableTags = this.extractAvailableTags(products);
        // 取前10个标签作为示例，用逗号分隔
        const sampleTags = availableTags.slice(0, 10).join(', ');
        // 构建一个从标签映射到包含该标签的商品名称列表的索引
        const tagToProductsIndex = this.buildTagToProductsIndex(products);

        // 更新页面数据
        this.setData({
            availableTags: availableTags, // 设置可用标签列表
            availableTagsSample: sampleTags, // 设置标签示例字符串
            tagToProductsIndex: tagToProductsIndex, // 设置标签到商品的索引
        });
        console.log("Products data processed. Available tags:", availableTags.length); // 控制台输出处理结果

        // 基于加载的商品数据初始化或更新Bandit算法的Q值和N值
        this.initializeBanditData(products);

        // 如果商品数据和可用标签都存在，则显示标签输入框
        if (Object.keys(products).length > 0 && availableTags.length > 0) {
            this.setData({showTagInput: true});
        } else {
            // 否则，隐藏标签输入框并给出相应提示
            this.setData({showTagInput: false});
            const msg = Object.keys(products).length > 0 ?
                '商品数据已加载，但没有找到标签，无法进行标签推荐。您可以尝试获取新推荐。' :
                '商品数据不可用，无法进行商品推荐。';
            this.addMessage('system', msg);
        }
    },

    /**
     * 从商品数据中提取所有唯一的、非空的标签。
     * @param {Object} products - 商品数据对象，键为商品名，值为商品信息（包含标签数组）。
     * @returns {string[]} - 包含所有不重复标签的字符串数组。
     */
    extractAvailableTags: function (products) {
        const allTagsSet = new Set(); // 使用Set来自动去重
        if (!products) return []; // 如果商品数据为空，返回空数组
        // 遍历商品对象中的每个商品
        for (const productName in products) {
            // 确保是对象自身的属性，而不是原型链上的
            if (products.hasOwnProperty(productName)) {
                const productData = products[productName];
                const tags = productData.标签 || []; // 获取商品的标签数组，如果不存在则为空数组
                // 遍历每个商品的标签
                tags.forEach(tag => {
                    // 确保标签是字符串且去除首尾空格后不为空
                    if (typeof tag === 'string' && tag.trim()) {
                        allTagsSet.add(tag.trim()); // 将处理后的标签添加到Set中
                    }
                });
            }
        }
        return Array.from(allTagsSet); // 将Set转换为数组并返回
    },

    /**
     * 构建一个从标签名到包含该标签的商品名称列表的映射（索引）。
     * @param {Object} products - 商品数据对象。
     * @returns {Object} - 标签到商品名数组的映射，例如: {"美食": ["烤鱼", "披萨"], "户外": ["帐篷"]}。
     */
    buildTagToProductsIndex: function (products) {
        const tagToProducts = {}; // 初始化结果对象
        if (!products) return tagToProducts; // 商品数据为空则返回空对象
        // 遍历商品
        for (const productName in products) {
            if (products.hasOwnProperty(productName)) {
                const productData = products[productName];
                const tags = productData.标签 || []; // 获取标签
                // 遍历标签
                tags.forEach(tag => {
                    if (typeof tag === 'string' && tag.trim()) {
                        const cleanedTag = tag.trim(); // 清理标签字符串
                        // 如果该标签首次出现，则在映射中为其创建一个新数组
                        if (!tagToProducts[cleanedTag]) {
                            tagToProducts[cleanedTag] = [];
                        }
                        // 将当前商品名称添加到该标签对应的数组中
                        tagToProducts[cleanedTag].push(productName);
                    }
                });
            }
        }
        return tagToProducts; // 返回构建好的索引
    },

    /**
     * 从微信小程序的本地缓存中加载Bandit算法的Q值和N值。
     */
    loadBanditData: function () {
        try {
            // 尝试从缓存中读取之前保存的Bandit数据
            const data = wx.getStorageSync(CACHE_BANDIT_DATA_KEY);
            if (data) {
                // 如果缓存中有数据，则设置到页面的data中
                this.setData({Q: data.Q || {}, N: data.N || {}});
            } else {
                // 如果缓存中没有数据，则初始化为空对象
                this.setData({Q: {}, N: {}});
            }
        } catch (e) {
            // 如果读取缓存失败，打印错误并提示用户
            console.error("Failed to load Bandit data from cache:", e);
            this.addMessage('system', '加载本地偏好数据失败。');
        }
    },

    /**
     * 基于当前的商品列表初始化或更新Bandit算法的Q值和N值。
     * 如果Q和N为空，则为每个商品初始化Q为0，N为0。
     * 如果Q和N已存在，则确保所有当前商品都在Q和N中有条目（新商品初始化为0）。
     * @param {Object} products - 当前的商品数据对象。
     */
    initializeBanditData: function (products) {
        // 如果商品数据为空或无效，则重置Q, N和推荐轮次计数
        if (!products || Object.keys(products).length === 0) {
            this.setData({Q: {}, N: {}, recommendationCycleCount: 0});
            return;
        }
        const productNames = Object.keys(products); // 获取所有商品名称列表
        let currentQ = this.data.Q || {}; // 获取当前Q值，若无则为空对象
        let currentN = this.data.N || {}; // 获取当前N值，若无则为空对象
        let updatedQ = {}; // 用于存储更新后的Q值
        let updatedN = {}; // 用于存储更新后的N值
        // 判断是否为完全重置（Q和N为空但商品列表不为空）
        let reinitialized = Object.keys(currentQ).length === 0 && Object.keys(currentN).length === 0 && productNames.length > 0;

        // 遍历所有当前商品
        productNames.forEach(p => {
            // 为每个商品设置Q值，如果已存在则使用原值，否则初始化为0.0
            updatedQ[p] = parseFloat(currentQ[p] || 0.0);
            // 为每个商品设置N值，如果已存在则使用原值，否则初始化为0
            updatedN[p] = parseInt(currentN[p] || 0);
        });

        // 更新页面的Q, N数据。如果不是重置，则保持原推荐轮次计数
        this.setData({
            Q: updatedQ,
            N: updatedN,
            recommendationCycleCount: reinitialized ? 0 : (this.data.recommendationCycleCount || 0)
        });
        // 如果是重置操作，给用户一个提示
        if (reinitialized) this.addMessage('system', '商品列表或偏好数据已重置，推荐系统数据已同步。');
    },

    /**
     * 将当前的Bandit数据 (Q值和N值) 保存到微信小程序的本地缓存。
     */
    saveBanditData: function () {
        // 如果没有商品数据，则不执行保存操作
        if (!this.data.products || Object.keys(this.data.products).length === 0) return;
        try {
            // 将Q和N对象存入本地缓存
            wx.setStorageSync(CACHE_BANDIT_DATA_KEY, {Q: this.data.Q, N: this.data.N});
        } catch (e) {
            // 如果保存失败，打印错误并提示用户
            console.error("Failed to save Bandit data to cache:", e);
            this.addMessage('system', '保存本地偏好数据失败。');
        }
    },

    /**
     * 异步获取天气信息，并根据天气情况推荐饮品和判断是否适合划船。
     * @returns {Promise} - 一个Promise对象，在请求完成后resolve或reject。
     */
    getWeatherAndDrinks: function () {
        const that = this; // 保存Page实例的this上下文
        wx.showLoading({title: '加载天气饮品...'}); // 显示加载提示
        // 构建高德天气API的请求URL
        const weatherApiUrl = `https://restapi.amap.com/v3/weather/weatherInfo?city=${CITY_CODE}&key=${GAODE_API_KEY}`;

        return new Promise((resolve, reject) => {
            // 发起微信小程序网络请求
            wx.request({
                url: weatherApiUrl,
                method: 'GET',
                success: function (res) { // 请求成功回调
                    wx.hideLoading(); // 隐藏加载提示
                    let weather_info, boat_suitability = "抱歉，暂时无法判断划船适宜性。", recommended_drinks = [],
                        success = false; // 初始化变量

                    // 检查API响应是否成功且包含有效数据
                    if (res.statusCode === 200 && res.data && res.data.status === "1" && res.data.lives && res.data.lives.length > 0) {
                        const r = res.data.lives[0]; // 获取实时天气数据
                        // 解析天气信息
                        weather_info = {
                            "weather": r.weather || "未知",
                            "temperature": r.temperature || "未知",
                            "winddirection": r.winddirection || "未知",
                            "windpower": r.windpower || "未知",
                            "humidity": r.humidity || "未知"
                        };
                        // 判断是否适合划船
                        boat_suitability = that.isGoodForBoating(r) ? "今天天气不错，非常适合划船！" : "今天天气不太适合划船哦。";
                        // 根据温度推荐饮品
                        recommended_drinks = that.getRecommendedDrinks(weather_info.temperature);
                        success = true; // 标记API请求成功处理
                    } else {
                        // API返回错误或数据格式不符
                        console.error("Gaode API Error:", res.data);
                    }

                    // 根据获取到的天气信息，向用户发送消息
                    if (weather_info) that.addMessage('system', '今日天气信息：', {
                        type: 'weather', // 消息类型为天气
                        content: weather_info, // 天气详情
                        suitability: boat_suitability // 划船适宜性
                    });
                    else that.addMessage('system', (res.data && res.data.info) ? `获取天气信息失败: ${res.data.info}` : '抱歉，暂时无法获取天气信息。');

                    // 根据推荐的饮品，向用户发送消息
                    if (recommended_drinks.length > 0) that.addMessage('system', '根据天气，为您推荐以下饮品：', {
                        type: 'drinks', // 消息类型为饮品
                        content: recommended_drinks, // 推荐的饮品列表
                        selected: false, // 初始未选择
                        selectedIndex: -2 // 初始选择索引 (-2表示未选择任何一项，-1表示“不想喝”)
                    });
                    else if (success && weather_info) that.addMessage('system', '暂无推荐饮品（可能温度数据异常）。');
                    else that.addMessage('system', '暂无推荐饮品。');

                    resolve(); // Promise完成
                },
                fail: function (err) { // 请求失败回调
                    wx.hideLoading(); // 隐藏加载提示
                    console.error("Get weather failed:", err); // 控制台打印错误
                    that.addMessage('system', '获取天气饮品网络请求失败。'); // 提示用户网络错误
                    reject(err); // Promise拒绝
                }
            });
        });
    },

    /**
     * 根据天气数据判断是否适合划船。
     * @param {Object} weatherData - 从高德API获取的实时天气对象 (res.data.lives[0])。
     * @returns {boolean} - 如果适合划船返回true，否则返回false。
     */
    isGoodForBoating: function (weatherData) {
        if (!weatherData) return false; // 无天气数据则认为不适合
        const weatherCondition = weatherData.weather || ""; // 天气现象描述
        const windPowerStr = weatherData.windpower || "0"; // 风力描述字符串
        let windPowerNumeric = 0; // 解析后的数字风力等级

        // 尝试从风力描述中提取数字 (例如 "≤3" 取 3, "<3级" 取 3)
        const match = windPowerStr.match(/\d+/);
        if (match) {
            windPowerNumeric = parseInt(match[0]);
        } else {
            // 如果无法解析风力，则警告并认为不适合（保守策略）
            console.warn("Cannot parse wind power:", windPowerStr);
            return false;
        }

        // 如果天气现象在不适宜列表中，或者风力等级大于4级，则不适合划船
        if (unsuitableWeatherConditionsForRowing.includes(weatherCondition) || windPowerNumeric > 4) return false;
        return true; // 否则认为适合划船
    },

    /**
     * 根据温度字符串推荐饮品。
     * @param {string} temperatureStr - 温度字符串 (例如 "25")。
     * @returns {string[]} - 推荐的饮品名称数组。
     */
    getRecommendedDrinks: function (temperatureStr) {
        try {
            const tempInt = parseInt(temperatureStr); // 将温度字符串转换为整数
            if (isNaN(tempInt)) return []; // 如果转换失败 (非数字)，则不推荐

            // 根据温度区间选择饮品类型
            if (tempInt < 15) return AVAILABLE_DRINKS.hot || []; // 低于15度推荐热饮
            if (tempInt >= 25) return AVAILABLE_DRINKS.cold || []; // 高于等于25度推荐冷饮
            return AVAILABLE_DRINKS.neutral || []; // 15到24度推荐中性饮品
        } catch (e) {
            // 发生异常则打印错误并返回空数组
            console.error("Drink recommendation error:", e);
            return [];
        }
    },

    /**
     * 计算两个字符串之间的编辑距离 (Levenshtein Distance)。
     * 编辑距离是指由一个字符串转换为另一个字符串所需最少单字符编辑（插入、删除或替换）次数。
     * @param {string} a - 第一个字符串。
     * @param {string} b - 第二个字符串。
     * @returns {number} - 两个字符串之间的编辑距离。
     */
    levenshteinDistance: function (a, b) {
        const an = a ? a.length : 0, bn = b ? b.length : 0; // 获取字符串长度，处理null或undefined情况
        if (an === 0) return bn; // 如果a为空，距离为b的长度 (插入bn个字符)
        if (bn === 0) return an; // 如果b为空，距离为a的长度 (删除an个字符)

        // 创建一个 (an+1) x (bn+1) 的矩阵来存储子问题的解
        const matrix = Array(an + 1).fill(null).map(() => Array(bn + 1).fill(null));

        // 初始化第一行和第一列
        for (let i = 0; i <= an; i++) matrix[i][0] = i; // a的前i个字符变为空字符串需要i次删除
        for (let j = 0; j <= bn; j++) matrix[0][j] = j; // 空字符串变为b的前j个字符需要j次插入

        // 动态规划填表
        for (let i = 1; i <= an; i++) {
            for (let j = 1; j <= bn; j++) {
                // 计算三种操作的成本：
                // 1. matrix[i-1][j] + 1: 删除a的第i个字符
                // 2. matrix[i][j-1] + 1: 插入b的第j个字符
                // 3. matrix[i-1][j-1] + cost: 替换a的第i个字符为b的第j个字符 (如果字符相同cost=0,否则cost=1)
                const cost = (a[i - 1] === b[j - 1] ? 0 : 1);
                matrix[i][j] = Math.min(
                    matrix[i - 1][j] + 1,        // 删除
                    matrix[i][j - 1] + 1,        // 插入
                    matrix[i - 1][j - 1] + cost  // 替换或匹配
                );
            }
        }
        return matrix[an][bn]; // 矩阵右下角的值即为a和b的编辑距离
    },

    /**
     * 计算两个字符串基于编辑距离的相似度。
     * 相似度 = 1 - (编辑距离 / 较长字符串的长度)。结果范围在0到1之间。
     * @param {string} s1 - 第一个字符串。
     * @param {string} s2 - 第二个字符串。
     * @returns {number} - 相似度得分 (0.0 到 1.0)。
     */
    levenshteinSimilarity: function (s1, s2) {
        if (!s1 && !s2) return 1.0; // 两者都为空或null，视为完全相似
        if (!s1 || !s2) return 0.0; // 其中一个为空或null，视为完全不相似

        const M = Math.max(s1.length, s2.length); // 取两个字符串中较长的那个的长度
        if (M === 0) return 1.0; // 如果两个字符串都为空字符串，视为完全相似

        // 相似度公式
        return 1.0 - (this.levenshteinDistance(s1, s2) / M);
    },

    /**
     * 为给定的无效标签查找最相似的可用标签。
     * @param {string} invalidTag - 用户输入的无效标签。
     * @returns {string[]} - 一个包含建议的相似标签的数组，按相似度降序排列。
     */
    findSimilarTags: function (invalidTag) {
        const availableTags = this.data.availableTags; // 获取所有可用标签列表
        const suggestions = []; // 初始化建议列表

        if (!availableTags || availableTags.length === 0) return []; // 如果没有可用标签，返回空数组

        // 遍历所有可用标签
        availableTags.forEach(at => {
            // 计算输入标签与当前可用标签的相似度 (忽略大小写)
            const sim = this.levenshteinSimilarity(invalidTag.toLowerCase(), at.toLowerCase());
            // 如果相似度达到预设阈值，则将该可用标签及其相似度添加到建议列表中
            if (sim >= this.data.tagSimilarityThreshold) {
                suggestions.push({tag: at, similarity: sim});
            }
        });

        // 按相似度从高到低对建议列表进行排序
        suggestions.sort((a, b) => b.similarity - a.similarity);

        // 返回最多 `maxSuggestedTags` 个最相似的标签名称
        return suggestions.slice(0, this.data.maxSuggestedTags).map(s => s.tag);
    },

    /**
     * 商品推荐的核心逻辑。
     * 结合用户偏好的标签和Epsilon-greedy策略（探索与利用）来生成商品推荐列表。
     * @returns {string[]} - 推荐的商品名称数组。
     */
    getRecommendationsLogic: function () {
        // 如果没有商品数据，则无法推荐，返回空数组
        if (!this.data.products || Object.keys(this.data.products).length === 0) return [];

        // 解构获取页面数据中与推荐相关的状态
        const {
            products,           // 商品数据
            Q,                  // Bandit算法的Q值 (商品回报)
            N,                  // Bandit算法的N值 (商品选择次数)
            likedTags,          // 用户喜欢的标签
            recommendedProductsAll, // 已推荐过的商品列表
            shoppingCart,       // 购物车中的商品
            topN,               // 推荐数量
            recommendationCycleCount, // 当前推荐轮次
            initialEpsilon,     // 初始探索率
            epsilonDecayRate,   // 探索率衰减率
            minEpsilon,         // 最小探索率
            tagToProductsIndex  // 标签到商品的索引
        } = this.data;

        const productNames = Object.keys(products); // 获取所有商品名称

        // Epsilon-greedy策略：计算当前探索率 (epsilon)，随推荐轮次增加而衰减
        const currentEpsilon = Math.max(minEpsilon, initialEpsilon - epsilonDecayRate * recommendationCycleCount);

        // 清理用户喜欢的标签：去除首尾空格并过滤掉空标签
        const cleanedLikedTags = likedTags.map(t => t.trim()).filter(t => t !== '');

        // 初始化候选商品及其得分
        let candidateProductsWithScores = {};
        productNames.forEach(p => candidateProductsWithScores[p] = 0.0); // 初始时，所有商品得分为0

        // 如果用户指定了偏好标签，则根据标签匹配度为商品打分
        if (cleanedLikedTags.length > 0) {
            candidateProductsWithScores = {}; // 重置候选商品，只考虑与标签相关的
            cleanedLikedTags.forEach(tag => {
                // 如果标签在索引中存在，则其对应的商品得分增加
                if (tagToProductsIndex && tagToProductsIndex[tag]) {
                    tagToProductsIndex[tag].forEach(p => {
                        candidateProductsWithScores[p] = (candidateProductsWithScores[p] || 0.0) + 1; // 每匹配一个标签，得分+1
                    });
                }
            });
        }

        // 创建一个排除列表，包含所有已推荐过的商品和购物车中的商品，避免重复
        const excludedSet = new Set([...recommendedProductsAll, ...shoppingCart.map(item => item.name)]);
        // 从候选商品中移除已在排除列表中的商品
        for (const p in candidateProductsWithScores) {
            if (excludedSet.has(p)) {
                delete candidateProductsWithScores[p];
            }
        }

        let recommendations = []; // 初始化推荐结果数组
        const candidateList = Object.keys(candidateProductsWithScores); // 获取最终的候选商品列表

        // 如果经过标签筛选和排除后没有候选商品了
        if (candidateList.length === 0) {
            // 则回退策略：从所有未被排除的商品中，按Q值（预期回报）降序选择
            const fallback = productNames
                .filter(p => !excludedSet.has(p)) // 过滤掉已排除的
                .sort((a, b) => (Q[b] || 0.0) - (Q[a] || 0.0)); // 按Q值降序排序
            return fallback.slice(0, topN); // 返回前N个
        }

        // Epsilon-greedy 策略:
        if (Math.random() < currentEpsilon) {
            // 探索 (Exploration): 以 currentEpsilon 的概率随机选择商品
            // 打乱候选商品列表，取前N个
            recommendations = this.shuffleArray(candidateList).slice(0, Math.min(topN, candidateList.length));
        } else {
            // 利用 (Exploitation): 以 (1 - currentEpsilon) 的概率选择“最佳”商品
            // “最佳”定义：首先按标签匹配得分降序，得分相同则按Q值降序
            const sorted = Object.entries(candidateProductsWithScores).sort((a, b) => {
                const scoreA = a[1]; // 商品A的标签匹配得分
                const scoreB = b[1]; // 商品B的标签匹配得分
                const productA = a[0]; // 商品A的名称
                const productB = b[0]; // 商品B的名称

                if (scoreB !== scoreA) return scoreB - scoreA; // 主要按得分降序
                return (Q[productB] || 0.0) - (Q[productA] || 0.0); // 次要按Q值降序
            });
            // 取排序后的前N个商品名称
            recommendations = sorted.slice(0, topN).map(item => item[0]);
        }
        return recommendations; // 返回推荐的商品名称列表
    },

    /**
     * 使用 Fisher-Yates (Knuth) 洗牌算法打乱数组元素的顺序。
     * @param {Array} array - 需要被打乱的数组。
     * @returns {Array} - 一个新的被打乱顺序的数组 (原数组不变)。
     */
    shuffleArray: function (array) {
        const s = [...array]; // 创建数组的副本，避免修改原数组
        for (let i = s.length - 1; i > 0; i--) {
            // 生成一个从0到i（包含i）的随机索引j
            const j = Math.floor(Math.random() * (i + 1));
            // 交换s[i]和s[j]
            [s[i], s[j]] = [s[j], s[i]];
        }
        return s; // 返回打乱后的数组
    },

    /**
     * 更新指定商品的Q值和N值 (Bandit算法的核心更新步骤)。
     * 当用户对某个商品做出选择（如喜欢、购买），会给予该商品一个回报 (reward)。
     * @param {string} productName - 被选择的商品名称。
     * @param {number} reward - 该商品获得的回报值 (例如，喜欢为1，不喜欢为0或-1)。
     */
    updateProductReward: function (productName, reward) {
        // 检查商品是否存在于商品列表中
        if (!this.data.products || !this.data.products[productName]) return; // 如果商品无效，则不更新

        let {Q, N} = this.data; // 获取当前的Q值和N值对象

        // 确保商品在Q和N中都有条目，如果没有则初始化
        Q[productName] = (Q[productName] || 0.0); // 如果不存在，Q值默认为0.0
        N[productName] = (N[productName] || 0);   // 如果不存在，N值默认为0

        N[productName]++; // 该商品被选择的次数加1

        // 这是指数加权移动平均的计算方式，用于更新对商品价值的估计
        Q[productName] = (1 - learningRate) * Q[productName] + learningRate * reward;
        // 更新页面数据中的Q和N
        this.setData({Q, N});
        // 将更新后的Bandit数据保存到本地缓存
        this.saveBanditData();
    },

    /**
     * 处理用户选择饮品的事件。
     * @param {Object} e - 事件对象，包含来自wxml模板的data-*属性。
     */
    selectDrink: function (e) {
        // 从事件对象中获取消息索引和用户选择的饮品索引
        const msgIndex = e.currentTarget.dataset.msgIndex; // 饮品消息在messages数组中的索引
        const index = parseInt(e.currentTarget.dataset.drinkIndex); // 用户选择的饮品在饮品列表中的索引 (-1表示"不想喝")

        let updatedMessages = this.data.messages; // 获取当前消息列表的副本
        // 校验消息索引和消息类型是否正确
        if (msgIndex >= 0 && msgIndex < updatedMessages.length && updatedMessages[msgIndex].data && updatedMessages[msgIndex].data.type === 'drinks') {
            // 如果这条饮品消息已经被选择过，则不做任何操作 (防止重复选择)
            if (updatedMessages[msgIndex].data.selected) return;

            // 更新该条饮品消息的状态为已选择，并记录选择的索引
            updatedMessages[msgIndex].data.selected = true;
            updatedMessages[msgIndex].data.selectedIndex = index;
            this.setData({messages: updatedMessages}); // 更新页面数据
            this.scrollToBottom(); // 滚动到底部
        } else {
            // 如果消息校验失败，打印错误并返回
            console.error("Failed to update drink selection. Invalid message index or type.");
            return;
        }

        // 根据用户的选择，构造用户消息文本
        const selectedItemText = index === -1 ? "不想喝" : updatedMessages[msgIndex].data.content[index];
        this.addMessage('user', selectedItemText); // 将用户的选择作为一条用户消息添加到对话中

        // 提示用户选择结果
        app.tip({content: index === -1 ? "好的，祝您开心！" : `好的，正在为您准备：${selectedItemText}，请稍候！`});

        // 延迟一段时间后，根据当前情况决定下一步操作：
        // 如果商品数据已加载：
        //   - 如果可用标签为空 (意味着无法通过标签筛选)，或者用户已设置过偏好标签，则直接获取商品推荐。
        //   - 否则 (有可用标签且用户未设置偏好)，则显示标签输入框让用户输入偏好。
        setTimeout(() => {
            if (this.data.products && Object.keys(this.data.products).length > 0) {
                if (this.data.availableTags.length === 0 || (this.data.likedTags && this.data.likedTags.length > 0)) {
                    this.getProductRecommendations();
                } else {
                    this.setData({showTagInput: true});
                }
            }
        }, 1500); // 延迟1.5秒
    },

    /**
     * 处理标签输入框内容变化的事件。
     * @param {Object} e - 事件对象，e.detail.value 为输入框的当前内容。
     */
    handleTagInputChange: function (e) {
        // 将输入框的最新内容同步到页面的data中
        this.setData({currentTagInput: e.detail.value});
    },

    /**
     * 处理用户确认（提交）标签输入的事件。
     * 校验用户输入的标签，处理无效标签，并最终更新用户的偏好标签。
     */
    confirmTags: function () {
        // 获取用户输入的标签字符串，并去除首尾空格
        const input = (this.data.currentTagInput || '').trim();
        // 如果输入为空，提示用户并返回
        if (!input) {
            app.alert({content: "请输入您喜欢的标签。"});
            return;
        }

        // 将中文逗号替换为英文逗号，然后按逗号分割成标签数组
        // 每个标签再去除首尾空格，并过滤掉空字符串标签
        const processed = input.replace(/，/g, ',');
        const entered = processed.split(',').map(t => t.trim()).filter(t => t !== '');

        // 如果处理后没有有效的标签输入，提示用户并返回
        if (entered.length === 0) {
            app.alert({content: "请至少输入一个您喜欢的标签。"});
            return;
        }

        // 将可用的标签列表转换为Set，方便快速查找
        const availableSet = new Set(this.data.availableTags);
        // 筛选出用户输入的有效标签 (存在于可用标签列表中)
        const valid = entered.filter(t => availableSet.has(t));
        // 筛选出用户输入的无效标签 (不存在于可用标签列表中)
        const invalid = entered.filter(t => !availableSet.has(t));

        // 如果存在无效标签
        if (invalid.length > 0) {
            const suggestionsMap = {}; // 用于存储无效标签及其对应的建议标签
            // 为每个无效标签查找相似的有效标签
            invalid.forEach(inv => {
                const sim = this.findSimilarTags(inv); // 查找相似标签
                if (sim.length > 0) suggestionsMap[inv] = sim; // 如果找到，则存入map
            });

            let prompt = `您输入的以下标签无效：${invalid.join(', ')}。\n`; // 构建提示信息
            // 如果找到了任何建议标签
            if (Object.keys(suggestionsMap).length > 0) {
                prompt += '您是否想使用以下建议标签来替代：\n';
                for (const inv in suggestionsMap) {
                    prompt += `  "${inv}" ➔ ${suggestionsMap[inv].join(' 或 ')}\n`; // "原无效标签" -> "建议1 或 建议2"
                }
                // 弹出确认框，让用户选择如何处理
                app.tip({
                    title: '无效标签提示',
                    content: prompt,
                    confirmText: '使用建议+有效', // 按钮：使用建议的标签和原先就有效的标签
                    cancelText: '只用有效标签',   // 按钮：只使用原先就有效的标签
                    success: (res) => { // 用户点击按钮后的回调
                        if (res.confirm) { // 用户选择 "使用建议+有效"
                            const suggestedTagsFromMap = Object.values(suggestionsMap).flat(); // 获取所有建议标签并扁平化
                            // 合并原有效标签和建议标签，并去重
                            this.proceedWithValidTags(Array.from(new Set([...valid, ...suggestedTagsFromMap])), invalid);
                        } else if (res.cancel) { // 用户选择 "只用有效标签"
                            if (valid.length > 0) { // 如果存在有效标签
                                this.proceedWithValidTags(valid, invalid);
                            } else { // 如果原先也没有有效标签
                                app.alert({content: "没有有效的标签可以使用，请重新输入。"});
                                this.addMessage('system', '没有有效的标签可以使用，请重新输入您的偏好标签。');
                            }
                        }
                    }
                });
            } else { // 如果没有找到任何建议标签
                prompt += valid.length > 0 ? '有效标签已保留。是否只使用有效标签？' : '没有有效的标签可以使用。请重新输入。';
                app.tip({
                    title: '无效标签提示',
                    content: prompt,
                    confirmText: '只用有效标签',
                    cancelText: '重新输入',
                    showCancel: valid.length > 0, // 仅当有有效标签时才显示“重新输入”作为取消选项
                    success: (res) => {
                        if (res.confirm && valid.length > 0) { // 用户确认使用有效标签
                            this.proceedWithValidTags(valid, invalid);
                        } else { // 用户选择重新输入，或没有有效标签
                            app.alert({content: "请重新输入您的偏好标签。"});
                            this.addMessage('system', '请重新输入您的偏好标签。');
                        }
                    }
                });
            }
        } else { // 如果所有输入的标签都有效
            this.proceedWithValidTags(entered, []); // 直接使用所有输入的标签
        }
    },

    /**
     * 使用最终确定的有效标签列表来更新用户偏好，并触发商品推荐。
     * @param {string[]} validTags - 经过处理和用户确认的有效偏好标签列表。
     * @param {string[]} ignoredTags - 在处理过程中被忽略的无效标签列表（用于用户提示）。
     */
    proceedWithValidTags: function (validTags, ignoredTags) {
        // 更新页面数据：设置偏好标签，清空输入框，隐藏输入界面，重置已推荐列表和推荐轮次
        this.setData({
            likedTags: validTags,
            currentTagInput: '',
            showTagInput: false,
            recommendedProductsAll: [], // 清空历史推荐，以便基于新标签重新推荐
            recommendationCycleCount: 0 // 重置推荐轮次，epsilon会回到初始值
        });
        // 添加用户消息，告知系统其选择的偏好标签
        this.addMessage('user', `我的偏好标签是：${validTags.join(', ')}` + (ignoredTags.length > 0 ? ` (忽略无效标签：${ignoredTags.join(', ')})` : ''));
        // 添加系统消息，确认偏好已更新
        this.addMessage('system', "偏好标签已更新。");
        // 基于新的偏好标签获取商品推荐
        this.getProductRecommendations();
    },

    /**
     * 获取并向用户展示商品推荐。
     */
    getProductRecommendations: function () {
        // 检查商品数据是否已加载且不为空
        if (!this.data.products || Object.keys(this.data.products).length === 0) {
            this.addMessage('system', '商品数据未加载或为空，无法推荐。');
            return; // 无法推荐则退出
        }
        this.addMessage('system', '正在为您挑选合适的商品...'); // 提示用户正在处理
        wx.showLoading({title: '生成推荐中...'}); // 显示加载动画

        // 增加推荐轮次计数 (用于epsilon衰减)
        this.setData({
            recommendationCycleCount: this.data.recommendationCycleCount + 1,
            hasInteractedWithCurrentRecommendations: false // <--- 新增：每次新推荐，重置交互状态
        });
        // 调用核心推荐逻辑函数获取推荐的商品名称列表
        const recommendations = this.getRecommendationsLogic();
        wx.hideLoading(); // 隐藏加载动画

        // 将推荐的商品名称列表转换为包含商品详情的对象数组
        const recDetails = recommendations.map(name => {
            const p = this.data.products[name]; // 从总商品数据中查找商品详情
            return p ? {name: name, id: p.id, ...p} : null; // 如果找到，则创建包含名称、ID和其它属性的对象
        }).filter(p => p !== null); // 过滤掉未找到详情的商品 (理论上不应发生)

        // 筛选出本次新推荐的商品（不在历史推荐列表和购物车中的）
        const newlyRec = recommendations.filter(p =>
            !this.data.recommendedProductsAll.includes(p) &&
            !this.data.shoppingCart.some(item => item.name === p)
        );
        // 将新推荐的商品添加到历史推荐总列表中
        this.setData({recommendedProductsAll: [...this.data.recommendedProductsAll, ...newlyRec]});

        // 如果成功获取到推荐商品详情
        if (recDetails && recDetails.length > 0) {
            this.addMessage('system', '为您推荐以下商品:', { // 添加系统消息
                type: 'recommendations', // 消息类型为推荐
                content: recDetails,     // 推荐的商品详情列表
                interacted: false        // <--- 新增：初始化为未交互
            });
            this.setData({
                currentRecommendationsForFeedback: recDetails.map(p => ({name: p.name, id: p.id})) // <--- 新增：存储当前推荐的商品名和ID
            });
        } else {
            // 如果没有找到更多可推荐的商品
            this.addMessage('system', '当前没有找到更多推荐商品了。您可以尝试修改偏好标签。');
            this.setData({
                currentRecommendationsForFeedback: [] // <--- 新增：如果没有推荐，则清空
            });
        }
        // 保存Bandit数据 (因为推荐过程可能间接影响了N值，或者未来可能直接更新Q/N)
        this.saveBanditData();
    },

    /**
     * 处理用户选择（点击喜欢）某个推荐商品的事件。
     * 将商品添加到购物车（心仪列表），并更新该商品的Bandit回报。
     * @param {Object} e - 事件对象，包含data-product-name属性。
     */
    selectProduct: function (e) {
        const selectedProductName = e.currentTarget.dataset.productName; // 获取被选中的商品名称
        const msgIndex = e.currentTarget.dataset.msgIndex; // 获取消息索引
        const productData = this.data.products[selectedProductName]; // 从总商品数据中获取该商品的原始数据

        // 校验商品数据和ID是否存在
        if (!productData || !productData.id) {
            console.error(`Invalid product selected or missing ID: ${selectedProductName}`);
            this.addMessage('system', `无效商品选择或缺少ID: ${selectedProductName}`);
            return;
        }

        // 创建要添加到购物车的商品对象，至少包含id和name
        const selectedProductObject = {
            id: productData.id,
            name: selectedProductName
            // 如果需要，可以添加更多商品信息到购物车对象中，如价格、图片等
        };

        let shoppingCart = this.data.shoppingCart; // 获取当前购物车列表
        // 检查该商品是否已在购物车中
        const existingItemIndex = shoppingCart.findIndex(item => item.name === selectedProductName);

        if (existingItemIndex === -1) { // 如果商品不在购物车中
            shoppingCart = [...shoppingCart, selectedProductObject]; // 将商品添加到购物车
            this.setData({shoppingCart}); // 更新页面数据

            // --- 核心改进：给予反馈 ---
            // 1. 给被选择的商品正反馈 (reward = 1)
            this.updateProductReward(selectedProductName, 1);

            // <--- 新增：标记当前批次推荐已被交互
            this.setData({hasInteractedWithCurrentRecommendations: true});

            // 2. 遍历同批次推荐中的其他商品，给予负反馈 (reward = 0)
            // 获取当前推荐消息对象
            let updatedMessages = [...this.data.messages]; // 创建消息数组的副本
            if (msgIndex !== undefined && updatedMessages[msgIndex]) {
                const currentRecMessage = updatedMessages[msgIndex];
                if (currentRecMessage.data && currentRecMessage.data.type === 'recommendations') {
                    // 标记这条推荐消息已被用户交互
                    currentRecMessage.data.interacted = true; // <-- 新增：标记为已交互
                    this.setData({messages: updatedMessages}); // 更新消息列表以保存 interacted 状态

                    const recommendedProductsInThisBatch = currentRecMessage.data.content;
                    recommendedProductsInThisBatch.forEach(product => {
                        // 如果是当前被选中的商品，则跳过（它已经获得了正反馈）
                        // 如果是未被选中的商品，则给予负反馈 (reward = 0)
                        if (product.name !== selectedProductName) {
                            this.updateProductReward(product.name, 0); // 负反馈：reward = 0
                        }
                    });
                }
            }
            // --- 改进结束 ---

            this.addMessage('user', `我选择了商品：${selectedProductName}`); // 添加用户消息
            this.addMessage('system', `'${selectedProductName}' 已添加到心仪商品并记录偏好。`); // 添加系统消息
        } else { // 如果商品已在购物车中
            this.addMessage('system', `'${selectedProductName}' 已在您的心仪商品中。`); // 提示用户
            // 考虑：如果用户再次点击已在购物车中的商品，是否也算一次正反馈？
            // 如果希望累积偏好强度，可以取消下面这行注释：
            // this.updateProductReward(selectedProductName, 1);
        }
    },

    /**
     * 用户请求查看心仪商品列表（购物车）。
     */
    viewCart: function () {
        console.log("User viewed cart."); // 控制台记录
        this.addMessage('user', '查看心仪商品'); // 添加用户行为消息
        this.displayCartMessage(); // 调用显示购物车内容的方法
    },

    /**
     * 构建并向用户显示当前心仪商品（购物车）的内容。
     */
    displayCartMessage: function () {
        // 准备用于在消息中显示的购物车列表，只包含name和id
        const cartListForDisplay = this.data.shoppingCart.map(item => {
            return {name: item.name, id: item.id};
        });
        // 添加系统消息，类型为'cart'，内容为购物车列表
        this.addMessage('system', '您的心仪商品：', {
            type: 'cart',
            content: cartListForDisplay
        });
    },

    /**
     * 导航到商品详情页。
     * @param {Object} e - 事件对象，包含data-product-id和data-product-name。
     */
    navigateToProductDetail: function (e) {
        const productId = e.currentTarget.dataset.productId; // 获取商品ID
        const productName = e.currentTarget.dataset.productName; // 获取商品名称 (用于提示)

        // 检查事件源是否是购物车项中的删除按钮，如果是，则不执行导航
        // 这是因为删除按钮可能与整个商品项共享同一个点击事件处理函数
        if (e.target.dataset.action === 'deleteSingleCartItem') {
            return; // 如果是删除操作，则中止导航
        }

        // 如果商品ID有效
        if (productId) {
            // 使用微信小程序的API跳转到商品详情页
            // 假设详情页路径为 /pages/goods/info，并通过id参数传递商品ID
            wx.navigateTo({
                url: `/pages/goods/info?id=${productId}`,
                success: () => {
                    // 导航成功的回调，可以添加日志或用户提示
                    // Optional: this.addMessage('system', `正在查看 '${productName}' 的详情...`);
                },
                fail: (err) => { // 导航失败的回调
                    console.error("Failed to navigate to product detail:", err);
                    app.alert({content: "无法跳转到商品详情页"}); // 提示用户
                }
            });
        } else { // 如果商品ID无效
            console.warn("Product ID not found for:", productName);
            app.alert({content: "暂时无法查看该商品详情"}); // 提示用户
        }
    },

    /**
     * 从心仪商品（购物车）中删除指定的商品。
     * @param {Object} e - 事件对象，包含data-product-name。
     */
    deleteCartItem: function (e) {
        const productNameToDelete = e.currentTarget.dataset.productName; // 获取要删除的商品名称
        console.log("User requested to delete from cart:", productNameToDelete); // 控制台记录

        // 过滤购物车列表，保留所有名称不等于待删除商品名称的项
        const updatedCart = this.data.shoppingCart.filter(item => item.name !== productNameToDelete);

        // 如果购物车长度确实减少了（表示成功删除了商品）
        if (updatedCart.length < this.data.shoppingCart.length) {
            this.setData({shoppingCart: updatedCart}); // 更新页面数据
            this.addMessage('system', `'${productNameToDelete}' 已从心仪商品中移除。`); // 提示用户
            this.displayCartMessage(); // 重新显示更新后的购物车内容
        }
    },

    /**
     * 清空整个心仪商品列表（购物车）。
     */
    clearCart: function () {
        // 弹出确认对话框，防止用户误操作
        app.tip({
            title: '提示',
            content: '确定要清空所有心仪商品吗？',
            cb_confirm: () => { // 用户点击确认后的回调
                this.setData({shoppingCart: []}); // 清空购物车数组
                this.addMessage('user', '清空心仪商品'); // 添加用户操作消息
                this.addMessage('system', '心仪商品已清空。'); // 添加系统反馈消息
                this.displayCartMessage(); // 显示空的购物车（或提示购物车已空）
            }
        });
    },

    /**
     * 处理页面底部操作按钮的点击事件。
     * @param {Object} e - 事件对象，包含data-action属性，值为'a', 'b', 'c', 'd'等。
     */
    handleAction: function (e) {
        const action = e.currentTarget.dataset.action; // 获取按钮定义的动作类型
        console.log("User action:", action); // 用于调试，在控制台输出用户行为

        // --- 负反馈逻辑块：在用户明确要求新推荐或修改偏好时触发 ---
        // 这一块逻辑在用户点击 'a' (新推荐) 或 'b' (改标签) 时执行
        if (action === 'a' || action === 'b') {
            let lastRecommendationMessageIndex = -1;
            for (let i = this.data.messages.length - 1; i >= 0; i--) {
                const msg = this.data.messages[i];
                if (msg.data && msg.data.type === 'recommendations') {
                    lastRecommendationMessageIndex = i;
                    break;
                }
            }

            if (lastRecommendationMessageIndex !== -1) {
                let updatedMessages = [...this.data.messages];
                const lastRecMessage = updatedMessages[lastRecommendationMessageIndex];

                // 只有当这条推荐消息还未被处理过 (interacted 为 false)
                // 并且用户没有通过“加入心仪商品”与本批次进行过交互 (hasInteractedWithCurrentRecommendations 为 false)
                // 才能触发隐式负反馈
                if (!lastRecMessage.data.interacted && !this.data.hasInteractedWithCurrentRecommendations) {
                    const productsToGiveNegativeFeedback = lastRecMessage.data.content;
                    productsToGiveNegativeFeedback.forEach(product => {
                        this.updateProductReward(product.name, 0); // 负反馈：reward = 0
                        console.log(`Implicit negative feedback for: ${product.name} due to action: ${action}`);
                    });
                    lastRecMessage.data.interacted = true; // 标记为已处理
                    this.setData({messages: updatedMessages});
                    this.addMessage('system', '您已查看新推荐，当前推荐商品已记录为未操作。');
                }
            }
        }
        // --- 负反馈逻辑块结束 ---

        switch (action) {
            case 'a': // 动作'a': 获取新推荐
                if (!this.data.products || Object.keys(this.data.products).length === 0) {
                    this.addMessage('system', '商品数据未加载或为空，无法推荐。');
                    return;
                }
                this.getProductRecommendations(); // 调用获取商品推荐的函数
                break;
            case 'b': // 动作'b': 修改偏好标签
                this.addMessage('user', '修改偏好标签'); // 添加用户消息
                if (!this.data.products || Object.keys(this.data.products).length === 0 || this.data.availableTags.length === 0) {
                    this.addMessage('system', '商品数据或标签缺失，无法设置偏好标签。');
                    this.setData({showTagInput: false});
                } else {
                    this.addMessage('system', '请重新输入您喜欢的标签：');
                    this.setData({
                        showTagInput: true,
                        currentTagInput: '',
                        likedTags: [],
                        recommendedProductsAll: [],
                        recommendationCycleCount: 0
                    });
                }
                break;
            case 'c': // 动作'c': 查看心仪商品
                this.viewCart(); // 调用查看购物车的函数
                break;
            case 'd': // 动作'd': 重新开始会话 (退出)
                console.log('--- 退出操作开始调试 ---');
                console.log('当前推荐商品列表 (currentRecommendationsForFeedback):', this.data.currentRecommendationsForFeedback);
                console.log('购物车列表 (shoppingCart):', this.data.shoppingCart);

                if (this.data.currentRecommendationsForFeedback.length > 0) {
                    const currentRecProducts = this.data.currentRecommendationsForFeedback;
                    const shoppingCartNames = new Set(this.data.shoppingCart.map(item => item.name));

                    let likedCountInCurrentRec = 0;
                    currentRecProducts.forEach(product => {
                        if (shoppingCartNames.has(product.name)) {
                            likedCountInCurrentRec++;
                        }
                    });

                    console.log('当前批次推荐商品总数:', currentRecProducts.length);
                    console.log('当前批次中已心仪商品数量 (likedCountInCurrentRec):', likedCountInCurrentRec);
                    console.log('是否已通过点击心仪按钮交互 (hasInteractedWithCurrentRecommendations):', this.data.hasInteractedWithCurrentRecommendations);


                    // 情景一：所有推荐商品都已加入心仪
                    if (likedCountInCurrentRec === currentRecProducts.length && currentRecProducts.length > 0) { // 增加一个条件防止空数组误判
                        app.tip({
                            title: '提示',
                            content: '您已将所有推荐商品加入心仪。',
                            confirmText: '好的',
                            showCancel: false, // 确保这里是 false
                            success: () => {
                                this.finalizeExit();
                            }
                        });
                    }
                    // 情景二：部分推荐商品加入心仪 (likedCountInCurrentRec > 0 且小于总数)
                    else if (likedCountInCurrentRec > 0) {
                        app.tip({
                            title: '记录本次推荐？',
                            content: '您已将部分商品加入心仪，是否同时记录其他未选择商品的偏好？',
                            confirmText: '确定',
                            cancelText: '取消',
                            success: (res) => {
                                if (res.confirm) {
                                    this.processExitFeedback(true);
                                } else {
                                    this.processExitFeedback(false);
                                }
                                this.finalizeExit();
                            }
                        });
                    }
                    // 情景三：没有任何推荐商品被加入心仪 (likedCountInCurrentRec === 0)
                    else {
                        app.tip({
                            title: '记录本次推荐？',
                            content: '您未对本次推荐商品进行操作，是否将它们记录为不感兴趣？',
                            confirmText: '确定',
                            cancelText: '取消',
                            success: (res) => {
                                if (res.confirm) {
                                    this.processExitFeedback(true);
                                } else {
                                    this.processExitFeedback(false);
                                }
                                this.finalizeExit();
                            }
                        });
                    }
                } else {
                    console.log('没有当前推荐商品，直接退出。');
                    this.finalizeExit();
                }
                console.log('--- 退出操作调试结束 ---');
                break;
            default: // 未知动作
                console.warn("Unknown action:", action);
                this.addMessage('system', `未知操作：${action}`);
        }
    },

    // 辅助函数：处理退出时的反馈逻辑
    processExitFeedback: function (applyNegativeFeedback) {
        // 首先，找到最近的推荐消息并标记为已交互，以防后续意外触发
        // 这一步确保了无论用户最终如何选择，这条推荐消息的状态都会被标记为“已处理”，
        // 避免在用户再次进入该会话（或通过其他途径）时，同一批次推荐被重复处理。
        let lastRecommendationMessageIndex = -1;
        for (let i = this.data.messages.length - 1; i >= 0; i--) {
            const msg = this.data.messages[i];
            if (msg.data && msg.data.type === 'recommendations') {
                lastRecommendationMessageIndex = i;
                break;
            }
        }
        if (lastRecommendationMessageIndex !== -1) {
            let updatedMessages = [...this.data.messages];
            updatedMessages[lastRecommendationMessageIndex].data.interacted = true;
            this.setData({messages: updatedMessages});
        }


        if (applyNegativeFeedback) {
            const currentRecProducts = this.data.currentRecommendationsForFeedback;
            const shoppingCartNames = new Set(this.data.shoppingCart.map(item => item.name));

            currentRecProducts.forEach(product => {
                // 只有那些在当前推荐批次中但不在购物车里的商品才给予负反馈
                if (!shoppingCartNames.has(product.name)) {
                    this.updateProductReward(product.name, 0);
                    console.log(`Explicit negative feedback for: ${product.name} on exit confirmation.`);
                }
            });
            this.addMessage('system', '商品偏好已记录。');
        } else {
            this.addMessage('system', '未记录本次推荐的负反馈偏好。');
        }
        // 清空当前推荐，因为已经处理完了
        this.setData({
            currentRecommendationsForFeedback: [],
            hasInteractedWithCurrentRecommendations: false
        });
    },

    // 辅助函数：最终化退出操作
    finalizeExit: function () {
        this.saveBanditData(); // 保存当前的Bandit数据
        app.tip({ // 再次提示退出
            title: '提示',
            content: '雪碧期待下次再和您玩耍哦！',
            confirmText: '好的',
            showCancel: false, // 只有确定按钮
            success: () => {
                wx.reLaunch({url: '/pages/csr/csr'}); // 重新加载当前页面
            }
        });
    },
})