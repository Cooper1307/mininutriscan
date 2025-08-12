/**
 * API请求工具
 * 统一管理网络请求，提供请求拦截、响应处理、错误处理等功能
 */

import { showLoading, hideLoading, showError, checkNetworkStatus } from './util.js';

// API配置
const API_CONFIG = {
  // 基础URL（开发环境）
  BASE_URL_DEV: 'https://dev-api.nutriscan.com',
  // 基础URL（生产环境）
  BASE_URL_PROD: 'https://api.nutriscan.com',
  // 请求超时时间
  TIMEOUT: 10000,
  // 重试次数
  RETRY_COUNT: 3,
  // 重试间隔（毫秒）
  RETRY_DELAY: 1000
};

// 获取当前环境的基础URL
function getBaseUrl() {
  // 可以根据环境变量或其他方式判断
  const accountInfo = wx.getAccountInfoSync();
  const envVersion = accountInfo.miniProgram.envVersion;
  
  return envVersion === 'release' ? API_CONFIG.BASE_URL_PROD : API_CONFIG.BASE_URL_DEV;
}

// 请求拦截器
function requestInterceptor(config) {
  // 添加通用请求头
  config.header = {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
    ...config.header
  };
  
  // 添加用户token
  const token = wx.getStorageSync('userToken');
  if (token) {
    config.header['Authorization'] = `Bearer ${token}`;
  }
  
  // 添加设备信息
  const systemInfo = wx.getSystemInfoSync();
  config.header['X-Device-Info'] = JSON.stringify({
    platform: systemInfo.platform,
    version: systemInfo.version,
    model: systemInfo.model
  });
  
  return config;
}

// 响应拦截器
function responseInterceptor(response, config) {
  const { data, statusCode } = response;
  
  // HTTP状态码检查
  if (statusCode >= 200 && statusCode < 300) {
    // 业务状态码检查
    if (data.code === 0 || data.success) {
      return Promise.resolve(data.data || data);
    } else {
      // 业务错误处理
      const error = new Error(data.message || '请求失败');
      error.code = data.code;
      error.data = data;
      return Promise.reject(error);
    }
  } else {
    // HTTP错误处理
    let errorMessage = '网络请求失败';
    
    switch (statusCode) {
      case 400:
        errorMessage = '请求参数错误';
        break;
      case 401:
        errorMessage = '未授权，请重新登录';
        // 清除token并跳转到登录页
        wx.removeStorageSync('userToken');
        wx.navigateTo({
          url: '/pages/login/login'
        });
        break;
      case 403:
        errorMessage = '拒绝访问';
        break;
      case 404:
        errorMessage = '请求地址不存在';
        break;
      case 500:
        errorMessage = '服务器内部错误';
        break;
      case 502:
        errorMessage = '网关错误';
        break;
      case 503:
        errorMessage = '服务不可用';
        break;
      case 504:
        errorMessage = '网关超时';
        break;
      default:
        errorMessage = `请求失败 (${statusCode})`;
    }
    
    const error = new Error(errorMessage);
    error.statusCode = statusCode;
    error.data = data;
    return Promise.reject(error);
  }
}

// 错误处理
function handleError(error, config) {
  console.error('API请求错误:', error);
  
  // 网络错误
  if (error.errMsg) {
    if (error.errMsg.includes('timeout')) {
      error.message = '请求超时，请检查网络连接';
    } else if (error.errMsg.includes('fail')) {
      error.message = '网络连接失败，请检查网络设置';
    }
  }
  
  // 显示错误提示（如果配置了显示）
  if (config.showError !== false) {
    showError(error.message || '请求失败');
  }
  
  return Promise.reject(error);
}

// 基础请求方法
function request(config) {
  return new Promise(async (resolve, reject) => {
    // 检查网络状态
    const isNetworkAvailable = await checkNetworkStatus();
    if (!isNetworkAvailable) {
      const error = new Error('网络不可用，请检查网络连接');
      if (config.showError !== false) {
        showError(error.message);
      }
      reject(error);
      return;
    }
    
    // 显示加载提示
    if (config.showLoading !== false) {
      showLoading(config.loadingText || '请求中...');
    }
    
    // 请求拦截
    config = requestInterceptor(config);
    
    // 构建完整URL
    const url = config.url.startsWith('http') ? config.url : getBaseUrl() + config.url;
    
    // 发起请求
    wx.request({
      url,
      method: config.method || 'GET',
      data: config.data,
      header: config.header,
      timeout: config.timeout || API_CONFIG.TIMEOUT,
      success: (response) => {
        // 隐藏加载提示
        if (config.showLoading !== false) {
          hideLoading();
        }
        
        // 响应拦截
        responseInterceptor(response, config)
          .then(resolve)
          .catch(reject);
      },
      fail: (error) => {
        // 隐藏加载提示
        if (config.showLoading !== false) {
          hideLoading();
        }
        
        // 错误处理
        handleError(error, config).catch(reject);
      }
    });
  });
}

