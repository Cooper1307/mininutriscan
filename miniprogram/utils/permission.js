/**
 * 权限管理工具
 * 提供小程序各种权限的申请、检查和管理功能
 */

/**
 * 权限类型枚举
 */
const PERMISSION_TYPE = {
  CAMERA: 'scope.camera',                    // 摄像头
  RECORD: 'scope.record',                   // 录音
  LOCATION: 'scope.userLocation',           // 位置信息
  ALBUM: 'scope.writePhotosAlbum',          // 保存到相册
  ADDRESS: 'scope.address',                 // 通讯地址
  INVOICE_TITLE: 'scope.invoiceTitle',      // 发票抬头
  INVOICE: 'scope.invoice',                 // 获取发票
  WERUN: 'scope.werun',                     // 微信运动步数
  BLUETOOTH: 'scope.bluetooth'              // 蓝牙
};

/**
 * 权限状态枚举
 */
const PERMISSION_STATUS = {
  AUTHORIZED: 'authorized',     // 已授权
  DENIED: 'denied',            // 已拒绝
  NOT_DETERMINED: 'notDetermined'  // 未确定
};

/**
 * 权限描述映射
 */
const PERMISSION_DESCRIPTIONS = {
  [PERMISSION_TYPE.CAMERA]: {
    name: '摄像头',
    description: '用于扫描食品条码和拍摄食品照片',
    reason: '需要使用摄像头来扫描商品条码和拍摄食品图片，以便为您提供营养信息分析服务'
  },
  [PERMISSION_TYPE.RECORD]: {
    name: '麦克风',
    description: '用于语音输入和语音搜索',
    reason: '需要使用麦克风来实现语音搜索功能，提升您的使用体验'
  },
  [PERMISSION_TYPE.LOCATION]: {
    name: '位置信息',
    description: '用于推荐附近的健康餐厅和商店',
    reason: '需要获取您的位置信息，为您推荐附近的健康餐厅和食品商店'
  },
  [PERMISSION_TYPE.ALBUM]: {
    name: '保存到相册',
    description: '用于保存营养报告和食品图片',
    reason: '需要保存权限来将营养分析报告和食品图片保存到您的相册'
  },
  [PERMISSION_TYPE.ADDRESS]: {
    name: '通讯地址',
    description: '用于配送地址管理',
    reason: '需要获取您的通讯地址，用于健康食品配送服务'
  },
  [PERMISSION_TYPE.INVOICE_TITLE]: {
    name: '发票抬头',
    description: '用于开具购买发票',
    reason: '需要获取发票抬头信息，为您的健康食品购买开具发票'
  },
  [PERMISSION_TYPE.WERUN]: {
    name: '微信运动',
    description: '用于运动数据分析和健康建议',
    reason: '需要获取您的运动数据，结合营养摄入为您提供更精准的健康建议'
  },
  [PERMISSION_TYPE.BLUETOOTH]: {
    name: '蓝牙',
    description: '用于连接智能健康设备',
    reason: '需要蓝牙权限来连接智能体重秤、血糖仪等健康设备'
  }
};

/**
 * 权限管理器类
 */
class PermissionManager {
  constructor() {
    this.permissionCache = new Map();
    this.requestQueue = new Map();
  }
  
  /**
   * 检查权限状态
   * @param {string} scope - 权限范围
   * @param {boolean} useCache - 是否使用缓存
   */
  async checkPermission(scope, useCache = true) {
    // 检查缓存
    if (useCache && this.permissionCache.has(scope)) {
      const cached = this.permissionCache.get(scope);
      // 缓存5分钟
      if (Date.now() - cached.timestamp < 5 * 60 * 1000) {
        return cached.status;
      }
    }
    
    try {
      const result = await this.getSetting();
      const authSetting = result.authSetting || {};
      
      let status;
      if (authSetting[scope] === true) {
        status = PERMISSION_STATUS.AUTHORIZED;
      } else if (authSetting[scope] === false) {
        status = PERMISSION_STATUS.DENIED;
      } else {
        status = PERMISSION_STATUS.NOT_DETERMINED;
      }
      
      // 更新缓存
      this.permissionCache.set(scope, {
        status,
        timestamp: Date.now()
      });
      
      return status;
    } catch (error) {
      console.error('检查权限失败:', error);
      return PERMISSION_STATUS.NOT_DETERMINED;
    }
  }
  
