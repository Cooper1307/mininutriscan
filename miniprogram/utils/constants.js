/**
 * 应用常量定义
 * 统一管理应用中使用的各种常量
 */

/**
 * 应用基本信息
 */
export const APP_INFO = {
  NAME: 'MiniNutriScan',
  VERSION: '1.0.0',
  DESCRIPTION: '智能营养扫描小程序',
  AUTHOR: 'NutriScan Team',
  COPYRIGHT: '© 2024 NutriScan. All rights reserved.'
};

/**
 * API相关常量
 */
export const API = {
  // 基础配置
  BASE_URL: 'https://api.nutriscan.com',
  TIMEOUT: 10000,
  RETRY_COUNT: 3,
  
  // 版本
  VERSION: 'v1',
  
  // 端点
  ENDPOINTS: {
    // 用户相关
    USER_LOGIN: '/auth/login',
    USER_REGISTER: '/auth/register',
    USER_PROFILE: '/user/profile',
    USER_PREFERENCES: '/user/preferences',
    
    // 食品相关
    FOOD_SEARCH: '/food/search',
    FOOD_DETAIL: '/food/detail',
    FOOD_NUTRITION: '/food/nutrition',
    FOOD_BARCODE: '/food/barcode',
    
    // 扫码相关
    SCAN_ANALYZE: '/scan/analyze',
    SCAN_HISTORY: '/scan/history',
    
    // 图片识别
    IMAGE_RECOGNIZE: '/image/recognize',
    IMAGE_UPLOAD: '/image/upload',
    
    // 营养分析
    NUTRITION_ANALYZE: '/nutrition/analyze',
    NUTRITION_REPORT: '/nutrition/report',
    
    // 食谱相关
    RECIPE_LIST: '/recipe/list',
    RECIPE_DETAIL: '/recipe/detail',
    RECIPE_RECOMMEND: '/recipe/recommend',
    
    // 百科相关
    ENCYCLOPEDIA_LIST: '/encyclopedia/list',
    ENCYCLOPEDIA_DETAIL: '/encyclopedia/detail',
    ENCYCLOPEDIA_SEARCH: '/encyclopedia/search',
    
    // 反馈相关
    FEEDBACK_SUBMIT: '/feedback/submit',
    FEEDBACK_LIST: '/feedback/list',
    
    // 帮助相关
    HELP_FAQ: '/help/faq',
    HELP_CATEGORIES: '/help/categories',
    HELP_SEARCH: '/help/search'
  }
};

/**
 * 存储键名常量
 */
export const STORAGE_KEYS = {
  // 用户相关
  USER_TOKEN: 'userToken',
  USER_INFO: 'userInfo',
  USER_PREFERENCES: 'userPreferences',
  
  // 应用设置
  APP_SETTINGS: 'appSettings',
  THEME_MODE: 'themeMode',
  LANGUAGE: 'language',
  
  // 缓存数据
  FOOD_CACHE: 'foodCache',
  SEARCH_HISTORY: 'searchHistory',
  SCAN_HISTORY: 'scanHistory',
  
  // 设备信息
  DEVICE_ID: 'deviceId',
  DEVICE_INFO: 'deviceInfo',
  
  // 权限相关
  PERMISSION_CACHE: 'permissionCache',
  
  // 其他
  FIRST_LAUNCH: 'firstLaunch',
  LAST_UPDATE_CHECK: 'lastUpdateCheck'
};

/**
 * 页面路径常量
 */
