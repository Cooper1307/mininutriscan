// app.js
import api from './utils/api.js'
const { API_CONFIG } = require('./config/api')

App({
  // 全局数据
  globalData: {
    userInfo: null,
    hasLogin: false,
    openid: null,
    sessionKey: null,
    baseUrl: API_CONFIG.BASE_URL,
    version: '1.0.0'
  },

  // 应用启动
  onLaunch(options) {
    console.log('小程序启动', options)
    
    // 检查更新
    this.checkForUpdate()
    
    // 初始化用户信息
    this.initUserInfo()
    
    // 设置网络状态监听
    this.setupNetworkListener()
  },

  // 应用显示
  onShow(options) {
    console.log('小程序显示', options)
  },

  // 应用隐藏
  onHide() {
    console.log('小程序隐藏')
  },

  // 应用错误
  onError(error) {
    console.error('小程序错误:', error)
    // 可以在这里上报错误信息
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

  // 初始化用户信息
  initUserInfo() {
    // 从缓存获取用户信息
    const userInfo = wx.getStorageSync('userInfo')
    if (userInfo) {
      this.globalData.userInfo = userInfo
      this.globalData.hasLogin = true
    }
  },

  // 设置网络状态监听
  setupNetworkListener() {
    wx.onNetworkStatusChange((res) => {
      if (!res.isConnected) {
        this.showToast('网络连接已断开', 'none')
      }
    })
  },

  // 显示加载提示
  showLoading(title = '加载中...', mask = true) {
    wx.showLoading({
      title: title,
      mask: mask
    })
  },

  // 隐藏加载提示
  hideLoading() {
    wx.hideLoading()
  },

  // 显示成功提示
  showSuccess(title, duration = 2000) {
    wx.showToast({
      title: title,
      icon: 'success',
      duration: duration
    })
  },

  // 显示错误提示
  showError(title, duration = 2000) {
    wx.showToast({
      title: title,
      icon: 'error',
      duration: duration
    })
  },

  // 显示普通提示
  showToast(title, icon = 'none', duration = 2000) {
    wx.showToast({
      title: title,
      icon: icon,
      duration: duration
    })
  },

  // 网络请求封装
  request(options) {
    // 确保传递完整的配置
    const config = {
      ...options,
      baseUrl: this.globalData.baseUrl
    }
    
    // 如果有success/fail回调，直接使用微信原生请求
    if (options.success || options.fail) {
      const url = options.url.startsWith('http') ? options.url : this.globalData.baseUrl + options.url
      
      return wx.request({
        url,
        method: options.method || 'GET',
        data: options.data,
        header: {
          'Content-Type': 'application/json',
          ...options.header
        },
        timeout: options.timeout || 30000,
        success: options.success,
        fail: options.fail,
        complete: options.complete
      })
    }
    
    // 否则使用封装的api.request
    return api.request(config)
  },

  // 获取用户位置
  getUserLocation(callback) {
    wx.getLocation({
      type: 'gcj02',
      success: (res) => {
        if (callback) callback(true, res)
      },
      fail: (error) => {
        console.warn('获取位置失败:', error)
        if (callback) callback(false, error)
      }
    })
  },

  // 登录
  login() {
    return new Promise((resolve, reject) => {
      wx.login({
        success: (res) => {
          if (res.code) {
            // 发送 res.code 到后台换取 openId, sessionKey, unionId
            this.request({
              url: '/auth/login',
              method: 'POST',
              data: {
                code: res.code
              },
              success: (result) => {
                if (result.statusCode === 200) {
                  this.globalData.openid = result.data.openid
                  this.globalData.sessionKey = result.data.sessionKey
                  this.globalData.hasLogin = true
                  resolve(result.data)
                } else {
                  reject(new Error('登录失败'))
                }
              },
              fail: reject
            })
          } else {
            reject(new Error('获取登录凭证失败'))
          }
        },
        fail: reject
      })
    })
  },

  // 获取用户信息
  getUserInfo() {
    return new Promise((resolve, reject) => {
      if (this.globalData.userInfo) {
        resolve(this.globalData.userInfo)
        return
      }
      
      wx.getUserProfile({
        desc: '用于完善用户资料',
        success: (res) => {
          this.globalData.userInfo = res.userInfo
          wx.setStorageSync('userInfo', res.userInfo)
          resolve(res.userInfo)
        },
        fail: reject
      })
    })
  },

  // 退出登录
  logout() {
    this.globalData.userInfo = null
    this.globalData.hasLogin = false
    this.globalData.openid = null
    this.globalData.sessionKey = null
    wx.removeStorageSync('userInfo')
    wx.removeStorageSync('token')
  }
})