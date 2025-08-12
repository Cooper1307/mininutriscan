/**
 * 缓存管理工具
 * 提供数据缓存、图片缓存、离线数据管理等功能
 */

/**
 * 缓存类型枚举
 */
const CACHE_TYPE = {
  MEMORY: 'memory',     // 内存缓存
  STORAGE: 'storage',   // 本地存储缓存
  FILE: 'file'          // 文件缓存
};

/**
 * 缓存策略枚举
 */
const CACHE_STRATEGY = {
  LRU: 'lru',           // 最近最少使用
  LFU: 'lfu',           // 最少使用频率
  FIFO: 'fifo',         // 先进先出
  TTL: 'ttl'            // 生存时间
};

/**
 * 内存缓存管理器
 */
class MemoryCache {
  constructor(options = {}) {
    this.maxSize = options.maxSize || 100;
    this.strategy = options.strategy || CACHE_STRATEGY.LRU;
    this.defaultTTL = options.defaultTTL || 30 * 60 * 1000; // 30分钟
    
    this.cache = new Map();
    this.accessTimes = new Map();
    this.accessCounts = new Map();
    this.timers = new Map();
  }
  
  /**
   * 设置缓存
   * @param {string} key - 缓存键
   * @param {any} value - 缓存值
   * @param {number} ttl - 生存时间（毫秒）
   */
  set(key, value, ttl = this.defaultTTL) {
    // 如果缓存已满，根据策略清理
    if (this.cache.size >= this.maxSize && !this.cache.has(key)) {
      this.evict();
    }
    
    // 清除旧的定时器
    if (this.timers.has(key)) {
      clearTimeout(this.timers.get(key));
    }
    
    // 设置缓存
    this.cache.set(key, value);
    this.accessTimes.set(key, Date.now());
    this.accessCounts.set(key, (this.accessCounts.get(key) || 0) + 1);
    
    // 设置TTL定时器
    if (ttl > 0) {
      const timer = setTimeout(() => {
        this.delete(key);
      }, ttl);
      this.timers.set(key, timer);
    }
    
    return this;
  }
  
  /**
   * 获取缓存
   * @param {string} key - 缓存键
   */
  get(key) {
    if (!this.cache.has(key)) {
      return undefined;
    }
    
    // 更新访问信息
    this.accessTimes.set(key, Date.now());
    this.accessCounts.set(key, (this.accessCounts.get(key) || 0) + 1);
    
    return this.cache.get(key);
  }
  
  /**
   * 检查缓存是否存在
   * @param {string} key - 缓存键
   */
  has(key) {
    return this.cache.has(key);
  }
  
  /**
   * 删除缓存
   * @param {string} key - 缓存键
   */
  delete(key) {
    if (this.timers.has(key)) {
      clearTimeout(this.timers.get(key));
      this.timers.delete(key);
    }
    
    this.cache.delete(key);
    this.accessTimes.delete(key);
    this.accessCounts.delete(key);
    
    return this;
  }
  
  /**
   * 清空缓存
   */
  clear() {
    // 清除所有定时器
    for (const timer of this.timers.values()) {
      clearTimeout(timer);
    }
    
    this.cache.clear();
    this.accessTimes.clear();
    this.accessCounts.clear();
    this.timers.clear();
    
    return this;
  }
  
  /**
   * 根据策略清理缓存
   */
  evict() {
    if (this.cache.size === 0) return;
    
    let keyToEvict;
    
    switch (this.strategy) {
      case CACHE_STRATEGY.LRU:
        keyToEvict = this.getLRUKey();
        break;
      case CACHE_STRATEGY.LFU:
        keyToEvict = this.getLFUKey();
        break;
      case CACHE_STRATEGY.FIFO:
        keyToEvict = this.cache.keys().next().value;
        break;
      default:
        keyToEvict = this.cache.keys().next().value;
    }
    
    if (keyToEvict) {
      this.delete(keyToEvict);
    }
  }
  
