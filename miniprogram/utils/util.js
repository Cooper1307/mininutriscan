/**
 * 通用工具函数库
 * 提供常用的工具方法，提高开发效率
 */

/**
 * 格式化时间
 * @param {Date|string|number} date - 日期对象、时间戳或日期字符串
 * @param {string} format - 格式化模板，如 'YYYY-MM-DD HH:mm:ss'
 * @returns {string} 格式化后的时间字符串
 */
export function formatTime(date, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!date) return '';
  
  const d = new Date(date);
  if (isNaN(d.getTime())) return '';
  
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hour = String(d.getHours()).padStart(2, '0');
  const minute = String(d.getMinutes()).padStart(2, '0');
  const second = String(d.getSeconds()).padStart(2, '0');
  
  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hour)
    .replace('mm', minute)
    .replace('ss', second);
}

/**
 * 获取相对时间
 * @param {Date|string|number} date - 日期
 * @returns {string} 相对时间描述
 */
export function getRelativeTime(date) {
  if (!date) return '';
  
  const now = new Date();
  const target = new Date(date);
  const diff = now - target;
  
  if (diff < 0) return '未来时间';
  
  const minute = 60 * 1000;
  const hour = 60 * minute;
  const day = 24 * hour;
  const week = 7 * day;
  const month = 30 * day;
  const year = 365 * day;
  
  if (diff < minute) {
    return '刚刚';
  } else if (diff < hour) {
    return `${Math.floor(diff / minute)}分钟前`;
  } else if (diff < day) {
    return `${Math.floor(diff / hour)}小时前`;
  } else if (diff < week) {
    return `${Math.floor(diff / day)}天前`;
  } else if (diff < month) {
    return `${Math.floor(diff / week)}周前`;
  } else if (diff < year) {
    return `${Math.floor(diff / month)}个月前`;
  } else {
    return `${Math.floor(diff / year)}年前`;
  }
}

/**
 * 防抖函数
 * @param {Function} func - 要防抖的函数
 * @param {number} delay - 延迟时间（毫秒）
 * @returns {Function} 防抖后的函数
 */
export function debounce(func, delay = 300) {
  let timeoutId;
  return function (...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(this, args), delay);
  };
}

/**
 * 节流函数
 * @param {Function} func - 要节流的函数
 * @param {number} delay - 间隔时间（毫秒）
 * @returns {Function} 节流后的函数
 */
export function throttle(func, delay = 300) {
  let lastTime = 0;
  return function (...args) {
    const now = Date.now();
    if (now - lastTime >= delay) {
      lastTime = now;
      func.apply(this, args);
    }
  };
}

/**
 * 深拷贝对象
 * @param {any} obj - 要拷贝的对象
 * @returns {any} 拷贝后的对象
 */
export function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }
  
  if (obj instanceof Date) {
    return new Date(obj.getTime());
  }
  
  if (obj instanceof Array) {
    return obj.map(item => deepClone(item));
  }
  
  if (typeof obj === 'object') {
    const cloned = {};
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        cloned[key] = deepClone(obj[key]);
      }
    }
    return cloned;
  }
  
  return obj;
}

/**
 * 生成唯一ID
 * @param {number} length - ID长度
 * @returns {string} 唯一ID
 */
export function generateId(length = 8) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

/**
 * 格式化文件大小
 * @param {number} bytes - 字节数
 * @param {number} decimals - 小数位数
 * @returns {string} 格式化后的文件大小
 */