  /**
   * 请求权限
   * @param {string} scope - 权限范围
   * @param {object} options - 请求选项
   */
  async requestPermission(scope, options = {}) {
    const {
      showModal = true,
      customMessage = '',
      autoOpenSetting = true
    } = options;
    
    // 防止重复请求
    if (this.requestQueue.has(scope)) {
      return this.requestQueue.get(scope);
    }
    
    const requestPromise = this._requestPermissionInternal(scope, {
      showModal,
      customMessage,
      autoOpenSetting
    });
    
    this.requestQueue.set(scope, requestPromise);
    
    try {
      const result = await requestPromise;
      return result;
    } finally {
      this.requestQueue.delete(scope);
    }
  }
  
  /**
   * 内部权限请求方法
   */
  async _requestPermissionInternal(scope, options) {
    const { showModal, customMessage, autoOpenSetting } = options;
    
    try {
      // 首先检查当前权限状态
      const currentStatus = await this.checkPermission(scope, false);
      
      if (currentStatus === PERMISSION_STATUS.AUTHORIZED) {
        return {
          success: true,
          status: PERMISSION_STATUS.AUTHORIZED,
          message: '权限已授权'
        };
      }
      
      // 如果已被拒绝，直接引导到设置页面
      if (currentStatus === PERMISSION_STATUS.DENIED) {
        if (autoOpenSetting) {
          return this.handleDeniedPermission(scope, customMessage);
        } else {
          return {
            success: false,
            status: PERMISSION_STATUS.DENIED,
            message: '权限已被拒绝'
          };
        }
      }
      
      // 显示权限说明弹窗
      if (showModal) {
        const shouldRequest = await this.showPermissionModal(scope, customMessage);
        if (!shouldRequest) {
          return {
            success: false,
            status: PERMISSION_STATUS.DENIED,
            message: '用户取消授权'
          };
        }
      }
      
      // 请求权限
      const authorized = await this.authorize(scope);
      
      if (authorized) {
        // 更新缓存
        this.permissionCache.set(scope, {
          status: PERMISSION_STATUS.AUTHORIZED,
          timestamp: Date.now()
        });
        
        return {
          success: true,
          status: PERMISSION_STATUS.AUTHORIZED,
          message: '权限授权成功'
        };
      } else {
        // 权限被拒绝
        this.permissionCache.set(scope, {
          status: PERMISSION_STATUS.DENIED,
          timestamp: Date.now()
        });
        
        if (autoOpenSetting) {
          return this.handleDeniedPermission(scope, customMessage);
        } else {
          return {
            success: false,
            status: PERMISSION_STATUS.DENIED,
            message: '权限授权失败'
          };
        }
      }
    } catch (error) {
      console.error('请求权限失败:', error);
      return {
        success: false,
        status: PERMISSION_STATUS.NOT_DETERMINED,
        message: error.message || '权限请求失败'
      };
    }
  }
  
  /**
   * 处理被拒绝的权限
   */
  async handleDeniedPermission(scope, customMessage) {
    const permission = PERMISSION_DESCRIPTIONS[scope];
    const message = customMessage || 
      `${permission?.reason || '应用需要相关权限才能正常使用'}\n\n请在设置中开启权限`;
    
    try {
      const result = await this.showModal({
        title: '权限申请',
        content: message,
        confirmText: '去设置',
        cancelText: '取消'
      });
      
      if (result.confirm) {
        // 打开设置页面
        await this.openSetting();
        
        // 重新检查权限
        const newStatus = await this.checkPermission(scope, false);
        
        return {
          success: newStatus === PERMISSION_STATUS.AUTHORIZED,
          status: newStatus,
          message: newStatus === PERMISSION_STATUS.AUTHORIZED ? '权限授权成功' : '权限仍未授权'
        };
      } else {
        return {
          success: false,
          status: PERMISSION_STATUS.DENIED,
          message: '用户取消设置权限'
        };
      }
    } catch (error) {
      console.error('处理拒绝权限失败:', error);
      return {
        success: false,
        status: PERMISSION_STATUS.DENIED,
        message: '处理权限失败'
      };
    }
  }
  
