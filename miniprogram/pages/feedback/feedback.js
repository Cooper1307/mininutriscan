// 意见反馈页面逻辑
Page({
  /**
   * 页面的初始数据
   */
  data: {
    // 反馈类型选项
    feedbackTypes: [
      { id: 'bug', icon: '🐛', text: '功能异常' },
      { id: 'suggestion', icon: '💡', text: '功能建议' },
      { id: 'ui', icon: '🎨', text: '界面问题' },
      { id: 'other', icon: '💬', text: '其他问题' }
    ],
    
    // 表单数据
    formData: {
      type: '', // 反馈类型
      title: '', // 问题标题
      description: '', // 详细描述
      contact: {
        wechat: '', // 微信号
        phone: '', // 手机号
        email: '' // 邮箱
      },
      images: [] // 上传的图片
    },
    
    // 字符计数
    titleCount: 0,
    descCount: 0,
    
    // 设备信息
    deviceInfo: {
      model: '', // 设备型号
      system: '', // 系统版本
      version: '', // 微信版本
      platform: '', // 平台
      appVersion: '1.0.0' // 应用版本
    },
    
    // 提交状态
    isSubmitting: false,
    
    // 历史反馈
    historyList: [],
    showHistory: false,
    
    // 常见问题
    faqList: [
      {
        question: '如何提高检测准确率？',
        answer: '请确保拍摄清晰、光线充足，食物完整可见。'
      },
      {
        question: '为什么检测结果不准确？',
        answer: '可能是光线不足或食物遮挡，建议重新拍摄。'
      },
      {
        question: '如何联系客服？',
        answer: '可通过意见反馈或拨打客服电话400-123-4567。'
      }
    ],
    showFaq: false
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    // 获取设备信息
    this.getDeviceInfo();
    
    // 加载历史反馈
    this.loadHistoryFeedback();
    
    // 如果有传入的反馈类型，自动选择
    if (options.type) {
      this.setData({
        'formData.type': options.type
      });
    }
  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {
    // 刷新历史反馈
    this.loadHistoryFeedback();
  },

  /**
   * 获取设备信息
   */
  getDeviceInfo() {
    const systemInfo = wx.getSystemInfoSync();
    const accountInfo = wx.getAccountInfoSync();
    
    this.setData({
      deviceInfo: {
        model: systemInfo.model,
        system: `${systemInfo.system} ${systemInfo.version}`,
        version: systemInfo.version,
        platform: systemInfo.platform,
        appVersion: accountInfo.miniProgram.version || '1.0.0'
      }
    });
  },

  /**
   * 选择反馈类型
   */
  selectType(e) {
    const type = e.currentTarget.dataset.type;
    this.setData({
      'formData.type': type
    });
    
    // 触觉反馈
    wx.vibrateShort({
      type: 'light'
    });
  },

  /**
   * 输入标题
   */
  onTitleInput(e) {
    const value = e.detail.value;
    this.setData({
      'formData.title': value,
      titleCount: value.length
    });
  },

  /**
   * 输入描述
   */
  onDescInput(e) {
    const value = e.detail.value;
    this.setData({
      'formData.description': value,
      descCount: value.length
    });
  },

  /**
   * 输入联系方式
   */
  onContactInput(e) {
    const { field } = e.currentTarget.dataset;
    const value = e.detail.value;
    this.setData({
      [`formData.contact.${field}`]: value
    });
  },

  /**
   * 选择图片
   */
  chooseImage() {
    const { images } = this.data.formData;
    const remainCount = 3 - images.length;
    
    if (remainCount <= 0) {
      wx.showModal({
        title: '提示',
        content: '最多只能上传3张图片，请先删除部分图片后再添加',
        showCancel: false
      });
      return;
    }
    
    // 触觉反馈
    wx.vibrateShort({
      type: 'light'
    });
    
    wx.chooseMedia({
      count: remainCount,
      mediaType: ['image'],
      sourceType: ['album', 'camera'],
      maxDuration: 30,
      camera: 'back',
      success: (res) => {
        const newImages = res.tempFiles.map(file => ({
          url: file.tempFilePath,
          size: file.size
        }));
        
        this.setData({
          'formData.images': [...images, ...newImages]
        });
        
        wx.showToast({
          title: '图片添加成功',
          icon: 'success'
        });
      },
      fail: (err) => {
        console.error('选择图片失败:', err);
        
        let errorMsg = '选择图片失败';
        if (err.errMsg && err.errMsg.includes('cancel')) {
          return; // 用户取消，不显示错误
        } else if (err.errMsg && err.errMsg.includes('permission')) {
          errorMsg = '请允许访问相册和相机权限';
        } else if (err.errMsg && err.errMsg.includes('size')) {
          errorMsg = '图片文件过大，请选择较小的图片';
        }
        
        wx.showModal({
          title: '选择图片失败',
          content: errorMsg + '，请重试或联系客服',
          showCancel: false
        });
      }
    });
  },

  /**
   * 预览图片
   */
  previewImage(e) {
    const { index } = e.currentTarget.dataset;
    const { images } = this.data.formData;
    const urls = images.map(img => img.url);
    
    wx.previewImage({
      current: urls[index],
      urls: urls
    });
  },

  /**
   * 删除图片
   */
  deleteImage(e) {
    const { index } = e.currentTarget.dataset;
    const { images } = this.data.formData;
    
    wx.showModal({
      title: '确认删除',
      content: '确定要删除这张图片吗？',
      success: (res) => {
        if (res.confirm) {
          images.splice(index, 1);
          this.setData({
            'formData.images': images
          });
        }
      }
    });
  },

  /**
   * 检查表单有效性
   */
  isFormValid() {
    const { type, title, description } = this.data.formData;
    return type && title.trim() && description.trim();
  },

  /**
   * 提交反馈
   */
  async submitFeedback() {
    if (!this.isFormValid()) {
      const { type, title, description } = this.data.formData;
      let missingFields = [];
      
      if (!type) missingFields.push('反馈类型');
      if (!title.trim()) missingFields.push('问题标题');
      if (!description.trim()) missingFields.push('详细描述');
      
      wx.showModal({
        title: '信息不完整',
        content: `请填写以下必填信息：${missingFields.join('、')}`,
        showCancel: false
      });
      return;
    }
    
    if (this.data.isSubmitting) {
      return;
    }
    
    // 触觉反馈
    wx.vibrateShort({
      type: 'medium'
    });
    
    this.setData({ isSubmitting: true });
    
    try {
      // 上传图片
      const imageUrls = await this.uploadImages();
      
      // 构建提交数据
      const submitData = {
        ...this.data.formData,
        images: imageUrls,
        deviceInfo: this.data.deviceInfo,
        timestamp: Date.now()
      };
      
      // 模拟API调用
      await this.mockSubmitFeedback(submitData);
      
      wx.showModal({
        title: '提交成功',
        content: '感谢您的反馈！我们会尽快处理您的问题，处理结果将通过微信消息通知您。',
        showCancel: false,
        success: () => {
          // 重置表单
          this.resetForm();
          
          // 刷新历史记录
          this.loadHistoryFeedback();
        }
      });
      
    } catch (error) {
      console.error('提交反馈失败:', error);
      
      let errorMsg = '提交失败，请重试';
      if (error.message) {
        if (error.message.includes('network')) {
          errorMsg = '网络连接异常，请检查网络后重试';
        } else if (error.message.includes('upload')) {
          errorMsg = '图片上传失败，请重新选择图片或稍后重试';
        } else if (error.message.includes('server')) {
          errorMsg = '服务器繁忙，请稍后重试';
        }
      }
      
      wx.showModal({
        title: '提交失败',
        content: errorMsg + '\n\n如问题持续存在，请联系客服：400-123-4567',
        confirmText: '重试',
        cancelText: '取消',
        success: (res) => {
          if (res.confirm) {
            // 用户选择重试
            setTimeout(() => {
              this.submitFeedback();
            }, 500);
          }
        }
      });
    } finally {
      this.setData({ isSubmitting: false });
    }
  },

  /**
   * 上传图片
   */
  uploadImages() {
    return new Promise((resolve) => {
      const { images } = this.data.formData;
      
      if (images.length === 0) {
        resolve([]);
        return;
      }
      
      // 模拟上传过程
      setTimeout(() => {
        const urls = images.map((img, index) => 
          `https://example.com/feedback/image_${Date.now()}_${index}.jpg`
        );
        resolve(urls);
      }, 1000);
    });
  },

  /**
   * 模拟提交反馈API
   */
  mockSubmitFeedback(data) {
    return new Promise((resolve) => {
      // 模拟网络延迟
      setTimeout(() => {
        console.log('提交反馈数据:', data);
        
        // 保存到本地存储（模拟）
        const feedbackList = wx.getStorageSync('feedbackHistory') || [];
        const newFeedback = {
          id: Date.now(),
          ...data,
          status: 'pending', // pending, processing, completed, closed
          createTime: new Date().toISOString(),
          updateTime: new Date().toISOString()
        };
        
        feedbackList.unshift(newFeedback);
        wx.setStorageSync('feedbackHistory', feedbackList);
        
        resolve(newFeedback);
      }, 1500);
    });
  },

  /**
   * 重置表单
   */
  resetForm() {
    this.setData({
      formData: {
        type: '',
        title: '',
        description: '',
        contact: {
          wechat: '',
          phone: '',
          email: ''
        },
        images: []
      },
      titleCount: 0,
      descCount: 0
    });
  },

  /**
   * 加载历史反馈
   */
  loadHistoryFeedback() {
    try {
      const historyList = wx.getStorageSync('feedbackHistory') || [];
      this.setData({
        historyList: historyList.slice(0, 5), // 只显示最近5条
        showHistory: historyList.length > 0
      });
    } catch (error) {
      console.error('加载历史反馈失败:', error);
    }
  },

  /**
   * 查看历史反馈详情
   */
  viewHistoryDetail(e) {
    const { id } = e.currentTarget.dataset;
    wx.navigateTo({
      url: `/pages/feedback-detail/feedback-detail?id=${id}`
    });
  },

  /**
   * 查看更多历史
   */
  viewMoreHistory() {
    wx.navigateTo({
      url: '/pages/feedback-history/feedback-history'
    });
  },

  /**
   * 查看常见问题详情
   */
  viewFaqDetail(e) {
    const { index } = e.currentTarget.dataset;
    const faq = this.data.faqList[index];
    
    wx.showModal({
      title: faq.question,
      content: faq.answer,
      showCancel: false,
      confirmText: '知道了'
    });
  },

  /**
   * 查看更多常见问题
   */
  viewMoreFaq() {
    wx.navigateTo({
      url: '/pages/help/help'
    });
  },

  /**
   * 获取状态文本
   */
  getStatusText(status) {
    const statusMap = {
      pending: '待处理',
      processing: '处理中',
      completed: '已完成',
      closed: '已关闭'
    };
    return statusMap[status] || '未知';
  },

  /**
   * 格式化时间
   */
  formatTime(timeStr) {
    const time = new Date(timeStr);
    const now = new Date();
    const diff = now - time;
    
    if (diff < 60000) { // 1分钟内
      return '刚刚';
    } else if (diff < 3600000) { // 1小时内
      return `${Math.floor(diff / 60000)}分钟前`;
    } else if (diff < 86400000) { // 1天内
      return `${Math.floor(diff / 3600000)}小时前`;
    } else {
      return time.toLocaleDateString();
    }
  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {
    return {
      title: 'NutriScan - 智能食品安全检测',
      path: '/pages/index/index',
      imageUrl: '/images/share-bg.svg'
    };
  },

  /**
   * 用户点击右上角分享到朋友圈
   */
  onShareTimeline() {
    return {
      title: 'NutriScan - 智能食品安全检测',
      imageUrl: '/images/share-bg.jpg'
    };
  }
});