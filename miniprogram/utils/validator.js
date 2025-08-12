/**
 * 数据验证工具
 * 提供常用的数据验证方法和表单验证功能
 */

/**
 * 验证规则类型
 */
const RULE_TYPES = {
  REQUIRED: 'required',
  MIN_LENGTH: 'minLength',
  MAX_LENGTH: 'maxLength',
  PATTERN: 'pattern',
  EMAIL: 'email',
  PHONE: 'phone',
  ID_CARD: 'idCard',
  NUMBER: 'number',
  INTEGER: 'integer',
  MIN: 'min',
  MAX: 'max',
  CUSTOM: 'custom'
};

/**
 * 内置验证规则
 */
const BUILT_IN_RULES = {
  // 必填验证
  [RULE_TYPES.REQUIRED]: {
    validator: (value) => {
      if (typeof value === 'string') {
        return value.trim().length > 0;
      }
      return value !== null && value !== undefined && value !== '';
    },
    message: '此字段为必填项'
  },
  
  // 最小长度验证
  [RULE_TYPES.MIN_LENGTH]: {
    validator: (value, length) => {
      if (!value) return true; // 空值跳过验证
      return String(value).length >= length;
    },
    message: (length) => `最少需要${length}个字符`
  },
  
  // 最大长度验证
  [RULE_TYPES.MAX_LENGTH]: {
    validator: (value, length) => {
      if (!value) return true; // 空值跳过验证
      return String(value).length <= length;
    },
    message: (length) => `最多只能输入${length}个字符`
  },
  
  // 正则表达式验证
  [RULE_TYPES.PATTERN]: {
    validator: (value, pattern) => {
      if (!value) return true; // 空值跳过验证
      return pattern.test(String(value));
    },
    message: '格式不正确'
  },
  
  // 邮箱验证
  [RULE_TYPES.EMAIL]: {
    validator: (value) => {
      if (!value) return true; // 空值跳过验证
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailRegex.test(String(value));
    },
    message: '请输入有效的邮箱地址'
  },
  
  // 手机号验证
  [RULE_TYPES.PHONE]: {
    validator: (value) => {
      if (!value) return true; // 空值跳过验证
      const phoneRegex = /^1[3-9]\d{9}$/;
      return phoneRegex.test(String(value));
    },
    message: '请输入有效的手机号码'
  },
  
  // 身份证号验证
  [RULE_TYPES.ID_CARD]: {
    validator: (value) => {
      if (!value) return true; // 空值跳过验证
      const idCardRegex = /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/;
      return idCardRegex.test(String(value));
    },
    message: '请输入有效的身份证号码'
  },
  
  // 数字验证
  [RULE_TYPES.NUMBER]: {
    validator: (value) => {
      if (!value) return true; // 空值跳过验证
      return !isNaN(Number(value)) && isFinite(Number(value));
    },
    message: '请输入有效的数字'
  },
  
  // 整数验证
  [RULE_TYPES.INTEGER]: {
    validator: (value) => {
      if (!value) return true; // 空值跳过验证
      return Number.isInteger(Number(value));
    },
    message: '请输入整数'
  },
  
  // 最小值验证
  [RULE_TYPES.MIN]: {
    validator: (value, min) => {
      if (!value) return true; // 空值跳过验证
      return Number(value) >= min;
    },
    message: (min) => `值不能小于${min}`
  },
  
  // 最大值验证
  [RULE_TYPES.MAX]: {
    validator: (value, max) => {
      if (!value) return true; // 空值跳过验证
      return Number(value) <= max;
    },
    message: (max) => `值不能大于${max}`
  }
};

/**
 * 验证器类
 */
class Validator {
  constructor() {
    this.rules = { ...BUILT_IN_RULES };
  }
  
  /**
   * 添加自定义验证规则
   * @param {string} name - 规则名称
   * @param {Function} validator - 验证函数
   * @param {string|Function} message - 错误消息
   */
  addRule(name, validator, message) {
    this.rules[name] = {
      validator,
      message
    };
  }
  
