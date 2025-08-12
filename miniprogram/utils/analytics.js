/**
 * 数据统计和分析工具
 * 提供用户行为追踪、性能监控、错误统计等功能
 */

/**
 * 事件类型枚举
 */
const EVENT_TYPE = {
  // 页面事件
  PAGE_VIEW: 'page_view',           // 页面访问
  PAGE_LEAVE: 'page_leave',         // 页面离开
  PAGE_SHARE: 'page_share',         // 页面分享
  
  // 用户行为事件
  BUTTON_CLICK: 'button_click',     // 按钮点击
  SEARCH: 'search',                 // 搜索
  SCAN: 'scan',                     // 扫码
  UPLOAD: 'upload',                 // 上传
  DOWNLOAD: 'download',             // 下载
  
  // 功能使用事件
  NUTRITION_ANALYSIS: 'nutrition_analysis',  // 营养分析
  FOOD_RECOGNITION: 'food_recognition',      // 食物识别
  RECIPE_VIEW: 'recipe_view',               // 食谱查看
  ENCYCLOPEDIA_VIEW: 'encyclopedia_view',    // 百科查看
  
  // 错误事件
  ERROR: 'error',                   // 错误
  API_ERROR: 'api_error',          // API错误
  NETWORK_ERROR: 'network_error',   // 网络错误
  
  // 性能事件
  PERFORMANCE: 'performance',       // 性能指标
  LOAD_TIME: 'load_time',          // 加载时间
  
  // 用户生命周期事件
  USER_REGISTER: 'user_register',   // 用户注册
  USER_LOGIN: 'user_login',        // 用户登录
  USER_LOGOUT: 'user_logout',      // 用户登出
  
  // 业务事件
  FEEDBACK: 'feedback',            // 反馈
  SETTING_CHANGE: 'setting_change' // 设置更改
};

/**
 * 数据统计管理器
 */
class AnalyticsManager {
  constructor() {
    this.sessionId = this.generateSessionId();
    this.userId = null;
    this.deviceInfo = null;
    this.appInfo = null;
    this.eventQueue = [];
    this.isEnabled = true;
    this.batchSize = 10;
    this.flushInterval = 30000; // 30秒
    this.maxQueueSize = 100;
    
    this.init();
  }
  
  /**
   * 初始化
   */
  async init() {
    try {
      // 获取设备信息
      this.deviceInfo = await this.getDeviceInfo();
      
      // 获取应用信息
      this.appInfo = await this.getAppInfo();
      
      // 从本地存储获取用户ID
      this.userId = wx.getStorageSync('userId') || null;
      
      // 启动定时上报
      this.startBatchReporting();
      
      // 监听应用生命周期
      this.setupLifecycleListeners();
      
    } catch (error) {
      console.error('Analytics初始化失败:', error);
    }
  }
  
  /**
   * 生成会话ID
   */
  generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  
  /**
   * 获取设备信息
   */
  async getDeviceInfo() {
    return new Promise((resolve) => {
      wx.getSystemInfo({
        success: (res) => {
          resolve({
            brand: res.brand,
            model: res.model,
            system: res.system,
            platform: res.platform,
            version: res.version,
            SDKVersion: res.SDKVersion,
            screenWidth: res.screenWidth,
            screenHeight: res.screenHeight,
            pixelRatio: res.pixelRatio,
            language: res.language,
            fontSizeSetting: res.fontSizeSetting,
            theme: res.theme
          });
        },
        fail: () => {
          resolve({});
        }
      });
    });
  }
  
  /**
   * 获取应用信息
   */
  async getAppInfo() {
    return new Promise((resolve) => {
      wx.getAccountInfoSync && resolve({
        appId: wx.getAccountInfoSync().miniProgram?.appId,
        version: wx.getAccountInfoSync().miniProgram?.version,
        envVersion: wx.getAccountInfoSync().miniProgram?.envVersion
      }) || resolve({});
    });
  }
  
  /**
   * 设置用户ID
   * @param {string} userId - 用户ID
   */
  setUserId(userId) {
    this.userId = userId;
    wx.setStorageSync('userId', userId);
  }
  
  /**
   * 启用/禁用统计
   * @param {boolean} enabled - 是否启用
   */
  setEnabled(enabled) {
    this.isEnabled = enabled;
    if (!enabled) {
      this.eventQueue = [];
    }
  }
  
