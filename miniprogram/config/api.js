// miniprogram/config/api.js
// API配置文件 - 统一管理所有API地址

/**
 * API配置说明:
 * 1. 开发环境: 本地FastAPI服务器地址
 * 2. 生产环境: 部署后的服务器地址
 * 3. 请根据实际情况修改BASE_URL
 */

// 环境配置
const ENV = {
  // 开发环境 (本地开发时使用)
  development: {
    BASE_URL: 'http://127.0.0.1:8000',
    API_VERSION: '/api/v1'
  },
  
  // 生产环境 (部署后使用)
  production: {
    BASE_URL: 'https://your-domain.com',  // 请替换为实际域名
    API_VERSION: '/api/v1'
  }
}

// 当前环境 (请根据需要修改)
// 开发时设置为 'development'
// 部署时设置为 'production'
const CURRENT_ENV = 'development'

// 获取当前环境配置
const config = ENV[CURRENT_ENV]

// API地址配置
const API_CONFIG = {
  // 基础配置
  BASE_URL: config.BASE_URL,
  API_VERSION: config.API_VERSION,
  
  // 完整API地址
  API_BASE: config.BASE_URL + config.API_VERSION,
  
  // 具体接口地址
  ENDPOINTS: {
    // 用户认证相关
    AUTH: {
      LOGIN: '/auth/login',
      REGISTER: '/auth/register',
      REFRESH: '/auth/refresh',
      LOGOUT: '/auth/logout'
    },
    
    // 用户管理相关
    USERS: {
      PROFILE: '/users/profile',
      UPDATE: '/users/update',
      AVATAR: '/users/avatar'
    },
    
    // 营养检测相关
    DETECTION: {
      UPLOAD_IMAGE: '/detection/upload-image',
      MANUAL_INPUT: '/detection/manual-input',
      BARCODE: '/detection/barcode',
      HISTORY: '/detection/history',
      DETAIL: '/detection',  // + /{id}
      FEEDBACK: '/detection'  // + /{id}/feedback
    },
    
    // 营养报告相关
    REPORTS: {
      LIST: '/reports',
      DETAIL: '/reports',  // + /{id}
      EXPORT: '/reports',  // + /{id}/export
      SHARE: '/reports'    // + /{id}/share
    },
    
    // 教育内容相关
    EDUCATION: {
      ARTICLES: '/education/articles',
      CATEGORIES: '/education/categories',
      SEARCH: '/education/search',
      DETAIL: '/education/articles'  // + /{id}
    },
    
    // 志愿者服务相关
    VOLUNTEERS: {
      REGISTER: '/volunteers/register',
      TASKS: '/volunteers/tasks',
      REPORTS: '/volunteers/reports',
      STATISTICS: '/volunteers/statistics'
    }
  },
  
  // 请求配置
  REQUEST_CONFIG: {
    timeout: 10000,  // 请求超时时间 (毫秒)
    header: {
      'Content-Type': 'application/json'
    }
  }
}

/**
 * 获取完整的API地址
 * @param {string} endpoint - 接口路径
 * @returns {string} 完整的API地址
 */
function getApiUrl(endpoint) {
  return API_CONFIG.API_BASE + endpoint
}

/**
 * 获取特定模块的API地址
 * @param {string} module - 模块名 (如: 'AUTH', 'DETECTION')
 * @param {string} action - 操作名 (如: 'LOGIN', 'UPLOAD_IMAGE')
 * @returns {string} 完整的API地址
 */
function getModuleApiUrl(module, action) {
  const endpoint = API_CONFIG.ENDPOINTS[module][action]
  return getApiUrl(endpoint)
}

/**
 * 构建带参数的API地址
 * @param {string} baseEndpoint - 基础接口路径
 * @param {string|number} param - 参数值
 * @returns {string} 完整的API地址
 */
function getApiUrlWithParam(baseEndpoint, param) {
  return getApiUrl(baseEndpoint + '/' + param)
}

// 导出配置
module.exports = {
  API_CONFIG,
  getApiUrl,
  getModuleApiUrl,
  getApiUrlWithParam,
  
  // 常用API地址 (便于直接使用)
  API_URLS: {
    // 认证
    LOGIN: getModuleApiUrl('AUTH', 'LOGIN'),
    REGISTER: getModuleApiUrl('AUTH', 'REGISTER'),
    
    // 检测
    UPLOAD_IMAGE: getModuleApiUrl('DETECTION', 'UPLOAD_IMAGE'),
    DETECTION_HISTORY: getModuleApiUrl('DETECTION', 'HISTORY'),
    
    // 用户
    USER_PROFILE: getModuleApiUrl('USERS', 'PROFILE'),
    
    // 教育内容
    EDUCATION_ARTICLES: getModuleApiUrl('EDUCATION', 'ARTICLES')
  }
}

/**
 * 使用示例:
 * 
 * // 方式1: 直接使用预定义的URL
 * const { API_URLS } = require('./config/api')
 * wx.request({
 *   url: API_URLS.LOGIN,
 *   method: 'POST',
 *   data: { username, password }
 * })
 * 
 * // 方式2: 动态构建URL
 * const { getModuleApiUrl } = require('./config/api')
 * const url = getModuleApiUrl('DETECTION', 'UPLOAD_IMAGE')
 * 
 * // 方式3: 带参数的URL
 * const { getApiUrlWithParam } = require('./config/api')
 * const url = getApiUrlWithParam('/detection', detectionId)
 */