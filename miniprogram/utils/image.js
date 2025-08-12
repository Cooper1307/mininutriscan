/**
 * 图片处理工具
 * 提供图片压缩、裁剪、格式转换、上传等功能
 */

/**
 * 图片质量枚举
 */
const IMAGE_QUALITY = {
  LOW: 0.3,
  MEDIUM: 0.6,
  HIGH: 0.8,
  ORIGINAL: 1.0
};

/**
 * 图片格式枚举
 */
const IMAGE_FORMAT = {
  JPG: 'jpg',
  PNG: 'png',
  WEBP: 'webp'
};

/**
 * 图片尺寸预设
 */
const IMAGE_SIZE_PRESET = {
  THUMBNAIL: { width: 150, height: 150 },
  SMALL: { width: 300, height: 300 },
  MEDIUM: { width: 600, height: 600 },
  LARGE: { width: 1200, height: 1200 },
  AVATAR: { width: 200, height: 200 }
};

/**
 * 图片处理器类
 */
class ImageProcessor {
  constructor() {
    this.canvas = null;
    this.ctx = null;
  }
  
  /**
   * 初始化Canvas
   */
  initCanvas() {
    if (!this.canvas) {
      this.canvas = wx.createCanvasContext('imageCanvas');
    }
    return this.canvas;
  }
  
  /**
   * 获取图片信息
   * @param {string} src - 图片路径
   */
  getImageInfo(src) {
    return new Promise((resolve, reject) => {
      wx.getImageInfo({
        src,
        success: resolve,
        fail: reject
      });
    });
  }
  
  /**
   * 压缩图片
   * @param {string} src - 图片路径
   * @param {object} options - 压缩选项
   */
  async compressImage(src, options = {}) {
    const {
      quality = IMAGE_QUALITY.MEDIUM,
      maxWidth = 1200,
      maxHeight = 1200,
      format = IMAGE_FORMAT.JPG
    } = options;
    
    try {
      // 获取图片信息
      const imageInfo = await this.getImageInfo(src);
      const { width, height } = imageInfo;
      
      // 计算压缩后的尺寸
      const { newWidth, newHeight } = this.calculateSize(width, height, maxWidth, maxHeight);
      
      // 压缩图片
      const compressedPath = await this.compressToFile(src, {
        quality,
        width: newWidth,
        height: newHeight,
        format
      });
      
      return {
        path: compressedPath,
        originalSize: { width, height },
        compressedSize: { width: newWidth, height: newHeight },
        quality,
        format
      };
    } catch (error) {
      console.error('压缩图片失败:', error);
      throw error;
    }
  }
  
  /**
   * 计算压缩后的尺寸
   */
  calculateSize(width, height, maxWidth, maxHeight) {
    let newWidth = width;
    let newHeight = height;
    
    // 按比例缩放
    if (width > maxWidth || height > maxHeight) {
      const ratio = Math.min(maxWidth / width, maxHeight / height);
      newWidth = Math.round(width * ratio);
      newHeight = Math.round(height * ratio);
    }
    
    return { newWidth, newHeight };
  }
  
  /**
   * 压缩图片到文件
   */
  compressToFile(src, options) {
    return new Promise((resolve, reject) => {
      wx.compressImage({
        src,
        quality: Math.round(options.quality * 100),
        success: (res) => resolve(res.tempFilePath),
        fail: reject
      });
    });
  }
  
  /**
   * 裁剪图片
   * @param {string} src - 图片路径
   * @param {object} cropArea - 裁剪区域 {x, y, width, height}
   * @param {object} options - 裁剪选项
   */
  async cropImage(src, cropArea, options = {}) {
    const {
      outputWidth = cropArea.width,
      outputHeight = cropArea.height,
      quality = IMAGE_QUALITY.HIGH,
      format = IMAGE_FORMAT.JPG
    } = options;
    
    try {
      // 使用Canvas进行裁剪
      const canvas = this.initCanvas();
      
      // 绘制裁剪后的图片
      canvas.drawImage(
        src,
        cropArea.x, cropArea.y, cropArea.width, cropArea.height,
        0, 0, outputWidth, outputHeight
      );
      
      canvas.draw();
      
      // 导出为临时文件
      const tempFilePath = await this.canvasToTempFile(canvas, {
        width: outputWidth,
        height: outputHeight,
        quality,
        format
      });
      
      return {
        path: tempFilePath,
        cropArea,
        outputSize: { width: outputWidth, height: outputHeight },
        quality,
        format
      };
    } catch (error) {
      console.error('裁剪图片失败:', error);
      throw error;
    }
  }
  