  /**
   * 获取最近最少使用的键
   */
  getLRUKey() {
    let oldestTime = Date.now();
    let oldestKey = null;
    
    for (const [key, time] of this.accessTimes) {
      if (time < oldestTime) {
        oldestTime = time;
        oldestKey = key;
      }
    }
    
    return oldestKey;
  }
  
  /**
   * 获取最少使用频率的键
   */
  getLFUKey() {
    let minCount = Infinity;
    let minKey = null;
    
    for (const [key, count] of this.accessCounts) {
      if (count < minCount) {
        minCount = count;
        minKey = key;
      }
    }
    
    return minKey;
  }
  
  /**
   * 获取缓存大小
   */
  size() {
    return this.cache.size;
  }
  
  /**
   * 获取所有键
   */
  keys() {
    return Array.from(this.cache.keys());
  }
  
  /**
   * 获取缓存统计信息
   */
  getStats() {
    return {
      size: this.cache.size,
      maxSize: this.maxSize,
      strategy: this.strategy,
      keys: this.keys()
    };
  }
}

/**
 * 本地存储缓存管理器
 */
class StorageCache {
  constructor(options = {}) {
    this.prefix = options.prefix || 'cache_';
    this.defaultTTL = options.defaultTTL || 24 * 60 * 60 * 1000; // 24小时
  }
  
  /**
   * 生成存储键
   */
  getStorageKey(key) {
    return `${this.prefix}${key}`;
  }
  
  /**
   * 设置缓存
   * @param {string} key - 缓存键
   * @param {any} value - 缓存值
   * @param {number} ttl - 生存时间（毫秒）
   */
  async set(key, value, ttl = this.defaultTTL) {
    try {
      const storageKey = this.getStorageKey(key);
      const cacheData = {
        value,
        timestamp: Date.now(),
        ttl,
        expireTime: ttl > 0 ? Date.now() + ttl : null
      };
      
      await this.setStorage(storageKey, cacheData);
      return this;
    } catch (error) {
      console.error('设置存储缓存失败:', error);
      throw error;
    }
  }
  
  /**
   * 获取缓存
   * @param {string} key - 缓存键
   */
  async get(key) {
    try {
      const storageKey = this.getStorageKey(key);
      const cacheData = await this.getStorage(storageKey);
      
      if (!cacheData) {
        return undefined;
      }
      
      // 检查是否过期
      if (cacheData.expireTime && Date.now() > cacheData.expireTime) {
        await this.delete(key);
        return undefined;
      }
      
      return cacheData.value;
    } catch (error) {
      console.error('获取存储缓存失败:', error);
      return undefined;
    }
  }
  
  /**
   * 检查缓存是否存在
   * @param {string} key - 缓存键
   */
  async has(key) {
    const value = await this.get(key);
    return value !== undefined;
  }
  
  /**
   * 删除缓存
   * @param {string} key - 缓存键
   */
  async delete(key) {
    try {
      const storageKey = this.getStorageKey(key);
      await this.removeStorage(storageKey);
      return this;
    } catch (error) {
      console.error('删除存储缓存失败:', error);
      throw error;
    }
  }
  
  /**
   * 清空所有缓存
   */
  async clear() {
    try {
      const info = await this.getStorageInfo();
      const keys = info.keys.filter(key => key.startsWith(this.prefix));
      
      for (const key of keys) {
        await this.removeStorage(key);
      }
      
      return this;
    } catch (error) {
      console.error('清空存储缓存失败:', error);
      throw error;
    }
  }
  