// 带重试的请求方法
function requestWithRetry(config, retryCount = 0) {
  return request(config).catch(error => {
    // 如果是网络错误且还有重试次数
    if (retryCount < API_CONFIG.RETRY_COUNT && 
        (error.errMsg?.includes('timeout') || error.errMsg?.includes('fail'))) {
      
      console.log(`请求失败，${API_CONFIG.RETRY_DELAY}ms后进行第${retryCount + 1}次重试`);
      
      return new Promise(resolve => {
        setTimeout(() => {
          resolve(requestWithRetry(config, retryCount + 1));
        }, API_CONFIG.RETRY_DELAY);
      });
    }
    
    return Promise.reject(error);
  });
}

// GET请求
export function get(url, params = {}, config = {}) {
  return requestWithRetry({
    url,
    method: 'GET',
    data: params,
    ...config
  });
}

// POST请求
export function post(url, data = {}, config = {}) {
  return requestWithRetry({
    url,
    method: 'POST',
    data,
    ...config
  });
}

// PUT请求
export function put(url, data = {}, config = {}) {
  return requestWithRetry({
    url,
    method: 'PUT',
    data,
    ...config
  });
}

// DELETE请求
export function del(url, params = {}, config = {}) {
  return requestWithRetry({
    url,
    method: 'DELETE',
    data: params,
    ...config
  });
}

// 文件上传
export function upload(url, filePath, formData = {}, config = {}) {
  return new Promise((resolve, reject) => {
    // 显示加载提示
    if (config.showLoading !== false) {
      showLoading(config.loadingText || '上传中...');
    }
    
    // 添加认证头
    const header = {
      ...config.header
    };
    
    const token = wx.getStorageSync('userToken');
    if (token) {
      header['Authorization'] = `Bearer ${token}`;
    }
    
    // 构建完整URL
    const fullUrl = url.startsWith('http') ? url : getBaseUrl() + url;
    
    wx.uploadFile({
      url: fullUrl,
      filePath,
      name: config.name || 'file',
      formData,
      header,
      success: (response) => {
        // 隐藏加载提示
        if (config.showLoading !== false) {
          hideLoading();
        }
        
        try {
          const data = JSON.parse(response.data);
          if (data.code === 0 || data.success) {
            resolve(data.data || data);
          } else {
            const error = new Error(data.message || '上传失败');
            error.code = data.code;
            error.data = data;
            reject(error);
          }
        } catch (e) {
          reject(new Error('响应数据解析失败'));
        }
      },
      fail: (error) => {
        // 隐藏加载提示
        if (config.showLoading !== false) {
          hideLoading();
        }
        
        handleError(error, config).catch(reject);
      }
    });
  });
}

// 文件下载
export function download(url, config = {}) {
  return new Promise((resolve, reject) => {
    // 显示加载提示
    if (config.showLoading !== false) {
      showLoading(config.loadingText || '下载中...');
    }
    
    // 添加认证头
    const header = {
      ...config.header
    };
    
    const token = wx.getStorageSync('userToken');
    if (token) {
      header['Authorization'] = `Bearer ${token}`;
    }
    
    // 构建完整URL
    const fullUrl = url.startsWith('http') ? url : getBaseUrl() + url;
    
    wx.downloadFile({
      url: fullUrl,
      header,
      success: (response) => {
        // 隐藏加载提示
        if (config.showLoading !== false) {
          hideLoading();
        }
        
        if (response.statusCode === 200) {
          resolve(response.tempFilePath);
        } else {
          reject(new Error('下载失败'));
        }
      },
      fail: (error) => {
        // 隐藏加载提示
        if (config.showLoading !== false) {
          hideLoading();
        }
        
        handleError(error, config).catch(reject);
      }
    });
  });
}

// 批量请求
export function all(requests) {
  return Promise.all(requests);
}

// 竞速请求（返回最快的结果）
export function race(requests) {
  return Promise.race(requests);
}

// 设置全局配置
export function setConfig(config) {
  Object.assign(API_CONFIG, config);
}

// 获取配置
export function getConfig() {
  return { ...API_CONFIG };
}

// 默认导出
export default {
  get,
  post,
  put,
  del,
  upload,
  download,
  all,
  race,
  setConfig,
  getConfig,
  request: requestWithRetry
};