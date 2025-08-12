const app = getApp();

Page({
  data: {
    // 用户信息
    userInfo: {
      avatar: '',
      nickname: '',
      level: 'LV1',
      levelDesc: '新手用户',
      detectCount: 0,
      points: 0,
      isVip: false,
      vipExpire: '',
      isLogin: false
    },
    
    // 统计数据
    stats: {
      totalDetections: 0,
      safeCount: 0,
      warningCount: 0,
      totalPoints: 0,
      todayDetections: 0,
      pendingReports: 0
    },
    
    // 应用版本
    version: '1.0.0'
  },

  onLoad() {
    this.loadUserInfo();
    this.loadUserStats();
  },

  onShow() {
    // 页面显示时刷新数据
    this.loadUserInfo();
    this.loadUserStats();
  },

  onPullDownRefresh() {
    this.refreshData();
  },

  // 刷新数据
  async refreshData() {
    try {
      await Promise.all([
        this.loadUserInfo(),
        this.loadUserStats()
      ]);
      
      wx.showToast({
        title: '刷新成功',
        icon: 'success'
      });
    } catch (error) {
      console.error('刷新失败:', error);
      wx.showToast({
        title: '刷新失败',
        icon: 'none'
      });
    } finally {
      wx.stopPullDownRefresh();
    }
  },

  // 加载用户信息
  async loadUserInfo() {
    try {
      const token = wx.getStorageSync('token');
      if (!token) {
        this.setData({
          'userInfo.isLogin': false
        });
        return;
      }

      // 这里应该调用实际的API
      // const result = await app.request({
      //   url: '/api/user/profile',
      //   method: 'GET'
      // });
      
      // 模拟用户数据
      const mockUserInfo = {
        avatar: '/images/default-avatar.png',
        nickname: '营养达人',
        level: 'LV3',
        levelDesc: '资深用户',
        detectCount: 156,
        points: 2580,
        isVip: true,
        vipExpire: '2024-12-31',
        isLogin: true
      };
      
      this.setData({
        userInfo: mockUserInfo
      });
      
    } catch (error) {
      console.error('加载用户信息失败:', error);
    }
  },

  // 加载用户统计
  async loadUserStats() {
    try {
      // 这里应该调用实际的API
      // const result = await app.request({
      //   url: '/api/user/stats',
      //   method: 'GET'
      // });
      
      // 模拟统计数据
      const mockStats = {
        totalDetections: 156,
        safeCount: 128,
        warningCount: 28,
        totalPoints: 2580,
        todayDetections: 3,
        pendingReports: 1
      };
      
      this.setData({
        stats: mockStats
      });
      
    } catch (error) {
      console.error('加载统计数据失败:', error);
    }
  },

  // 设置按钮
  onSettings() {
    wx.navigateTo({
      url: '/pages/settings/settings'
    });
  },

  // 头像点击
  onAvatarTap() {
    if (!this.data.userInfo.isLogin) {
      this.onLogin();
      return;
    }
    
    wx.showActionSheet({
      itemList: ['查看头像', '更换头像'],
      success: (res) => {
        switch (res.tapIndex) {
          case 0:
            this.previewAvatar();
            break;
          case 1:
            this.changeAvatar();
            break;
        }
      }
    });
  },

  // 预览头像
  previewAvatar() {
    const { avatar } = this.data.userInfo;
    if (avatar) {
      wx.previewImage({
        urls: [avatar],
        current: avatar
      });
    }
  },

  // 更换头像
  changeAvatar() {
    wx.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const tempFilePath = res.tempFilePaths[0];
        this.uploadAvatar(tempFilePath);
      }
    });
  },

  // 上传头像
  async uploadAvatar(filePath) {
    wx.showLoading({ title: '上传中...' });
    
    try {
      // 这里应该调用实际的上传API
      // const result = await new Promise((resolve, reject) => {
      //   wx.uploadFile({
      //     url: `${app.globalData.apiBaseUrl}/api/upload/avatar`,
      //     filePath: filePath,
      //     name: 'avatar',
      //     header: {
      //       'Authorization': `Bearer ${wx.getStorageSync('token')}`
      //     },
      //     success: resolve,
      //     fail: reject
      //   });
      // });
      
      // 模拟上传成功
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      this.setData({
        'userInfo.avatar': filePath
      });
      
      wx.showToast({
        title: '头像更新成功',
        icon: 'success'
      });
      
    } catch (error) {
      console.error('上传头像失败:', error);
      wx.showToast({
        title: '上传失败',
        icon: 'none'
      });
    } finally {
      wx.hideLoading();
    }
  },

  // 编辑昵称
  onNameEdit() {
    if (!this.data.userInfo.isLogin) {
      this.onLogin();
      return;
    }
    
    wx.showModal({
      title: '修改昵称',
      editable: true,
      placeholderText: '请输入新昵称',
      success: (res) => {
        if (res.confirm && res.content) {
          this.updateNickname(res.content);
        }
      }
    });
  },

  // 更新昵称
  async updateNickname(nickname) {
    try {
      // 这里应该调用实际的API
      // await app.request({
      //   url: '/api/user/nickname',
      //   method: 'PUT',
      //   data: { nickname }
      // });
      
      this.setData({
        'userInfo.nickname': nickname
      });
      
      wx.showToast({
        title: '昵称更新成功',
        icon: 'success'
      });
      
    } catch (error) {
      console.error('更新昵称失败:', error);
      wx.showToast({
        title: '更新失败',
        icon: 'none'
      });
    }
  },

  // VIP升级
  onVipUpgrade() {
    wx.navigateTo({
      url: '/pages/vip/vip'
    });
  },

  // 统计卡片点击
  onStatTap(e) {
    const type = e.currentTarget.dataset.type;
    
    switch (type) {
      case 'detect':
        wx.navigateTo({
          url: '/pages/history/history'
        });
        break;
      case 'safe':
        wx.navigateTo({
          url: '/pages/history/history?filter=safe'
        });
        break;
      case 'warning':
        wx.navigateTo({
          url: '/pages/history/history?filter=warning'
        });
        break;
      case 'points':
        wx.navigateTo({
          url: '/pages/points/points'
        });
        break;
    }
  },

  // 菜单项点击
  onMenuTap(e) {
    const type = e.currentTarget.dataset.type;
    
    // 需要登录的功能
    const needLoginTypes = ['history', 'favorites', 'reports', 'points', 'invite'];
    if (needLoginTypes.includes(type) && !this.data.userInfo.isLogin) {
      this.onLogin();
      return;
    }
    
    switch (type) {
      case 'history':
        wx.navigateTo({
          url: '/pages/history/history'
        });
        break;
      case 'favorites':
        wx.navigateTo({
          url: '/pages/favorites/favorites'
        });
        break;
      case 'reports':
        wx.navigateTo({
          url: '/pages/report/history'
        });
        break;
      case 'points':
        wx.navigateTo({
          url: '/pages/points/points'
        });
        break;
      case 'invite':
        this.onInviteFriends();
        break;
      case 'feedback':
        wx.navigateTo({
          url: '/pages/feedback/feedback'
        });
        break;
      case 'help':
        wx.navigateTo({
          url: '/pages/help/help'
        });
        break;
      case 'about':
        wx.navigateTo({
          url: '/pages/about/about'
        });
        break;
    }
  },

  // 邀请好友
  onInviteFriends() {
    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage', 'shareTimeline']
    });
    
    wx.showModal({
      title: '邀请好友',
      content: '分享给好友，双方都可获得积分奖励！',
      confirmText: '立即分享',
      success: (res) => {
        if (res.confirm) {
          // 触发分享
          wx.showToast({
            title: '请点击右上角分享',
            icon: 'none'
          });
        }
      }
    });
  },

  // 登录
  onLogin() {
    wx.getUserProfile({
      desc: '用于完善用户资料',
      success: (res) => {
        console.log('用户信息:', res.userInfo);
        this.doLogin(res.userInfo);
      },
      fail: (err) => {
        console.error('获取用户信息失败:', err);
        wx.showToast({
          title: '登录失败',
          icon: 'none'
        });
      }
    });
  },

  // 执行登录
  async doLogin(userInfo) {
    wx.showLoading({ title: '登录中...' });
    
    try {
      // 获取登录凭证
      const loginRes = await new Promise((resolve, reject) => {
        wx.login({
          success: resolve,
          fail: reject
        });
      });
      
      // 这里应该调用实际的登录API
      // const result = await app.request({
      //   url: '/api/auth/login',
      //   method: 'POST',
      //   data: {
      //     code: loginRes.code,
      //     userInfo: userInfo
      //   }
      // });
      
      // 模拟登录成功
      const mockToken = 'mock_token_' + Date.now();
      wx.setStorageSync('token', mockToken);
      
      this.setData({
        'userInfo.isLogin': true,
        'userInfo.avatar': userInfo.avatarUrl,
        'userInfo.nickname': userInfo.nickName
      });
      
      wx.showToast({
        title: '登录成功',
        icon: 'success'
      });
      
      // 重新加载数据
      this.loadUserInfo();
      this.loadUserStats();
      
    } catch (error) {
      console.error('登录失败:', error);
      wx.showToast({
        title: '登录失败',
        icon: 'none'
      });
    } finally {
      wx.hideLoading();
    }
  },

  // 退出登录
  onLogout() {
    wx.showModal({
      title: '确认退出',
      content: '退出登录后将无法使用个性化功能',
      success: (res) => {
        if (res.confirm) {
          this.doLogout();
        }
      }
    });
  },

  // 执行退出登录
  doLogout() {
    // 清除本地存储
    wx.removeStorageSync('token');
    wx.removeStorageSync('userInfo');
    
    // 重置用户信息
    this.setData({
      userInfo: {
        avatar: '',
        nickname: '',
        level: 'LV1',
        levelDesc: '新手用户',
        detectCount: 0,
        points: 0,
        isVip: false,
        vipExpire: '',
        isLogin: false
      },
      stats: {
        totalDetections: 0,
        safeCount: 0,
        warningCount: 0,
        totalPoints: 0,
        todayDetections: 0,
        pendingReports: 0
      }
    });
    
    wx.showToast({
      title: '已退出登录',
      icon: 'success'
    });
  },

  // 底部链接点击
  onFooterTap(e) {
    const type = e.currentTarget.dataset.type;
    
    switch (type) {
      case 'privacy':
        wx.navigateTo({
          url: '/pages/legal/privacy'
        });
        break;
      case 'terms':
        wx.navigateTo({
          url: '/pages/legal/terms'
        });
        break;
      case 'contact':
        wx.showModal({
          title: '联系我们',
          content: '客服电话：400-123-4567\n邮箱：support@mininutriscan.com',
          showCancel: false
        });
        break;
    }
  },

  // 分享给朋友
  onShareAppMessage() {
    return {
      title: '发现一个超好用的食品检测小程序！',
      path: '/pages/index/index',
      imageUrl: '/images/share-profile.png'
    };
  },

  // 分享到朋友圈
  onShareTimeline() {
    return {
      title: '食品安全检测神器，守护健康生活',
      imageUrl: '/images/share-profile.png'
    };
  }
});