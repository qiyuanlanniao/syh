// pages/csr/csr.js
// 获取应用实例
const app = getApp();
const CACHE_BANDIT_DATA_KEY = "csr_bandit_data"; // 用于存储Bandit数据的缓存key

// --- Import Local Products Data ---
// Make sure products_data.js exists in the same directory and exports the products object
const PRODUCTS_DATA = require('./products_data.js'); // <-- Import data here

// --- Frontend Constants ---
// IMPORTANT: Placing API Key here is a SECURITY RISK!
// In a real application, weather requests should be proxied through your backend.
const GAODE_API_KEY = "476b504b1883432f8cb2005493b16580"; // <-- Your API Key is now here! Replace if needed
const CITY_CODE = "350505"; // Jinjiang adcode


const AVAILABLE_DRINKS = {
    "hot": ["热可可", "奶茶", "咖啡", "姜茶"],
    "cold": ["冰镇果汁", "冷泡茶", "冰咖啡", "椰汁", "汽水"],
    "neutral": ["常温矿泉水", "花草茶"]
};

const unsuitableWeatherConditionsForRowing = [
    // 降水类 (根据您的includes条件)
    "阵雨",
    "雷阵雨", // 雷电非常危险
    "雷阵雨并伴有冰雹", // 雷电和冰雹都很危险
    "小雨", // 持续降雨可能影响能见度和保暖
    "中雨",
    "大雨",
    "暴雨",
    "大暴雨",
    "特大暴雨",
    "强阵雨",
    "强雷阵雨", // 雷电非常危险
    "极端降雨",
    "毛毛雨/细雨", // 持续潮湿和能见度影响
    "雨",
    "小雨-中雨",
    "中雨-大雨",
    "大雨-暴雨",
    "暴雨-大暴雨",
    "大暴雨-特大暴雨",
    "雨雪天气", // 混合天气通常不稳定且危险
    "雨夹雪",
    "阵雨夹雪",
    "冻雨", // 导致结冰，非常危险

    // 降雪类 (根据您的includes条件)
    "雪",
    "阵雪",
    "小雪", // 积雪和低温影响
    "中雪",
    "大雪",
    "暴雪",
    "小雪-中雪",
    "中雪-大雪",
    "大雪-暴雪",

    // 强风类 (即使不完全匹配includes("大风"), 强度高的都不适合)
    // 您原条件只包含了 "大风"
    "有风", // 需要评估具体风力
    "强风/劲风", // 明显不适合
    "疾风", // 明显不适合
    "大风", // 根据您的includes条件
    "烈风", // 明显不适合
    "风暴", // 明显不适合
    "狂爆风", // 明显不适合
    "飓风", // 明显不适合 (虽然列表里没有"台风"，但飓风是同类极端天气)
    "龙卷风", // 极端危险

    // 低能见度类 (您指出的，未包含在原includes条件中)
    "霾", // 中度以上霾可能影响能见度
    "中度霾",
    "重度霾",
    "严重霾",
    "浮尘", // 可能影响能见度和呼吸
    "扬沙", // 严重影响能见度和呼吸
    "沙尘暴", // 极端低能见度和危险
    "强沙尘暴", // 极端危险
    "雾", // 影响能见度
    "浓雾", // 严重影响能见度
    "强浓雾", // 严重影响能见度
    "轻雾", // 持续可能转浓或影响判断
    "大雾", // 严重影响能见度
    "特强浓雾", // 极端低能见度，非常危险

    // 极端气温类 (虽然没有直接的includes条件，但极端冷热也可能不适合)
    // "热", // 极端高温可能导致中暑
    // "冷", // 极端低温可能导致失温
    // 注：是否包含极端气温取决于划船类型和装备，这里先主要包含现象类。
];



