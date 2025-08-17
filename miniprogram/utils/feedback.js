/**
 * 用户反馈工具类
 * 提供统一的错误处理、成功提示、加载状态等用户反馈机制
 */
class FeedbackManager {
  constructor() {
    this.loadingCount = 0;
    this.defaultOptions = {
      duration: 2000,
      mask: true,
      vibrate: true
    };
  }

  /**
   * 显示成功提示
   * @param {string} message 提示消息
   * @param {Object} options 配置选项
   */
  showSuccess(message, options = {}) {
    const config = { ...this.defaultOptions, ...options };
    
    wx.showToast({
      title: message,
      icon: 'success',
      duration: config.duration,
      mask: config.mask
    });
    
    // 触发成功震动反馈
    if (config.vibrate) {
      wx.vibrateShort({
        type: 'light'
      });
    }
  }

  /**
   * 显示错误提示
   * @param {string} message 错误消息
   * @param {Object} options 配置选项
   */
  showError(message, options = {}) {
    const config = { ...this.defaultOptions, ...options };
    const friendlyMessage = this.getFriendlyErrorMessage(message);
    
    wx.showToast({
      title: friendlyMessage,
      icon: 'error',
      duration: config.duration,
      mask: config.mask
    });
    
    // 触发错误震动反馈
    if (config.vibrate) {
      wx.vibrateShort({
        type: 'heavy'
      });
    }
  }

  /**
   * 显示警告提示
   * @param {string} message 警告消息
   * @param {Object} options 配置选项
   */
  showWarning(message, options = {}) {
    const config = { ...this.defaultOptions, ...options };
    
    wx.showToast({
      title: message,
      icon: 'none',
      duration: config.duration,
      mask: config.mask
    });
  }

  /**
   * 显示加载提示
   * @param {string} message 加载消息
   * @param {boolean} mask 是否显示遮罩
   */
  showLoading(message = '加载中...', mask = true) {
    this.loadingCount++;
    
    wx.showLoading({
      title: message,
      mask: mask
    });
  }

  /**
   * 隐藏加载提示
   */
  hideLoading() {
    this.loadingCount = Math.max(0, this.loadingCount - 1);
    
    if (this.loadingCount === 0) {
      wx.hideLoading();
    }
  }

  /**
   * 显示确认对话框
   * @param {string} title 标题
   * @param {string} content 内容
   * @param {Object} options 配置选项
   * @returns {Promise<boolean>} 用户选择结果
   */
  showConfirm(title, content, options = {}) {
    return new Promise((resolve) => {
      wx.showModal({
        title,
        content,
        showCancel: true,
        cancelText: options.cancelText || '取消',
        confirmText: options.confirmText || '确定',
        cancelColor: options.cancelColor || '#000000',
        confirmColor: options.confirmColor || '#576B95',
        success: (res) => {
          resolve(res.confirm);
        },
        fail: () => {
          resolve(false);
        }
      });
    });
  }

  /**
   * 显示操作菜单
   * @param {Array} itemList 菜单项列表
   * @returns {Promise<number>} 选择的菜单项索引
   */
  showActionSheet(itemList) {
    return new Promise((resolve, reject) => {
      wx.showActionSheet({
        itemList,
        success: (res) => {
          resolve(res.tapIndex);
        },
        fail: (err) => {
          reject(err);
        }
      });
    });
  }

  /**
   * 处理网络请求错误
   * @param {Error} error 错误对象
   * @param {string} defaultMessage 默认错误消息
   */
  handleNetworkError(error, defaultMessage = '网络请求失败') {
    console.error('Network Error:', error);
    
    let message = defaultMessage;
    
    if (error.statusCode) {
      switch (error.statusCode) {
        case 400:
          message = '请求参数错误';
          break;
        case 401:
          message = '未授权，请重新登录';
          this.redirectToLogin();
          return;
        case 403:
          message = '访问被拒绝';
          break;
        case 404:
          message = '请求的资源不存在';
          break;
        case 500:
          message = '服务器内部错误';
          break;
        case 502:
          message = '网关错误';
          break;
        case 503:
          message = '服务暂时不可用';
          break;
        default:
          message = `请求失败 (${error.statusCode})`;
      }
    } else if (error.errMsg) {
      if (error.errMsg.includes('timeout')) {
        message = '请求超时，请检查网络连接';
      } else if (error.errMsg.includes('fail')) {
        message = '网络连接失败，请检查网络设置';
      }
    }
    
    this.showError(message);
  }

  /**
   * 获取用户友好的错误消息
   * @param {string} errorMessage 原始错误消息
   * @returns {string} 用户友好的错误消息
   */
  getFriendlyErrorMessage(errorMessage) {
    const errorMap = {
      'network error': '网络连接失败',
      'timeout': '请求超时',
      'unauthorized': '未授权访问',
      'forbidden': '访问被拒绝',
      'not found': '资源不存在',
      'server error': '服务器错误',
      'invalid parameter': '参数错误',
      'permission denied': '权限不足'
    };
    
    const lowerMessage = errorMessage.toLowerCase();
    
    for (const [key, value] of Object.entries(errorMap)) {
      if (lowerMessage.includes(key)) {
        return value;
      }
    }
    
    return errorMessage || '操作失败';
  }

  /**
   * 跳转到登录页面
   */
  redirectToLogin() {
    wx.navigateTo({
      url: '/pages/login/login'
    });
  }

  /**
   * 检查网络状态
   * @returns {Promise<boolean>} 网络是否可用
   */
  checkNetworkStatus() {
    return new Promise((resolve) => {
      wx.getNetworkType({
        success: (res) => {
          const isConnected = res.networkType !== 'none';
          if (!isConnected) {
            this.showError('网络连接不可用，请检查网络设置');
          }
          resolve(isConnected);
        },
        fail: () => {
          this.showError('无法获取网络状态');
          resolve(false);
        }
      });
    });
  }

  /**
   * 复制文本到剪贴板
   * @param {string} text 要复制的文本
   * @param {string} successMessage 成功提示消息
   */
  copyToClipboard(text, successMessage = '已复制到剪贴板') {
    wx.setClipboardData({
      data: text,
      success: () => {
        this.showSuccess(successMessage);
      },
      fail: () => {
        this.showError('复制失败');
      }
    });
  }
}

// 创建全局实例
const feedback = new FeedbackManager();

// 导出实例
module.exports = feedback;