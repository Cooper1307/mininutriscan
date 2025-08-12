/**
 * 网络状态管理工具
 * 提供网络状态监控、离线处理、请求队列等功能
 */

/**
 * 网络状态枚举
 */
const NETWORK_TYPE = {
  WIFI: 'wifi',
  '2G': '2g',
  '3G': '3g',
  '4G': '4g',
  '5G': '5g',
  UNKNOWN: 'unknown',
  NONE: 'none'
};

/**
 * 网络状态管理器
 */
class NetworkManager {
  constructor() {
    this.isOnline = true;
    this.networkType = NETWORK_TYPE.UNKNOWN;
    this.listeners = [];
    this.requestQueue = [];
    this.retryQueue = [];
    this.maxRetries = 3;
    this.retryDelay = 1000;
    
    this.init();
  }
  
  /**
   * 初始化网络监控
   */
  init() {
    // 获取初始网络状态
    this.checkNetworkStatus();
    
    // 监听网络状态变化
    wx.onNetworkStatusChange((res) => {
      this.handleNetworkChange(res);
    });
  }
  
  /**
   * 检查当前网络状态
   */
  async checkNetworkStatus() {
    try {
      const res = await this.getNetworkType();
      this.updateNetworkStatus(res.networkType, res.networkType !== NETWORK_TYPE.NONE);
    } catch (error) {
      console.error('检查网络状态失败:', error);
      this.updateNetworkStatus(NETWORK_TYPE.UNKNOWN, false);
    }
  }
  
  /**
   * 获取网络类型
   */
  getNetworkType() {
    return new Promise((resolve, reject) => {
      wx.getNetworkType({
        success: resolve,
        fail: reject
      });
    });
  }
  
  /**
   * 处理网络状态变化
   */
  handleNetworkChange(res) {
    const { isConnected, networkType } = res;
    const wasOnline = this.isOnline;
    
    this.updateNetworkStatus(networkType, isConnected);
    
    // 网络从离线变为在线时，处理队列中的请求
    if (!wasOnline && isConnected) {
      this.processQueuedRequests();
      this.processRetryQueue();
    }
    
    // 通知监听器
    this.notifyListeners({
      isOnline: isConnected,
      networkType,
      wasOnline,
      isConnected
    });
  }
  
  /**
   * 更新网络状态
   */
  updateNetworkStatus(networkType, isOnline) {
    this.networkType = networkType;
    this.isOnline = isOnline;
    
    console.log(`网络状态更新: ${networkType}, 在线: ${isOnline}`);
  }
  
  /**
   * 添加网络状态监听器
   */
  addListener(callback) {
    if (typeof callback === 'function') {
      this.listeners.push(callback);
    }
  }
  
  /**
   * 移除网络状态监听器
   */
  removeListener(callback) {
    const index = this.listeners.indexOf(callback);
    if (index > -1) {
      this.listeners.splice(index, 1);
    }
  }
  
