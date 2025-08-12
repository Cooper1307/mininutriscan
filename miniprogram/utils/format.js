/**
 * 数据格式化和转换工具
 * 提供各种数据格式转换、显示格式化、单位转换等功能
 */

/**
 * 时间格式化工具
 */
class TimeFormatter {
  /**
   * 格式化时间戳
   * @param {number|string|Date} timestamp - 时间戳
   * @param {string} format - 格式字符串
   */
  static format(timestamp, format = 'YYYY-MM-DD HH:mm:ss') {
    const date = new Date(timestamp);
    
    if (isNaN(date.getTime())) {
      return '无效时间';
    }
    
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hour = String(date.getHours()).padStart(2, '0');
    const minute = String(date.getMinutes()).padStart(2, '0');
    const second = String(date.getSeconds()).padStart(2, '0');
    const weekDay = ['日', '一', '二', '三', '四', '五', '六'][date.getDay()];
    
    return format
      .replace(/YYYY/g, year)
      .replace(/YY/g, String(year).slice(-2))
      .replace(/MM/g, month)
      .replace(/M/g, date.getMonth() + 1)
      .replace(/DD/g, day)
      .replace(/D/g, date.getDate())
      .replace(/HH/g, hour)
      .replace(/H/g, date.getHours())
      .replace(/mm/g, minute)
      .replace(/m/g, date.getMinutes())
      .replace(/ss/g, second)
      .replace(/s/g, date.getSeconds())
      .replace(/W/g, weekDay);
  }
  
  /**
   * 相对时间格式化
   * @param {number|string|Date} timestamp - 时间戳
   */
  static relative(timestamp) {
    const now = Date.now();
    const time = new Date(timestamp).getTime();
    const diff = now - time;
    
    if (diff < 0) {
      return '未来时间';
    }
    
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
   * 智能时间格式化
   * @param {number|string|Date} timestamp - 时间戳
   */
  static smart(timestamp) {
    const now = new Date();
    const date = new Date(timestamp);
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000);
    const dateOnly = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    
    if (dateOnly.getTime() === today.getTime()) {
      return `今天 ${this.format(timestamp, 'HH:mm')}`;
    } else if (dateOnly.getTime() === yesterday.getTime()) {
      return `昨天 ${this.format(timestamp, 'HH:mm')}`;
    } else if (date.getFullYear() === now.getFullYear()) {
      return this.format(timestamp, 'MM-DD HH:mm');
    } else {
      return this.format(timestamp, 'YYYY-MM-DD');
    }
  }
  
  /**
   * 持续时间格式化
   * @param {number} duration - 持续时间（毫秒）
   */
  static duration(duration) {
    if (duration < 0) return '0秒';
    
    const second = 1000;
    const minute = 60 * second;
    const hour = 60 * minute;
    const day = 24 * hour;
    
    const days = Math.floor(duration / day);
    const hours = Math.floor((duration % day) / hour);
    const minutes = Math.floor((duration % hour) / minute);
    const seconds = Math.floor((duration % minute) / second);
    
    const parts = [];
    if (days > 0) parts.push(`${days}天`);
    if (hours > 0) parts.push(`${hours}小时`);
    if (minutes > 0) parts.push(`${minutes}分钟`);
    if (seconds > 0 || parts.length === 0) parts.push(`${seconds}秒`);
    
    return parts.join('');
  }
}

/**
 * 数字格式化工具
 */
class NumberFormatter {
  /**
   * 格式化数字（添加千分位分隔符）
   * @param {number} num - 数字
   * @param {number} decimals - 小数位数
   */
  static format(num, decimals = 2) {
    if (isNaN(num)) return '0';
    
    const fixed = Number(num).toFixed(decimals);
    return fixed.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  }
  
  /**
   * 格式化百分比
   * @param {number} num - 数字（0-1之间）
   * @param {number} decimals - 小数位数
   */
  static percentage(num, decimals = 1) {
    if (isNaN(num)) return '0%';
    return `${(num * 100).toFixed(decimals)}%`;
  }
  