  /**
   * Canvas导出为临时文件
   */
  canvasToTempFile(canvas, options) {
    return new Promise((resolve, reject) => {
      wx.canvasToTempFilePath({
        canvasId: 'imageCanvas',
        width: options.width,
        height: options.height,
        quality: options.quality,
        fileType: options.format,
        success: (res) => resolve(res.tempFilePath),
        fail: reject
      });
    });
  }
  
  /**
   * 生成缩略图
   * @param {string} src - 图片路径
   * @param {string} preset - 尺寸预设
   */
  async generateThumbnail(src, preset = 'THUMBNAIL') {
    const size = IMAGE_SIZE_PRESET[preset] || IMAGE_SIZE_PRESET.THUMBNAIL;
    
    return this.compressImage(src, {
      maxWidth: size.width,
      maxHeight: size.height,
      quality: IMAGE_QUALITY.MEDIUM,
      format: IMAGE_FORMAT.JPG
    });
  }
  
  /**
   * 批量压缩图片
   * @param {Array} srcList - 图片路径数组
   * @param {object} options - 压缩选项
   */
  async batchCompress(srcList, options = {}) {
    const results = [];
    
    for (let i = 0; i < srcList.length; i++) {
      try {
        const result = await this.compressImage(srcList[i], options);
        results.push({
          index: i,
          success: true,
          result
        });
      } catch (error) {
        results.push({
          index: i,
          success: false,
          error: error.message
        });
      }
    }
    
    return results;
  }
  
  /**
   * 添加水印
   * @param {string} src - 图片路径
   * @param {object} watermark - 水印配置
   */
  async addWatermark(src, watermark) {
    const {
      text = '',
      image = '',
      position = 'bottom-right',
      opacity = 0.5,
      fontSize = 20,
      color = '#ffffff'
    } = watermark;
    
    try {
      const imageInfo = await this.getImageInfo(src);
      const canvas = this.initCanvas();
      
      // 绘制原图
      canvas.drawImage(src, 0, 0, imageInfo.width, imageInfo.height);
      
      // 设置透明度
      canvas.setGlobalAlpha(opacity);
      
      if (text) {
        // 添加文字水印
        await this.drawTextWatermark(canvas, text, position, imageInfo, {
          fontSize,
          color
        });
      }
      
      if (image) {
        // 添加图片水印
        await this.drawImageWatermark(canvas, image, position, imageInfo);
      }
      
      canvas.draw();
      
      // 导出为临时文件
      const tempFilePath = await this.canvasToTempFile(canvas, {
        width: imageInfo.width,
        height: imageInfo.height,
        quality: IMAGE_QUALITY.HIGH,
        format: IMAGE_FORMAT.PNG
      });
      
      return tempFilePath;
    } catch (error) {
      console.error('添加水印失败:', error);
      throw error;
    }
  }
  
  /**
   * 绘制文字水印
   */
  async drawTextWatermark(canvas, text, position, imageInfo, textOptions) {
    const { fontSize, color } = textOptions;
    const { x, y } = this.calculateWatermarkPosition(position, imageInfo, {
      width: text.length * fontSize * 0.6,
      height: fontSize
    });
    
    canvas.setFontSize(fontSize);
    canvas.setFillStyle(color);
    canvas.fillText(text, x, y);
  }
  
  /**
   * 绘制图片水印
   */
  async drawImageWatermark(canvas, watermarkSrc, position, imageInfo) {
    const watermarkInfo = await this.getImageInfo(watermarkSrc);
    const { x, y } = this.calculateWatermarkPosition(position, imageInfo, watermarkInfo);
    
    canvas.drawImage(watermarkSrc, x, y, watermarkInfo.width, watermarkInfo.height);
  }
  
  /**
   * 计算水印位置
   */
  calculateWatermarkPosition(position, imageInfo, watermarkSize) {
    const margin = 20;
    let x = 0;
    let y = 0;
    
    switch (position) {
      case 'top-left':
        x = margin;
        y = margin;
        break;
      case 'top-right':
        x = imageInfo.width - watermarkSize.width - margin;
        y = margin;
        break;
      case 'bottom-left':
        x = margin;
        y = imageInfo.height - watermarkSize.height - margin;
        break;
      case 'bottom-right':
        x = imageInfo.width - watermarkSize.width - margin;
        y = imageInfo.height - watermarkSize.height - margin;
        break;
      case 'center':
        x = (imageInfo.width - watermarkSize.width) / 2;
        y = (imageInfo.height - watermarkSize.height) / 2;
        break;
      default:
        x = imageInfo.width - watermarkSize.width - margin;
        y = imageInfo.height - watermarkSize.height - margin;
    }
    
    return { x, y };
  }
  
