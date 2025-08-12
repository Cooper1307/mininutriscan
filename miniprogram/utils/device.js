/**
 * 设备信息和硬件功能检测工具
 * 提供设备信息获取、硬件能力检测、设备适配等功能
 */

/**
 * 设备类型枚举
 */
const DEVICE_TYPE = {
  PHONE: 'phone',           // 手机
  TABLET: 'tablet',         // 平板
  DESKTOP: 'desktop',       // 桌面
  UNKNOWN: 'unknown'        // 未知
};

/**
 * 操作系统类型枚举
 */
const OS_TYPE = {
  IOS: 'ios',
  ANDROID: 'android',
  WINDOWS: 'windows',
  MAC: 'mac',
  UNKNOWN: 'unknown'
};

/**
 * 网络类型枚举
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
 * 设备信息管理器
 */
class DeviceManager {
  constructor() {
    this.systemInfo = null;
    this.networkInfo = null;
    this.batteryInfo = null;
    this.locationInfo = null;
    this.capabilities = null;
    this.isInitialized = false;
    
    this.init();
  }
  
  /**
   * 初始化设备信息
   */
  async init() {
    try {
      await Promise.all([
        this.getSystemInfo(),
        this.getNetworkInfo(),
        this.getBatteryInfo(),
        this.detectCapabilities()
      ]);
      
      this.isInitialized = true;
    } catch (error) {
      console.error('设备信息初始化失败:', error);
    }
  }
  
  /**
   * 获取系统信息
   */
  async getSystemInfo() {
    return new Promise((resolve, reject) => {
      wx.getSystemInfo({
        success: (res) => {
          this.systemInfo = {
            // 基本信息
            brand: res.brand,                    // 设备品牌
            model: res.model,                    // 设备型号
            system: res.system,                  // 操作系统及版本
            platform: res.platform,             // 客户端平台
            version: res.version,                // 微信版本号
            SDKVersion: res.SDKVersion,          // 客户端基础库版本
            
            // 屏幕信息
            screenWidth: res.screenWidth,        // 屏幕宽度
            screenHeight: res.screenHeight,      // 屏幕高度
            windowWidth: res.windowWidth,        // 可使用窗口宽度
            windowHeight: res.windowHeight,      // 可使用窗口高度
            pixelRatio: res.pixelRatio,         // 设备像素比
            
            // 状态栏信息
            statusBarHeight: res.statusBarHeight, // 状态栏高度
            
            // 安全区域
            safeArea: res.safeArea,             // 安全区域
            
            // 其他信息
            language: res.language,              // 微信设置的语言
            fontSizeSetting: res.fontSizeSetting, // 用户字体大小设置
            theme: res.theme,                    // 系统主题
            
            // 性能相关
            benchmarkLevel: res.benchmarkLevel,  // 设备性能等级
            
            // 计算属性
            deviceType: this.getDeviceType(res),
            osType: this.getOSType(res),
            isIOS: res.platform === 'ios',
            isAndroid: res.platform === 'android',
            isTablet: this.isTablet(res),
            isLowEnd: this.isLowEndDevice(res),
            screenRatio: res.screenWidth / res.screenHeight,
            dpi: this.calculateDPI(res)
          };
          resolve(this.systemInfo);
        },
        fail: reject
      });
    });
  }
  
  /**
   * 获取网络信息
   */
  async getNetworkInfo() {
    return new Promise((resolve, reject) => {
      wx.getNetworkType({
        success: (res) => {
          this.networkInfo = {
            networkType: res.networkType,
            isConnected: res.networkType !== 'none',
            isWifi: res.networkType === 'wifi',
            isMobile: ['2g', '3g', '4g', '5g'].includes(res.networkType),
            isHighSpeed: ['wifi', '4g', '5g'].includes(res.networkType),
            isLowSpeed: ['2g', '3g'].includes(res.networkType)
          };
          resolve(this.networkInfo);
        },
        fail: reject
      });
    });
  }
  
