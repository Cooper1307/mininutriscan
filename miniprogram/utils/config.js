/**
 * 应用配置管理
 * 统一管理应用的各种配置项
 */

import { STORAGE_KEYS, THEME, LANGUAGES, DEFAULTS } from './constants.js';

/**
 * 环境配置
 */
const ENV_CONFIG = {
  // 开发环境
  development: {
    API_BASE_URL: 'https://dev-api.nutriscan.com',
    DEBUG: true,
    LOG_LEVEL: 'debug',
    MOCK_DATA: true,
    ANALYTICS_ENABLED: false
  },
  
  // 测试环境
  testing: {
    API_BASE_URL: 'https://test-api.nutriscan.com',
    DEBUG: true,
    LOG_LEVEL: 'info',
    MOCK_DATA: false,
    ANALYTICS_ENABLED: false
  },
  
  // 生产环境
  production: {
    API_BASE_URL: 'https://api.nutriscan.com',
    DEBUG: false,
    LOG_LEVEL: 'error',
    MOCK_DATA: false,
    ANALYTICS_ENABLED: true
  }
};

/**
 * 默认配置
 */
const DEFAULT_CONFIG = {
  // 主题设置
  theme: THEME.AUTO,
  
  // 语言设置
  language: LANGUAGES.ZH_CN,
  
  // 扫码设置
  scan: {
    autoFocus: true,
    flashEnabled: false,
    soundEnabled: true,
    vibrateEnabled: true,
    scanInterval: 1000
  },
  
  // 营养分析设置
  nutrition: {
    showDetailedInfo: true,
    showDailyValue: true,
    preferredUnit: 'metric', // metric | imperial
    allergenWarnings: true
  },
  
  // 搜索设置
  search: {
    saveHistory: true,
    maxHistoryItems: 20,
    autoComplete: true,
    searchDelay: DEFAULTS.SEARCH_DELAY
  },
  
  // 缓存设置
  cache: {
    enabled: true,
    maxSize: 50 * 1024 * 1024, // 50MB
    expireTime: DEFAULTS.CACHE_EXPIRE,
    autoCleanup: true
  },
  
  // 网络设置
  network: {
    timeout: 10000,
    retryCount: 3,
    retryDelay: DEFAULTS.RETRY_DELAY,
    offlineMode: true
  },
  
  // 隐私设置
  privacy: {
    analyticsEnabled: true,
    crashReportEnabled: true,
    locationEnabled: false,
    dataCollection: true
  },
  
  // 通知设置
  notification: {
    enabled: true,
    soundEnabled: true,
    vibrateEnabled: true,
    showBadge: true
  },
  
  // 显示设置
  display: {
    fontSize: 'normal', // small | normal | large
    density: 'normal',  // compact | normal | comfortable
    animations: true,
    hapticFeedback: true
  },
  
  // 数据同步设置
  sync: {
    enabled: false,
    autoSync: false,
    syncInterval: 30 * 60 * 1000, // 30分钟
    wifiOnly: true
  }
};

/**
 * 配置管理器
 */
class ConfigManager {
  constructor() {
    this.config = { ...DEFAULT_CONFIG };
    this.env = this.getCurrentEnv();
    this.envConfig = ENV_CONFIG[this.env] || ENV_CONFIG.production;
    this.listeners = new Map();
    
    // 初始化配置
    this.init();
  }
  
  /**
   * 初始化配置
   */
  init() {
    try {
      // 从本地存储加载配置
      const savedConfig = wx.getStorageSync(STORAGE_KEYS.APP_SETTINGS);
      if (savedConfig) {
        this.config = this.mergeConfig(this.config, savedConfig);
      }
      
      // 合并环境配置
      this.config = { ...this.config, ...this.envConfig };
      
      console.log('[ConfigManager] 配置初始化完成:', this.config);
    } catch (error) {
      console.error('[ConfigManager] 配置初始化失败:', error);
    }
  }
  
