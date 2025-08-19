// app.js
App({
  onLaunch() {
    console.log('社区食安AI小卫士启动')
    
    // 检查更新
    this.checkForUpdate()
    
    // 初始化全局数据
    this.initGlobalData()
    
    // 检查登录状态
    this.checkLoginStatus()
    
    // 获取系统信息
    this.getSystemInfo()
  },

  onShow() {
    console.log('应用显示')
  },

  onHide() {
    console.log('应用隐藏')
  },

  onError(msg) {
    console.error('应用错误:', msg)
  },

  // 检查小程序更新
  checkForUpdate() {
    if (wx.canIUse('getUpdateManager')) {
      const updateManager = wx.getUpdateManager()
      
      updateManager.onCheckForUpdate((res) => {
        if (res.hasUpdate) {
          console.log('发现新版本')
        }
      })
      
      updateManager.onUpdateReady(() => {
        wx.showModal({
          title: '更新提示',
          content: '新版本已经准备好，是否重启应用？',
          success: (res) => {
            if (res.confirm) {
              updateManager.applyUpdate()
            }
          }
        })
      })
      
      updateManager.onUpdateFailed(() => {
        console.error('新版本下载失败')
      })
    }
  },

  // 初始化全局数据
  initGlobalData() {
    this.globalData = {
      userInfo: null,
      token: null,
      systemInfo: null,
      apiBaseUrl: 'http://127.0.0.1:8000/api/v1',
      isLoggedIn: false,
      userLocation: null,
      detectionHistory: [],
      reportHistory: []
    }
  },

  // 检查登录状态
  checkLoginStatus() {
    const token = wx.getStorageSync('token')
    const userInfo = wx.getStorageSync('userInfo')
    
    if (token && userInfo) {
      this.globalData.token = token
      this.globalData.userInfo = userInfo
      this.globalData.isLoggedIn = true
      
      // 验证token有效性
      this.validateToken()
    }
  },

  // 验证token有效性
  validateToken() {
    wx.request({
      url: `${this.globalData.apiBaseUrl}/auth/validate`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${this.globalData.token}`
      },
      success: (res) => {
        if (res.statusCode !== 200) {
          this.logout()
        }
      },
      fail: () => {
        this.logout()
      }
    })
  },

  // 获取系统信息
  getSystemInfo() {
    wx.getSystemInfo({
      success: (res) => {
        this.globalData.systemInfo = res
        console.log('系统信息:', res)
      }
    })
  },

  // 登录方法
  login(userInfo, callback) {
    wx.login({
      success: (res) => {
        if (res.code) {
          // 发送code到后端
          wx.request({
            url: `${this.globalData.apiBaseUrl}/auth/wechat/login`,
            method: 'POST',
            data: {
              code: res.code,
              userInfo: userInfo
            },
            success: (response) => {
              if (response.statusCode === 200) {
                const { token, user } = response.data
                
                // 保存登录信息
                this.globalData.token = token
                this.globalData.userInfo = user
                this.globalData.isLoggedIn = true
                
                // 持久化存储
                wx.setStorageSync('token', token)
                wx.setStorageSync('userInfo', user)
                
                if (callback) callback(true, user)
              } else {
                if (callback) callback(false, response.data.message)
              }
            },
            fail: (error) => {
              console.error('登录失败:', error)
              if (callback) callback(false, '网络错误')
            }
          })
        } else {
          console.error('获取用户登录态失败:', res.errMsg)
          if (callback) callback(false, '获取登录态失败')
        }
      }
    })
  },

  // 登出方法
  logout() {
    this.globalData.token = null
    this.globalData.userInfo = null
    this.globalData.isLoggedIn = false
    
    wx.removeStorageSync('token')
    wx.removeStorageSync('userInfo')
    
    console.log('用户已登出')
  },

  // 获取用户位置
  getUserLocation(callback) {
    wx.getLocation({
      type: 'gcj02',
      success: (res) => {
        this.globalData.userLocation = {
          latitude: res.latitude,
          longitude: res.longitude
        }
        if (callback) callback(true, res)
      },
      fail: (error) => {
        console.error('获取位置失败:', error)
        if (callback) callback(false, error)
      }
    })
  },

  // 显示加载提示
  showLoading(title = '加载中...') {
    wx.showLoading({
      title: title,
      mask: true
    })
  },

  // 隐藏加载提示
  hideLoading() {
    wx.hideLoading()
  },

  // 显示成功提示
  showSuccess(title) {
    wx.showToast({
      title: title,
      icon: 'success',
      duration: 2000
    })
  },

  // 显示错误提示
  showError(title) {
    wx.showToast({
      title: title,
      icon: 'none',
      duration: 2000
    })
  },

  // 网络请求封装
  request(options) {
    const { url, method = 'GET', data = {}, header = {}, success, fail, complete } = options
    
    // 添加token
    if (this.globalData.token) {
      header['Authorization'] = `Bearer ${this.globalData.token}`
    }
    
    wx.request({
      url: url.startsWith('http') ? url : `${this.globalData.apiBaseUrl}${url}`,
      method: method,
      data: data,
      header: {
        'Content-Type': 'application/json',
        ...header
      },
      success: (res) => {
        if (res.statusCode === 401) {
          // token过期，重新登录
          this.logout()
          wx.showModal({
            title: '提示',
            content: '登录已过期，请重新登录',
            showCancel: false,
            success: () => {
              wx.switchTab({ url: '/pages/profile/profile' })
            }
          })
          return
        }
        
        if (success) success(res)
      },
      fail: (error) => {
        console.error('网络请求失败:', error)
        if (fail) fail(error)
      },
      complete: (res) => {
        // 确保complete回调被正确执行，用于隐藏loading状态
        if (complete) complete(res)
      }
    })
  }
})