export function formatFileSize(bytes, decimals = 2) {
  if (bytes === 0) return '0 B';
  
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * 验证手机号
 * @param {string} phone - 手机号
 * @returns {boolean} 是否有效
 */
export function validatePhone(phone) {
  const phoneRegex = /^1[3-9]\d{9}$/;
  return phoneRegex.test(phone);
}

/**
 * 验证邮箱
 * @param {string} email - 邮箱地址
 * @returns {boolean} 是否有效
 */
export function validateEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * 验证身份证号
 * @param {string} idCard - 身份证号
 * @returns {boolean} 是否有效
 */
export function validateIdCard(idCard) {
  const idCardRegex = /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/;
  return idCardRegex.test(idCard);
}

/**
 * 获取URL参数
 * @param {string} url - URL字符串
 * @returns {object} 参数对象
 */
export function getUrlParams(url) {
  const params = {};
  const urlObj = new URL(url);
  
  for (const [key, value] of urlObj.searchParams) {
    params[key] = value;
  }
  
  return params;
}

/**
 * 数组去重
 * @param {Array} arr - 原数组
 * @param {string} key - 去重依据的键名（对象数组时使用）
 * @returns {Array} 去重后的数组
 */
export function uniqueArray(arr, key) {
  if (!Array.isArray(arr)) return [];
  
  if (key) {
    const seen = new Set();
    return arr.filter(item => {
      const value = item[key];
      if (seen.has(value)) {
        return false;
      }
      seen.add(value);
      return true;
    });
  }
  
  return [...new Set(arr)];
}

/**
 * 数组分组
 * @param {Array} arr - 原数组
 * @param {string|Function} key - 分组依据
 * @returns {object} 分组后的对象
 */
export function groupBy(arr, key) {
  if (!Array.isArray(arr)) return {};
  
  return arr.reduce((groups, item) => {
    const groupKey = typeof key === 'function' ? key(item) : item[key];
    if (!groups[groupKey]) {
      groups[groupKey] = [];
    }
    groups[groupKey].push(item);
    return groups;
  }, {});
}

/**
 * 数字格式化
 * @param {number} num - 数字
 * @param {number} precision - 精度
 * @returns {string} 格式化后的数字
 */
export function formatNumber(num, precision = 2) {
  if (typeof num !== 'number' || isNaN(num)) return '0';
  
  if (num >= 100000000) {
    return (num / 100000000).toFixed(precision) + '亿';
  } else if (num >= 10000) {
    return (num / 10000).toFixed(precision) + '万';
  } else if (num >= 1000) {
    return (num / 1000).toFixed(precision) + 'k';
  }
  
  return num.toString();
}

/**
 * 颜色转换
 * @param {string} hex - 十六进制颜色
 * @param {number} alpha - 透明度
 * @returns {string} RGBA颜色
 */
export function hexToRgba(hex, alpha = 1) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  if (!result) return hex;
  
  const r = parseInt(result[1], 16);
  const g = parseInt(result[2], 16);
  const b = parseInt(result[3], 16);
  
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

/**
 * 获取随机颜色
 * @returns {string} 十六进制颜色
 */
export function getRandomColor() {
  return '#' + Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0');
}

/**
 * 计算两点间距离
 * @param {object} point1 - 点1 {x, y}
 * @param {object} point2 - 点2 {x, y}
 * @returns {number} 距离
 */
export function getDistance(point1, point2) {
  const dx = point2.x - point1.x;
  const dy = point2.y - point1.y;
  return Math.sqrt(dx * dx + dy * dy);
}

/**
 * 本地存储封装
 */
export const storage = {
  /**
   * 设置存储
   * @param {string} key - 键名
   * @param {any} value - 值
   * @param {number} expire - 过期时间（毫秒）
   */
  set(key, value, expire) {
    const data = {
      value,
      expire: expire ? Date.now() + expire : null
    };
    
    try {
      wx.setStorageSync(key, JSON.stringify(data));
    } catch (error) {
      console.error('存储失败:', error);
    }
  },
  
  /**
   * 获取存储
   * @param {string} key - 键名
   * @param {any} defaultValue - 默认值
   * @returns {any} 存储的值
   */
  get(key, defaultValue = null) {
    try {
      const stored = wx.getStorageSync(key);
      if (!stored) return defaultValue;
      
      const data = JSON.parse(stored);
      
      // 检查是否过期
      if (data.expire && Date.now() > data.expire) {
        this.remove(key);
        return defaultValue;
      }
      
      return data.value;
    } catch (error) {
      console.error('读取存储失败:', error);
      return defaultValue;
    }
  },
  
  /**
   * 删除存储
   * @param {string} key - 键名
   */
  remove(key) {
    try {
      wx.removeStorageSync(key);
    } catch (error) {
      console.error('删除存储失败:', error);
    }
  },
  
  /**
   * 清空存储
   */
  clear() {
    try {
      wx.clearStorageSync();
    } catch (error) {
      console.error('清空存储失败:', error);
    }
  }
};

/**
 * 网络请求状态检查
 * @returns {Promise<boolean>} 网络是否可用
 */
export function checkNetworkStatus() {
  return new Promise((resolve) => {
    wx.getNetworkType({
      success: (res) => {
        resolve(res.networkType !== 'none');
      },
      fail: () => {
        resolve(false);
      }
    });
  });
}

/**
 * 显示加载提示
 * @param {string} title - 提示文字
 * @param {boolean} mask - 是否显示透明蒙层
 */
export function showLoading(title = '加载中...', mask = true) {
  wx.showLoading({
    title,
    mask
  });
}

/**
 * 隐藏加载提示
 */
export function hideLoading() {
  wx.hideLoading();
}

/**
 * 显示成功提示
 * @param {string} title - 提示文字
 * @param {number} duration - 持续时间
 */
export function showSuccess(title, duration = 2000) {
  wx.showToast({
    title,
    icon: 'success',
    duration
  });
}

/**
 * 显示错误提示
 * @param {string} title - 提示文字
 * @param {number} duration - 持续时间
 */
export function showError(title, duration = 2000) {
  wx.showToast({
    title,
    icon: 'error',
    duration
  });
}

/**
 * 显示普通提示
 * @param {string} title - 提示文字
 * @param {number} duration - 持续时间
 */
export function showToast(title, duration = 2000) {
  wx.showToast({
    title,
    icon: 'none',
    duration
  });
}

/**
 * 确认对话框
 * @param {string} content - 内容
 * @param {string} title - 标题
 * @returns {Promise<boolean>} 用户是否确认
 */
export function showConfirm(content, title = '提示') {
  return new Promise((resolve) => {
    wx.showModal({
      title,
      content,
      success: (res) => {
        resolve(res.confirm);
      },
      fail: () => {
        resolve(false);
      }
    });
  });
}

// 默认导出所有工具函数
export default {
  formatTime,
  getRelativeTime,
  debounce,
  throttle,
  deepClone,
  generateId,
  formatFileSize,
  validatePhone,
  validateEmail,
  validateIdCard,
  getUrlParams,
  uniqueArray,
  groupBy,
  formatNumber,
  hexToRgba,
  getRandomColor,
  getDistance,
  storage,
  checkNetworkStatus,
  showLoading,
  hideLoading,
  showSuccess,
  showError,
  showToast,
  showConfirm
};