  /**
   * 显示权限说明弹窗
   */
  async showPermissionModal(scope, customMessage) {
    const permission = PERMISSION_DESCRIPTIONS[scope];
    const message = customMessage || permission?.reason || '应用需要相关权限才能正常使用';
    
    try {
      const result = await this.showModal({
        title: `申请${permission?.name || '权限'}`,
        content: message,
        confirmText: '同意',
        cancelText: '拒绝'
      });
      
      return result.confirm;
    } catch (error) {
      console.error('显示权限弹窗失败:', error);
      return false;
    }
  }
  
  /**
   * 批量检查权限
   * @param {Array} scopes - 权限范围数组
   */
  async checkMultiplePermissions(scopes) {
    const results = {};
    
    for (const scope of scopes) {
      try {
        results[scope] = await this.checkPermission(scope);
      } catch (error) {
        results[scope] = PERMISSION_STATUS.NOT_DETERMINED;
      }
    }
    
    return results;
  }
  
  /**
   * 批量请求权限
   * @param {Array} scopes - 权限范围数组
   * @param {object} options - 请求选项
   */
  async requestMultiplePermissions(scopes, options = {}) {
    const results = {};
    
    for (const scope of scopes) {
      try {
        results[scope] = await this.requestPermission(scope, options);
      } catch (error) {
        results[scope] = {
          success: false,
          status: PERMISSION_STATUS.NOT_DETERMINED,
          message: error.message || '权限请求失败'
        };
      }
    }
    
    return results;
  }
  
  /**
   * 检查是否有必需权限
   * @param {Array} requiredScopes - 必需权限数组
   */
  async checkRequiredPermissions(requiredScopes) {
    const results = await this.checkMultiplePermissions(requiredScopes);
    
    const missing = [];
    const denied = [];
    
    for (const scope of requiredScopes) {
      const status = results[scope];
      if (status === PERMISSION_STATUS.NOT_DETERMINED) {
        missing.push(scope);
      } else if (status === PERMISSION_STATUS.DENIED) {
        denied.push(scope);
      }
    }
    
    return {
      allGranted: missing.length === 0 && denied.length === 0,
      missing,
      denied,
      results
    };
  }
  
  /**
   * 清除权限缓存
   * @param {string} scope - 权限范围（可选）
   */
  clearCache(scope) {
    if (scope) {
      this.permissionCache.delete(scope);
    } else {
      this.permissionCache.clear();
    }
  }
  
  /**
   * 获取权限描述
   * @param {string} scope - 权限范围
   */
  getPermissionDescription(scope) {
    return PERMISSION_DESCRIPTIONS[scope] || {
      name: '未知权限',
      description: '未知权限描述',
      reason: '应用需要此权限才能正常使用'
    };
  }
  
  // 微信小程序API包装方法
  
  getSetting() {
    return new Promise((resolve, reject) => {
      wx.getSetting({
        success: resolve,
        fail: reject
      });
    });
  }
  
  authorize(scope) {
    return new Promise((resolve) => {
      wx.authorize({
        scope,
        success: () => resolve(true),
        fail: () => resolve(false)
      });
    });
  }
  
  openSetting() {
    return new Promise((resolve, reject) => {
      wx.openSetting({
        success: resolve,
        fail: reject
      });
    });
  }
  
  showModal(options) {
    return new Promise((resolve, reject) => {
      wx.showModal({
        ...options,
        success: resolve,
        fail: reject
      });
    });
  }
}

/**
 * 特定权限的便捷方法
 */
class SpecificPermissions {
  constructor(permissionManager) {
    this.pm = permissionManager;
  }
  
  /**
   * 请求摄像头权限
   */
  async requestCamera(customMessage) {
    return this.pm.requestPermission(PERMISSION_TYPE.CAMERA, {
      customMessage: customMessage || '需要使用摄像头来扫描商品条码和拍摄食品图片'
    });
  }
  
  /**
   * 请求位置权限
   */
  async requestLocation(customMessage) {
    return this.pm.requestPermission(PERMISSION_TYPE.LOCATION, {
      customMessage: customMessage || '需要获取您的位置信息，为您推荐附近的健康餐厅和食品商店'
    });
  }
  