  /**
   * 获取当前环境
   */
  getCurrentEnv() {
    // 可以通过编译时变量或其他方式确定环境
    // 这里简单通过域名判断
    const accountInfo = wx.getAccountInfoSync();
    const envVersion = accountInfo.miniProgram.envVersion;
    
    switch (envVersion) {
      case 'develop':
        return 'development';
      case 'trial':
        return 'testing';
      case 'release':
        return 'production';
      default:
        return 'production';
    }
  }
  
  /**
   * 深度合并配置
   */
  mergeConfig(target, source) {
    const result = { ...target };
    
    for (const key in source) {
      if (source.hasOwnProperty(key)) {
        if (typeof source[key] === 'object' && source[key] !== null && !Array.isArray(source[key])) {
          result[key] = this.mergeConfig(target[key] || {}, source[key]);
        } else {
          result[key] = source[key];
        }
      }
    }
    
    return result;
  }
  
  /**
   * 获取配置值
   */
  get(key, defaultValue = null) {
    const keys = key.split('.');
    let value = this.config;
    
    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        return defaultValue;
      }
    }
    
    return value;
  }
  
  /**
   * 设置配置值
   */
  set(key, value) {
    const keys = key.split('.');
    let target = this.config;
    
    // 导航到目标对象
    for (let i = 0; i < keys.length - 1; i++) {
      const k = keys[i];
      if (!target[k] || typeof target[k] !== 'object') {
        target[k] = {};
      }
      target = target[k];
    }
    
    // 设置值
    const lastKey = keys[keys.length - 1];
    const oldValue = target[lastKey];
    target[lastKey] = value;
    
    // 保存到本地存储
    this.save();
    
    // 触发监听器
    this.notifyListeners(key, value, oldValue);
    
    return this;
  }
  
  /**
   * 批量设置配置
   */
  setMultiple(configs) {
    for (const [key, value] of Object.entries(configs)) {
      this.set(key, value);
    }
    return this;
  }
  
  /**
   * 重置配置
   */
  reset(key = null) {
    if (key) {
      // 重置特定配置
      const defaultValue = this.getDefaultValue(key);
      this.set(key, defaultValue);
    } else {
      // 重置所有配置
      this.config = { ...DEFAULT_CONFIG, ...this.envConfig };
      this.save();
      this.notifyListeners('*', this.config, null);
    }
    return this;
  }
  
  /**
   * 获取默认值
   */
  getDefaultValue(key) {
    const keys = key.split('.');
    let value = DEFAULT_CONFIG;
    
    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        return null;
      }
    }
    
    return value;
  }
  
  /**
   * 保存配置到本地存储
   */
  save() {
    try {
      // 过滤掉环境配置，只保存用户配置
      const userConfig = this.filterUserConfig(this.config);
      wx.setStorageSync(STORAGE_KEYS.APP_SETTINGS, userConfig);
    } catch (error) {
      console.error('[ConfigManager] 保存配置失败:', error);
    }
  }
  
  /**
   * 过滤用户配置
   */
  filterUserConfig(config) {
    const userConfig = { ...config };
    
    // 移除环境相关配置
    delete userConfig.API_BASE_URL;
    delete userConfig.DEBUG;
    delete userConfig.LOG_LEVEL;
    delete userConfig.MOCK_DATA;
    delete userConfig.ANALYTICS_ENABLED;
    
    return userConfig;
  }
  
  /**
   * 监听配置变化
   */
  watch(key, callback) {
    if (!this.listeners.has(key)) {
      this.listeners.set(key, new Set());
    }
    this.listeners.get(key).add(callback);
    
    // 返回取消监听的函数
    return () => {
      const callbacks = this.listeners.get(key);
      if (callbacks) {
        callbacks.delete(callback);
        if (callbacks.size === 0) {
          this.listeners.delete(key);
        }
      }
    };
  }
  
  /**
   * 通知监听器
   */
  notifyListeners(key, newValue, oldValue) {
    // 通知特定键的监听器
    const callbacks = this.listeners.get(key);
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(newValue, oldValue, key);
        } catch (error) {
          console.error('[ConfigManager] 监听器执行失败:', error);
        }
      });
    }
    
    // 通知通配符监听器
    const wildcardCallbacks = this.listeners.get('*');
    if (wildcardCallbacks) {
      wildcardCallbacks.forEach(callback => {
        try {
          callback(newValue, oldValue, key);
        } catch (error) {
          console.error('[ConfigManager] 通配符监听器执行失败:', error);
        }
      });
    }
  }
  
  /**
   * 获取所有配置
   */
  getAll() {
    return { ...this.config };
  }
  
  /**
   * 获取环境配置
   */
  getEnvConfig() {
    return { ...this.envConfig };
  }
  
  /**
   * 检查是否为开发环境
   */
  isDevelopment() {
    return this.env === 'development';
  }
  
  /**
   * 检查是否为生产环境
   */
  isProduction() {
    return this.env === 'production';
  }
  
  /**
   * 检查是否启用调试
   */
  isDebugEnabled() {
    return this.get('DEBUG', false);
  }
  
  /**
   * 检查是否启用模拟数据
   */
  isMockEnabled() {
    return this.get('MOCK_DATA', false);
  }
  
  /**
   * 导出配置
   */
  export() {
    return {
      config: this.getAll(),
      env: this.env,
      timestamp: Date.now()
    };
  }
  
  /**
   * 导入配置
   */
  import(data) {
    try {
      if (data && data.config) {
        this.config = this.mergeConfig(DEFAULT_CONFIG, data.config);
        this.config = { ...this.config, ...this.envConfig };
        this.save();
        this.notifyListeners('*', this.config, null);
        return true;
      }
      return false;
    } catch (error) {
      console.error('[ConfigManager] 导入配置失败:', error);
      return false;
    }
  }
  
  /**
   * 验证配置
   */
  validate() {
    const errors = [];
    
    // 验证主题设置
    const theme = this.get('theme');
    if (!Object.values(THEME).includes(theme)) {
      errors.push(`无效的主题设置: ${theme}`);
    }
    
    // 验证语言设置
    const language = this.get('language');
    if (!Object.values(LANGUAGES).includes(language)) {
      errors.push(`无效的语言设置: ${language}`);
    }
    
    // 验证网络超时设置
    const timeout = this.get('network.timeout');
    if (typeof timeout !== 'number' || timeout < 1000 || timeout > 60000) {
      errors.push(`无效的网络超时设置: ${timeout}`);
    }
    
    return {
      valid: errors.length === 0,
      errors
    };
  }
}