  /**
   * 格式化文件大小
   * @param {number} bytes - 字节数
   * @param {number} decimals - 小数位数
   */
  static fileSize(bytes, decimals = 2) {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(decimals))} ${sizes[i]}`;
  }
  
  /**
   * 格式化大数字（K, M, B）
   * @param {number} num - 数字
   * @param {number} decimals - 小数位数
   */
  static abbreviate(num, decimals = 1) {
    if (isNaN(num)) return '0';
    
    const absNum = Math.abs(num);
    const sign = num < 0 ? '-' : '';
    
    if (absNum >= 1e9) {
      return `${sign}${(absNum / 1e9).toFixed(decimals)}B`;
    } else if (absNum >= 1e6) {
      return `${sign}${(absNum / 1e6).toFixed(decimals)}M`;
    } else if (absNum >= 1e3) {
      return `${sign}${(absNum / 1e3).toFixed(decimals)}K`;
    } else {
      return `${sign}${absNum}`;
    }
  }
  
  /**
   * 格式化货币
   * @param {number} amount - 金额
   * @param {string} currency - 货币符号
   * @param {number} decimals - 小数位数
   */
  static currency(amount, currency = '¥', decimals = 2) {
    if (isNaN(amount)) return `${currency}0.00`;
    return `${currency}${this.format(amount, decimals)}`;
  }
  
  /**
   * 格式化评分
   * @param {number} rating - 评分
   * @param {number} maxRating - 最大评分
   */
  static rating(rating, maxRating = 5) {
    if (isNaN(rating)) return '0.0';
    const clampedRating = Math.max(0, Math.min(rating, maxRating));
    return clampedRating.toFixed(1);
  }
}

/**
 * 营养数据格式化工具
 */
class NutritionFormatter {
  /**
   * 格式化卡路里
   * @param {number} calories - 卡路里值
   */
  static calories(calories) {
    if (isNaN(calories)) return '0 kcal';
    return `${Math.round(calories)} kcal`;
  }
  
  /**
   * 格式化重量
   * @param {number} weight - 重量（克）
   * @param {string} unit - 单位
   */
  static weight(weight, unit = 'auto') {
    if (isNaN(weight)) return '0g';
    
    if (unit === 'auto') {
      if (weight >= 1000) {
        return `${(weight / 1000).toFixed(1)}kg`;
      } else {
        return `${Math.round(weight)}g`;
      }
    }
    
    switch (unit) {
      case 'kg':
        return `${(weight / 1000).toFixed(2)}kg`;
      case 'g':
      default:
        return `${Math.round(weight)}g`;
    }
  }
  
  /**
   * 格式化营养素含量
   * @param {number} amount - 含量
   * @param {string} unit - 单位
   */
  static nutrient(amount, unit = 'g') {
    if (isNaN(amount)) return `0${unit}`;
    
    if (unit === 'mg' && amount >= 1000) {
      return `${(amount / 1000).toFixed(1)}g`;
    } else if (unit === 'μg' && amount >= 1000) {
      return `${(amount / 1000).toFixed(1)}mg`;
    }
    
    const decimals = amount < 1 ? 2 : amount < 10 ? 1 : 0;
    return `${amount.toFixed(decimals)}${unit}`;
  }
  
  /**
   * 格式化营养密度
   * @param {number} nutrientPer100g - 每100g营养素含量
   * @param {string} unit - 单位
   */
  static density(nutrientPer100g, unit = 'g') {
    return `${this.nutrient(nutrientPer100g, unit)}/100g`;
  }
  
  /**
   * 格式化每日推荐摄入量百分比
   * @param {number} amount - 摄入量
   * @param {number} dv - 每日推荐值
   */
  static dailyValue(amount, dv) {
    if (isNaN(amount) || isNaN(dv) || dv === 0) return '0%';
    const percentage = (amount / dv) * 100;
    return `${Math.round(percentage)}%`;
  }
}

/**
 * 文本格式化工具
 */
class TextFormatter {
  /**
   * 截断文本
   * @param {string} text - 文本
   * @param {number} maxLength - 最大长度
   * @param {string} suffix - 后缀
   */
  static truncate(text, maxLength = 50, suffix = '...') {
    if (!text || text.length <= maxLength) return text || '';
    return text.substring(0, maxLength - suffix.length) + suffix;
  }
  
  /**
   * 首字母大写
   * @param {string} text - 文本
   */
  static capitalize(text) {
    if (!text) return '';
    return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
  }
  
  /**
   * 驼峰命名转换
   * @param {string} text - 文本
   */
  static camelCase(text) {
    if (!text) return '';
    return text
      .replace(/[-_\s]+(.)?/g, (_, char) => char ? char.toUpperCase() : '')
      .replace(/^[A-Z]/, char => char.toLowerCase());
  }
  
  /**
   * 短横线命名转换
   * @param {string} text - 文本
   */
  static kebabCase(text) {
    if (!text) return '';
    return text
      .replace(/([a-z])([A-Z])/g, '$1-$2')
      .replace(/[_\s]+/g, '-')
      .toLowerCase();
  }
  
  /**
   * 格式化手机号
   * @param {string} phone - 手机号
   */
  static phone(phone) {
    if (!phone) return '';
    const cleaned = phone.replace(/\D/g, '');
    if (cleaned.length === 11) {
      return cleaned.replace(/(\d{3})(\d{4})(\d{4})/, '$1 $2 $3');
    }
    return phone;
  }
  
  /**
   * 脱敏手机号
   * @param {string} phone - 手机号
   */
  static maskPhone(phone) {
    if (!phone) return '';
    const cleaned = phone.replace(/\D/g, '');
    if (cleaned.length === 11) {
      return cleaned.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2');
    }
    return phone;
  }
  
  /**
   * 脱敏身份证号
   * @param {string} idCard - 身份证号
   */
  static maskIdCard(idCard) {
    if (!idCard) return '';
    if (idCard.length === 18) {
      return idCard.replace(/(\d{6})\d{8}(\d{4})/, '$1********$2');
    } else if (idCard.length === 15) {
      return idCard.replace(/(\d{6})\d{6}(\d{3})/, '$1******$2');
    }
    return idCard;
  }
  
  /**
   * 高亮关键词
   * @param {string} text - 文本
   * @param {string} keyword - 关键词
   * @param {string} className - CSS类名
   */
  static highlight(text, keyword, className = 'highlight') {
    if (!text || !keyword) return text;
    const regex = new RegExp(`(${keyword})`, 'gi');
    return text.replace(regex, `<span class="${className}">$1</span>`);
  }
}

/**
 * 地址格式化工具
 */
class AddressFormatter {
  /**
   * 格式化完整地址
   * @param {object} address - 地址对象
   */
  static full(address) {
    if (!address) return '';
    
    const parts = [
      address.province,
      address.city,
      address.district,
      address.street,
      address.detail
    ].filter(Boolean);
    
    return parts.join('');
  }
  
  /**
   * 格式化简短地址
   * @param {object} address - 地址对象
   */
  static short(address) {
    if (!address) return '';
    
    // 如果城市和省份相同（如北京市、上海市），只显示城市
    if (address.province === address.city) {
      return `${address.city}${address.district || ''}`;
    }
    
    return `${address.city || address.province}${address.district || ''}`;
  }
  
  /**
   * 格式化距离
   * @param {number} distance - 距离（米）
   */
  static distance(distance) {
    if (isNaN(distance)) return '';
    
    if (distance < 1000) {
      return `${Math.round(distance)}m`;
    } else {
      return `${(distance / 1000).toFixed(1)}km`;
    }
  }
}

/**
 * 数据转换工具
 */
class DataConverter {
  /**
   * 对象转查询字符串
   * @param {object} obj - 对象
   */
  static objectToQuery(obj) {
    if (!obj || typeof obj !== 'object') return '';
    
    return Object.keys(obj)
      .filter(key => obj[key] !== null && obj[key] !== undefined && obj[key] !== '')
      .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(obj[key])}`)
      .join('&');
  }
  
  /**
   * 查询字符串转对象
   * @param {string} query - 查询字符串
   */
  static queryToObject(query) {
    if (!query) return {};
    
    const params = new URLSearchParams(query.startsWith('?') ? query.slice(1) : query);
    const result = {};
    
    for (const [key, value] of params) {
      result[key] = value;
    }
    
    return result;
  }
  
  /**
   * 数组转树形结构
   * @param {Array} array - 数组
   * @param {string} idKey - ID字段
   * @param {string} parentKey - 父级ID字段
   * @param {string} childrenKey - 子级字段
   */
  static arrayToTree(array, idKey = 'id', parentKey = 'parentId', childrenKey = 'children') {
    if (!Array.isArray(array)) return [];
    
    const map = {};
    const roots = [];
    
    // 创建映射
    array.forEach(item => {
      map[item[idKey]] = { ...item, [childrenKey]: [] };
    });
    
    // 构建树形结构
    array.forEach(item => {
      const node = map[item[idKey]];
      const parentId = item[parentKey];
      
      if (parentId && map[parentId]) {
        map[parentId][childrenKey].push(node);
      } else {
        roots.push(node);
      }
    });
    
    return roots;
  }
  
  /**
   * 树形结构转数组
   * @param {Array} tree - 树形数据
   * @param {string} childrenKey - 子级字段
   */
  static treeToArray(tree, childrenKey = 'children') {
    if (!Array.isArray(tree)) return [];
    
    const result = [];
    
    function traverse(nodes) {
      nodes.forEach(node => {
        const { [childrenKey]: children, ...item } = node;
        result.push(item);
        
        if (children && children.length > 0) {
          traverse(children);
        }
      });
    }
    
    traverse(tree);
    return result;
  }
}