  /**
   * 追踪事件
   * @param {string} eventType - 事件类型
   * @param {object} properties - 事件属性
   * @param {object} options - 选项
   */
  track(eventType, properties = {}, options = {}) {
    if (!this.isEnabled) return;
    
    const event = {
      eventType,
      properties: {
        ...properties,
        timestamp: Date.now(),
        sessionId: this.sessionId,
        userId: this.userId,
        page: this.getCurrentPage(),
        ...this.getCommonProperties()
      },
      options
    };
    
    // 添加到队列
    this.eventQueue.push(event);
    
    // 检查是否需要立即上报
    if (options.immediate || this.eventQueue.length >= this.batchSize) {
      this.flush();
    }
    
    // 防止队列过大
    if (this.eventQueue.length > this.maxQueueSize) {
      this.eventQueue = this.eventQueue.slice(-this.maxQueueSize);
    }
  }
  
  /**
   * 获取通用属性
   */
  getCommonProperties() {
    return {
      deviceInfo: this.deviceInfo,
      appInfo: this.appInfo,
      networkType: this.getNetworkType(),
      batteryLevel: this.getBatteryLevel()
    };
  }
  
  /**
   * 获取当前页面
   */
  getCurrentPage() {
    const pages = getCurrentPages();
    if (pages.length > 0) {
      const currentPage = pages[pages.length - 1];
      return {
        route: currentPage.route,
        options: currentPage.options
      };
    }
    return null;
  }
  
  /**
   * 获取网络类型
   */
  getNetworkType() {
    try {
      return wx.getNetworkType();
    } catch (error) {
      return 'unknown';
    }
  }
  
  /**
   * 获取电池电量
   */
  getBatteryLevel() {
    try {
      return wx.getBatteryInfoSync().level;
    } catch (error) {
      return null;
    }
  }
  
  /**
   * 页面访问追踪
   * @param {string} pageName - 页面名称
   * @param {object} options - 页面参数
   */
  trackPageView(pageName, options = {}) {
    this.track(EVENT_TYPE.PAGE_VIEW, {
      pageName,
      pageOptions: options,
      referrer: this.getReferrer()
    });
  }
  
  /**
   * 页面离开追踪
   * @param {string} pageName - 页面名称
   * @param {number} duration - 停留时长
   */
  trackPageLeave(pageName, duration) {
    this.track(EVENT_TYPE.PAGE_LEAVE, {
      pageName,
      duration
    });
  }
  
  /**
   * 按钮点击追踪
   * @param {string} buttonName - 按钮名称
   * @param {object} context - 上下文信息
   */
  trackButtonClick(buttonName, context = {}) {
    this.track(EVENT_TYPE.BUTTON_CLICK, {
      buttonName,
      ...context
    });
  }
  
  /**
   * 搜索追踪
   * @param {string} keyword - 搜索关键词
   * @param {string} category - 搜索分类
   * @param {number} resultCount - 结果数量
   */
  trackSearch(keyword, category, resultCount) {
    this.track(EVENT_TYPE.SEARCH, {
      keyword,
      category,
      resultCount
    });
  }
  
  /**
   * 扫码追踪
   * @param {string} scanType - 扫码类型
   * @param {boolean} success - 是否成功
   * @param {object} result - 扫码结果
   */
  trackScan(scanType, success, result = {}) {
    this.track(EVENT_TYPE.SCAN, {
      scanType,
      success,
      result
    });
  }
  
  /**
   * 营养分析追踪
   * @param {string} foodType - 食物类型
   * @param {string} analysisMethod - 分析方法
   * @param {boolean} success - 是否成功
   */
  trackNutritionAnalysis(foodType, analysisMethod, success) {
    this.track(EVENT_TYPE.NUTRITION_ANALYSIS, {
      foodType,
      analysisMethod,
      success
    });
  }
  
  /**
   * 错误追踪
   * @param {Error} error - 错误对象
   * @param {string} context - 错误上下文
   */
  trackError(error, context = '') {
    this.track(EVENT_TYPE.ERROR, {
      errorMessage: error.message,
      errorStack: error.stack,
      errorName: error.name,
      context
    }, { immediate: true });
  }
  
  /**
   * API错误追踪
   * @param {string} api - API名称
   * @param {number} statusCode - 状态码
   * @param {string} errorMessage - 错误信息
   */
  trackApiError(api, statusCode, errorMessage) {
    this.track(EVENT_TYPE.API_ERROR, {
      api,
      statusCode,
      errorMessage
    }, { immediate: true });
  }
  