  /**
   * 清理过期缓存
   */
  async clearExpired() {
    try {
      const info = await this.getStorageInfo();
      const cacheKeys = info.keys.filter(key => key.startsWith(this.prefix));
      
      for (const storageKey of cacheKeys) {
        try {
          const cacheData = await this.getStorage(storageKey);
          if (cacheData && cacheData.expireTime && Date.now() > cacheData.expireTime) {
            await this.removeStorage(storageKey);
          }
        } catch (error) {
          // 忽略单个缓存项的错误
          console.warn('清理过期缓存项失败:', storageKey, error);
        }
      }
    } catch (error) {
      console.error('清理过期缓存失败:', error);
    }
  }
  
  /**
   * 获取缓存大小信息
   */
  async getSize() {
    try {
      const info = await this.getStorageInfo();
      const cacheKeys = info.keys.filter(key => key.startsWith(this.prefix));
      
      let totalSize = 0;
      for (const key of cacheKeys) {
        totalSize += key.length * 2; // 估算字符串大小
      }
      
      return {
        count: cacheKeys.length,
        size: totalSize,
        totalStorageSize: info.currentSize,
        limitSize: info.limitSize
      };
    } catch (error) {
      console.error('获取缓存大小失败:', error);
      return { count: 0, size: 0 };
    }
  }
  
  // 微信小程序存储API包装
  setStorage(key, data) {
    return new Promise((resolve, reject) => {
      wx.setStorage({
        key,
        data,
        success: resolve,
        fail: reject
      });
    });
  }
  
  getStorage(key) {
    return new Promise((resolve, reject) => {
      wx.getStorage({
        key,
        success: (res) => resolve(res.data),
        fail: () => resolve(null) // 不存在时返回null而不是错误
      });
    });
  }
  
  removeStorage(key) {
    return new Promise((resolve, reject) => {
      wx.removeStorage({
        key,
        success: resolve,
        fail: reject
      });
    });
  }
  
  getStorageInfo() {
    return new Promise((resolve, reject) => {
      wx.getStorageInfo({
        success: resolve,
        fail: reject
      });
    });
  }
}

/**
 * 文件缓存管理器
 */
class FileCache {
  constructor(options = {}) {
    this.maxSize = options.maxSize || 50 * 1024 * 1024; // 50MB
    this.defaultTTL = options.defaultTTL || 7 * 24 * 60 * 60 * 1000; // 7天
    this.fileManager = wx.getFileSystemManager();
    this.cacheDir = `${wx.env.USER_DATA_PATH}/cache`;
    
    this.init();
  }
  
  /**
   * 初始化缓存目录
   */
  init() {
    try {
      this.fileManager.mkdirSync(this.cacheDir, true);
    } catch (error) {
      if (error.errMsg && !error.errMsg.includes('file already exists')) {
        console.error('创建缓存目录失败:', error);
      }
    }
  }
  
  /**
   * 生成缓存文件路径
   */
  getCacheFilePath(key) {
    const hash = this.hashCode(key);
    return `${this.cacheDir}/${hash}.cache`;
  }
  
  /**
   * 生成元数据文件路径
   */
  getMetaFilePath(key) {
    const hash = this.hashCode(key);
    return `${this.cacheDir}/${hash}.meta`;
  }
  
