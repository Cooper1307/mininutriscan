/**
 * 事件总线
 * 用于组件间通信和全局事件管理
 */

import { EVENTS } from './constants.js';

/**
 * 事件总线类
 */
class EventBus {
  constructor() {
    // 事件监听器映射
    this.listeners = new Map();
    
    // 一次性监听器映射
    this.onceListeners = new Map();
    
    // 事件历史记录
    this.history = [];
    
    // 最大历史记录数
    this.maxHistory = 100;
    
    // 调试模式
    this.debug = false;
    
    // 命名空间
    this.namespaces = new Map();
  }
  
  /**
   * 添加事件监听器
   * @param {string} event 事件名称
   * @param {Function} listener 监听器函数
   * @param {Object} options 选项
   */
  on(event, listener, options = {}) {
    if (typeof event !== 'string' || typeof listener !== 'function') {
      throw new Error('事件名称必须是字符串，监听器必须是函数');
    }
    
    // 处理命名空间
    const { namespace, priority = 0, once = false } = options;
    const fullEvent = namespace ? `${namespace}:${event}` : event;
    
    if (once) {
      return this.once(fullEvent, listener, { priority });
    }
    
    if (!this.listeners.has(fullEvent)) {
      this.listeners.set(fullEvent, []);
    }
    
    const listenerObj = {
      listener,
      priority,
      id: this.generateId(),
      namespace,
      timestamp: Date.now()
    };
    
    const listeners = this.listeners.get(fullEvent);
    listeners.push(listenerObj);
    
    // 按优先级排序（优先级高的先执行）
    listeners.sort((a, b) => b.priority - a.priority);
    
    this.log(`添加监听器: ${fullEvent}`, listenerObj);
    
    // 返回取消监听的函数
    return () => this.off(fullEvent, listener);
  }
  
  /**
   * 添加一次性事件监听器
   * @param {string} event 事件名称
   * @param {Function} listener 监听器函数
   * @param {Object} options 选项
   */
  once(event, listener, options = {}) {
    if (typeof event !== 'string' || typeof listener !== 'function') {
      throw new Error('事件名称必须是字符串，监听器必须是函数');
    }
    
    const { namespace, priority = 0 } = options;
    const fullEvent = namespace ? `${namespace}:${event}` : event;
    
    if (!this.onceListeners.has(fullEvent)) {
      this.onceListeners.set(fullEvent, []);
    }
    
    const listenerObj = {
      listener,
      priority,
      id: this.generateId(),
      namespace,
      timestamp: Date.now()
    };
    
    const listeners = this.onceListeners.get(fullEvent);
    listeners.push(listenerObj);
    
    // 按优先级排序
    listeners.sort((a, b) => b.priority - a.priority);
    
    this.log(`添加一次性监听器: ${fullEvent}`, listenerObj);
    
    // 返回取消监听的函数
    return () => this.off(fullEvent, listener, true);
  }
  
  /**
   * 移除事件监听器
   * @param {string} event 事件名称
   * @param {Function} listener 监听器函数
   * @param {boolean} isOnce 是否为一次性监听器
   */
  off(event, listener, isOnce = false) {
    const listenersMap = isOnce ? this.onceListeners : this.listeners;
    
    if (!listenersMap.has(event)) {
      return false;
    }
    
    const listeners = listenersMap.get(event);
    const index = listeners.findIndex(item => item.listener === listener);
    
    if (index !== -1) {
      const removed = listeners.splice(index, 1)[0];
      this.log(`移除监听器: ${event}`, removed);
      
      // 如果没有监听器了，删除事件
      if (listeners.length === 0) {
        listenersMap.delete(event);
      }
      
      return true;
    }
    
    return false;
  }
  
  /**
   * 移除所有事件监听器
   * @param {string} event 事件名称（可选）
   */
  offAll(event) {
    if (event) {
      // 移除特定事件的所有监听器
      this.listeners.delete(event);
      this.onceListeners.delete(event);
      this.log(`移除所有监听器: ${event}`);
    } else {
      // 移除所有监听器
      this.listeners.clear();
      this.onceListeners.clear();
      this.log('移除所有监听器');
    }
  }
  
  /**
   * 触发事件
   * @param {string} event 事件名称
   * @param {*} data 事件数据
   * @param {Object} options 选项
   */
  emit(event, data, options = {}) {
    const { async = false, timeout = 5000 } = options;
    
    // 记录事件历史
    this.addToHistory(event, data);
    
    this.log(`触发事件: ${event}`, data);
    
    if (async) {
      return this.emitAsync(event, data, timeout);
    } else {
      return this.emitSync(event, data);
    }
  }
  
