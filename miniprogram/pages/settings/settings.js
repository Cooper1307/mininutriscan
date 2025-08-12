// 设置页面逻辑
Page({
  /**
   * 页面的初始数据
   */
  data: {
    // 用户信息
    userInfo: {
      nickname: '',
      isLogin: false
    },
    
    // 通知设置
    notifications: {
      detection: true,      // 检测结果通知
      system: true,         // 系统公告
      recommendation: false // 个性化推荐
    },
    
    // 应用设置
    language: '简体中文',
    darkMode: false,
    vibration: true,
    cacheSize: '12.5MB',
    
    // 检测设置
    detection: {
      autoSave: true,    // 自动保存检测图片
      quality: '高精度',  // 检测精度
      fastMode: false    // 快速检测模式
    },
    
    // 版本信息
    version: '1.0.0',
    
    // 选择器相关
    showPicker: false,
    pickerTitle: '',
    pickerValue: [0],
    pickerOptions: [],
    currentPickerType: ''
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    this.loadUserInfo();
    this.loadSettings();
    this.calculateCacheSize();
  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {
    this.loadUserInfo();
  },

  /**
   * 加载用户信息
   */
  loadUserInfo() {
    try {
      const userInfo = wx.getStorageSync('userInfo') || {};
      this.setData({
        'userInfo.nickname': userInfo.nickname || '未设置',
        'userInfo.isLogin': userInfo.isLogin || false
      });
    } catch (error) {
      console.error('加载用户信息失败:', error);
    }
  },

  /**
   * 加载设置信息
   */
  loadSettings() {
    try {
      const settings = wx.getStorageSync('appSettings') || {};
      
      this.setData({
        notifications: {
          detection: settings.notifications?.detection !== false,
          system: settings.notifications?.system !== false,
          recommendation: settings.notifications?.recommendation || false
        },
        language: settings.language || '简体中文',
        darkMode: settings.darkMode || false,
        vibration: settings.vibration !== false,
        detection: {
          autoSave: settings.detection?.autoSave !== false,
          quality: settings.detection?.quality || '高精度',
          fastMode: settings.detection?.fastMode || false
        }
      });
    } catch (error) {
      console.error('加载设置失败:', error);
    }
  },

  /**
   * 保存设置
   */
  saveSettings() {
    try {
      const settings = {
        notifications: this.data.notifications,
        language: this.data.language,
        darkMode: this.data.darkMode,
        vibration: this.data.vibration,
        detection: this.data.detection
      };
      
      wx.setStorageSync('appSettings', settings);
    } catch (error) {
      console.error('保存设置失败:', error);
      wx.showToast({
        title: '保存失败',
        icon: 'error'
      });
    }
  },

  /**
   * 计算缓存大小
   */
  calculateCacheSize() {
    // 模拟计算缓存大小
    const sizes = ['8.2MB', '12.5MB', '15.8MB', '20.1MB', '25.6MB'];
    const randomSize = sizes[Math.floor(Math.random() * sizes.length)];
    this.setData({
      cacheSize: randomSize
    });
  },

  /**
   * 个人资料编辑
   */
  onProfileEdit() {
    wx.navigateTo({
      url: '/pages/profile/edit/edit'
    });
  },

  /**
   * 修改密码
   */
  onPasswordChange() {
    wx.navigateTo({
      url: '/pages/auth/password/password'
    });
  },

  /**
   * 隐私设置
   */
  onPrivacySettings() {
    wx.navigateTo({
      url: '/pages/settings/privacy/privacy'
    });
  },

  /**
   * 通知设置变更
   */
  onNotificationChange(e) {
    const type = e.currentTarget.dataset.type;
    const value = e.detail.value;
    
    this.setData({
      [`notifications.${type}`]: value
    });
    
    this.saveSettings();
    
    // 震动反馈
    if (this.data.vibration) {
      wx.vibrateShort();
    }
  },

  /**
   * 语言选择
   */
  onLanguageSelect() {
    const options = [
      { label: '简体中文', value: '简体中文' },
      { label: '繁體中文', value: '繁體中文' },
      { label: 'English', value: 'English' }
    ];
    
    const currentIndex = options.findIndex(item => item.value === this.data.language);
    
    this.setData({
      showPicker: true,
      pickerTitle: '选择语言',
      pickerOptions: options,
      pickerValue: [currentIndex >= 0 ? currentIndex : 0],
      currentPickerType: 'language'
    });
  },

  /**
   * 深色模式切换
   */
  onDarkModeChange(e) {
    const value = e.detail.value;
    
    this.setData({
      darkMode: value
    });
    
    this.saveSettings();
    
    // 震动反馈
    if (this.data.vibration) {
      wx.vibrateShort();
    }
    
    wx.showToast({
      title: value ? '已开启深色模式' : '已关闭深色模式',
      icon: 'success'
    });
  },

  /**
   * 震动反馈切换
   */
  onVibrationChange(e) {
    const value = e.detail.value;
    
    this.setData({
      vibration: value
    });
    
    this.saveSettings();
    
    // 震动反馈（如果开启）
    if (value) {
      wx.vibrateShort();
    }
  },

  /**
   * 缓存管理
   */
  onCacheManage() {
    wx.showActionSheet({
      itemList: ['清理图片缓存', '清理检测记录', '清理全部缓存'],
      success: (res) => {
        const actions = [
          () => this.clearImageCache(),
          () => this.clearDetectionCache(),
          () => this.clearAllCache()
        ];
        
        if (res.tapIndex < actions.length) {
          actions[res.tapIndex]();
        }
      }
    });
  },

  /**
   * 清理图片缓存
   */
  clearImageCache() {
    wx.showLoading({ title: '清理中...' });
    
    setTimeout(() => {
      wx.hideLoading();
      this.calculateCacheSize();
      wx.showToast({
        title: '图片缓存已清理',
        icon: 'success'
      });
    }, 1500);
  },

  /**
   * 清理检测记录缓存
   */
  clearDetectionCache() {
    wx.showModal({
      title: '确认清理',
      content: '清理后检测历史记录将被删除，是否继续？',
      success: (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '清理中...' });
          
          setTimeout(() => {
            wx.removeStorageSync('detectionHistory');
            wx.hideLoading();
            this.calculateCacheSize();
            wx.showToast({
              title: '检测记录已清理',
              icon: 'success'
            });
          }, 1000);
        }
      }
    });
  },

  /**
   * 清理全部缓存
   */
  clearAllCache() {
    wx.showModal({
      title: '确认清理',
      content: '清理后所有缓存数据将被删除，是否继续？',
      success: (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '清理中...' });
          
          setTimeout(() => {
            wx.clearStorageSync();
            wx.hideLoading();
            this.setData({
              cacheSize: '0MB'
            });
            wx.showToast({
              title: '缓存已清理',
              icon: 'success'
            });
          }, 2000);
        }
      }
    });
  },

  /**
   * 检测设置变更
   */
  onDetectionSettingChange(e) {
    const type = e.currentTarget.dataset.type;
    const value = e.detail.value;
    
    this.setData({
      [`detection.${type}`]: value
    });
    
    this.saveSettings();
    
    // 震动反馈
    if (this.data.vibration) {
      wx.vibrateShort();
    }
  },

  /**
   * 检测精度选择
   */
  onQualitySelect() {
    const options = [
      { label: '标准', value: '标准' },
      { label: '高精度', value: '高精度' },
      { label: '超高精度', value: '超高精度' }
    ];
    
    const currentIndex = options.findIndex(item => item.value === this.data.detection.quality);
    
    this.setData({
      showPicker: true,
      pickerTitle: '选择检测精度',
      pickerOptions: options,
      pickerValue: [currentIndex >= 0 ? currentIndex : 1],
      currentPickerType: 'quality'
    });
  },

  /**
   * 检查更新
   */
  onCheckUpdate() {
    wx.showLoading({ title: '检查中...' });
    
    // 模拟检查更新
    setTimeout(() => {
      wx.hideLoading();
      wx.showModal({
        title: '检查更新',
        content: '当前已是最新版本',
        showCancel: false
      });
    }, 1500);
  },

  /**
   * 意见反馈
   */
  onFeedback() {
    wx.navigateTo({
      url: '/pages/feedback/feedback'
    });
  },

  /**
   * 关于我们
   */
  onAbout() {
    wx.navigateTo({
      url: '/pages/about/about'
    });
  },

  /**
   * 退出登录
   */
  onLogout() {
    wx.showModal({
      title: '确认退出',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          // 清除用户信息
          wx.removeStorageSync('userInfo');
          wx.removeStorageSync('token');
          
          this.setData({
            'userInfo.isLogin': false,
            'userInfo.nickname': '未设置'
          });
          
          wx.showToast({
            title: '已退出登录',
            icon: 'success'
          });
          
          // 返回上一页或首页
          setTimeout(() => {
            wx.navigateBack({
              fail: () => {
                wx.switchTab({
                  url: '/pages/index/index'
                });
              }
            });
          }, 1500);
        }
      }
    });
  },

  /**
   * 选择器变更
   */
  onPickerChange(e) {
    this.setData({
      pickerValue: e.detail.value
    });
  },

  /**
   * 选择器确认
   */
  onPickerConfirm() {
    const index = this.data.pickerValue[0];
    const selectedOption = this.data.pickerOptions[index];
    
    if (this.data.currentPickerType === 'language') {
      this.setData({
        language: selectedOption.value,
        showPicker: false
      });
      this.saveSettings();
      
      wx.showToast({
        title: `已切换到${selectedOption.label}`,
        icon: 'success'
      });
    } else if (this.data.currentPickerType === 'quality') {
      this.setData({
        'detection.quality': selectedOption.value,
        showPicker: false
      });
      this.saveSettings();
      
      wx.showToast({
        title: `检测精度已设为${selectedOption.label}`,
        icon: 'success'
      });
    }
  },

  /**
   * 选择器取消
   */
  onPickerCancel() {
    this.setData({
      showPicker: false
    });
  },

  /**
   * 阻止事件冒泡
   */
  stopPropagation() {
    // 阻止事件冒泡
  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {
    return {
      title: 'NutriScan - 智能食品安全检测',
      path: '/pages/index/index'
    };
  },

  /**
   * 用户点击右上角分享到朋友圈
   */
  onShareTimeline() {
    return {
      title: 'NutriScan - 智能食品安全检测'
    };
  }
});