  /**
   * 简单哈希函数
   */
  hashCode(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // 转换为32位整数
    }
    return Math.abs(hash).toString(36);
  }
  
  /**
   * 缓存文件
   * @param {string} key - 缓存键
   * @param {string} filePath - 文件路径
   * @param {number} ttl - 生存时间（毫秒）
   */
  async cacheFile(key, filePath, ttl = this.defaultTTL) {
    try {
      const cacheFilePath = this.getCacheFilePath(key);
      const metaFilePath = this.getMetaFilePath(key);
      
      // 复制文件到缓存目录
      this.fileManager.copyFileSync(filePath, cacheFilePath);
      
      // 保存元数据
      const metadata = {
        key,
        originalPath: filePath,
        timestamp: Date.now(),
        ttl,
        expireTime: ttl > 0 ? Date.now() + ttl : null,
        size: this.getFileSize(cacheFilePath)
      };
      
      this.fileManager.writeFileSync(metaFilePath, JSON.stringify(metadata), 'utf8');
      
      // 检查缓存大小
      await this.checkCacheSize();
      
      return cacheFilePath;
    } catch (error) {
      console.error('缓存文件失败:', error);
      throw error;
    }
  }
  
  /**
   * 获取缓存文件
   * @param {string} key - 缓存键
   */
  async getCachedFile(key) {
    try {
      const cacheFilePath = this.getCacheFilePath(key);
      const metaFilePath = this.getMetaFilePath(key);
      
      // 检查文件是否存在
      if (!this.fileExists(cacheFilePath) || !this.fileExists(metaFilePath)) {
        return null;
      }
      
      // 读取元数据
      const metadataStr = this.fileManager.readFileSync(metaFilePath, 'utf8');
      const metadata = JSON.parse(metadataStr);
      
      // 检查是否过期
      if (metadata.expireTime && Date.now() > metadata.expireTime) {
        await this.deleteCachedFile(key);
        return null;
      }
      
      return {
        filePath: cacheFilePath,
        metadata
      };
    } catch (error) {
      console.error('获取缓存文件失败:', error);
      return null;
    }
  }
  
  /**
   * 删除缓存文件
   * @param {string} key - 缓存键
   */
  async deleteCachedFile(key) {
    try {
      const cacheFilePath = this.getCacheFilePath(key);
      const metaFilePath = this.getMetaFilePath(key);
      
      if (this.fileExists(cacheFilePath)) {
        this.fileManager.unlinkSync(cacheFilePath);
      }
      
      if (this.fileExists(metaFilePath)) {
        this.fileManager.unlinkSync(metaFilePath);
      }
    } catch (error) {
      console.error('删除缓存文件失败:', error);
    }
  }
  
  /**
   * 清空所有缓存文件
   */
  async clearAll() {
    try {
      const files = this.fileManager.readdirSync(this.cacheDir);
      
      for (const file of files) {
        const filePath = `${this.cacheDir}/${file}`;
        this.fileManager.unlinkSync(filePath);
      }
    } catch (error) {
      console.error('清空缓存文件失败:', error);
    }
  }
  
  /**
   * 检查缓存大小并清理
   */
  async checkCacheSize() {
    try {
      const totalSize = await this.getCacheSize();
      
      if (totalSize > this.maxSize) {
        await this.cleanupCache();
      }
    } catch (error) {
      console.error('检查缓存大小失败:', error);
    }
  }
  
  /**
   * 获取缓存总大小
   */
  async getCacheSize() {
    try {
      const files = this.fileManager.readdirSync(this.cacheDir);
      let totalSize = 0;
      
      for (const file of files) {
        const filePath = `${this.cacheDir}/${file}`;
        totalSize += this.getFileSize(filePath);
      }
      
      return totalSize;
    } catch (error) {
      console.error('获取缓存大小失败:', error);
      return 0;
    }
  }
  
  /**
   * 清理缓存（删除最旧的文件）
   */
  async cleanupCache() {
    try {
      const files = this.fileManager.readdirSync(this.cacheDir);
      const metaFiles = files.filter(file => file.endsWith('.meta'));
      
      // 读取所有元数据并按时间排序
      const fileInfos = [];
      
      for (const metaFile of metaFiles) {
        try {
          const metaPath = `${this.cacheDir}/${metaFile}`;
          const metadataStr = this.fileManager.readFileSync(metaPath, 'utf8');
          const metadata = JSON.parse(metadataStr);
          fileInfos.push(metadata);
        } catch (error) {
          console.warn('读取元数据失败:', metaFile, error);
        }
      }
      
      // 按时间排序，删除最旧的文件直到大小合适
      fileInfos.sort((a, b) => a.timestamp - b.timestamp);
      
      let currentSize = await this.getCacheSize();
      
      for (const fileInfo of fileInfos) {
        if (currentSize <= this.maxSize * 0.8) { // 清理到80%
          break;
        }
        
        await this.deleteCachedFile(fileInfo.key);
        currentSize -= fileInfo.size;
      }
    } catch (error) {
      console.error('清理缓存失败:', error);
    }
  }
  
  /**
   * 检查文件是否存在
   */
  fileExists(filePath) {
    try {
      this.fileManager.accessSync(filePath);
      return true;
    } catch (error) {
      return false;
    }
  }
  
  /**
   * 获取文件大小
   */
  getFileSize(filePath) {
    try {
      const stats = this.fileManager.statSync(filePath);
      return stats.size;
    } catch (error) {
      return 0;
    }
  }
}