  /**
   * 同步触发事件
   */
  emitSync(event, data) {
    const results = [];
    
    // 执行普通监听器
    const listeners = this.listeners.get(event) || [];
    for (const listenerObj of listeners) {
      try {
        const result = listenerObj.listener(data, event);
        results.push({ success: true, result, listener: listenerObj });
      } catch (error) {
        results.push({ success: false, error, listener: listenerObj });
        this.log(`监听器执行失败: ${event}`, error);
      }
    }
    
    // 执行一次性监听器
    const onceListeners = this.onceListeners.get(event) || [];
    for (const listenerObj of onceListeners) {
      try {
        const result = listenerObj.listener(data, event);
        results.push({ success: true, result, listener: listenerObj });
      } catch (error) {
        results.push({ success: false, error, listener: listenerObj });
        this.log(`一次性监听器执行失败: ${event}`, error);
      }
    }
    
    // 清除一次性监听器
    if (onceListeners.length > 0) {
      this.onceListeners.delete(event);
    }
    
    return results;
  }
  
  /**
   * 异步触发事件
   */
  async emitAsync(event, data, timeout) {
    const results = [];
    
    // 执行普通监听器
    const listeners = this.listeners.get(event) || [];
    const listenerPromises = listeners.map(async (listenerObj) => {
      try {
        const result = await Promise.race([
          Promise.resolve(listenerObj.listener(data, event)),
          new Promise((_, reject) => 
            setTimeout(() => reject(new Error('监听器执行超时')), timeout)
          )
        ]);
        return { success: true, result, listener: listenerObj };
      } catch (error) {
        this.log(`异步监听器执行失败: ${event}`, error);
        return { success: false, error, listener: listenerObj };
      }
    });
    
    // 执行一次性监听器
    const onceListeners = this.onceListeners.get(event) || [];
    const oncePromises = onceListeners.map(async (listenerObj) => {
      try {
        const result = await Promise.race([
          Promise.resolve(listenerObj.listener(data, event)),
          new Promise((_, reject) => 
            setTimeout(() => reject(new Error('一次性监听器执行超时')), timeout)
          )
        ]);
        return { success: true, result, listener: listenerObj };
      } catch (error) {
        this.log(`异步一次性监听器执行失败: ${event}`, error);
        return { success: false, error, listener: listenerObj };
      }
    });
    
    // 等待所有监听器执行完成
    const allResults = await Promise.allSettled([...listenerPromises, ...oncePromises]);
    
    allResults.forEach(result => {
      if (result.status === 'fulfilled') {
        results.push(result.value);
      } else {
        results.push({ success: false, error: result.reason });
      }
    });
    
    // 清除一次性监听器
    if (onceListeners.length > 0) {
      this.onceListeners.delete(event);
    }
    
    return results;
  }
  
  /**
   * 检查是否有监听器
   * @param {string} event 事件名称
   */
  hasListeners(event) {
    return (this.listeners.has(event) && this.listeners.get(event).length > 0) ||
           (this.onceListeners.has(event) && this.onceListeners.get(event).length > 0);
  }
  
  /**
   * 获取监听器数量
   * @param {string} event 事件名称
   */
  getListenerCount(event) {
    const normalCount = this.listeners.has(event) ? this.listeners.get(event).length : 0;
    const onceCount = this.onceListeners.has(event) ? this.onceListeners.get(event).length : 0;
    return normalCount + onceCount;
  }
  
  /**
   * 获取所有事件名称
   */
  getEventNames() {
    const normalEvents = Array.from(this.listeners.keys());
    const onceEvents = Array.from(this.onceListeners.keys());
    return [...new Set([...normalEvents, ...onceEvents])];
  }
  
  /**
   * 创建命名空间
   * @param {string} namespace 命名空间名称
   */
  namespace(namespace) {
    if (!this.namespaces.has(namespace)) {
      const namespacedBus = {
        on: (event, listener, options = {}) => {
          return this.on(event, listener, { ...options, namespace });
        },
        once: (event, listener, options = {}) => {
          return this.once(event, listener, { ...options, namespace });
        },
        off: (event, listener) => {
          return this.off(`${namespace}:${event}`, listener);
        },
        emit: (event, data, options = {}) => {
          return this.emit(`${namespace}:${event}`, data, options);
        },
        offAll: (event) => {
          if (event) {
            this.offAll(`${namespace}:${event}`);
          } else {
            // 移除该命名空间下的所有事件
            const events = this.getEventNames();
            events.forEach(eventName => {
              if (eventName.startsWith(`${namespace}:`)) {
                this.offAll(eventName);
              }
            });
          }
        }
      };
      
      this.namespaces.set(namespace, namespacedBus);
    }
    
    return this.namespaces.get(namespace);
  }
  
  /**
   * 添加到历史记录
   */
  addToHistory(event, data) {
    this.history.push({
      event,
      data,
      timestamp: Date.now()
    });
    
    // 限制历史记录数量
    if (this.history.length > this.maxHistory) {
      this.history.shift();
    }
  }
  
  /**
   * 获取事件历史
   * @param {string} event 事件名称（可选）
   * @param {number} limit 限制数量
   */
  getHistory(event, limit = 10) {
    let history = this.history;
    
    if (event) {
      history = history.filter(item => item.event === event);
    }
    
    return history.slice(-limit);
  }
  