  /**
   * 验证单个值
   * @param {any} value - 要验证的值
   * @param {Array} rules - 验证规则数组
   * @returns {object} 验证结果 { valid: boolean, message: string }
   */
  validate(value, rules) {
    if (!Array.isArray(rules)) {
      rules = [rules];
    }
    
    for (const rule of rules) {
      const result = this.validateRule(value, rule);
      if (!result.valid) {
        return result;
      }
    }
    
    return { valid: true, message: '' };
  }
  
  /**
   * 验证单个规则
   * @param {any} value - 要验证的值
   * @param {object} rule - 验证规则
   * @returns {object} 验证结果
   */
  validateRule(value, rule) {
    const { type, param, message, validator } = rule;
    
    let ruleConfig;
    let isValid;
    let errorMessage;
    
    if (validator) {
      // 自定义验证函数
      isValid = validator(value, param);
      errorMessage = message || '验证失败';
    } else if (this.rules[type]) {
      // 内置验证规则
      ruleConfig = this.rules[type];
      isValid = ruleConfig.validator(value, param);
      
      if (typeof ruleConfig.message === 'function') {
        errorMessage = message || ruleConfig.message(param);
      } else {
        errorMessage = message || ruleConfig.message;
      }
    } else {
      throw new Error(`未知的验证规则: ${type}`);
    }
    
    return {
      valid: isValid,
      message: isValid ? '' : errorMessage
    };
  }
  
  /**
   * 验证表单数据
   * @param {object} data - 表单数据
   * @param {object} schema - 验证模式
   * @returns {object} 验证结果 { valid: boolean, errors: object }
   */
  validateForm(data, schema) {
    const errors = {};
    let valid = true;
    
    for (const field in schema) {
      const fieldRules = schema[field];
      const fieldValue = data[field];
      
      const result = this.validate(fieldValue, fieldRules);
      
      if (!result.valid) {
        errors[field] = result.message;
        valid = false;
      }
    }
    
    return {
      valid,
      errors
    };
  }
  
  /**
   * 异步验证
   * @param {any} value - 要验证的值
   * @param {Array} rules - 验证规则数组
   * @returns {Promise} 验证结果
   */
  async validateAsync(value, rules) {
    if (!Array.isArray(rules)) {
      rules = [rules];
    }
    
    for (const rule of rules) {
      const result = await this.validateRuleAsync(value, rule);
      if (!result.valid) {
        return result;
      }
    }
    
    return { valid: true, message: '' };
  }
  
  /**
   * 异步验证单个规则
   * @param {any} value - 要验证的值
   * @param {object} rule - 验证规则
   * @returns {Promise} 验证结果
   */
  async validateRuleAsync(value, rule) {
    const { validator, message } = rule;
    
    if (validator && typeof validator === 'function') {
      try {
        const isValid = await validator(value);
        return {
          valid: isValid,
          message: isValid ? '' : (message || '验证失败')
        };
      } catch (error) {
        return {
          valid: false,
          message: error.message || '验证过程中发生错误'
        };
      }
    }
    
    // 如果不是异步验证函数，使用同步验证
    return this.validateRule(value, rule);
  }
}

// 创建默认验证器实例
const defaultValidator = new Validator();

/**
 * 快捷验证方法
 */

// 验证必填
export function required(message) {
  return {
    type: RULE_TYPES.REQUIRED,
    message
  };
}

// 验证最小长度
export function minLength(length, message) {
  return {
    type: RULE_TYPES.MIN_LENGTH,
    param: length,
    message
  };
}

// 验证最大长度
export function maxLength(length, message) {
  return {
    type: RULE_TYPES.MAX_LENGTH,
    param: length,
    message
  };
}

// 验证正则表达式
export function pattern(regex, message) {
  return {
    type: RULE_TYPES.PATTERN,
    param: regex,
    message
  };
}