export const PAGES = {
  // 主要页面
  INDEX: '/pages/index/index',
  SCAN: '/pages/scan/scan',
  RESULT: '/pages/result/result',
  PROFILE: '/pages/profile/profile',
  
  // 功能页面
  SEARCH: '/pages/search/search',
  HISTORY: '/pages/history/history',
  FAVORITES: '/pages/favorites/favorites',
  SETTINGS: '/pages/settings/settings',
  
  // 内容页面
  FOOD_DETAIL: '/pages/food-detail/food-detail',
  NUTRITION_REPORT: '/pages/nutrition-report/nutrition-report',
  RECIPE_LIST: '/pages/recipe-list/recipe-list',
  RECIPE_DETAIL: '/pages/recipe-detail/recipe-detail',
  ENCYCLOPEDIA: '/pages/encyclopedia/encyclopedia',
  
  // 帮助页面
  HELP: '/pages/help/help',
  ABOUT: '/pages/about/about',
  FEEDBACK: '/pages/feedback/feedback',
  
  // 其他页面
  WEBVIEW: '/pages/webview/webview',
  ERROR: '/pages/error/error'
};

/**
 * 事件名称常量
 */
export const EVENTS = {
  // 用户事件
  USER_LOGIN: 'user:login',
  USER_LOGOUT: 'user:logout',
  USER_UPDATE: 'user:update',
  
  // 扫码事件
  SCAN_SUCCESS: 'scan:success',
  SCAN_FAILED: 'scan:failed',
  SCAN_CANCEL: 'scan:cancel',
  
  // 网络事件
  NETWORK_CHANGE: 'network:change',
  NETWORK_ERROR: 'network:error',
  
  // 数据事件
  DATA_UPDATE: 'data:update',
  DATA_SYNC: 'data:sync',
  
  // 主题事件
  THEME_CHANGE: 'theme:change',
  
  // 权限事件
  PERMISSION_GRANTED: 'permission:granted',
  PERMISSION_DENIED: 'permission:denied'
};

/**
 * 营养素相关常量
 */
export const NUTRITION = {
  // 宏量营养素
  MACRONUTRIENTS: {
    ENERGY: 'energy',           // 能量
    PROTEIN: 'protein',         // 蛋白质
    FAT: 'fat',                // 脂肪
    CARBOHYDRATE: 'carbohydrate', // 碳水化合物
    FIBER: 'fiber',            // 膳食纤维
    SUGAR: 'sugar'             // 糖
  },
  
  // 微量营养素
  MICRONUTRIENTS: {
    VITAMIN_A: 'vitaminA',      // 维生素A
    VITAMIN_B1: 'vitaminB1',    // 维生素B1
    VITAMIN_B2: 'vitaminB2',    // 维生素B2
    VITAMIN_B6: 'vitaminB6',    // 维生素B6
    VITAMIN_B12: 'vitaminB12',  // 维生素B12
    VITAMIN_C: 'vitaminC',      // 维生素C
    VITAMIN_D: 'vitaminD',      // 维生素D
    VITAMIN_E: 'vitaminE',      // 维生素E
    VITAMIN_K: 'vitaminK',      // 维生素K
    FOLATE: 'folate',          // 叶酸
    NIACIN: 'niacin',          // 烟酸
    CALCIUM: 'calcium',        // 钙
    IRON: 'iron',              // 铁
    MAGNESIUM: 'magnesium',    // 镁
    PHOSPHORUS: 'phosphorus',  // 磷
    POTASSIUM: 'potassium',    // 钾
    SODIUM: 'sodium',          // 钠
    ZINC: 'zinc',              // 锌
    SELENIUM: 'selenium'       // 硒
  },
  
  // 单位
  UNITS: {
    KCAL: 'kcal',
    KJ: 'kJ',
    G: 'g',
    MG: 'mg',
    UG: 'μg',
    IU: 'IU'
  },
  
  // 每日推荐摄入量（成人）
  DRV: {
    ENERGY: 2000,              // kcal
    PROTEIN: 60,               // g
    FAT: 67,                   // g
    CARBOHYDRATE: 300,         // g
    FIBER: 25,                 // g
    VITAMIN_C: 100,            // mg
    CALCIUM: 800,              // mg
    IRON: 15,                  // mg
    SODIUM: 2300               // mg
  }
};

/**
 * 食品分类常量
 */