Page({
    data: {
        messages: [], // 存储聊天消息的数组
        scrollToView: '', // 控制scroll-view滚动到指定元素

        // UI control state
        showTagInput: false, // Whether to show tag input box

        // Data (From imported JS file)
        products: PRODUCTS_DATA, // Use the imported data directly
        availableTags: [], // Extracted from products data
        tagToProductsIndex: null, // Cache tag to products index

        // Bandit state (Stored in local cache)
        Q: {}, // Estimated reward values for products
        N: {}, // Number of times product was selected
        likedTags: [], // User's preferred tags (session-level + for recommendation calculation)
        recommendedProductsAll: [], // Products recommended in this session (for exclusion)
        recommendationCycleCount: 0, // Recommendation cycle count (for epsilon decay)
        shoppingCart: [], // Shopping cart contents (list of product names)

        // Epsilon-Greedy Parameters (Adjustable)
        initialEpsilon: 0.5,
        epsilonDecayRate: 0.005,
        minEpsilon: 0.05,
        topN: 3, // Number of items to recommend per cycle

        // Tag similarity threshold (adjust as needed)
        tagSimilarityThreshold: 0.5, // Minimum similarity (0 to 1, higher means more similar)
        maxSuggestedTags: 3, // Max number of suggestions per invalid tag
    },

    onLoad: function () {
        // --- Initial Setup (Chain asynchronous calls) ---

        // 1. Add welcome message immediately
        this.addMessage('system', '汪！欢迎来到山屿海营地，我是营地的拉布拉多——"雪碧"！由我为您提供推荐服务。');

        this.addMessage('system', '', { type: 'image', content: '../../images/dog.png' });

        console.log('Messages after adding image:', this.data.messages);

        // 2. Load local Bandit data (Synchronous)
        this.loadBanditData(); // Load Q/N from cache

        // 3. Process imported product data and build tag index (Synchronous)
        this.processProductsData(); // Process the already available PRODUCTS_DATA

        // 4. Get initial weather and drink data (Asynchronous)
        // We call getWeatherAndDrinks, and once its messages are added, the next step (showing tag input if applicable) happens.
        this.getWeatherAndDrinks()
             .catch(() => {
                // If weather/drinks failed, proceed anyway to showing products part prompt
                 console.warn("Weather/Drinks failed, proceeding to show products part prompt.");
             });

        // The logic to display tag input or initial recommendation prompt is now inside processProductsData,
        // which runs after products data is loaded and messages from weather/drinks are added via the promise chain.
    },

    onReady: function() { this.scrollToBottom(); },
    onShow: function () { this.scrollToBottom(); },
    onUnload: function() { this.saveBanditData(); }, // Save Bandit data when page is unloaded

    // --- Message Handling ---
    addMessage: function(type, text, data = null) {
        const newMessage = { type, text, data, timestamp: Date.now() };
        this.setData({ messages: [...this.data.messages, newMessage] }, () => this.scrollToBottom());
    },
    scrollToBottom: function() {
         setTimeout(() => {
            if (this.data.messages.length > 0) {
                 this.setData({ scrollToView: `msg-${this.data.messages[this.data.messages.length - 1].timestamp}` });
            } else {
                 this.setData({ scrollToView: 'bottom' });
            }
         }, 100);
    },


    // --- Data Processing, Loading, Saving ---

    // Process imported products data and build tag index
    processProductsData: function() {
        const products = this.data.products; // Get the imported data

        if (!products || Object.keys(products).length === 0) {
             console.warn("Imported products data is empty.");
             this.addMessage('system', '商品数据为空，无法提供商品推荐服务。');
             this.setData({ showTagInput: false }); // Hide tag input if no products
             this.initializeBanditData({}); // Init Bandit with empty products
             this.setData({ tagToProductsIndex: null }); // Clear index
             return;
        }

        const availableTags = this.extractAvailableTags(products);
        const sampleTags = availableTags.slice(0, 10).join(', ');
        const tagToProductsIndex = this.buildTagToProductsIndex(products); // Build index

        this.setData({
            availableTags: availableTags,
            availableTagsSample: sampleTags,
            tagToProductsIndex: tagToProductsIndex, // Store index in data
        });
        console.log("Products data processed. Available tags:", availableTags.length);

        // Initialize/Sync Bandit data with current products
        this.initializeBanditData(products);


        // After products are processed and Bandit is initialized, determine if tag input should be shown
        // The message prompting for tags is added after weather/drinks, so we just set the UI flag here.
        if (Object.keys(products).length > 0 && availableTags.length > 0) {
             this.setData({ showTagInput: true }); // Show tag input if products and tags are available
             // The message is triggered after weather/drinks complete
        } else {
             // No products or no tags, cannot use tag input
             this.setData({ showTagInput: false });
              if (Object.keys(products).length > 0 && availableTags.length === 0) {
                   // Products available but no tags, inform user
                   this.addMessage('system', '商品数据已加载，但没有找到标签，无法进行标签推荐。您可以尝试获取新推荐。');
               } else {
                   // Products data wasn't even available/empty
                   this.addMessage('system', '商品数据不可用，无法进行商品推荐。');
               }
        }
    },


    // From products data, extract all available tags
    extractAvailableTags: function(products) {
         const allTagsSet = new Set();
         if (!products) return [];
         for (const productName in products) {
             if (products.hasOwnProperty(productName)) {
                 const productData = products[productName];
                 const tags = productData.标签 || [];
                 tags.forEach(tag => {
                     if (typeof tag === 'string' && tag.trim()) {
                         allTagsSet.add(tag.trim());
                     }
                 });
             }
         }
         return Array.from(allTagsSet);
    },

     // Helper: Build tag to products index
    buildTagToProductsIndex: function(products) {
         const tagToProducts = {};
         if (!products) return tagToProducts;
         for (const productName in products) {
             if (products.hasOwnProperty(productName)) {
                 const productData = products[productName];
                 const tags = productData.标签 || [];
                 tags.forEach(tag => {
                     if (typeof tag === 'string' && tag.trim()) {
                         const cleanedTag = tag.trim();
                         if (!tagToProducts[cleanedTag]) {
                             tagToProducts[cleanedTag] = [];
                         }
                         tagToProducts[cleanedTag].push(productName);
                     }
                 });
             }
         }
         return tagToProducts;
    },


    // Load Bandit data from local cache (Unchanged)
    loadBanditData: function() {
        try {
            const data = wx.getStorageSync(CACHE_BANDIT_DATA_KEY);
            if (data) {
                console.log("Loaded Bandit data from cache.");
                this.setData({
                     Q: data.Q || {},
                     N: data.N || {},
                });
            } else {
                console.log("No Bandit data found in cache.");
                this.setData({ Q: {}, N: {}, });
            }
        } catch (e) {
            console.error("Failed to load Bandit data from cache:", e);
             this.addMessage('system', '加载本地偏好数据失败。');
        }
    },

    // Initialize or sync Bandit data (Q, N) with current products (Unchanged)
    initializeBanditData: function(products) {
        if (!products || Object.keys(products).length === 0) {
             console.warn("Products data is empty or null, cannot initialize Bandit data.");
             this.setData({ Q: {}, N: {}, recommendationCycleCount: 0 });
             return;
        }

        const productNames = Object.keys(products);
        let currentQ = this.data.Q || {};
        let currentN = this.data.N || {};

        let updatedQ = {};
        let updatedN = {};
        let reinitialized = false;

        productNames.forEach(p => {
             updatedQ[p] = parseFloat(currentQ[p] || 0.0);
             updatedN[p] = parseInt(currentN[p] || 0);
        });

         if (Object.keys(currentQ).length === 0 && Object.keys(currentN).length === 0 && productNames.length > 0) {
              reinitialized = true;
              console.log("Bandit data loaded empty, reinitializing based on current products.");
         }

        this.setData({
            Q: updatedQ,
            N: updatedN,
            recommendationCycleCount: reinitialized ? 0 : (this.data.recommendationCycleCount || 0)
        });

         if (reinitialized) {
              this.addMessage('system', '商品列表或偏好数据已重置，推荐系统数据已同步。');
         }
         console.log("Bandit data initialized/synced with products. Current Q/N counts:", Object.keys(this.data.Q).length, Object.keys(this.data.N).length);
    },


    // Save Bandit data to local cache (Unchanged)
    saveBanditData: function() {
        if (!this.data.products || Object.keys(this.data.products).length === 0) {
             console.warn("Products data not loaded, skipping saving Bandit data.");
             return;
        }
        try {
            const dataToSave = {
                Q: this.data.Q,
                N: this.data.N,
            };
            wx.setStorageSync(CACHE_BANDIT_DATA_KEY, dataToSave);
            console.log("Bandit data saved to cache.");
        } catch (e) {
            console.error("Failed to save Bandit data to cache:", e);
             this.addMessage('system', '保存本地偏好数据失败。');
        }
    },


    // --- Weather and Drink Logic (Frontend Implementation) ---

    // Modified to return a Promise (Unchanged)
    getWeatherAndDrinks: function() {
        const that = this;
        wx.showLoading({ title: '加载天气饮品...' });
        const weatherApiUrl = `https://restapi.amap.com/v3/weather/weatherInfo?city=${CITY_CODE}&key=${GAODE_API_KEY}`;

        return new Promise((resolve, reject) => {
            wx.request({
                 url: weatherApiUrl,
                 method: 'GET',
                 success: function(res) {
                     wx.hideLoading();
                     let weather_info = null;
                     let boat_suitability = "抱歉，暂时无法判断划船适宜性。";
                     let recommended_drinks = [];
                     let success = false;

                     if (res.statusCode === 200 && res.data && res.data.status === "1") {
                         if (res.data.lives && res.data.lives.length > 0) {
                              const weather_result = res.data.lives[0];
                              weather_info = {
                                  "weather": weather_result.weather || "未知",
                                  "temperature": weather_result.temperature || "未知",
                                  "winddirection": weather_result.winddirection || "未知",
                                  "windpower": weather_result.windpower || "未知",
                                  "humidity": weather_result.humidity || "未知"
                              };
                              boat_suitability = that.isGoodForBoating(weather_result) ? "今天天气不错，非常适合划船！" : "今天天气不太适合划船哦。";
                              recommended_drinks = that.getRecommendedDrinks(weather_info.temperature);

                              success = true;
                         } else {
                             console.warn("Gaode API returned status 1 but lives array is empty.", res.data);
                         }
                     } else {
                         const infocode = res.data ? res.data.infocode : '未知';
                         const info = res.data ? res.data.info : '未知';
                          console.error(`Gaode API request failed. Status: ${res.statusCode}, infocode: ${infocode}, info: ${info}`);
                     }

                     if (weather_info) {
                         that.addMessage('system', '今日天气信息：', { type: 'weather', content: weather_info, suitability: boat_suitability });
                     } else {
                          const failureMessage = res.data && res.data.info ? `获取天气信息失败: ${res.data.info}` : '抱歉，暂时无法获取天气信息。';
                         that.addMessage('system', failureMessage);
                     }

                     if (recommended_drinks.length > 0) {
                          that.addMessage('system', '根据天气，为您推荐以下饮品：', {
                              type: 'drinks',
                              content: recommended_drinks,
                              selected: false,
                              selectedIndex: -2,
                          });
                     } else if (success && weather_info) {
                         that.addMessage('system', '暂无推荐饮品（可能温度数据异常）。');
                     } else {
                         that.addMessage('system', '暂无推荐饮品。');
                     }
                    resolve(); // Resolve even if weather fetch failed
                 },
                 fail: function(err) {
                     wx.hideLoading();
                     console.error("Get weather network failed:", err);
                     that.addMessage('system', '获取天气饮品网络请求失败。');
                     reject(err); // Reject if network request failed
                 }
            });
        });
    },

    isGoodForBoating: function(weatherData) {
        /**
         * Determines if good for boating based on weather data.
         * weatherData: Realtime weather data dictionary from Gaode API 'lives' array item.
         */
        if (!weatherData) {
             console.warn("Boating check: Invalid weatherData provided.");
             return false;
        }
        const weatherCondition = weatherData.weather || "";
        const windPowerStr = weatherData.windpower || "0";
        const windPower = parseInt(windPowerStr);

        if (isNaN(windPower)) {
             console.warn(`Boating check: Unable to parse wind power: ${windPowerStr}`);
             return false;
        }

        // Conditions not suitable for boating (add more conditions if needed, like thunderstorms)
        if (unsuitableWeatherConditionsForRowing.includes(weatherCondition)) {
            return false;
        }
        if (windPower > 4) { // Wind force > 4 not suitable (Beaufort scale)
            return false;
        }
        return true;
    },

    getRecommendedDrinks: function(temperatureStr) {
        /**
         * Recommends drinks based on temperature.
         * temperatureStr: Temperature string.
         * Returns: Array of drink names.
         */
        const recommendedDrinksList = [];
        try {
            const tempInt = parseInt(temperatureStr);
            if (isNaN(tempInt)) {
                 console.warn(`Drink recommendation: Unable to parse temperature: ${temperatureStr}`);
                 return [];
            }

            // Recommend based on temperature ranges
            if (tempInt < 15) {
                return AVAILABLE_DRINKS.hot || [];
            } else if (tempInt >= 25) {
                return AVAILABLE_DRINKS.cold || [];
            } else { // 15 <= tempInt < 25
                return AVAILABLE_DRINKS.neutral || [];
            }
        } catch (e) {
            console.error("Drink recommendation: Error processing temperature or accessing drinks data:", e);
            return [];
        }
    },

    // --- String Similarity Helper (Levenshtein Distance) ---
    // Function to calculate Levenshtein distance between two strings (Unchanged)
    levenshteinDistance: function(a, b) {
        const an = a ? a.length : 0;
        const bn = b ? b.length : 0;
        if (an === 0) return bn;
        if (bn === 0) return an;

        const matrix = [];

        for (let i = 0; i <= an; i++) { matrix[i] = [i]; }
        for (let j = 0; j <= bn; j++) { matrix[0][j] = j; }

        for (let i = 1; i <= an; i++) {
            for (let j = 1; j <= bn; j++) {
                const cost = (a[i - 1] === b[j - 1]) ? 0 : 1;
                matrix[i][j] = Math.min( matrix[i - 1][j] + 1, matrix[i][j - 1] + 1, matrix[i - 1][j - 1] + cost );
            }
        }
        return matrix[an][bn];
    },

    // Function to calculate similarity based on Levenshtein distance (Unchanged)
    levenshteinSimilarity: function(s1, s2) {
        if (!s1 && !s2) return 1.0;
        if (!s1 || !s2) return 0.0;
        const maxLength = Math.max(s1.length, s2.length);
        if (maxLength === 0) return 1.0;
        const distance = this.levenshteinDistance(s1, s2);
        return 1.0 - (distance / maxLength);
    },

    // Find similar available tags for an invalid tag (Unchanged)
    findSimilarTags: function(invalidTag) {
        const availableTags = this.data.availableTags;
        const suggestions = [];

        if (!availableTags || availableTags.length === 0) { return []; }

        availableTags.forEach(availableTag => {
            const similarity = this.levenshteinSimilarity(invalidTag.toLowerCase(), availableTag.toLowerCase());
            if (similarity >= this.data.tagSimilarityThreshold) {
                suggestions.push({ tag: availableTag, similarity: similarity });
            }
        });

        suggestions.sort((a, b) => b.similarity - a.similarity);

        return suggestions.slice(0, this.data.maxSuggestedTags).map(s => s.tag);
    },


    // --- Bandit Logic (Frontend Implementation) ---

    // Generate recommendations based on tags and Bandit Q-values (Corrected sort logic)
    getRecommendationsLogic: function() {
         if (!this.data.products || Object.keys(this.data.products).length === 0) {
             console.warn("Products data missing for recommendations logic.");
             return [];
         }

        const products = this.data.products;
        const productNames = Object.keys(products);
        const Q = this.data.Q;
        const N = this.data.N;
        const likedTags = this.data.likedTags;
        const excludedProducts = [...this.data.recommendedProductsAll, ...this.data.shoppingCart];
        const topN = this.data.topN;
        const recommendationCycleCount = this.data.recommendationCycleCount;

        const currentEpsilon = Math.max(this.data.minEpsilon, this.data.initialEpsilon - this.data.epsilonDecayRate * recommendationCycleCount);
        console.log(`Recommendation Cycle: ${recommendationCycleCount}, Current epsilon: ${currentEpsilon.toFixed(4)}`);

        const cleanedLikedTags = likedTags.map(tag => tag.trim()).filter(tag => tag !== '');
        const tagToProducts = this.data.tagToProductsIndex; // Use cached index


        let candidateProductsWithScores = {};
        productNames.forEach(p => candidateProductsWithScores[p] = 0.0);


        if (cleanedLikedTags.length > 0) {
            candidateProductsWithScores = {};
            cleanedLikedTags.forEach(tag => {
                if (tagToProducts && tagToProducts[tag]) {
                    tagToProducts[tag].forEach(product => {
                         candidateProductsWithScores[product] = (candidateProductsWithScores[product] || 0.0) + 1;
                    });
                } else {
                    console.warn(`Liked tag "${tag}" not found in products data's tag index.`);
                }
            });
        }


        const excludedSet = new Set(excludedProducts);
        for (const product in candidateProductsWithScores) {
            if (excludedSet.has(product)) {
                delete candidateProductsWithScores[product];
            }
        }

        let recommendations = [];
        const candidateProductsList = Object.keys(candidateProductsWithScores);


        if (candidateProductsList.length === 0) {
            console.log("No suitable candidates found, falling back to all available.");
            const allAvailableProducts = productNames.filter(p => !excludedSet.has(p));

            if (allAvailableProducts.length === 0) {
                console.log("No products left to recommend.");
                return [];
            }

            allAvailableProducts.sort((a, b) => (Q[b] || 0.0) - (Q[a] || 0.0));
            recommendations = allAvailableProducts.slice(0, topN);
            console.log(`Fallback recommended ${recommendations.length} items.`);
            return recommendations;
        }

        // Epsilon-Greedy Selection
        if (Math.random() < currentEpsilon) {
            console.log(`(Explore stage - epsilon=${currentEpsilon.toFixed(4)})`);
            recommendations = this.shuffleArray(candidateProductsList).slice(0, Math.min(topN, candidateProductsList.length));
        } else {
            console.log(`(Exploit stage - epsilon=${currentEpsilon.toFixed(4)})`);
            // Corrected sort logic:
            const sortedCandidates = Object.entries(candidateProductsWithScores).sort((a, b) => {
                 const scoreA = a[1];
                 const scoreB = b[1];
                 const productA = a[0];
                 const productB = b[0];
                 const Q = this.data.Q;

                 if (scoreB !== scoreA) {
                     return scoreB - scoreA;
                 }
                 return (Q[productB] || 0.0) - (Q[productA] || 0.0);
             });

            recommendations = sortedCandidates.slice(0, topN).map(item => item[0]);
        }

        console.log(`Generated ${recommendations.length} recommendations.`);
        return recommendations;
    },


    // Helper: Build tag to products index (Modified to be callable) (Unchanged)
    buildTagToProductsIndex: function(products) {
         const tagToProducts = {};
         if (!products) return tagToProducts;
         for (const productName in products) {
             if (products.hasOwnProperty(productName)) {
                 const productData = products[productName];
                 const tags = productData.标签 || [];
                 tags.forEach(tag => {
                     if (typeof tag === 'string' && tag.trim()) {
                         const cleanedTag = tag.trim();
                         if (!tagToProducts[cleanedTag]) {
                             tagToProducts[cleanedTag] = [];
                         }
                         tagToProducts[cleanedTag].push(productName);
                     }
                 });
             }
         }
         return tagToProducts;
    },

    // Helper: Shuffle array (Unchanged)
    shuffleArray: function(array) {
        const shuffled = [...array];
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        return shuffled;
    },


    // Update product estimated reward (local logic) (Unchanged)
    updateProductReward: function(productName, reward) {
        if (!this.data.products || !this.data.products[productName]) {
             console.warn(`Cannot update reward for unknown product: ${productName}`);
             return;
        }
        let Q = this.data.Q;
        let N = this.data.N;

         if (!Q.hasOwnProperty(productName)) Q[productName] = 0.0;
         if (!N.hasOwnProperty(productName)) N[productName] = 0;


        N[productName] = (N[productName] || 0) + 1;
        Q[productName] = (Q[productName] || 0.0) + (reward - (Q[productName] || 0.0)) / N[productName];

        console.log(`Updated product '${productName}' Q: ${Q[productName].toFixed(4)}, N: ${N[productName]}`);

        this.setData({ Q, N });
        this.saveBanditData(); // Save after update
    },


    // --- User Interaction Handlers ---

    // Drink selection (Modified to trigger getProductRecommendations)
    selectDrink: function(e) {
        const msgIndex = e.currentTarget.dataset.msgIndex;
        const index = parseInt(e.currentTarget.dataset.drinkIndex);

        const updatedMessages = this.data.messages;
        if (msgIndex >= 0 && msgIndex < updatedMessages.length && updatedMessages[msgIndex].data && updatedMessages[msgIndex].data.type === 'drinks') {
             if (updatedMessages[msgIndex].data.selected) {
                  console.log("Drink already selected for this message.");
                  return;
             }
             updatedMessages[msgIndex].data.selected = true;
             updatedMessages[msgIndex].data.selectedIndex = index;
             this.setData({ messages: updatedMessages });
             this.scrollToBottom();
        } else {
            console.error("Failed to update drink message state.");
        }

        let selectedItemText = "";
        if (index === -1) {
            selectedItemText = "不想喝";
        } else if (index >= 0 && updatedMessages[msgIndex].data && updatedMessages[msgIndex].data.content && index < updatedMessages[msgIndex].data.content.length) {
             selectedItemText = updatedMessages[msgIndex].data.content[index];
        } else {
             console.error("Invalid drink index selected.");
             return;
        }

        this.addMessage('user', selectedItemText);

        app.tip({ content: index === -1 ? "好的，祝您开心！" : `好的，正在为您准备：${selectedItemText}，请稍候！` });

        // --- Automatically proceed to product recommendation after drink selection ---
        // Wait a moment for messages/tip to show, then proceed
        setTimeout(() => {
            // If products data is available and has tags, the UI is waiting for tag input.
            // If products data is available but has NO tags, we can auto-recommend.
            // If products data is NOT available, we can't do anything.
             if (this.data.products && Object.keys(this.data.products).length > 0) {
                  // Check if we should proceed directly to recommendation or wait for tags
                  if (this.data.availableTags.length === 0 || (this.data.likedTags && this.data.likedTags.length > 0) ) {
                       // Case 1: No tags available in products data -> proceed with general rec
                       // Case 2: Liked tags are already set (user returned to page) -> proceed with rec
                       console.log("Proceeding with recommendation after drink selection.");
                       this.getProductRecommendations();
                  } else {
                      // Tags are available but not set. UI is showing tag input. Wait for user.
                       console.log("Available tags exist but not set. Waiting for user to confirm tags.");
                       // The tag input message is already added by processProductsData
                       // Ensure the tag input UI is visible
                        this.setData({ showTagInput: true });
                  }
             } else {
                  console.warn("Product data not available, cannot proceed to recommendations.");
             }
        }, 1500); // Wait 1.5 seconds
    },


    // Handle tag input handler (Unchanged)
    handleTagInputChange: function(e) {
        this.setData({ currentTagInput: e.detail.value });
    },

    // Confirm tags input (Modified to handle invalid tags and suggestions) (Unchanged)
    confirmTags: function() {
        const input = (this.data.currentTagInput || '').trim();
        if (!input) {
             app.alert({ content: "请输入您喜欢的标签。" });
             return;
        }
        const processedInput = input.replace(/，/g, ',');
        let enteredTags = processedInput.split(',').map(tag => tag.trim()).filter(tag => tag !== '');

         if (enteredTags.length === 0) {
             app.alert({ content: "请至少输入一个您喜欢的标签。" });
             return;
         }

        // Validate entered tags against available tags
         const availableTagsSet = new Set(this.data.availableTags);
         const validTags = enteredTags.filter(tag => availableTagsSet.has(tag));
         const invalidTags = enteredTags.filter(tag => !availableTagsSet.has(tag));

         if (invalidTags.length > 0) {
              // Find similar tags for each invalid tag
              const suggestionsMap = {}; // { invalidTag: [suggestedTag1, ...] }
              invalidTags.forEach(invalidTag => {
                   const similarTags = this.findSimilarTags(invalidTag);
                   if (similarTags.length > 0) {
                        suggestionsMap[invalidTag] = similarTags;
                   }
              });

              let promptMessage = `您输入的以下标签无效：${invalidTags.join(', ')}。\n`;
              if (Object.keys(suggestionsMap).length > 0) {
                   promptMessage += '您是否想使用以下建议标签来替代：\n';
                   for (const invalidTag in suggestionsMap) {
                        promptMessage += `  "${invalidTag}" ➔ ${suggestionsMap[invalidTag].join(' 或 ')}\n`;
                   }

                   app.tip({
                      title: '无效标签提示',
                      content: promptMessage,
                      confirmText: '使用建议+有效',
                      cancelText: '只用有效标签',
                      success: (res) => {
                          if (res.confirm) {
                              const suggestedTags = Object.values(suggestionsMap).flat();
                              const finalLikedTags = Array.from(new Set([...validTags, ...suggestedTags]));
                              this.proceedWithValidTags(finalLikedTags, invalidTags);
                          } else if (res.cancel) {
                               if (validTags.length > 0) {
                                   this.proceedWithValidTags(validTags, invalidTags);
                               } else {
                                    app.alert({ content: "没有有效的标签可以使用，请重新输入。" });
                                    this.addMessage('system', '没有有效的标签可以使用，请重新输入您的偏好标签。');
                               }
                          }
                      }
                   });

              } else {
                  // No similar tags found, just inform about invalid tags
                  promptMessage += validTags.length > 0 ? '有效标签已保留。是否只使用有效标签？' : '没有有效的标签可以使用。请重新输入。';

                   app.tip({
                      title: '无效标签提示',
                      content: promptMessage,
                      confirmText: '只用有效标签',
                      cancelText: '重新输入',
                       showCancel: validTags.length > 0,
                      success: (res) => {
                           if (res.confirm && validTags.length > 0) {
                                this.proceedWithValidTags(validTags, invalidTags);
                           } else {
                                app.alert({ content: "请重新输入您的偏好标签。" });
                                this.addMessage('system', '请重新输入您的偏好标签。');
                           }
                      }
                   });
              }


         } else {
             // All tags are valid, proceed directly
             this.proceedWithValidTags(enteredTags, []);
         }
    },

    // Helper function to proceed after tag validation (Unchanged)
    proceedWithValidTags: function(validTags, ignoredTags) {
         this.setData({
             likedTags: validTags,
             currentTagInput: '',
             showTagInput: false,
             recommendedProductsAll: [],
             recommendationCycleCount: 0,
         });
         this.addMessage('user', `我的偏好标签是：${validTags.join(', ')}` + (ignoredTags.length > 0 ? ` (忽略无效标签：${ignoredTags.join(', ')})` : ''));
         this.addMessage('system', "偏好标签已更新。");

         // Tags set successfully, get recommendations
         this.getProductRecommendations();
    },


    // Get product recommendations (Calls local Bandit logic and displays result) (Unchanged logic, just added comment)
    getProductRecommendations: function() {
         if (!this.data.products || Object.keys(this.data.products).length === 0) {
              this.addMessage('system', '商品数据未加载或为空，无法推荐。');
              return;
         }

         this.addMessage('system', '正在为您挑选合适的商品...');
         wx.showLoading({ title: '生成推荐中...' });

         this.setData({ recommendationCycleCount: this.data.recommendationCycleCount + 1 });

         const recommendations = this.getRecommendationsLogic();

         wx.hideLoading();

         const recommendationDetails = recommendations.map(name => {
              const product = this.data.products[name];
              return product ? { name: name, ...product } : null;
         }).filter(p => p !== null);

         const newlyRecommended = recommendations.filter(p =>
              !this.data.recommendedProductsAll.includes(p) && !this.data.shoppingCart.includes(p)
         );
         this.setData({
              recommendedProductsAll: [...this.data.recommendedProductsAll, ...newlyRecommended],
         });

         if (recommendationDetails && recommendationDetails.length > 0) {
             this.addMessage('system', '为您推荐以下商品:', { type: 'recommendations', content: recommendationDetails });
         } else {
             this.addMessage('system', '当前没有找到更多推荐商品了。您可以尝试修改偏好标签。');
         }

         this.saveBanditData();
    },

    // Select recommended product (Add to cart and update Bandit) (Unchanged)
    selectProduct: function(e) {
         const selectedProduct = e.currentTarget.dataset.productName;
         console.log("User selected product:", selectedProduct);

         if (!this.data.products || !this.data.products[selectedProduct]) {
              console.error(`Invalid product selected: ${selectedProduct}`);
              this.addMessage('system', `无效商品选择: ${selectedProduct}`);
              return;
         }

         const shoppingCart = [...this.data.shoppingCart, selectedProduct];
         this.setData({ shoppingCart });

         this.updateProductReward(selectedProduct, 1);

         this.addMessage('user', `我选择了商品：${selectedProduct}`);
         this.addMessage('system', `'${selectedProduct}' 已添加到心仪商品并记录偏好。`);
    },

    // View shopping cart (Display local cart state) (Unchanged)
    viewCart: function() {
        console.log("User viewed cart.");
         this.addMessage('user', '查看心仪商品');

        const cartCounts = {};
        this.data.shoppingCart.forEach(item => { cartCounts[item] = (cartCounts[item] || 0) + 1; });
        const cartList = Object.keys(cartCounts).map(item => ({ name: item, count: cartCounts[item] }));

        this.addMessage('system', '您的心仪商品：', { type: 'cart', content: cartList });
    },

    // New function to delete a single item from the cart (Unchanged)
    deleteCartItem: function(e) {
         const productNameToDelete = e.currentTarget.dataset.productName;
         console.log("User requested to delete from cart:", productNameToDelete);

         const indexToDelete = this.data.shoppingCart.indexOf(productNameToDelete);

         if (indexToDelete !== -1) {
              const updatedCart = [...this.data.shoppingCart];
              updatedCart.splice(indexToDelete, 1);

              this.setData({ shoppingCart: updatedCart });
              console.log("Updated cart:", updatedCart);

              this.addMessage('user', `从心仪商品删除：${productNameToDelete}`);
              this.addMessage('system', `'${productNameToDelete}' 已从心仪商品中移除。`);

              this.displayCartMessage();
         } else {
              console.warn(`Attempted to delete item "${productNameToDelete}" not found in cart.`);
              this.addMessage('system', `尝试删除的商品 "${productNameToToDelete}" 不在心仪商品中。`);
         }
    },


    // Clear shopping cart (Unchanged)
    clearCart: function() {
         app.tip({
            title: '提示',
            content: '确定要清空心仪商品吗？',
            cb_confirm: () => {
                console.log("User cleared cart.");
                 this.setData({ shoppingCart: [] });
                this.addMessage('user', '清空心仪商品');
                this.addMessage('system', '心仪商品已清空。');
                this.displayCartMessage();
            }
         });
    },

    // Helper to display current cart message (Unchanged)
    displayCartMessage: function() {
        const cartCounts = {};
        this.data.shoppingCart.forEach(item => {
            cartCounts[item] = (cartCounts[item] || 0) + 1;
        });
        const cartList = Object.keys(cartCounts).map(item => ({ name: item, count: cartCounts[item] }));

        this.addMessage('system', '您的心仪商品：', {
             type: 'cart',
             content: cartList
         });
    },


    // Handle bottom action buttons (Unchanged)
    handleAction: function(e) {
        const action = e.currentTarget.dataset.action;
        console.log("User action:", action);

        switch (action) {
            case 'a': // Get new recommendations
                 if (!this.data.products || Object.keys(this.data.products).length === 0) {
                     this.addMessage('system', '商品数据未加载或为空，无法推荐。');
                     return;
                 }
                this.getProductRecommendations();
                break;
            case 'b': // Modify liked tags
                this.addMessage('user', '修改偏好标签');
                 if (!this.data.products || Object.keys(this.data.products).length === 0 || this.data.availableTags.length === 0) {
                     this.addMessage('system', '商品数据或标签缺失，无法设置偏好标签。');
                     this.setData({ showTagInput: false });
                 } else {
                     this.addMessage('system', '请重新输入您喜欢的标签：');
                     this.setData({
                          showTagInput: true,
                          currentTagInput: '',
                          likedTags: [],
                          recommendedProductsAll: [],
                          recommendationCycleCount: 0,
                     });
                 }
                break;
            case 'c': // View shopping cart
                this.viewCart();
                break;
            case 'clear_cart':
                 this.clearCart();
                 break;
            case 'd': // Exit (Modified exit logic)
                 app.tip({
                     title: '提示',
                     content: '雪碧期待下次再和您玩耍哦！',
                     cb_confirm: () => {
                          this.saveBanditData();
                          wx.reLaunch({
                              url: '/pages/csr/csr'
                          });
                     },
                     cb_cancel: () => {
                     }
                 });
                break;
            default:
                console.warn("Unknown action:", action);
                 this.addMessage('system', `未知操作：${action}`);
        }
    },

    // ... Other lifecycle functions or custom methods ...
})