/**
 * 统一缓存管理器
 */
class CacheManager {
  constructor(options = {}) {
    this.memoryCache = new MemoryCache(options.memory);
    this.storageCache = new StorageCache(options.storage);
    this.fileCache = new FileCache(options.file);
  }
  
  /**
   * 设置内存缓存
   */
  setMemory(key, value, ttl) {
    return this.memoryCache.set(key, value, ttl);
  }
  
  /**
   * 获取内存缓存
   */
  getMemory(key) {
    return this.memoryCache.get(key);
  }
  
  /**
   * 设置存储缓存
   */
  setStorage(key, value, ttl) {
    return this.storageCache.set(key, value, ttl);
  }
  
  /**
   * 获取存储缓存
   */
  getStorage(key) {
    return this.storageCache.get(key);
  }
  
  /**
   * 缓存文件
   */
  cacheFile(key, filePath, ttl) {
    return this.fileCache.cacheFile(key, filePath, ttl);
  }
  
  /**
   * 获取缓存文件
   */
  getCachedFile(key) {
    return this.fileCache.getCachedFile(key);
  }
  
  /**
   * 清空所有缓存
   */
  async clearAll() {
    this.memoryCache.clear();
    await this.storageCache.clear();
    await this.fileCache.clearAll();
  }
  
  /**
   * 清理过期缓存
   */
  async clearExpired() {
    await this.storageCache.clearExpired();
    // 内存缓存有自动TTL清理
    // 文件缓存在访问时检查过期
  }
  
  /**
   * 获取缓存统计信息
   */
  async getStats() {
    const memoryStats = this.memoryCache.getStats();
    const storageStats = await this.storageCache.getSize();
    const fileStats = {
      size: await this.fileCache.getCacheSize(),
      maxSize: this.fileCache.maxSize
    };
    
    return {
      memory: memoryStats,
      storage: storageStats,
      file: fileStats
    };
  }
}

// 创建全局缓存管理器实例
const cacheManager = new CacheManager();

/**
 * 工具函数
 */

// 设置内存缓存
export function setMemoryCache(key, value, ttl) {
  return cacheManager.setMemory(key, value, ttl);
}

// 获取内存缓存
export function getMemoryCache(key) {
  return cacheManager.getMemory(key);
}

// 设置存储缓存
export function setStorageCache(key, value, ttl) {
  return cacheManager.setStorage(key, value, ttl);
}

// 获取存储缓存
export function getStorageCache(key) {
  return cacheManager.getStorage(key);
}

// 缓存文件
export function cacheFile(key, filePath, ttl) {
  return cacheManager.cacheFile(key, filePath, ttl);
}

// 获取缓存文件
export function getCachedFile(key) {
  return cacheManager.getCachedFile(key);
}

// 清空所有缓存
export function clearAllCache() {
  return cacheManager.clearAll();
}

// 清理过期缓存
export function clearExpiredCache() {
  return cacheManager.clearExpired();
}

// 获取缓存统计信息
export function getCacheStats() {
  return cacheManager.getStats();
}

// 导出缓存管理器和相关类
export {
  CacheManager,
  MemoryCache,
  StorageCache,
  FileCache,
  CACHE_TYPE,
  CACHE_STRATEGY
};

export default cacheManager;