  /**
   * 通知所有监听器
   */
  notifyListeners(data) {
    this.listeners.forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error('网络状态监听器执行错误:', error);
      }
    });
  }
  
  /**
   * 检查是否为良好的网络连接
   */
  isGoodConnection() {
    return this.isOnline && [NETWORK_TYPE.WIFI, NETWORK_TYPE['4G'], NETWORK_TYPE['5G']].includes(this.networkType);
  }
  
  /**
   * 检查是否为慢速网络
   */
  isSlowConnection() {
    return this.isOnline && [NETWORK_TYPE['2G'], NETWORK_TYPE['3G']].includes(this.networkType);
  }
  
  /**
   * 添加请求到队列（离线时使用）
   */
  queueRequest(requestConfig) {
    const queueItem = {
      id: Date.now() + Math.random(),
      config: requestConfig,
      timestamp: Date.now(),
      retries: 0
    };
    
    this.requestQueue.push(queueItem);
    console.log('请求已加入队列:', queueItem.id);
    
    return queueItem.id;
  }
  
  /**
   * 处理队列中的请求
   */
  async processQueuedRequests() {
    if (!this.isOnline || this.requestQueue.length === 0) {
      return;
    }
    
    console.log(`开始处理队列中的 ${this.requestQueue.length} 个请求`);
    
    const queue = [...this.requestQueue];
    this.requestQueue = [];
    
    for (const item of queue) {
      try {
        await this.executeQueuedRequest(item);
      } catch (error) {
        console.error('执行队列请求失败:', error);
        // 失败的请求加入重试队列
        this.addToRetryQueue(item);
      }
    }
  }
  
  /**
   * 执行队列中的请求
   */
  async executeQueuedRequest(item) {
    const { config } = item;
    
    return new Promise((resolve, reject) => {
      wx.request({
        ...config,
        success: (res) => {
          console.log('队列请求执行成功:', item.id);
          if (config.success) {
            config.success(res);
          }
          resolve(res);
        },
        fail: (error) => {
          console.error('队列请求执行失败:', item.id, error);
          if (config.fail) {
            config.fail(error);
          }
          reject(error);
        }
      });
    });
  }
  
  /**
   * 添加到重试队列
   */
  addToRetryQueue(item) {
    if (item.retries < this.maxRetries) {
      item.retries++;
      item.nextRetry = Date.now() + (this.retryDelay * Math.pow(2, item.retries - 1));
      this.retryQueue.push(item);
      console.log(`请求加入重试队列: ${item.id}, 重试次数: ${item.retries}`);
    } else {
      console.log(`请求重试次数已达上限: ${item.id}`);
    }
  }
  
  /**
   * 处理重试队列
   */
  async processRetryQueue() {
    if (!this.isOnline || this.retryQueue.length === 0) {
      return;
    }
    
    const now = Date.now();
    const readyToRetry = this.retryQueue.filter(item => item.nextRetry <= now);
    
    if (readyToRetry.length === 0) {
      return;
    }
    
    console.log(`开始重试 ${readyToRetry.length} 个请求`);
    
    // 从重试队列中移除准备重试的请求
    this.retryQueue = this.retryQueue.filter(item => item.nextRetry > now);
    
    for (const item of readyToRetry) {
      try {
        await this.executeQueuedRequest(item);
      } catch (error) {
        console.error('重试请求失败:', error);
        this.addToRetryQueue(item);
      }
    }
  }
  
  /**
   * 清空请求队列
   */
  clearQueue() {
    this.requestQueue = [];
    this.retryQueue = [];
    console.log('请求队列已清空');
  }
  
  /**
   * 获取队列状态
   */
  getQueueStatus() {
    return {
      pending: this.requestQueue.length,
      retrying: this.retryQueue.length,
      total: this.requestQueue.length + this.retryQueue.length
    };
  }
  
  /**
   * 网络请求包装器
   * 自动处理离线状态和重试逻辑
   */
  request(config) {
    return new Promise((resolve, reject) => {
      // 如果离线，直接加入队列
      if (!this.isOnline) {
        const queueId = this.queueRequest({
          ...config,
          success: resolve,
          fail: reject
        });
        
        // 返回一个特殊的Promise，表示请求已排队
        reject({
          type: 'NETWORK_OFFLINE',
          message: '网络连接不可用，请求已加入队列',
          queueId
        });
        return;
      }
      
      // 在线时直接发送请求
      wx.request({
        ...config,
        success: resolve,
        fail: (error) => {
          // 网络错误时加入重试队列
          if (this.isNetworkError(error)) {
            const queueId = this.queueRequest({
              ...config,
              success: resolve,
              fail: reject
            });
            
            reject({
              type: 'NETWORK_ERROR',
              message: '网络请求失败，已加入重试队列',
              queueId,
              originalError: error
            });
          } else {
            reject(error);
          }
        }
      });
    });
  }
  
  /**
   * 判断是否为网络错误
   */
  isNetworkError(error) {
    const networkErrorCodes = [
      'request:fail timeout',
      'request:fail',
      'request:fail net::ERR_NETWORK_CHANGED',
      'request:fail net::ERR_INTERNET_DISCONNECTED'
    ];
    
    return networkErrorCodes.some(code => 
      error.errMsg && error.errMsg.includes(code)
    );
  }
  
  /**
   * 显示网络状态提示
   */
  showNetworkStatus() {
    let title = '';
    let icon = 'none';
    
    if (!this.isOnline) {
      title = '网络连接不可用';
      icon = 'none';
    } else if (this.isSlowConnection()) {
      title = `当前网络较慢 (${this.networkType.toUpperCase()})`;
      icon = 'none';
    } else if (this.isGoodConnection()) {
      title = `网络连接良好 (${this.networkType.toUpperCase()})`;
      icon = 'success';
    } else {
      title = `网络类型: ${this.networkType.toUpperCase()}`;
      icon = 'none';
    }
    
    wx.showToast({
      title,
      icon,
      duration: 2000
    });
  }
  
  /**
   * 获取网络状态信息
   */
  getStatus() {
    return {
      isOnline: this.isOnline,
      networkType: this.networkType,
      isGoodConnection: this.isGoodConnection(),
      isSlowConnection: this.isSlowConnection(),
      queueStatus: this.getQueueStatus()
    };
  }
}