export const FOOD_CATEGORIES = {
  GRAINS: 'grains',              // 谷物类
  VEGETABLES: 'vegetables',       // 蔬菜类
  FRUITS: 'fruits',              // 水果类
  MEAT: 'meat',                  // 肉类
  POULTRY: 'poultry',           // 禽类
  SEAFOOD: 'seafood',           // 海鲜类
  DAIRY: 'dairy',               // 乳制品
  EGGS: 'eggs',                 // 蛋类
  NUTS: 'nuts',                 // 坚果类
  LEGUMES: 'legumes',           // 豆类
  OILS: 'oils',                 // 油脂类
  BEVERAGES: 'beverages',       // 饮料类
  SNACKS: 'snacks',             // 零食类
  CONDIMENTS: 'condiments',     // 调料类
  PROCESSED: 'processed'        // 加工食品
};

/**
 * 健康等级常量
 */
export const HEALTH_LEVELS = {
  EXCELLENT: {
    level: 5,
    name: '优秀',
    color: '#52c41a',
    description: '营养均衡，非常健康'
  },
  GOOD: {
    level: 4,
    name: '良好',
    color: '#73d13d',
    description: '营养较好，建议保持'
  },
  FAIR: {
    level: 3,
    name: '一般',
    color: '#faad14',
    description: '营养一般，可以改善'
  },
  POOR: {
    level: 2,
    name: '较差',
    color: '#ff7875',
    description: '营养不佳，需要调整'
  },
  BAD: {
    level: 1,
    name: '很差',
    color: '#ff4d4f',
    description: '营养很差，建议避免'
  }
};

/**
 * 扫码类型常量
 */
export const SCAN_TYPES = {
  BARCODE: 'barcode',           // 条形码
  QR_CODE: 'qrcode',           // 二维码
  DATA_MATRIX: 'datamatrix',   // 数据矩阵码
  PDF417: 'pdf417'             // PDF417码
};

/**
 * 图片相关常量
 */
export const IMAGE = {
  // 最大尺寸
  MAX_SIZE: 5 * 1024 * 1024,   // 5MB
  
  // 压缩质量
  QUALITY: {
    HIGH: 0.9,
    MEDIUM: 0.7,
    LOW: 0.5
  },
  
  // 支持格式
  FORMATS: ['jpg', 'jpeg', 'png', 'webp'],
  
  // 默认尺寸
  DEFAULT_SIZE: {
    WIDTH: 750,
    HEIGHT: 750
  }
};

/**
 * 错误码常量
 */
export const ERROR_CODES = {
  // 网络错误
  NETWORK_ERROR: 'NETWORK_ERROR',
  TIMEOUT_ERROR: 'TIMEOUT_ERROR',
  
  // 权限错误
  PERMISSION_DENIED: 'PERMISSION_DENIED',
  CAMERA_PERMISSION_DENIED: 'CAMERA_PERMISSION_DENIED',
  LOCATION_PERMISSION_DENIED: 'LOCATION_PERMISSION_DENIED',
  
  // 业务错误
  SCAN_FAILED: 'SCAN_FAILED',
  RECOGNITION_FAILED: 'RECOGNITION_FAILED',
  FOOD_NOT_FOUND: 'FOOD_NOT_FOUND',
  
  // 系统错误
  SYSTEM_ERROR: 'SYSTEM_ERROR',
  UNKNOWN_ERROR: 'UNKNOWN_ERROR'
};

/**
 * 主题相关常量
 */
export const THEME = {
  LIGHT: 'light',
  DARK: 'dark',
  AUTO: 'auto'
};

/**
 * 语言相关常量
 */
export const LANGUAGES = {
  ZH_CN: 'zh-CN',              // 简体中文
  ZH_TW: 'zh-TW',              // 繁体中文
  EN_US: 'en-US',              // 英语
  JA_JP: 'ja-JP',              // 日语
  KO_KR: 'ko-KR'               // 韩语
};

/**
 * 动画相关常量
 */