/**
 * 格式化混入
 */
export const formatMixin = {
  methods: {
    // 时间格式化
    formatTime: TimeFormatter.format,
    formatRelativeTime: TimeFormatter.relative,
    formatSmartTime: TimeFormatter.smart,
    formatDuration: TimeFormatter.duration,
    
    // 数字格式化
    formatNumber: NumberFormatter.format,
    formatPercentage: NumberFormatter.percentage,
    formatFileSize: NumberFormatter.fileSize,
    formatCurrency: NumberFormatter.currency,
    
    // 营养格式化
    formatCalories: NutritionFormatter.calories,
    formatWeight: NutritionFormatter.weight,
    formatNutrient: NutritionFormatter.nutrient,
    
    // 文本格式化
    truncateText: TextFormatter.truncate,
    maskPhone: TextFormatter.maskPhone,
    
    // 地址格式化
    formatAddress: AddressFormatter.full,
    formatDistance: AddressFormatter.distance
  }
};

/**
 * 导出所有格式化函数
 */
export {
  TimeFormatter,
  NumberFormatter,
  NutritionFormatter,
  TextFormatter,
  AddressFormatter,
  DataConverter
};

// 便捷函数导出
export const formatTime = TimeFormatter.format;
export const formatRelativeTime = TimeFormatter.relative;
export const formatSmartTime = TimeFormatter.smart;
export const formatDuration = TimeFormatter.duration;