  /**
   * 清除历史记录
   */
  clearHistory() {
    this.history = [];
  }
  
  /**
   * 生成唯一ID
   */
  generateId() {
    return `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  
  /**
   * 日志输出
   */
  log(message, data) {
    if (this.debug) {
      console.log(`[EventBus] ${message}`, data);
    }
  }
  
  /**
   * 启用调试模式
   */
  enableDebug() {
    this.debug = true;
  }
  
  /**
   * 禁用调试模式
   */
  disableDebug() {
    this.debug = false;
  }
  
  /**
   * 获取统计信息
   */
  getStats() {
    const events = this.getEventNames();
    const stats = {
      totalEvents: events.length,
      totalListeners: 0,
      totalOnceListeners: 0,
      events: {}
    };
    
    events.forEach(event => {
      const normalCount = this.listeners.has(event) ? this.listeners.get(event).length : 0;
      const onceCount = this.onceListeners.has(event) ? this.onceListeners.get(event).length : 0;
      
      stats.totalListeners += normalCount;
      stats.totalOnceListeners += onceCount;
      stats.events[event] = {
        listeners: normalCount,
        onceListeners: onceCount,
        total: normalCount + onceCount
      };
    });
    
    return stats;
  }
  
  /**
   * 销毁事件总线
   */
  destroy() {
    this.offAll();
    this.namespaces.clear();
    this.clearHistory();
    this.log('事件总线已销毁');
  }
}

// 创建全局事件总线实例
const eventBus = new EventBus();

/**
 * 事件总线混入
 */
export const eventBusMixin = {
  onLoad() {
    // 存储页面的监听器，用于页面卸载时清理
    this._eventListeners = [];
  },
  
  onUnload() {
    // 清理页面的所有监听器
    if (this._eventListeners) {
      this._eventListeners.forEach(unsubscribe => {
        if (typeof unsubscribe === 'function') {
          unsubscribe();
        }
      });
      this._eventListeners = [];
    }
  },
  
  methods: {
    /**
     * 添加事件监听器（页面卸载时自动清理）
     */
    $on(event, listener, options) {
      const unsubscribe = eventBus.on(event, listener, options);
      if (this._eventListeners) {
        this._eventListeners.push(unsubscribe);
      }
      return unsubscribe;
    },
    
    /**
     * 添加一次性事件监听器
     */
    $once(event, listener, options) {
      const unsubscribe = eventBus.once(event, listener, options);
      if (this._eventListeners) {
        this._eventListeners.push(unsubscribe);
      }
      return unsubscribe;
    },
    
    /**
     * 移除事件监听器
     */
    $off(event, listener) {
      return eventBus.off(event, listener);
    },
    
    /**
     * 触发事件
     */
    $emit(event, data, options) {
      return eventBus.emit(event, data, options);
    },
    
    /**
     * 创建命名空间
     */
    $namespace(namespace) {
      return eventBus.namespace(namespace);
    }
  }
};

/**
 * 导出事件总线和相关函数
 */
export default eventBus;

/**
 * 快捷访问函数
 */
export const on = (event, listener, options) => eventBus.on(event, listener, options);
export const once = (event, listener, options) => eventBus.once(event, listener, options);
export const off = (event, listener) => eventBus.off(event, listener);
export const emit = (event, data, options) => eventBus.emit(event, data, options);
export const offAll = (event) => eventBus.offAll(event);
export const hasListeners = (event) => eventBus.hasListeners(event);
export const namespace = (ns) => eventBus.namespace(ns);

/**
 * 预定义的事件常量
 */
export { EVENTS };

/**
 * 常用事件的快捷函数
 */
export const emitUserLogin = (userInfo) => emit(EVENTS.USER_LOGIN, userInfo);
export const emitUserLogout = () => emit(EVENTS.USER_LOGOUT);
export const emitScanSuccess = (result) => emit(EVENTS.SCAN_SUCCESS, result);
export const emitScanFailed = (error) => emit(EVENTS.SCAN_FAILED, error);
export const emitNetworkChange = (status) => emit(EVENTS.NETWORK_CHANGE, status);
export const emitThemeChange = (theme) => emit(EVENTS.THEME_CHANGE, theme);

/**
 * 监听常用事件的快捷函数
 */
export const onUserLogin = (listener, options) => on(EVENTS.USER_LOGIN, listener, options);
export const onUserLogout = (listener, options) => on(EVENTS.USER_LOGOUT, listener, options);
export const onScanSuccess = (listener, options) => on(EVENTS.SCAN_SUCCESS, listener, options);
export const onScanFailed = (listener, options) => on(EVENTS.SCAN_FAILED, listener, options);
export const onNetworkChange = (listener, options) => on(EVENTS.NETWORK_CHANGE, listener, options);
export const onThemeChange = (listener, options) => on(EVENTS.THEME_CHANGE, listener, options);