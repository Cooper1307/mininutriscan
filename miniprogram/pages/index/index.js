// pages/index/index.js
const app = getApp()

Page({
  data: {
    userLocation: '普陀区长风街道',
    notificationCount: 3,
    todayDetections: 23,
    todayReports: 2,
    quickActions: [
      { id: 1, icon: '🔍', label: 'AI检测', action: 'detection' },
      { id: 2, icon: '📷', label: '拍照识别', action: 'camera' },
      { id: 3, icon: '📢', label: '举报问题', action: 'report' },
      { id: 4, icon: '📚', label: '学习科普', action: 'education' }
    ],
    communityNews: [
      {
        id: 1,
        title: '🔴 紧急通知: XX超市食品召回',
        date: '2024-01-15',
        views: 156,
        urgent: true
      },
      {
        id: 2,
        title: '✅ 志愿者活动: 食品安全宣传周',
        date: '2024-01-12',
        views: 89,
        urgent: false
      },
      {
        id: 3,
        title: '📊 本月食品安全检测报告发布',
        date: '2024-01-10',
        views: 234,
        urgent: false
      }
    ],
    recommendations: [
      { id: 1, title: '冬季养生食谱推荐' },
      { id: 2, title: '如何识别过期食品' },
      { id: 3, title: '食品添加剂安全知识' }
    ]
  },

  onLoad() {
    console.log('首页加载')
    // 确保数据已初始化
    this.setData({
      userLocation: this.data.userLocation,
      notificationCount: this.data.notificationCount,
      todayDetections: this.data.todayDetections,
      todayReports: this.data.todayReports,
      quickActions: this.data.quickActions,
      communityNews: this.data.communityNews,
      recommendations: this.data.recommendations
    })
    
    // 统一管理loading状态，避免多个请求同时显示loading
    this.loadAllData()
  },

  onShow() {
    console.log('首页显示')
    // 页面显示时不自动刷新，避免频繁loading
  },

  onPullDownRefresh() {
    console.log('下拉刷新')
    this.refreshData()
  },

  // 快速功能点击
  onQuickActionTap(e) {
    const action = e.detail
    console.log('快速功能点击:', action)
    
    switch (action.action) {
      case 'detection':
        wx.navigateTo({ url: '/pages/detection/detection' })
        break
      case 'camera':
        this.openCamera()
        break
      case 'report':
        wx.navigateTo({ url: '/pages/report/report' })
        break
      case 'education':
        wx.switchTab({ url: '/pages/education/education' })
        break
      default:
        app.showError('功能暂未开放')
    }
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
        
        wx.navigateTo({
          url: `/pages/detection/result?image=${encodeURIComponent(imagePath)}`
        })
      },
      fail: (error) => {
        console.error('拍照失败:', error)
        if (error.errMsg.includes('cancel')) {
          return // 用户取消，不显示错误
        }
        app.showError('拍照失败，请检查相机权限')
      }
    })
  },

  // 通知点击
  onNotificationTap() {
    console.log('通知点击')
    wx.navigateTo({ 
      url: '/pages/notifications/notifications',
      fail: () => {
        app.showError('通知页面暂未开放')
      }
    })
  },

  // 设置点击
  onSettingsTap() {
    console.log('设置点击')
    wx.navigateTo({ 
      url: '/pages/settings/settings',
      fail: () => {
        app.showError('设置页面暂未开放')
      }
    })
  },

  // 新闻项点击
  onNewsItemTap(e) {
    const news = e.currentTarget.dataset.news
    console.log('新闻点击:', news)
    
    wx.navigateTo({
      url: `/pages/news/detail?id=${news.id}`,
      fail: () => {
        app.showError('新闻详情页面暂未开放')
      }
    })
  },

  // 推荐项点击
  onRecommendationTap(e) {
    const item = e.currentTarget.dataset.item
    console.log('推荐点击:', item)
    
    wx.navigateTo({
      url: `/pages/education/article?id=${item.id}`,
      fail: () => {
        app.showError('文章页面暂未开放')
      }
    })
  },

  // 查看更多推荐
  onViewMoreRecommendations() {
    console.log('查看更多推荐')
    wx.switchTab({ url: '/pages/education/education' })
  },

  // 统一加载所有数据，避免多个loading状态冲突
  loadAllData() {
    console.log('开始加载数据')
    app.showLoading('加载中...')
    
    // 设置超时保护，确保loading状态能被正确隐藏
    const timeout = new Promise((resolve) => {
      setTimeout(() => {
        console.warn('数据加载超时，强制隐藏loading')
        resolve()
      }, 10000) // 10秒超时
    })
    
    // 并行执行所有数据加载请求，添加超时保护
    Promise.race([
      Promise.all([
        this.loadUserDataAsync().catch(err => console.warn('用户数据加载失败:', err)),
        this.loadCommunityDataAsync().catch(err => console.warn('社区数据加载失败:', err)),
        this.loadStatisticsAsync().catch(err => console.warn('统计数据加载失败:', err))
      ]),
      timeout
    ]).finally(() => {
      app.hideLoading()
      console.log('数据加载完成，loading已隐藏')
    })
  },

  // 加载用户数据
  loadUserData() {
    // 获取用户位置
    app.getUserLocation((success, result) => {
      if (success) {
        this.reverseGeocode(result.latitude, result.longitude)
      } else {
        console.warn('获取位置失败:', result)
      }
    })
  },

  // 异步版本的用户数据加载
  loadUserDataAsync() {
    return new Promise((resolve) => {
      wx.getLocation({
        type: 'gcj02',
        success: (res) => {
          this.reverseGeocode(res.latitude, res.longitude)
          resolve()
        },
        fail: () => {
          console.log('获取位置失败，使用默认位置')
          resolve()
        }
      })
    })
  },

  // 加载社区数据
  loadCommunityData() {
    app.showLoading('加载中...')
    
    app.request({
      url: '/community/news',
      method: 'GET',
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            communityNews: res.data.news || this.data.communityNews,
            recommendations: res.data.recommendations || this.data.recommendations
          })
        }
      },
      fail: (error) => {
        console.warn('加载社区数据失败，使用默认数据:', error)
        // 网络请求失败时使用默认数据，确保界面正常显示
        this.setData({
          communityNews: this.data.communityNews,
          recommendations: this.data.recommendations
        })
      },
      complete: () => {
        app.hideLoading()
      }
    })
  },

  // 异步版本的社区数据加载
  loadCommunityDataAsync() {
    return new Promise((resolve) => {
      app.request({
        url: '/community/news',
        method: 'GET',
        success: (res) => {
          if (res.statusCode === 200) {
            this.setData({
              communityNews: res.data.news || this.data.communityNews,
              recommendations: res.data.recommendations || this.data.recommendations
            })
          }
        },
        fail: (error) => {
          console.warn('加载社区数据失败，使用默认数据:', error)
          // 网络请求失败时使用默认数据，确保界面正常显示
          this.setData({
            communityNews: this.data.communityNews,
            recommendations: this.data.recommendations
          })
        },
        complete: () => {
          // 确保请求完全结束后才resolve
          resolve()
        }
      })
    })
  },

  // 加载统计数据
  loadStatistics() {
    app.request({
      url: '/statistics/today',
      method: 'GET',
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            todayDetections: res.data.detections || this.data.todayDetections,
            todayReports: res.data.reports || this.data.todayReports,
            notificationCount: res.data.notifications || this.data.notificationCount
          })
        }
      },
      fail: (error) => {
        console.warn('加载统计数据失败，使用默认数据:', error)
        // 网络请求失败时使用默认数据，确保界面正常显示
        this.setData({
          todayDetections: this.data.todayDetections,
          todayReports: this.data.todayReports,
          notificationCount: this.data.notificationCount
        })
      }
    })
  },

  // 异步版本的统计数据加载
  loadStatisticsAsync() {
    return new Promise((resolve) => {
      app.request({
        url: '/statistics/today',
        method: 'GET',
        success: (res) => {
          if (res.statusCode === 200) {
            this.setData({
              todayDetections: res.data.detections || this.data.todayDetections,
              todayReports: res.data.reports || this.data.todayReports,
              notificationCount: res.data.notifications || this.data.notificationCount
            })
          }
        },
        fail: (error) => {
          console.warn('加载统计数据失败，使用默认数据:', error)
          // 网络请求失败时使用默认数据，确保界面正常显示
          this.setData({
            todayDetections: this.data.todayDetections,
            todayReports: this.data.todayReports,
            notificationCount: this.data.notificationCount
          })
        },
        complete: () => {
          // 确保请求完全结束后才resolve
          resolve()
        }
      })
    })
  },

  // 刷新数据
  refreshData() {
    Promise.all([
      this.loadCommunityDataAsync(),
      this.loadStatisticsAsync(),
      this.loadUserDataAsync()
    ]).finally(() => {
      wx.stopPullDownRefresh()
      app.showSuccess('刷新成功')
    })
  },

  // 逆地理编码
  reverseGeocode(lat, lng) {
    // 这里应该调用地图API获取地址
    // 由于需要API密钥，这里使用模拟数据
    const mockAddresses = [
      '普陀区长风街道',
      '黄浦区南京东路',
      '徐汇区衡山路',
      '静安区南京西路',
      '虹口区四川北路'
    ]
    
    const randomAddress = mockAddresses[Math.floor(Math.random() * mockAddresses.length)]
    this.setData({ userLocation: randomAddress })
    
    // 实际实现示例（需要腾讯地图API密钥）:
    /*
    wx.request({
      url: `https://apis.map.qq.com/ws/geocoder/v1/?location=${lat},${lng}&key=YOUR_KEY`,
      success: (res) => {
        if (res.data.status === 0) {
          const address = res.data.result.formatted_addresses.recommend
          this.setData({ userLocation: address })
        }
      },
      fail: (error) => {
        console.error('逆地理编码失败:', error)
      }
    })
    */
  },

  // 分享功能
  onShareAppMessage() {
    return {
      title: '社区食安AI小卫士 - 守护您的餐桌安全',
      path: '/pages/index/index',
      imageUrl: '/assets/images/share-cover.jpg'
    }
  },

  // 分享到朋友圈
  onShareTimeline() {
    return {
      title: '社区食安AI小卫士 - 守护您的餐桌安全',
      imageUrl: '/assets/images/share-cover.jpg'
    }
  }
})