export const formatNumber = NumberFormatter.format;
export const formatPercentage = NumberFormatter.percentage;
export const formatFileSize = NumberFormatter.fileSize;
export const formatCurrency = NumberFormatter.currency;
export const abbreviateNumber = NumberFormatter.abbreviate;

export const formatCalories = NutritionFormatter.calories;
export const formatWeight = NutritionFormatter.weight;
export const formatNutrient = NutritionFormatter.nutrient;
export const formatDailyValue = NutritionFormatter.dailyValue;

export const truncateText = TextFormatter.truncate;
export const capitalizeText = TextFormatter.capitalize;
export const maskPhone = TextFormatter.maskPhone;
export const maskIdCard = TextFormatter.maskIdCard;
export const highlightText = TextFormatter.highlight;

export const formatAddress = AddressFormatter.full;
export const formatShortAddress = AddressFormatter.short;
export const formatDistance = AddressFormatter.distance;

export const objectToQuery = DataConverter.objectToQuery;
export const queryToObject = DataConverter.queryToObject;
export const arrayToTree = DataConverter.arrayToTree;
export const treeToArray = DataConverter.treeToArray;

export default {
  time: TimeFormatter,
  number: NumberFormatter,
  nutrition: NutritionFormatter,
  text: TextFormatter,
  address: AddressFormatter,
  data: DataConverter
};