  /**
   * 获取图片文件大小
   * @param {string} filePath - 文件路径
   */
  async getFileSize(filePath) {
    try {
      const fileManager = wx.getFileSystemManager();
      const stats = await new Promise((resolve, reject) => {
        fileManager.stat({
          path: filePath,
          success: resolve,
          fail: reject
        });
      });
      
      return stats.size;
    } catch (error) {
      console.error('获取文件大小失败:', error);
      return 0;
    }
  }
  
  /**
   * 格式化文件大小
   * @param {number} bytes - 字节数
   */
  formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
}

/**
 * 图片选择器
 */
class ImagePicker {
  constructor(options = {}) {
    this.maxCount = options.maxCount || 9;
    this.sizeType = options.sizeType || ['original', 'compressed'];
    this.sourceType = options.sourceType || ['album', 'camera'];
  }
  
  /**
   * 选择图片
   * @param {object} options - 选择选项
   */
  chooseImage(options = {}) {
    const {
      count = this.maxCount,
      sizeType = this.sizeType,
      sourceType = this.sourceType
    } = options;
    
    return new Promise((resolve, reject) => {
      wx.chooseImage({
        count,
        sizeType,
        sourceType,
        success: resolve,
        fail: reject
      });
    });
  }
  
  /**
   * 选择媒体文件（图片和视频）
   * @param {object} options - 选择选项
   */
  chooseMedia(options = {}) {
    const {
      count = this.maxCount,
      mediaType = ['image'],
      sourceType = this.sourceType,
      maxDuration = 30,
      sizeType = this.sizeType,
      camera = 'back'
    } = options;
    
    return new Promise((resolve, reject) => {
      wx.chooseMedia({
        count,
        mediaType,
        sourceType,
        maxDuration,
        sizeType,
        camera,
        success: resolve,
        fail: reject
      });
    });
  }
  
  /**
   * 预览图片
   * @param {Array} urls - 图片URL数组
   * @param {number} current - 当前显示图片索引
   */
  previewImage(urls, current = 0) {
    return new Promise((resolve, reject) => {
      wx.previewImage({
        urls,
        current: typeof current === 'number' ? urls[current] : current,
        success: resolve,
        fail: reject
      });
    });
  }
  
  /**
   * 保存图片到相册
   * @param {string} filePath - 图片路径
   */
  saveImageToPhotosAlbum(filePath) {
    return new Promise((resolve, reject) => {
      wx.saveImageToPhotosAlbum({
        filePath,
        success: resolve,
        fail: reject
      });
    });
  }
}

/**
 * 图片上传器
 */
class ImageUploader {
  constructor(options = {}) {
    this.baseURL = options.baseURL || '';
    this.uploadPath = options.uploadPath || '/upload';
    this.headers = options.headers || {};
    this.maxSize = options.maxSize || 5 * 1024 * 1024; // 5MB
    this.allowedFormats = options.allowedFormats || ['jpg', 'jpeg', 'png', 'webp'];
  }
  
  /**
   * 上传单个图片
   * @param {string} filePath - 图片路径
   * @param {object} options - 上传选项
   */
  async uploadImage(filePath, options = {}) {
    const {
      name = 'file',
      formData = {},
      compress = true,
      onProgress
    } = options;
    
    try {
      // 验证图片
      await this.validateImage(filePath);
      
      // 压缩图片（如果需要）
      let uploadPath = filePath;
      if (compress) {
        const processor = new ImageProcessor();
        const compressed = await processor.compressImage(filePath, {
          quality: IMAGE_QUALITY.MEDIUM,
          maxWidth: 1200,
          maxHeight: 1200
        });
        uploadPath = compressed.path;
      }
      
      // 上传图片
      const result = await this.uploadFile(uploadPath, {
        name,
        formData,
        onProgress
      });
      
      return result;
    } catch (error) {
      console.error('上传图片失败:', error);
      throw error;
    }
  }
  
