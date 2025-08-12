// pages/detection/result.js
const app = getApp()

Page({
  data: {
    resultData: {},
    showShareModal: false,
    recommendations: [
      {
        id: 1,
        title: '食品安全小贴士',
        description: '如何正确保存水果',
        image: '/assets/images/tip1.jpg'
      },
      {
        id: 2,
        title: '营养搭配指南',
        description: '均衡饮食的重要性',
        image: '/assets/images/tip2.jpg'
      },
      {
        id: 3,
        title: '食材选购技巧',
        description: '挑选新鲜食材的方法',
        image: '/assets/images/tip3.jpg'
      }
    ],
    expertComment: {
      avatar: '/assets/images/expert-avatar.jpg',
      name: '张教授',
      title: '食品安全专家',
      content: '从检测结果来看，这个苹果的各项指标都在正常范围内，新鲜度良好，可以放心食用。建议食用前清洗干净，以去除表面可能残留的灰尘和细菌。'
    }
  },

  onLoad(options) {
    console.log('结果页面加载', options)
    
    if (options.data) {
      try {
        const resultData = JSON.parse(decodeURIComponent(options.data))
        this.setData({ resultData })
        console.log('检测结果数据:', resultData)
      } catch (error) {
        console.error('解析结果数据失败:', error)
        app.showError('数据解析失败')
        wx.navigateBack()
      }
    } else {
      app.showError('缺少检测结果数据')
      wx.navigateBack()
    }
    
    this.loadRecommendations()
    this.loadExpertComment()
  },

  onShow() {
    console.log('结果页面显示')
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

  // 获取安全等级标题
  getSafetyTitle(level) {
    const titles = {
      safe: '安全可食用',
      warning: '需要注意',
      danger: '不建议食用'
    }
    return titles[level] || '未知状态'
  },

  // 分享结果
  shareResult() {
    this.setData({ showShareModal: true })
  },

  // 隐藏分享弹窗
  hideShareModal() {
    this.setData({ showShareModal: false })
  },

  // 分享给朋友
  shareToFriend() {
    this.hideShareModal()
    
    const { resultData } = this.data
    const shareData = {
      title: `AI检测结果: ${resultData.foodName}`,
      path: `/pages/detection/result?data=${encodeURIComponent(JSON.stringify(resultData))}`,
      imageUrl: resultData.image
    }
    
    // 触发分享
    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage']
    })
    
    app.showSuccess('请点击右上角分享')
  },

  // 分享到朋友圈
  shareToMoments() {
    this.hideShareModal()
    
    const { resultData } = this.data
    const shareData = {
      title: `AI检测结果: ${resultData.foodName} - ${this.getSafetyTitle(resultData.safetyLevel)}`,
      imageUrl: resultData.image
    }
    
    // 触发朋友圈分享
    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareTimeline']
    })
    
    app.showSuccess('请点击右上角分享到朋友圈')
  },

  // 复制链接
  copyLink() {
    this.hideShareModal()
    
    const { resultData } = this.data
    const shareUrl = `https://your-domain.com/share/result?id=${resultData.id || Date.now()}`
    
    wx.setClipboardData({
      data: shareUrl,
      success: () => {
        app.showSuccess('链接已复制到剪贴板')
      },
      fail: () => {
        app.showError('复制失败')
      }
    })
  },

  // 保存到相册
  saveToAlbum() {
    const { resultData } = this.data
    
    if (!resultData.image) {
      app.showError('没有可保存的图片')
      return
    }

    app.showLoading('保存中...')
    
    // 如果是网络图片，先下载
    if (resultData.image.startsWith('http')) {
      wx.downloadFile({
        url: resultData.image,
        success: (res) => {
          if (res.statusCode === 200) {
            this.saveImageToAlbum(res.tempFilePath)
          } else {
            app.showError('下载图片失败')
          }
        },
        fail: () => {
          app.showError('下载图片失败')
        },
        complete: () => {
          app.hideLoading()
        }
      })
    } else {
      // 本地图片直接保存
      this.saveImageToAlbum(resultData.image)
      app.hideLoading()
    }
  },

  // 保存图片到相册
  saveImageToAlbum(imagePath) {
    wx.saveImageToPhotosAlbum({
      filePath: imagePath,
      success: () => {
        app.showSuccess('已保存到相册')
      },
      fail: (error) => {
        console.error('保存到相册失败:', error)
        if (error.errMsg.includes('auth')) {
          wx.showModal({
            title: '需要授权',
            content: '需要您授权保存图片到相册',
            confirmText: '去设置',
            success: (res) => {
              if (res.confirm) {
                wx.openSetting()
              }
            }
          })
        } else {
          app.showError('保存失败')
        }
      }
    })
  },

  // 再次检测
  detectAgain() {
    wx.navigateBack({
      delta: 1
    })
  },

  // 查看推荐内容
  viewRecommendation(e) {
    const item = e.currentTarget.dataset.item
    console.log('查看推荐:', item)
    
    wx.navigateTo({
      url: `/pages/education/article?id=${item.id}`,
      fail: () => {
        app.showError('页面暂未开放')
      }
    })
  },

  // 举报问题
  reportIssue() {
    const { resultData } = this.data
    
    wx.showModal({
      title: '举报问题',
      content: '请选择举报原因',
      showCancel: true,
      confirmText: '继续举报',
      success: (res) => {
        if (res.confirm) {
          this.showReportOptions()
        }
      }
    })
  },

  // 显示举报选项
  showReportOptions() {
    wx.showActionSheet({
      itemList: [
        '检测结果不准确',
        '食品信息错误',
        '系统故障',
        '其他问题'
      ],
      success: (res) => {
        const reasons = [
          '检测结果不准确',
          '食品信息错误',
          '系统故障',
          '其他问题'
        ]
        
        this.submitReport(reasons[res.tapIndex])
      }
    })
  },

  // 提交举报
  submitReport(reason) {
    const { resultData } = this.data
    
    app.showLoading('提交中...')
    
    app.request({
      url: '/api/v1/reports/create',
      method: 'POST',
      data: {
        type: 'detection_result',
        targetId: resultData.id || Date.now(),
        reason: reason,
        description: `检测结果举报: ${resultData.foodName}`,
        evidence: {
          image: resultData.image,
          detectionData: resultData
        }
      },
      success: (res) => {
        if (res.statusCode === 200) {
          app.showSuccess('举报已提交，感谢您的反馈')
        } else {
          app.showError('提交失败，请重试')
        }
      },
      fail: (error) => {
        console.error('提交举报失败:', error)
        app.showError('提交失败，请重试')
      },
      complete: () => {
        app.hideLoading()
      }
    })
  },

  // 加载相关推荐
  loadRecommendations() {
    const { resultData } = this.data
    
    app.request({
      url: '/api/v1/recommendations',
      method: 'GET',
      data: {
        type: 'detection_result',
        foodType: resultData.foodName,
        safetyLevel: resultData.safetyLevel
      },
      success: (res) => {
        if (res.statusCode === 200 && res.data.recommendations) {
          this.setData({
            recommendations: res.data.recommendations
          })
        }
      },
      fail: (error) => {
        console.warn('加载推荐失败:', error)
      }
    })
  },

  // 加载专家点评
  loadExpertComment() {
    const { resultData } = this.data
    
    app.request({
      url: '/api/v1/expert/comment',
      method: 'GET',
      data: {
        foodType: resultData.foodName,
        safetyLevel: resultData.safetyLevel,
        detectionId: resultData.id
      },
      success: (res) => {
        if (res.statusCode === 200 && res.data.comment) {
          this.setData({
            expertComment: res.data.comment
          })
        }
      },
      fail: (error) => {
        console.warn('加载专家点评失败:', error)
      }
    })
  },

  // 页面分享
  onShareAppMessage() {
    const { resultData } = this.data
    return {
      title: `AI检测结果: ${resultData.foodName} - ${this.getSafetyTitle(resultData.safetyLevel)}`,
      path: `/pages/detection/result?data=${encodeURIComponent(JSON.stringify(resultData))}`,
      imageUrl: resultData.image
    }
  },

  // 分享到朋友圈
  onShareTimeline() {
    const { resultData } = this.data
    return {
      title: `AI检测结果: ${resultData.foodName} - ${this.getSafetyTitle(resultData.safetyLevel)}`,
      imageUrl: resultData.image
    }
  }
})