// 创建全局网络管理器实例
const networkManager = new NetworkManager();

/**
 * 网络状态混入
 * 可以在页面中使用，提供网络状态相关功能
 */
export const networkMixin = {
  data: {
    networkStatus: {
      isOnline: true,
      networkType: 'unknown',
      isGoodConnection: false,
      isSlowConnection: false
    }
  },
  
  onLoad() {
    // 添加网络状态监听
    this.networkListener = (status) => {
      this.setData({
        networkStatus: {
          isOnline: status.isOnline,
          networkType: status.networkType,
          isGoodConnection: networkManager.isGoodConnection(),
          isSlowConnection: networkManager.isSlowConnection()
        }
      });
      
      // 网络状态变化时的处理
      this.onNetworkStatusChange && this.onNetworkStatusChange(status);
    };
    
    networkManager.addListener(this.networkListener);
    
    // 初始化网络状态
    this.setData({
      networkStatus: {
        isOnline: networkManager.isOnline,
        networkType: networkManager.networkType,
        isGoodConnection: networkManager.isGoodConnection(),
        isSlowConnection: networkManager.isSlowConnection()
      }
    });
  },
  
  onUnload() {
    // 移除网络状态监听
    if (this.networkListener) {
      networkManager.removeListener(this.networkListener);
    }
  },
  
  methods: {
    /**
     * 检查网络状态
     */
    checkNetwork() {
      return networkManager.checkNetworkStatus();
    },
    
    /**
     * 显示网络状态
     */
    showNetworkStatus() {
      networkManager.showNetworkStatus();
    },
    
    /**
     * 网络请求（带离线处理）
     */
    networkRequest(config) {
      return networkManager.request(config);
    }
  }
};

/**
 * 工具函数
 */

// 检查网络连接
export function checkNetworkConnection() {
  return networkManager.checkNetworkStatus();
}

// 获取网络状态
export function getNetworkStatus() {
  return networkManager.getStatus();
}

// 添加网络状态监听器
export function addNetworkListener(callback) {
  networkManager.addListener(callback);
}

// 移除网络状态监听器
export function removeNetworkListener(callback) {
  networkManager.removeListener(callback);
}

// 网络请求（带离线处理）
export function networkRequest(config) {
  return networkManager.request(config);
}

// 显示网络状态提示
export function showNetworkStatus() {
  networkManager.showNetworkStatus();
}

// 清空请求队列
export function clearRequestQueue() {
  networkManager.clearQueue();
}

// 获取队列状态
export function getQueueStatus() {
  return networkManager.getQueueStatus();
}

// 导出网络管理器和相关常量
export { NetworkManager, NETWORK_TYPE };
export default networkManager;