export const ANIMATION = {
  DURATION: {
    FAST: 200,
    NORMAL: 300,
    SLOW: 500
  },
  
  EASING: {
    EASE: 'ease',
    EASE_IN: 'ease-in',
    EASE_OUT: 'ease-out',
    EASE_IN_OUT: 'ease-in-out',
    LINEAR: 'linear'
  }
};

/**
 * 正则表达式常量
 */
export const REGEX = {
  // 手机号
  PHONE: /^1[3-9]\d{9}$/,
  
  // 邮箱
  EMAIL: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
  
  // 身份证号
  ID_CARD: /^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$/,
  
  // 中文字符
  CHINESE: /[\u4e00-\u9fa5]/,
  
  // 数字
  NUMBER: /^\d+$/,
  
  // 小数
  DECIMAL: /^\d+(\.\d+)?$/,
  
  // URL
  URL: /^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$/
};

/**
 * 默认配置常量
 */
export const DEFAULTS = {
  // 分页
  PAGE_SIZE: 20,
  
  // 搜索
  SEARCH_DELAY: 500,           // 搜索防抖延迟
  
  // 缓存
  CACHE_EXPIRE: 24 * 60 * 60 * 1000, // 24小时
  
  // 重试
  RETRY_DELAY: 1000,           // 重试延迟
  
  // 图片
  IMAGE_QUALITY: 0.8,          // 图片质量
  
  // 定位
  LOCATION_TIMEOUT: 10000      // 定位超时
};

/**
 * 颜色常量
 */
export const COLORS = {
  // 主色调
  PRIMARY: '#1890ff',
  PRIMARY_LIGHT: '#40a9ff',
  PRIMARY_DARK: '#096dd9',
  
  // 辅助色
  SUCCESS: '#52c41a',
  WARNING: '#faad14',
  ERROR: '#ff4d4f',
  INFO: '#1890ff',
  
  // 中性色
  WHITE: '#ffffff',
  BLACK: '#000000',
  GRAY_1: '#f5f5f5',
  GRAY_2: '#e8e8e8',
  GRAY_3: '#d9d9d9',
  GRAY_4: '#bfbfbf',
  GRAY_5: '#8c8c8c',
  GRAY_6: '#595959',
  GRAY_7: '#434343',
  GRAY_8: '#262626',
  GRAY_9: '#1f1f1f',
  
  // 营养素颜色
  PROTEIN: '#ff6b6b',          // 蛋白质
  CARBOHYDRATE: '#4ecdc4',     // 碳水化合物
  FAT: '#ffe66d',              // 脂肪
  FIBER: '#95e1d3',            // 膳食纤维
  VITAMIN: '#a8e6cf',          // 维生素
  MINERAL: '#ffd93d'           // 矿物质
};

/**
 * 尺寸常量
 */
export const SIZES = {
  // 字体大小
  FONT: {
    MINI: 10,
    SMALL: 12,
    NORMAL: 14,
    MEDIUM: 16,
    LARGE: 18,
    XLARGE: 20,
    XXLARGE: 24
  },
  
  // 间距
  SPACING: {
    MINI: 4,
    SMALL: 8,
    NORMAL: 12,
    MEDIUM: 16,
    LARGE: 20,
    XLARGE: 24,
    XXLARGE: 32
  },
  
  // 圆角
  RADIUS: {
    SMALL: 4,
    NORMAL: 8,
    MEDIUM: 12,
    LARGE: 16,
    ROUND: 50
  },
  
  // 图标大小
  ICON: {
    SMALL: 16,
    NORMAL: 20,
    MEDIUM: 24,
    LARGE: 32,
    XLARGE: 48
  }
};

/**
 * 导出所有常量
 */
export default {
  APP_INFO,
  API,
  STORAGE_KEYS,
  PAGES,
  EVENTS,
  NUTRITION,
  FOOD_CATEGORIES,
  HEALTH_LEVELS,
  SCAN_TYPES,
  IMAGE,
  ERROR_CODES,
  THEME,
  LANGUAGES,
  ANIMATION,
  REGEX,
  DEFAULTS,
  COLORS,
  SIZES
};