  /**
   * 性能追踪
   * @param {string} metric - 性能指标名称
   * @param {number} value - 指标值
   * @param {object} context - 上下文
   */
  trackPerformance(metric, value, context = {}) {
    this.track(EVENT_TYPE.PERFORMANCE, {
      metric,
      value,
      ...context
    });
  }
  
  /**
   * 加载时间追踪
   * @param {string} resource - 资源名称
   * @param {number} loadTime - 加载时间
   */
  trackLoadTime(resource, loadTime) {
    this.track(EVENT_TYPE.LOAD_TIME, {
      resource,
      loadTime
    });
  }
  
  /**
   * 用户行为追踪
   * @param {string} action - 行为动作
   * @param {object} properties - 属性
   */
  trackUserAction(action, properties = {}) {
    this.track(action, properties);
  }
  
  /**
   * 获取引用页面
   */
  getReferrer() {
    const pages = getCurrentPages();
    if (pages.length > 1) {
      const referrerPage = pages[pages.length - 2];
      return {
        route: referrerPage.route,
        options: referrerPage.options
      };
    }
    return null;
  }
  
  /**
   * 立即上报数据
   */
  async flush() {
    if (this.eventQueue.length === 0) return;
    
    const events = [...this.eventQueue];
    this.eventQueue = [];
    
    try {
      await this.sendEvents(events);
    } catch (error) {
      console.error('上报数据失败:', error);
      // 失败的事件重新加入队列
      this.eventQueue.unshift(...events.slice(0, this.batchSize));
    }
  }
  
  /**
   * 发送事件数据
   * @param {Array} events - 事件数组
   */
  async sendEvents(events) {
    // 这里应该调用实际的数据上报API
    // 目前使用模拟实现
    return new Promise((resolve, reject) => {
      // 模拟网络请求
      setTimeout(() => {
        if (Math.random() > 0.1) { // 90%成功率
          console.log('Analytics数据上报成功:', events.length, '条事件');
          resolve();
        } else {
          reject(new Error('网络错误'));
        }
      }, 100);
    });
  }
  
  /**
   * 启动批量上报
   */
  startBatchReporting() {
    setInterval(() => {
      if (this.eventQueue.length > 0) {
        this.flush();
      }
    }, this.flushInterval);
  }
  
  /**
   * 设置应用生命周期监听
   */
  setupLifecycleListeners() {
    // 监听应用隐藏
    wx.onAppHide(() => {
      this.flush(); // 应用隐藏时立即上报
    });
    
    // 监听应用显示
    wx.onAppShow(() => {
      this.sessionId = this.generateSessionId(); // 重新生成会话ID
    });
  }
  
  /**
   * 获取统计摘要
   */
  getSummary() {
    return {
      sessionId: this.sessionId,
      userId: this.userId,
      queueLength: this.eventQueue.length,
      isEnabled: this.isEnabled,
      deviceInfo: this.deviceInfo,
      appInfo: this.appInfo
    };
  }
}

/**
 * 性能监控器
 */
class PerformanceMonitor {
  constructor(analytics) {
    this.analytics = analytics;
    this.timers = new Map();
    this.observers = new Map();
  }
  
  /**
   * 开始计时
   * @param {string} name - 计时器名称
   */
  startTimer(name) {
    this.timers.set(name, Date.now());
  }
  
  /**
   * 结束计时并上报
   * @param {string} name - 计时器名称
   * @param {object} context - 上下文信息
   */
  endTimer(name, context = {}) {
    const startTime = this.timers.get(name);
    if (startTime) {
      const duration = Date.now() - startTime;
      this.analytics.trackPerformance(name, duration, context);
      this.timers.delete(name);
      return duration;
    }
    return null;
  }
  
  /**
   * 监控页面性能
   * @param {string} pageName - 页面名称
   */
  monitorPagePerformance(pageName) {
    const startTime = Date.now();
    
    // 监控页面加载完成
    wx.nextTick(() => {
      const loadTime = Date.now() - startTime;
      this.analytics.trackLoadTime(`page_${pageName}`, loadTime);
    });
  }
  
  /**
   * 监控API性能
   * @param {string} apiName - API名称
   * @param {Function} apiCall - API调用函数
   */
  async monitorApiPerformance(apiName, apiCall) {
    const startTime = Date.now();
    
    try {
      const result = await apiCall();
      const duration = Date.now() - startTime;
      this.analytics.trackPerformance(`api_${apiName}`, duration, {
        success: true
      });
      return result;
    } catch (error) {
      const duration = Date.now() - startTime;
      this.analytics.trackPerformance(`api_${apiName}`, duration, {
        success: false,
        error: error.message
      });
      throw error;
    }
  }
}