  /**
   * 批量上传图片
   * @param {Array} filePaths - 图片路径数组
   * @param {object} options - 上传选项
   */
  async batchUpload(filePaths, options = {}) {
    const {
      concurrent = 3, // 并发数
      onProgress,
      onItemComplete
    } = options;
    
    const results = [];
    const total = filePaths.length;
    let completed = 0;
    
    // 分批上传
    for (let i = 0; i < filePaths.length; i += concurrent) {
      const batch = filePaths.slice(i, i + concurrent);
      
      const batchPromises = batch.map(async (filePath, index) => {
        try {
          const result = await this.uploadImage(filePath, {
            ...options,
            onProgress: (progress) => {
              if (onProgress) {
                onProgress({
                  current: i + index + 1,
                  total,
                  progress,
                  overall: (completed + progress / 100) / total
                });
              }
            }
          });
          
          completed++;
          
          if (onItemComplete) {
            onItemComplete({
              index: i + index,
              success: true,
              result
            });
          }
          
          return {
            index: i + index,
            success: true,
            result
          };
        } catch (error) {
          completed++;
          
          if (onItemComplete) {
            onItemComplete({
              index: i + index,
              success: false,
              error: error.message
            });
          }
          
          return {
            index: i + index,
            success: false,
            error: error.message
          };
        }
      });
      
      const batchResults = await Promise.all(batchPromises);
      results.push(...batchResults);
    }
    
    return results;
  }
  
  /**
   * 验证图片
   * @param {string} filePath - 图片路径
   */
  async validateImage(filePath) {
    // 检查文件大小
    const processor = new ImageProcessor();
    const fileSize = await processor.getFileSize(filePath);
    
    if (fileSize > this.maxSize) {
      throw new Error(`图片大小超过限制 (${processor.formatFileSize(this.maxSize)})`);
    }
    
    // 检查图片格式
    const imageInfo = await processor.getImageInfo(filePath);
    const format = this.getImageFormat(imageInfo.type);
    
    if (!this.allowedFormats.includes(format)) {
      throw new Error(`不支持的图片格式: ${format}`);
    }
    
    return true;
  }
  
  /**
   * 获取图片格式
   * @param {string} type - 图片类型
   */
  getImageFormat(type) {
    const typeMap = {
      'image/jpeg': 'jpg',
      'image/jpg': 'jpg',
      'image/png': 'png',
      'image/webp': 'webp',
      'image/gif': 'gif'
    };
    
    return typeMap[type] || type.split('/')[1] || 'unknown';
  }
  
  /**
   * 上传文件
   * @param {string} filePath - 文件路径
   * @param {object} options - 上传选项
   */
  uploadFile(filePath, options) {
    const { name, formData, onProgress } = options;
    
    return new Promise((resolve, reject) => {
      const uploadTask = wx.uploadFile({
        url: this.baseURL + this.uploadPath,
        filePath,
        name,
        formData,
        header: this.headers,
        success: (res) => {
          try {
            const data = JSON.parse(res.data);
            resolve(data);
          } catch (error) {
            resolve(res.data);
          }
        },
        fail: reject
      });
      
      // 监听上传进度
      if (onProgress) {
        uploadTask.onProgressUpdate((res) => {
          onProgress(res.progress);
        });
      }
    });
  }
}

// 创建全局实例
const imageProcessor = new ImageProcessor();
const imagePicker = new ImagePicker();
const imageUploader = new ImageUploader();

/**
 * 工具函数
 */

// 压缩图片
export function compressImage(src, options) {
  return imageProcessor.compressImage(src, options);
}

// 裁剪图片
export function cropImage(src, cropArea, options) {
  return imageProcessor.cropImage(src, cropArea, options);
}

// 生成缩略图
export function generateThumbnail(src, preset) {
  return imageProcessor.generateThumbnail(src, preset);
}

// 添加水印
export function addWatermark(src, watermark) {
  return imageProcessor.addWatermark(src, watermark);
}

// 选择图片
export function chooseImage(options) {
  return imagePicker.chooseImage(options);
}

// 选择媒体文件
export function chooseMedia(options) {
  return imagePicker.chooseMedia(options);
}

// 预览图片
export function previewImage(urls, current) {
  return imagePicker.previewImage(urls, current);
}

// 保存图片到相册
export function saveImageToPhotosAlbum(filePath) {
  return imagePicker.saveImageToPhotosAlbum(filePath);
}

// 上传图片
export function uploadImage(filePath, options) {
  return imageUploader.uploadImage(filePath, options);
}

// 批量上传图片
export function batchUploadImages(filePaths, options) {
  return imageUploader.batchUpload(filePaths, options);
}

// 获取图片信息
export function getImageInfo(src) {
  return imageProcessor.getImageInfo(src);
}

// 获取文件大小
export function getFileSize(filePath) {
  return imageProcessor.getFileSize(filePath);
}

// 格式化文件大小
export function formatFileSize(bytes) {
  return imageProcessor.formatFileSize(bytes);
}

// 导出类和常量
export {
  ImageProcessor,
  ImagePicker,
  ImageUploader,
  IMAGE_QUALITY,
  IMAGE_FORMAT,
  IMAGE_SIZE_PRESET
};

export default {
  processor: imageProcessor,
  picker: imagePicker,
  uploader: imageUploader
};