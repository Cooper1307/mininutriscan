// 关于我们页面逻辑
Page({
  /**
   * 页面的初始数据
   */
  data: {
    // 应用版本
    appVersion: '1.0.0',
    
    // 核心功能
    features: [
      {
        id: 1,
        icon: '🔍',
        title: 'AI智能检测',
        description: '基于深度学习的食品安全检测技术'
      },
      {
        id: 2,
        icon: '⚡',
        title: '快速识别',
        description: '3秒内完成食品安全状态分析'
      },
      {
        id: 3,
        icon: '📊',
        title: '详细报告',
        description: '提供全面的食品安全检测报告'
      },
      {
        id: 4,
        icon: '🛡️',
        title: '安全可靠',
        description: '数据加密保护用户隐私安全'
      }
    ],
    
    // 技术优势
    techAdvantages: [
      {
        id: 1,
        icon: '🧠',
        title: '深度学习算法',
        description: '采用最新的深度神经网络技术，识别准确率高达98%'
      },
      {
        id: 2,
        icon: '☁️',
        title: '云端计算',
        description: '强大的云端计算能力，支持大规模并发检测'
      },
      {
        id: 3,
        icon: '📱',
        title: '移动优先',
        description: '专为移动设备优化，随时随地进行食品检测'
      },
      {
        id: 4,
        icon: '🔄',
        title: '持续更新',
        description: '算法模型持续优化，检测能力不断提升'
      }
    ],
    
    // 荣誉资质
    honors: [
      {
        id: 1,
        title: '国家高新技术企业',
        organization: '科技部',
        image: '/images/honor1.svg'
      },
      {
        id: 2,
        title: 'ISO27001认证',
        organization: '国际标准化组织',
        image: '/images/honor2.svg'
      },
      {
        id: 3,
        title: '食品安全创新奖',
        organization: '中国食品工业协会',
        image: '/images/honor3.svg'
      },
      {
        id: 4,
        title: 'AI应用优秀案例',
        organization: '人工智能产业联盟',
        image: '/images/honor4.svg'
      }
    ],
    
    // 联系方式
    contacts: [
      {
        type: 'email',
        icon: '📧',
        label: '邮箱地址',
        value: 'support@nutriscan.com',
        action: '复制',
        selectable: true
      },
      {
        type: 'phone',
        icon: '📞',
        label: '客服电话',
        value: '400-123-4567',
        action: '拨打',
        selectable: true
      },
      {
        type: 'address',
        icon: '📍',
        label: '公司地址',
        value: '北京市朝阳区科技园区创新大厦A座',
        action: '导航',
        selectable: true
      },
      {
        type: 'website',
        icon: '🌐',
        label: '官方网站',
        value: 'www.nutriscan.com',
        action: '访问',
        selectable: true
      }
    ],
    
    // 法律信息
    legalItems: [
      {
        id: 1,
        title: '用户协议',
        url: '/pages/legal/agreement/agreement'
      },
      {
        id: 2,
        title: '隐私政策',
        url: '/pages/legal/privacy/privacy'
      },
      {
        id: 3,
        title: '免责声明',
        url: '/pages/legal/disclaimer/disclaimer'
      },
      {
        id: 4,
        title: '知识产权',
        url: '/pages/legal/copyright/copyright'
      }
    ]
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    this.loadAppInfo();
  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {
    // 页面显示时的逻辑
  },

  /**
   * 加载应用信息
   */
  loadAppInfo() {
    try {
      // 获取应用版本信息
      const accountInfo = wx.getAccountInfoSync();
      if (accountInfo && accountInfo.miniProgram) {
        this.setData({
          appVersion: accountInfo.miniProgram.version || '1.0.0'
        });
      }
    } catch (error) {
      console.error('获取应用信息失败:', error);
    }
  },

  /**
   * 联系方式操作
   */
  onContactAction(e) {
    const { type, value } = e.currentTarget.dataset;
    
    switch (type) {
      case 'email':
        this.copyToClipboard(value, '邮箱地址已复制');
        break;
      case 'phone':
        this.makePhoneCall(value);
        break;
      case 'address':
        this.openLocation();
        break;
      case 'website':
        this.openWebsite(value);
        break;
      default:
        this.copyToClipboard(value);
    }
  },

  /**
   * 复制到剪贴板
   */
  copyToClipboard(text, message = '已复制到剪贴板') {
    wx.setClipboardData({
      data: text,
      success: () => {
        wx.showToast({
          title: message,
          icon: 'success'
        });
      },
      fail: () => {
        wx.showToast({
          title: '复制失败',
          icon: 'error'
        });
      }
    });
  },

  /**
   * 拨打电话
   */
  makePhoneCall(phoneNumber) {
    wx.makePhoneCall({
      phoneNumber: phoneNumber,
      fail: () => {
        wx.showToast({
          title: '拨打失败',
          icon: 'error'
        });
      }
    });
  },

  /**
   * 打开地图定位
   */
  openLocation() {
    wx.openLocation({
      latitude: 39.9042,  // 示例坐标
      longitude: 116.4074,
      name: 'NutriScan总部',
      address: '北京市朝阳区科技园区创新大厦A座',
      scale: 18,
      fail: () => {
        wx.showToast({
          title: '打开地图失败',
          icon: 'error'
        });
      }
    });
  },

  /**
   * 打开网站
   */
  openWebsite(url) {
    // 小程序中无法直接打开外部网站，复制链接
    this.copyToClipboard(`https://${url}`, '网站链接已复制');
  },

  /**
   * 查看法律文档
   */
  onLegalView(e) {
    const { id } = e.currentTarget.dataset;
    const item = this.data.legalItems.find(item => item.id === id);
    
    if (item) {
      wx.navigateTo({
        url: item.url,
        fail: () => {
          // 如果页面不存在，显示提示
          wx.showModal({
            title: '提示',
            content: '该页面正在建设中，敬请期待',
            showCancel: false
          });
        }
      });
    }
  },

  /**
   * 分享应用
   */
  onShareApp() {
    return {
      title: 'NutriScan - 智能食品安全检测专家',
      path: '/pages/index/index',
      imageUrl: '/images/share-logo.svg'
    };
  },

  /**
   * 检查更新
   */
  checkForUpdates() {
    const updateManager = wx.getUpdateManager();
    
    updateManager.onCheckForUpdate((res) => {
      if (res.hasUpdate) {
        wx.showModal({
          title: '发现新版本',
          content: '发现新版本，是否立即更新？',
          success: (modalRes) => {
            if (modalRes.confirm) {
              updateManager.onUpdateReady(() => {
                wx.showModal({
                  title: '更新提示',
                  content: '新版本已准备好，是否重启应用？',
                  success: (restartRes) => {
                    if (restartRes.confirm) {
                      updateManager.applyUpdate();
                    }
                  }
                });
              });
              
              updateManager.onUpdateFailed(() => {
                wx.showToast({
                  title: '更新失败',
                  icon: 'error'
                });
              });
            }
          }
        });
      } else {
        wx.showToast({
          title: '已是最新版本',
          icon: 'success'
        });
      }
    });
  },

  /**
   * 反馈问题
   */
  onFeedback() {
    wx.navigateTo({
      url: '/pages/feedback/feedback'
    });
  },

  /**
   * 联系客服
   */
  onContactService() {
    wx.showActionSheet({
      itemList: ['在线客服', '电话客服', '邮件客服'],
      success: (res) => {
        switch (res.tapIndex) {
          case 0:
            // 在线客服
            wx.showToast({
              title: '正在连接客服...',
              icon: 'loading'
            });
            break;
          case 1:
            // 电话客服
            this.makePhoneCall('400-123-4567');
            break;
          case 2:
            // 邮件客服
            this.copyToClipboard('support@nutriscan.com', '客服邮箱已复制');
            break;
        }
      }
    });
  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {
    return {
      title: 'NutriScan - 智能食品安全检测专家',
      path: '/pages/index/index',
      imageUrl: '/images/share-logo.png'
    };
  },

  /**
   * 用户点击右上角分享到朋友圈
   */
  onShareTimeline() {
    return {
      title: 'NutriScan - 智能食品安全检测专家',
      imageUrl: '/images/share-logo.png'
    };
  }
});