/**
 * 错误监控器
 */
class ErrorMonitor {
  constructor(analytics) {
    this.analytics = analytics;
    this.setupGlobalErrorHandler();
  }
  
  /**
   * 设置全局错误处理
   */
  setupGlobalErrorHandler() {
    // 监听未捕获的Promise错误
    wx.onUnhandledRejection && wx.onUnhandledRejection((res) => {
      this.analytics.trackError(new Error(res.reason), 'unhandled_promise_rejection');
    });
    
    // 监听小程序错误
    wx.onError && wx.onError((error) => {
      this.analytics.trackError(new Error(error), 'miniprogram_error');
    });
  }
  
  /**
   * 手动报告错误
   * @param {Error} error - 错误对象
   * @param {string} context - 错误上下文
   */
  reportError(error, context) {
    this.analytics.trackError(error, context);
  }
}

// 创建全局实例
const analytics = new AnalyticsManager();
const performanceMonitor = new PerformanceMonitor(analytics);
const errorMonitor = new ErrorMonitor(analytics);

/**
 * 页面统计混入
 */
export const analyticsMixin = {
  data() {
    return {
      pageStartTime: null
    };
  },
  
  onLoad(options) {
    this.pageStartTime = Date.now();
    analytics.trackPageView(this.route || this.__route__, options);
    performanceMonitor.monitorPagePerformance(this.route || this.__route__);
  },
  
  onUnload() {
    if (this.pageStartTime) {
      const duration = Date.now() - this.pageStartTime;
      analytics.trackPageLeave(this.route || this.__route__, duration);
    }
  },
  
  onShareAppMessage() {
    analytics.track(EVENT_TYPE.PAGE_SHARE, {
      pageName: this.route || this.__route__
    });
  },
  
  methods: {
    /**
     * 追踪按钮点击
     */
    trackClick(buttonName, context) {
      analytics.trackButtonClick(buttonName, context);
    },
    
    /**
     * 追踪用户行为
     */
    trackAction(action, properties) {
      analytics.trackUserAction(action, properties);
    }
  }
};

/**
 * 工具函数
 */

// 追踪事件
export function track(eventType, properties, options) {
  return analytics.track(eventType, properties, options);
}

// 追踪页面访问
export function trackPageView(pageName, options) {
  return analytics.trackPageView(pageName, options);
}

// 追踪按钮点击
export function trackButtonClick(buttonName, context) {
  return analytics.trackButtonClick(buttonName, context);
}

// 追踪搜索
export function trackSearch(keyword, category, resultCount) {
  return analytics.trackSearch(keyword, category, resultCount);
}

// 追踪扫码
export function trackScan(scanType, success, result) {
  return analytics.trackScan(scanType, success, result);
}

// 追踪营养分析
export function trackNutritionAnalysis(foodType, analysisMethod, success) {
  return analytics.trackNutritionAnalysis(foodType, analysisMethod, success);
}

// 追踪错误
export function trackError(error, context) {
  return analytics.trackError(error, context);
}

// 追踪API错误
export function trackApiError(api, statusCode, errorMessage) {
  return analytics.trackApiError(api, statusCode, errorMessage);
}

// 追踪性能
export function trackPerformance(metric, value, context) {
  return analytics.trackPerformance(metric, value, context);
}

// 设置用户ID
export function setUserId(userId) {
  return analytics.setUserId(userId);
}

// 启用/禁用统计
export function setEnabled(enabled) {
  return analytics.setEnabled(enabled);
}

// 立即上报
export function flush() {
  return analytics.flush();
}

// 开始计时
export function startTimer(name) {
  return performanceMonitor.startTimer(name);
}

// 结束计时
export function endTimer(name, context) {
  return performanceMonitor.endTimer(name, context);
}

// 监控API性能
export function monitorApiPerformance(apiName, apiCall) {
  return performanceMonitor.monitorApiPerformance(apiName, apiCall);
}

// 报告错误
export function reportError(error, context) {
  return errorMonitor.reportError(error, context);
}

// 获取统计摘要
export function getSummary() {
  return analytics.getSummary();
}

// 导出类和常量
export {
  AnalyticsManager,
  PerformanceMonitor,
  ErrorMonitor,
  EVENT_TYPE
};

export default {
  analytics,
  performanceMonitor,
  errorMonitor
};