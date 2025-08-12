const app = getApp();

Page({
  data: {
    // 举报类型
    reportTypes: [
      {
        id: 'quality',
        name: '食品质量',
        desc: '变质、过期等',
        icon: '🍎'
      },
      {
        id: 'safety',
        name: '食品安全',
        desc: '有害物质、污染',
        icon: '⚠️'
      },
      {
        id: 'fraud',
        name: '虚假宣传',
        desc: '误导性信息',
        icon: '📢'
      },
      {
        id: 'other',
        name: '其他问题',
        desc: '其他相关问题',
        icon: '❓'
      }
    ],
    selectedType: '',
    
    // 表单数据
    formData: {
      title: '',
      description: '',
      contact: '',
      location: ''
    },
    
    // 上传的文件
    uploadedFiles: [],
    
    // 紧急程度
    urgencyLevels: [
      {
        id: 'low',
        name: '一般',
        desc: '非紧急情况，可正常处理',
        icon: '🟢'
      },
      {
        id: 'medium',
        name: '紧急',
        desc: '需要优先处理',
        icon: '🟡'
      },
      {
        id: 'high',
        name: '非常紧急',
        desc: '立即处理，可能影响健康',
        icon: '🔴'
      }
    ],
    selectedUrgency: 'low',
    
    // 历史举报
    historyReports: [],
    
    // 状态
    isLoading: false,
    isSubmitting: false
  },

  onLoad(options) {
    // 如果从检测结果页面跳转过来，预填充相关信息
    if (options.type) {
      this.setData({
        selectedType: options.type
      });
    }
    
    if (options.title) {
      this.setData({
        'formData.title': decodeURIComponent(options.title)
      });
    }
    
    this.loadHistoryReports();
    this.getCurrentLocation();
  },

  onShow() {
    // 页面显示时刷新历史记录
    this.loadHistoryReports();
  },

  // 选择举报类型
  onTypeSelect(e) {
    const typeId = e.currentTarget.dataset.type;
    this.setData({
      selectedType: typeId
    });
    
    wx.vibrateShort();
  },

  // 表单输入
  onTitleInput(e) {
    this.setData({
      'formData.title': e.detail.value
    });
  },

  onDescriptionInput(e) {
    this.setData({
      'formData.description': e.detail.value
    });
  },

  onContactInput(e) {
    this.setData({
      'formData.contact': e.detail.value
    });
  },

  onLocationInput(e) {
    this.setData({
      'formData.location': e.detail.value
    });
  },

  // 获取当前位置
  getCurrentLocation() {
    wx.getLocation({
      type: 'gcj02',
      success: (res) => {
        // 这里应该调用逆地理编码API获取地址
        // 暂时使用模拟数据
        const mockAddress = '北京市朝阳区建国路88号';
        this.setData({
          'formData.location': mockAddress
        });
      },
      fail: (err) => {
        console.error('获取位置失败:', err);
      }
    });
  },

  // 选择位置
  onLocationTap() {
    wx.chooseLocation({
      success: (res) => {
        this.setData({
          'formData.location': res.address || res.name
        });
      },
      fail: (err) => {
        if (err.errMsg.includes('cancel')) {
          return;
        }
        wx.showToast({
          title: '获取位置失败',
          icon: 'none'
        });
      }
    });
  },

  // 上传文件
  onUploadTap() {
    const { uploadedFiles } = this.data;
    if (uploadedFiles.length >= 9) {
      wx.showToast({
        title: '最多上传9个文件',
        icon: 'none'
      });
      return;
    }

    wx.showActionSheet({
      itemList: ['拍照', '从相册选择', '录制视频'],
      success: (res) => {
        switch (res.tapIndex) {
          case 0:
            this.chooseImage('camera');
            break;
          case 1:
            this.chooseImage('album');
            break;
          case 2:
            this.chooseVideo();
            break;
        }
      }
    });
  },

  // 选择图片
  chooseImage(sourceType) {
    const { uploadedFiles } = this.data;
    const maxCount = 9 - uploadedFiles.length;
    
    wx.chooseImage({
      count: maxCount,
      sizeType: ['compressed'],
      sourceType: [sourceType],
      success: (res) => {
        const newFiles = res.tempFilePaths.map(path => ({
          type: 'image',
          path: path,
          id: Date.now() + Math.random()
        }));
        
        this.setData({
          uploadedFiles: [...uploadedFiles, ...newFiles]
        });
      },
      fail: (err) => {
        console.error('选择图片失败:', err);
      }
    });
  },

  // 选择视频
  chooseVideo() {
    wx.chooseVideo({
      sourceType: ['album', 'camera'],
      maxDuration: 60,
      camera: 'back',
      success: (res) => {
        const { uploadedFiles } = this.data;
        const newFile = {
          type: 'video',
          path: res.tempFilePath,
          id: Date.now()
        };
        
        this.setData({
          uploadedFiles: [...uploadedFiles, newFile]
        });
      },
      fail: (err) => {
        console.error('选择视频失败:', err);
      }
    });
  },

  // 删除文件
  onFileRemove(e) {
    const fileId = e.currentTarget.dataset.id;
    const { uploadedFiles } = this.data;
    
    this.setData({
      uploadedFiles: uploadedFiles.filter(file => file.id !== fileId)
    });
    
    wx.vibrateShort();
  },

  // 选择紧急程度
  onUrgencySelect(e) {
    const urgency = e.currentTarget.dataset.urgency;
    this.setData({
      selectedUrgency: urgency
    });
    
    wx.vibrateShort();
  },

  // 表单验证
  validateForm() {
    const { selectedType, formData } = this.data;
    
    if (!selectedType) {
      wx.showToast({
        title: '请选择举报类型',
        icon: 'none'
      });
      return false;
    }
    
    if (!formData.title.trim()) {
      wx.showToast({
        title: '请输入问题标题',
        icon: 'none'
      });
      return false;
    }
    
    if (!formData.description.trim()) {
      wx.showToast({
        title: '请描述具体问题',
        icon: 'none'
      });
      return false;
    }
    
    return true;
  },

  // 提交举报
  async onSubmit() {
    if (!this.validateForm()) {
      return;
    }
    
    if (this.data.isSubmitting) {
      return;
    }
    
    this.setData({ isSubmitting: true });
    
    try {
      // 上传文件
      const fileUrls = await this.uploadFiles();
      
      // 提交举报数据
      const reportData = {
        type: this.data.selectedType,
        title: this.data.formData.title,
        description: this.data.formData.description,
        contact: this.data.formData.contact,
        location: this.data.formData.location,
        urgency: this.data.selectedUrgency,
        files: fileUrls,
        timestamp: new Date().toISOString()
      };
      
      // 这里应该调用实际的API
      // const result = await app.request({
      //   url: '/api/reports',
      //   method: 'POST',
      //   data: reportData
      // });
      
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      wx.showToast({
        title: '举报提交成功',
        icon: 'success'
      });
      
      // 重置表单
      this.resetForm();
      
      // 刷新历史记录
      this.loadHistoryReports();
      
    } catch (error) {
      console.error('提交举报失败:', error);
      wx.showToast({
        title: '提交失败，请重试',
        icon: 'none'
      });
    } finally {
      this.setData({ isSubmitting: false });
    }
  },

  // 上传文件
  async uploadFiles() {
    const { uploadedFiles } = this.data;
    if (uploadedFiles.length === 0) {
      return [];
    }
    
    const uploadPromises = uploadedFiles.map(file => {
      return new Promise((resolve, reject) => {
        wx.uploadFile({
          url: `${app.globalData.apiBaseUrl}/api/upload`,
          filePath: file.path,
          name: 'file',
          header: {
            'Authorization': `Bearer ${wx.getStorageSync('token')}`
          },
          success: (res) => {
            try {
              const data = JSON.parse(res.data);
              resolve(data.url);
            } catch (e) {
              reject(e);
            }
          },
          fail: reject
        });
      });
    });
    
    return Promise.all(uploadPromises);
  },

  // 重置表单
  resetForm() {
    this.setData({
      selectedType: '',
      formData: {
        title: '',
        description: '',
        contact: '',
        location: ''
      },
      uploadedFiles: [],
      selectedUrgency: 'low'
    });
  },

  // 加载历史举报
  async loadHistoryReports() {
    try {
      // 这里应该调用实际的API
      // const result = await app.request({
      //   url: '/api/reports/history',
      //   method: 'GET'
      // });
      
      // 模拟数据
      const mockHistory = [
        {
          id: '1',
          title: '超市过期食品举报',
          status: 'processing',
          statusText: '处理中',
          time: '2024-01-15 14:30',
          type: 'quality'
        },
        {
          id: '2',
          title: '餐厅卫生问题',
          status: 'resolved',
          statusText: '已解决',
          time: '2024-01-10 09:15',
          type: 'safety'
        }
      ];
      
      this.setData({
        historyReports: mockHistory
      });
      
    } catch (error) {
      console.error('加载历史记录失败:', error);
    }
  },

  // 查看历史举报详情
  onHistoryTap(e) {
    const reportId = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: `/pages/report/detail?id=${reportId}`
    });
  },

  // 查看全部历史
  onViewAllHistory() {
    wx.navigateTo({
      url: '/pages/report/history'
    });
  },

  // 分享
  onShareAppMessage() {
    return {
      title: '食品安全举报 - 共同守护食品安全',
      path: '/pages/report/report',
      imageUrl: '/images/share-report.png'
    };
  },

  onShareTimeline() {
    return {
      title: '食品安全举报 - 共同守护食品安全',
      imageUrl: '/images/share-report.png'
    };
  }
});