  /**
   * 获取电池信息
   */
  async getBatteryInfo() {
    return new Promise((resolve) => {
      try {
        const batteryInfo = wx.getBatteryInfoSync();
        this.batteryInfo = {
          level: batteryInfo.level,           // 电量百分比
          isCharging: batteryInfo.isCharging, // 是否正在充电
          isLowBattery: batteryInfo.level < 20, // 是否低电量
          isCriticalBattery: batteryInfo.level < 10 // 是否极低电量
        };
        resolve(this.batteryInfo);
      } catch (error) {
        this.batteryInfo = {
          level: null,
          isCharging: null,
          isLowBattery: false,
          isCriticalBattery: false
        };
        resolve(this.batteryInfo);
      }
    });
  }
  
  /**
   * 检测设备能力
   */
  async detectCapabilities() {
    this.capabilities = {
      // 基础能力
      canUseCamera: await this.checkAPI('chooseImage'),
      canUseLocation: await this.checkAPI('getLocation'),
      canUseRecord: await this.checkAPI('startRecord'),
      canUseVibrate: await this.checkAPI('vibrateLong'),
      canUseClipboard: await this.checkAPI('setClipboardData'),
      
      // 存储能力
      canUseStorage: await this.checkAPI('setStorageSync'),
      canUseFileSystem: await this.checkAPI('getFileSystemManager'),
      
      // 网络能力
      canUseRequest: await this.checkAPI('request'),
      canUseWebSocket: await this.checkAPI('connectSocket'),
      canUseDownload: await this.checkAPI('downloadFile'),
      canUseUpload: await this.checkAPI('uploadFile'),
      
      // 界面能力
      canUseCanvas: await this.checkAPI('createCanvasContext'),
      canUseAnimation: await this.checkAPI('createAnimation'),
      canUseVideo: await this.checkAPI('createVideoContext'),
      
      // 设备能力
      canUseAccelerometer: await this.checkAPI('startAccelerometer'),
      canUseCompass: await this.checkAPI('startCompass'),
      canUseGyroscope: await this.checkAPI('startGyroscope'),
      canUseBluetooth: await this.checkAPI('openBluetoothAdapter'),
      canUseWifi: await this.checkAPI('startWifi'),
      
      // 微信能力
      canUseShare: await this.checkAPI('shareAppMessage'),
      canUsePayment: await this.checkAPI('requestPayment'),
      canUseLogin: await this.checkAPI('login'),
      canUseUserInfo: await this.checkAPI('getUserInfo'),
      
      // 扫码能力
      canUseScanCode: await this.checkAPI('scanCode'),
      
      // 地图能力
      canUseMap: await this.checkAPI('createMapContext'),
      
      // 音频能力
      canUseAudio: await this.checkAPI('createAudioContext'),
      canUseBackgroundAudio: await this.checkAPI('getBackgroundAudioManager'),
      
      // 实时通信
      canUseLivePlayer: await this.checkAPI('createLivePlayerContext'),
      canUseLivePusher: await this.checkAPI('createLivePusherContext')
    };
    
    return this.capabilities;
  }
  
  /**
   * 检查API是否可用
   * @param {string} apiName - API名称
   */
  async checkAPI(apiName) {
    return new Promise((resolve) => {
      if (typeof wx[apiName] === 'function') {
        resolve(true);
      } else {
        resolve(false);
      }
    });
  }
  
  /**
   * 获取设备类型
   * @param {object} systemInfo - 系统信息
   */
  getDeviceType(systemInfo) {
    const { screenWidth, screenHeight } = systemInfo;
    const minSize = Math.min(screenWidth, screenHeight);
    const maxSize = Math.max(screenWidth, screenHeight);
    
    // 简单的设备类型判断
    if (minSize >= 768) {
      return DEVICE_TYPE.TABLET;
    } else if (minSize >= 320) {
      return DEVICE_TYPE.PHONE;
    } else {
      return DEVICE_TYPE.UNKNOWN;
    }
  }
  