  /**
   * 请求相册保存权限
   */
  async requestAlbum(customMessage) {
    return this.pm.requestPermission(PERMISSION_TYPE.ALBUM, {
      customMessage: customMessage || '需要保存权限来将营养分析报告保存到您的相册'
    });
  }
  
  /**
   * 请求录音权限
   */
  async requestRecord(customMessage) {
    return this.pm.requestPermission(PERMISSION_TYPE.RECORD, {
      customMessage: customMessage || '需要使用麦克风来实现语音搜索功能'
    });
  }
  
  /**
   * 请求微信运动权限
   */
  async requestWeRun(customMessage) {
    return this.pm.requestPermission(PERMISSION_TYPE.WERUN, {
      customMessage: customMessage || '需要获取您的运动数据，结合营养摄入为您提供更精准的健康建议'
    });
  }
  
  /**
   * 检查摄像头权限
   */
  async checkCamera() {
    return this.pm.checkPermission(PERMISSION_TYPE.CAMERA);
  }
  
  /**
   * 检查位置权限
   */
  async checkLocation() {
    return this.pm.checkPermission(PERMISSION_TYPE.LOCATION);
  }
  
  /**
   * 检查相册权限
   */
  async checkAlbum() {
    return this.pm.checkPermission(PERMISSION_TYPE.ALBUM);
  }
}

// 创建全局权限管理器实例
const permissionManager = new PermissionManager();
const specificPermissions = new SpecificPermissions(permissionManager);

/**
 * 权限混入
 * 可以在页面中使用，提供权限相关功能
 */
export const permissionMixin = {
  methods: {
    /**
     * 检查权限
     */
    async checkPermission(scope) {
      return permissionManager.checkPermission(scope);
    },
    
    /**
     * 请求权限
     */
    async requestPermission(scope, options) {
      return permissionManager.requestPermission(scope, options);
    },
    
    /**
     * 检查必需权限
     */
    async checkRequiredPermissions(scopes) {
      return permissionManager.checkRequiredPermissions(scopes);
    },
    
    /**
     * 请求摄像头权限
     */
    async requestCameraPermission(customMessage) {
      return specificPermissions.requestCamera(customMessage);
    },
    
    /**
     * 请求位置权限
     */
    async requestLocationPermission(customMessage) {
      return specificPermissions.requestLocation(customMessage);
    },
    
    /**
     * 请求相册权限
     */
    async requestAlbumPermission(customMessage) {
      return specificPermissions.requestAlbum(customMessage);
    }
  }
};

/**
 * 工具函数
 */

// 检查权限
export function checkPermission(scope) {
  return permissionManager.checkPermission(scope);
}

// 请求权限
export function requestPermission(scope, options) {
  return permissionManager.requestPermission(scope, options);
}

// 批量检查权限
export function checkMultiplePermissions(scopes) {
  return permissionManager.checkMultiplePermissions(scopes);
}

// 批量请求权限
export function requestMultiplePermissions(scopes, options) {
  return permissionManager.requestMultiplePermissions(scopes, options);
}

// 检查必需权限
export function checkRequiredPermissions(scopes) {
  return permissionManager.checkRequiredPermissions(scopes);
}

// 请求摄像头权限
export function requestCameraPermission(customMessage) {
  return specificPermissions.requestCamera(customMessage);
}

// 请求位置权限
export function requestLocationPermission(customMessage) {
  return specificPermissions.requestLocation(customMessage);
}

// 请求相册权限
export function requestAlbumPermission(customMessage) {
  return specificPermissions.requestAlbum(customMessage);
}

// 请求录音权限
export function requestRecordPermission(customMessage) {
  return specificPermissions.requestRecord(customMessage);
}

// 请求微信运动权限
export function requestWeRunPermission(customMessage) {
  return specificPermissions.requestWeRun(customMessage);
}

// 获取权限描述
export function getPermissionDescription(scope) {
  return permissionManager.getPermissionDescription(scope);
}

// 清除权限缓存
export function clearPermissionCache(scope) {
  return permissionManager.clearCache(scope);
}

// 导出权限管理器和相关常量
export {
  PermissionManager,
  SpecificPermissions,
  PERMISSION_TYPE,
  PERMISSION_STATUS,
  PERMISSION_DESCRIPTIONS
};

export default {
  manager: permissionManager,
  specific: specificPermissions
};