// pages/detection/detection.js
const app = getApp()

Page({
  data: {
    selectedImage: '',
    detecting: false,
    detectionProgress: 0,
    detectionStatus: '准备检测',
    currentStep: 0,
    showLoading: false,
    loadingText: '处理中...',
    historyList: [
      {
        id: 1,
        image: '/assets/images/food-sample1.jpg',
        foodName: '苹果',
        safetyLevel: 'safe',
        safetyIcon: '✅',
        safetyText: '安全',
        detectionTime: '2024-01-15 14:30'
      },
      {
        id: 2,
        image: '/assets/images/food-sample2.jpg',
        foodName: '牛奶',
        safetyLevel: 'warning',
        safetyIcon: '⚠️',
        safetyText: '注意',
        detectionTime: '2024-01-15 10:15'
      }
    ]
  },

  onLoad(options) {
    console.log('检测页面加载', options)
    
    // 如果从其他页面传入图片
    if (options.image) {
      this.setData({
        selectedImage: decodeURIComponent(options.image)
      })
    }
    
    this.loadHistory()
  },

  onShow() {
    console.log('检测页面显示')
  },

  // 选择图片
  chooseImage() {
    wx.showActionSheet({
      itemList: ['拍照', '从相册选择'],
      success: (res) => {
        if (res.tapIndex === 0) {
          this.openCamera()
        } else {
          this.chooseFromAlbum()
        }
      }
    })
  },

  // 打开相机
  openCamera() {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['camera'],
      camera: 'back',
      success: (res) => {
        const imagePath = res.tempFiles[0].tempFilePath
        console.log('拍照成功:', imagePath)
        
        this.setData({
          selectedImage: imagePath
        })
        
        // 触发震动反馈
        wx.vibrateShort()
      },
      fail: (error) => {
        console.error('拍照失败:', error)
        if (!error.errMsg.includes('cancel')) {
          app.showError('拍照失败，请检查相机权限')
        }
      }
    })
  },

  // 从相册选择
  chooseFromAlbum() {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['album'],
      success: (res) => {
        const imagePath = res.tempFiles[0].tempFilePath
        console.log('选择图片成功:', imagePath)
        
        this.setData({
          selectedImage: imagePath
        })
      },
      fail: (error) => {
        console.error('选择图片失败:', error)
        if (!error.errMsg.includes('cancel')) {
          app.showError('选择图片失败')
        }
      }
    })
  },

  // 扫描条码
  scanBarcode() {
    wx.scanCode({
      scanType: ['barCode', 'qrCode'],
      success: (res) => {
        console.log('扫码成功:', res)
        
        // 根据条码查询商品信息
        this.queryProductByBarcode(res.result)
      },
      fail: (error) => {
        console.error('扫码失败:', error)
        if (!error.errMsg.includes('cancel')) {
          app.showError('扫码失败')
        }
      }
    })
  },

  // 重新拍照
  retakePhoto() {
    this.setData({
      selectedImage: '',
      detecting: false,
      detectionProgress: 0,
      currentStep: 0
    })
  },

  // 开始检测
  startDetection() {
    if (!this.data.selectedImage) {
      app.showError('请先选择图片')
      return
    }

    this.setData({
      detecting: true,
      detectionProgress: 0,
      currentStep: 0,
      detectionStatus: '正在上传图片...'
    })

    // 模拟检测过程
    this.simulateDetection()
  },

  // 模拟检测过程
  simulateDetection() {
    const steps = [
      { progress: 25, status: '图像预处理中...', step: 1, duration: 1000 },
      { progress: 50, status: 'AI模型分析中...', step: 2, duration: 2000 },
      { progress: 75, status: '安全评估中...', step: 3, duration: 1500 },
      { progress: 100, status: '检测完成', step: 4, duration: 500 }
    ]

    let currentIndex = 0

    const runStep = () => {
      if (currentIndex >= steps.length) {
        // 检测完成，跳转到结果页
        this.navigateToResult()
        return
      }

      const step = steps[currentIndex]
      
      this.setData({
        detectionProgress: step.progress,
        detectionStatus: step.status,
        currentStep: step.step
      })

      setTimeout(() => {
        currentIndex++
        runStep()
      }, step.duration)
    }

    runStep()
  },

  // 跳转到结果页
  navigateToResult() {
    // 生成模拟检测结果
    const mockResult = {
      image: this.data.selectedImage,
      foodName: '苹果',
      confidence: 0.95,
      safetyLevel: 'safe',
      safetyScore: 85,
      detectionTime: new Date().toLocaleString(),
      details: {
        freshness: '新鲜',
        pesticide: '未检出',
        bacteria: '正常',
        nutrition: '丰富'
      },
      suggestions: [
        '建议清洗后食用',
        '可以直接食用',
        '营养价值较高'
      ]
    }

    // 保存到历史记录
    this.saveToHistory(mockResult)

    wx.redirectTo({
      url: `/pages/detection/result?data=${encodeURIComponent(JSON.stringify(mockResult))}`
    })
  },

  // 实际API检测（当后端API可用时）
  async performActualDetection() {
    try {
      // 上传图片
      const uploadResult = await this.uploadImage(this.data.selectedImage)
      
      if (!uploadResult.success) {
        throw new Error('图片上传失败')
      }

      // 调用检测API
      const detectionResult = await app.request({
        url: '/api/v1/detection/analyze',
        method: 'POST',
        data: {
          imageUrl: uploadResult.imageUrl,
          detectionType: 'food_safety'
        }
      })

      if (detectionResult.statusCode === 200) {
        this.navigateToResult(detectionResult.data)
      } else {
        throw new Error('检测失败')
      }
    } catch (error) {
      console.error('检测失败:', error)
      app.showError('检测失败，请重试')
      
      this.setData({
        detecting: false,
        detectionProgress: 0,
        currentStep: 0
      })
    }
  },

  // 上传图片
  uploadImage(imagePath) {
    return new Promise((resolve, reject) => {
      wx.uploadFile({
        url: `${app.globalData.apiBaseUrl}/api/v1/upload/image`,
        filePath: imagePath,
        name: 'image',
        header: {
          'Authorization': `Bearer ${wx.getStorageSync('token')}`
        },
        success: (res) => {
          try {
            const data = JSON.parse(res.data)
            resolve({
              success: true,
              imageUrl: data.imageUrl
            })
          } catch (error) {
            reject(error)
          }
        },
        fail: reject
      })
    })
  },

  // 根据条码查询商品
  queryProductByBarcode(barcode) {
    app.showLoading('查询中...')
    
    app.request({
      url: '/api/v1/products/barcode',
      method: 'GET',
      data: { barcode },
      success: (res) => {
        if (res.statusCode === 200 && res.data.product) {
          const product = res.data.product
          
          wx.navigateTo({
            url: `/pages/product/detail?id=${product.id}`
          })
        } else {
          app.showError('未找到该商品信息')
        }
      },
      fail: (error) => {
        console.error('查询商品失败:', error)
        app.showError('查询失败，请重试')
      },
      complete: () => {
        app.hideLoading()
      }
    })
  },

  // 保存到历史记录
  saveToHistory(result) {
    const historyItem = {
      id: Date.now(),
      image: result.image,
      foodName: result.foodName,
      safetyLevel: result.safetyLevel,
      safetyIcon: this.getSafetyIcon(result.safetyLevel),
      safetyText: this.getSafetyText(result.safetyLevel),
      detectionTime: result.detectionTime
    }

    // 添加到本地存储
    let history = wx.getStorageSync('detectionHistory') || []
    history.unshift(historyItem)
    
    // 只保留最近20条记录
    if (history.length > 20) {
      history = history.slice(0, 20)
    }
    
    wx.setStorageSync('detectionHistory', history)
    
    // 更新页面数据
    this.setData({
      historyList: history.slice(0, 5) // 只显示最近5条
    })
  },

  // 获取安全等级图标
  getSafetyIcon(level) {
    const icons = {
      safe: '✅',
      warning: '⚠️',
      danger: '❌'
    }
    return icons[level] || '❓'
  },

  // 获取安全等级文本
  getSafetyText(level) {
    const texts = {
      safe: '安全',
      warning: '注意',
      danger: '危险'
    }
    return texts[level] || '未知'
  },

  // 加载历史记录
  loadHistory() {
    const history = wx.getStorageSync('detectionHistory') || []
    this.setData({
      historyList: history.slice(0, 5) // 只显示最近5条
    })
  },

  // 查看历史详情
  viewHistoryDetail(e) {
    const item = e.currentTarget.dataset.item
    console.log('查看历史详情:', item)
    
    wx.navigateTo({
      url: `/pages/detection/history-detail?id=${item.id}`
    })
  },

  // 查看全部历史
  viewAllHistory() {
    wx.navigateTo({
      url: '/pages/detection/history'
    })
  },

  // 分享功能
  onShareAppMessage() {
    return {
      title: 'AI智能检测 - 守护食品安全',
      path: '/pages/detection/detection',
      imageUrl: '/assets/images/share-detection.jpg'
    }
  },

  // 分享到朋友圈
  onShareTimeline() {
    return {
      title: 'AI智能检测 - 守护食品安全',
      imageUrl: '/assets/images/share-detection.jpg'
    }
  }
})