  /**
   * 获取操作系统类型
   * @param {object} systemInfo - 系统信息
   */
  getOSType(systemInfo) {
    const platform = systemInfo.platform.toLowerCase();
    
    if (platform.includes('ios')) {
      return OS_TYPE.IOS;
    } else if (platform.includes('android')) {
      return OS_TYPE.ANDROID;
    } else if (platform.includes('windows')) {
      return OS_TYPE.WINDOWS;
    } else if (platform.includes('mac')) {
      return OS_TYPE.MAC;
    } else {
      return OS_TYPE.UNKNOWN;
    }
  }
  
  /**
   * 判断是否为平板设备
   * @param {object} systemInfo - 系统信息
   */
  isTablet(systemInfo) {
    const { screenWidth, screenHeight } = systemInfo;
    const minSize = Math.min(screenWidth, screenHeight);
    return minSize >= 768;
  }
  
  /**
   * 判断是否为低端设备
   * @param {object} systemInfo - 系统信息
   */
  isLowEndDevice(systemInfo) {
    // 基于性能等级判断
    if (systemInfo.benchmarkLevel !== undefined) {
      return systemInfo.benchmarkLevel < 10;
    }
    
    // 基于内存和屏幕分辨率简单判断
    const totalPixels = systemInfo.screenWidth * systemInfo.screenHeight;
    return totalPixels < 1000000; // 小于100万像素认为是低端设备
  }
  
  /**
   * 计算DPI
   * @param {object} systemInfo - 系统信息
   */
  calculateDPI(systemInfo) {
    // 简单的DPI计算
    return systemInfo.pixelRatio * 160;
  }
  
  /**
   * 获取设备唯一标识
   */
  async getDeviceId() {
    try {
      // 尝试获取设备ID（需要用户授权）
      const res = await new Promise((resolve, reject) => {
        wx.getSystemInfo({
          success: resolve,
          fail: reject
        });
      });
      
      // 生成基于设备信息的唯一标识
      const deviceInfo = `${res.brand}_${res.model}_${res.system}_${res.screenWidth}x${res.screenHeight}`;
      return this.generateHash(deviceInfo);
    } catch (error) {
      // 生成随机ID并存储
      let deviceId = wx.getStorageSync('deviceId');
      if (!deviceId) {
        deviceId = this.generateRandomId();
        wx.setStorageSync('deviceId', deviceId);
      }
      return deviceId;
    }
  }
  
  /**
   * 生成哈希值
   * @param {string} str - 输入字符串
   */
  generateHash(str) {
    let hash = 0;
    if (str.length === 0) return hash.toString();
    
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // 转换为32位整数
    }
    