// 验证邮箱
export function email(message) {
  return {
    type: RULE_TYPES.EMAIL,
    message
  };
}

// 验证手机号
export function phone(message) {
  return {
    type: RULE_TYPES.PHONE,
    message
  };
}

// 验证身份证号
export function idCard(message) {
  return {
    type: RULE_TYPES.ID_CARD,
    message
  };
}

// 验证数字
export function number(message) {
  return {
    type: RULE_TYPES.NUMBER,
    message
  };
}

// 验证整数
export function integer(message) {
  return {
    type: RULE_TYPES.INTEGER,
    message
  };
}

// 验证最小值
export function min(value, message) {
  return {
    type: RULE_TYPES.MIN,
    param: value,
    message
  };
}

// 验证最大值
export function max(value, message) {
  return {
    type: RULE_TYPES.MAX,
    param: value,
    message
  };
}

// 自定义验证
export function custom(validator, message) {
  return {
    type: RULE_TYPES.CUSTOM,
    validator,
    message
  };
}

/**
 * 常用验证组合
 */

// 用户名验证（4-20位字母数字下划线）
export function username(message) {
  return [
    required('请输入用户名'),
    pattern(/^[a-zA-Z0-9_]{4,20}$/, message || '用户名只能包含字母、数字和下划线，长度4-20位')
  ];
}

// 密码验证（6-20位，包含字母和数字）
export function password(message) {
  return [
    required('请输入密码'),
    pattern(/^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{6,20}$/, 
           message || '密码必须包含字母和数字，长度6-20位')
  ];
}

// 确认密码验证
export function confirmPassword(originalPassword, message) {
  return [
    required('请确认密码'),
    custom((value) => value === originalPassword, message || '两次输入的密码不一致')
  ];
}

// 中文姓名验证
export function chineseName(message) {
  return [
    required('请输入姓名'),
    pattern(/^[\u4e00-\u9fa5]{2,10}$/, message || '请输入2-10位中文姓名')
  ];
}

// 年龄验证
export function age(message) {
  return [
    required('请输入年龄'),
    integer('年龄必须是整数'),
    min(1, '年龄不能小于1岁'),
    max(150, '年龄不能大于150岁')
  ];
}

// 验证码验证（4-6位数字）
export function verifyCode(message) {
  return [
    required('请输入验证码'),
    pattern(/^\d{4,6}$/, message || '请输入4-6位数字验证码')
  ];
}

/**
 * 表单验证混入
 * 可以在页面中使用，提供表单验证功能
 */
export const formValidatorMixin = {
  data: {
    formErrors: {}, // 表单错误信息
    formValid: true // 表单是否有效
  },
  
  methods: {
    /**
     * 验证表单字段
     * @param {string} field - 字段名
     * @param {any} value - 字段值
     * @param {Array} rules - 验证规则
     */
    validateField(field, value, rules) {
      const result = defaultValidator.validate(value, rules);
      
      this.setData({
        [`formErrors.${field}`]: result.message,
        formValid: result.valid && this.isFormValid()
      });
      
      return result.valid;
    },
    
    /**
     * 验证整个表单
     * @param {object} data - 表单数据
     * @param {object} schema - 验证模式
     */
    validateForm(data, schema) {
      const result = defaultValidator.validateForm(data, schema);
      
      this.setData({
        formErrors: result.errors,
        formValid: result.valid
      });
      
      return result.valid;
    },
    
    /**
     * 清除字段错误
     * @param {string} field - 字段名
     */
    clearFieldError(field) {
      this.setData({
        [`formErrors.${field}`]: ''
      });
    },
    
    /**
     * 清除所有错误
     */
    clearAllErrors() {
      this.setData({
        formErrors: {},
        formValid: true
      });
    },
    
    /**
     * 检查表单是否有效
     */
    isFormValid() {
      const errors = this.data.formErrors || {};
      return Object.values(errors).every(error => !error);
    }
  }
};

// 导出验证器实例和相关方法
export { Validator, RULE_TYPES };
export default defaultValidator;