// 创建全局配置管理器实例
const configManager = new ConfigManager();

/**
 * 配置相关的混入
 */
export const configMixin = {
  data() {
    return {
      config: configManager.getAll()
    };
  },
  
  onLoad() {
    // 监听配置变化
    this.unwatchConfig = configManager.watch('*', (newValue, oldValue, key) => {
      this.setData({
        config: configManager.getAll()
      });
    });
  },
  
  onUnload() {
    // 取消监听
    if (this.unwatchConfig) {
      this.unwatchConfig();
    }
  },
  
  methods: {
    /**
     * 获取配置值
     */
    getConfig(key, defaultValue) {
      return configManager.get(key, defaultValue);
    },
    
    /**
     * 设置配置值
     */
    setConfig(key, value) {
      return configManager.set(key, value);
    },
    
    /**
     * 重置配置
     */
    resetConfig(key) {
      return configManager.reset(key);
    }
  }
};

/**
 * 导出配置管理器和相关函数
 */
export default configManager;

/**
 * 快捷访问函数
 */
export const getConfig = (key, defaultValue) => configManager.get(key, defaultValue);
export const setConfig = (key, value) => configManager.set(key, value);
export const resetConfig = (key) => configManager.reset(key);
export const watchConfig = (key, callback) => configManager.watch(key, callback);
export const isDebug = () => configManager.isDebugEnabled();
export const isMock = () => configManager.isMockEnabled();
export const isDev = () => configManager.isDevelopment();
export const isProd = () => configManager.isProduction();

/**
 * 环境相关配置
 */
export { ENV_CONFIG, DEFAULT_CONFIG };