    return Math.abs(hash).toString(36);
  }
  
  /**
   * 生成随机ID
   */
  generateRandomId() {
    return `device_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  
  /**
   * 检查设备是否支持某个功能
   * @param {string} feature - 功能名称
   */
  supportsFeature(feature) {
    if (!this.capabilities) {
      console.warn('设备能力检测尚未完成');
      return false;
    }
    
    return this.capabilities[feature] || false;
  }
  
  /**
   * 获取设备性能等级
   */
  getPerformanceLevel() {
    if (!this.systemInfo) return 'unknown';
    
    if (this.systemInfo.benchmarkLevel !== undefined) {
      if (this.systemInfo.benchmarkLevel >= 30) return 'high';
      if (this.systemInfo.benchmarkLevel >= 10) return 'medium';
      return 'low';
    }
    
    // 基于其他指标判断
    const totalPixels = this.systemInfo.screenWidth * this.systemInfo.screenHeight;
    const pixelRatio = this.systemInfo.pixelRatio;
    
    if (totalPixels > 2000000 && pixelRatio >= 3) return 'high';
    if (totalPixels > 1000000 && pixelRatio >= 2) return 'medium';
    return 'low';
  }
  
  /**
   * 获取推荐的图片质量
   */
  getRecommendedImageQuality() {
    const performanceLevel = this.getPerformanceLevel();
    const isWifi = this.networkInfo?.isWifi;
    
    if (performanceLevel === 'high' && isWifi) return 'high';
    if (performanceLevel === 'medium') return 'medium';
    return 'low';
  }
  
  /**
   * 获取推荐的并发请求数
   */
  getRecommendedConcurrency() {
    const performanceLevel = this.getPerformanceLevel();
    
    switch (performanceLevel) {
      case 'high': return 6;
      case 'medium': return 4;
      case 'low': return 2;
      default: return 3;
    }
  }
  
  /**
   * 监听网络状态变化
   * @param {Function} callback - 回调函数
   */
  onNetworkStatusChange(callback) {
    wx.onNetworkStatusChange((res) => {
      this.networkInfo = {
        networkType: res.networkType,
        isConnected: res.isConnected,
        isWifi: res.networkType === 'wifi',
        isMobile: ['2g', '3g', '4g', '5g'].includes(res.networkType),
        isHighSpeed: ['wifi', '4g', '5g'].includes(res.networkType),
        isLowSpeed: ['2g', '3g'].includes(res.networkType)
      };
      
      callback(this.networkInfo);
    });
  }
  
  /**
   * 监听内存警告
   * @param {Function} callback - 回调函数
   */
  onMemoryWarning(callback) {
    wx.onMemoryWarning && wx.onMemoryWarning((res) => {
      callback({
        level: res.level,
        isLowMemory: res.level >= 10,
        isCriticalMemory: res.level >= 15
      });
    });
  }
  
  /**
   * 获取完整的设备信息
   */
  getDeviceInfo() {
    return {
      system: this.systemInfo,
      network: this.networkInfo,
      battery: this.batteryInfo,
      capabilities: this.capabilities,
      performance: {
        level: this.getPerformanceLevel(),
        recommendedImageQuality: this.getRecommendedImageQuality(),
        recommendedConcurrency: this.getRecommendedConcurrency()
      },
      isInitialized: this.isInitialized
    };
  }
  
  /**
   * 刷新设备信息
   */
  async refresh() {
    await this.init();
    return this.getDeviceInfo();
  }
}

/**
 * 设备适配器
 */
class DeviceAdapter {
  constructor(deviceManager) {
    this.deviceManager = deviceManager;
  }
  
  /**
   * 获取适配的样式
   * @param {object} baseStyles - 基础样式
   */
  getAdaptedStyles(baseStyles) {
    const deviceInfo = this.deviceManager.getDeviceInfo();
    const systemInfo = deviceInfo.system;
    
    if (!systemInfo) return baseStyles;
    
    const adaptedStyles = { ...baseStyles };
    
    // 根据设备类型调整
    if (systemInfo.isTablet) {
      adaptedStyles.fontSize = (adaptedStyles.fontSize || 14) * 1.2;
      adaptedStyles.padding = (adaptedStyles.padding || 10) * 1.5;
    }
    
    // 根据像素比调整
    if (systemInfo.pixelRatio >= 3) {
      adaptedStyles.borderWidth = Math.max(adaptedStyles.borderWidth || 1, 0.5);
    }
    
    // 根据屏幕尺寸调整
    if (systemInfo.screenWidth < 375) {
      adaptedStyles.fontSize = (adaptedStyles.fontSize || 14) * 0.9;
    }
    
    return adaptedStyles;
  }
  
  /**
   * 获取适配的图片尺寸
   * @param {number} baseWidth - 基础宽度
   * @param {number} baseHeight - 基础高度
   */
  getAdaptedImageSize(baseWidth, baseHeight) {
    const deviceInfo = this.deviceManager.getDeviceInfo();
    const systemInfo = deviceInfo.system;
    
    if (!systemInfo) return { width: baseWidth, height: baseHeight };
    
    const scale = systemInfo.pixelRatio;
    const screenWidth = systemInfo.screenWidth;
    
    // 根据屏幕宽度调整
    const widthScale = screenWidth / 375; // 以iPhone 6为基准
    
    return {
      width: Math.round(baseWidth * widthScale),
      height: Math.round(baseHeight * widthScale)
    };
  }
  
  /**
   * 获取安全区域样式
   */
  getSafeAreaStyles() {
    const deviceInfo = this.deviceManager.getDeviceInfo();
    const systemInfo = deviceInfo.system;
    
    if (!systemInfo || !systemInfo.safeArea) {
      return {
        paddingTop: 0,
        paddingBottom: 0,
        paddingLeft: 0,
        paddingRight: 0
      };
    }
    
    const safeArea = systemInfo.safeArea;
    
    return {
      paddingTop: safeArea.top,
      paddingBottom: systemInfo.screenHeight - safeArea.bottom,
      paddingLeft: safeArea.left,
      paddingRight: systemInfo.screenWidth - safeArea.right
    };
  }
}

// 创建全局实例
const deviceManager = new DeviceManager();
const deviceAdapter = new DeviceAdapter(deviceManager);

/**
 * 设备信息混入
 */
export const deviceMixin = {
  data() {
    return {
      deviceInfo: null,
      isLowEndDevice: false,
      isTablet: false
    };
  },
  
  async onLoad() {
    await deviceManager.init();
    this.deviceInfo = deviceManager.getDeviceInfo();
    this.isLowEndDevice = this.deviceInfo.system?.isLowEnd || false;
    this.isTablet = this.deviceInfo.system?.isTablet || false;
  },
  
  methods: {
    /**
     * 检查设备能力
     */
    checkCapability(feature) {
      return deviceManager.supportsFeature(feature);
    },
    
    /**
     * 获取适配样式
     */
    getAdaptedStyles(baseStyles) {
      return deviceAdapter.getAdaptedStyles(baseStyles);
    },
    
    /**
     * 获取安全区域样式
     */
    getSafeAreaStyles() {
      return deviceAdapter.getSafeAreaStyles();
    }
  }
};

/**
 * 工具函数
 */

// 获取设备信息
export function getDeviceInfo() {
  return deviceManager.getDeviceInfo();
}

// 检查设备能力
export function checkCapability(feature) {
  return deviceManager.supportsFeature(feature);
}

// 获取设备ID
export function getDeviceId() {
  return deviceManager.getDeviceId();
}

// 获取性能等级
export function getPerformanceLevel() {
  return deviceManager.getPerformanceLevel();
}

// 获取推荐图片质量
export function getRecommendedImageQuality() {
  return deviceManager.getRecommendedImageQuality();
}

// 获取推荐并发数
export function getRecommendedConcurrency() {
  return deviceManager.getRecommendedConcurrency();
}

// 监听网络状态变化
export function onNetworkStatusChange(callback) {
  return deviceManager.onNetworkStatusChange(callback);
}

// 监听内存警告
export function onMemoryWarning(callback) {
  return deviceManager.onMemoryWarning(callback);
}

// 获取适配样式
export function getAdaptedStyles(baseStyles) {
  return deviceAdapter.getAdaptedStyles(baseStyles);
}

// 获取适配图片尺寸
export function getAdaptedImageSize(baseWidth, baseHeight) {
  return deviceAdapter.getAdaptedImageSize(baseWidth, baseHeight);
}

// 获取安全区域样式
export function getSafeAreaStyles() {
  return deviceAdapter.getSafeAreaStyles();
}

// 刷新设备信息
export function refreshDeviceInfo() {
  return deviceManager.refresh();
}

// 导出类和常量
export {
  DeviceManager,
  DeviceAdapter,
  DEVICE_TYPE,
  OS_TYPE,
  NETWORK_TYPE
};

export default {
  manager: deviceManager,
  adapter: deviceAdapter
};