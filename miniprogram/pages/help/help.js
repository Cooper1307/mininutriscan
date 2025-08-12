// 帮助中心页面逻辑
Page({
  /**
   * 页面的初始数据
   */
  data: {
    // 搜索相关
    searchKeyword: '',
    searchResults: [],
    
    // 帮助分类
    categories: [
      {
        id: 1,
        icon: '📸',
        title: '检测使用',
        desc: '如何使用AI检测功能',
        count: 8
      },
      {
        id: 2,
        icon: '📊',
        title: '结果解读',
        desc: '理解检测结果和安全等级',
        count: 6
      },
      {
        id: 3,
        icon: '👤',
        title: '账户管理',
        desc: '注册登录和个人信息',
        count: 5
      },
      {
        id: 4,
        icon: '⚙️',
        title: '设置功能',
        desc: '应用设置和个性化配置',
        count: 4
      },
      {
        id: 5,
        icon: '🛡️',
        title: '隐私安全',
        desc: '数据保护和隐私政策',
        count: 3
      },
      {
        id: 6,
        icon: '❓',
        title: '常见问题',
        desc: '用户常遇到的问题解答',
        count: 12
      }
    ],
    
    // 热门FAQ
    hotFAQs: [
      {
        id: 1,
        question: '如何提高检测准确率？',
        answer: '确保拍摄环境光线充足，食品表面清洁，镜头对焦清晰，避免反光和阴影。'
      },
      {
        id: 2,
        question: '检测结果不准确怎么办？',
        answer: '可以重新拍摄检测，或通过"报告问题"功能反馈给我们，我们会持续优化算法。'
      },
      {
        id: 3,
        question: '支持检测哪些食品类型？',
        answer: '目前支持水果、蔬菜、肉类、海鲜、乳制品等常见食品的安全检测。'
      },
      {
        id: 4,
        question: '检测历史记录保存多久？',
        answer: '检测记录默认保存30天，VIP用户可永久保存，您也可以手动删除记录。'
      },
      {
        id: 5,
        question: '如何升级VIP会员？',
        answer: '在个人中心点击VIP图标，选择合适的套餐进行购买即可享受VIP特权。'
      }
    ],
    
    // 文章详情
    showArticle: false,
    currentArticle: {
      title: '',
      content: '',
      liked: false
    },
    
    // 所有帮助文章（用于搜索）
    allArticles: [
      {
        id: 1,
        title: '如何进行食品安全检测',
        content: '打开应用，点击检测按钮，选择拍照或从相册选择图片，等待AI分析结果...',
        category: '检测使用',
        updateTime: '2024-01-15'
      },
      {
        id: 2,
        title: '安全等级说明',
        content: '绿色表示安全，黄色表示需要注意，红色表示存在风险，建议谨慎食用...',
        category: '结果解读',
        updateTime: '2024-01-14'
      },
      {
        id: 3,
        title: '如何注册和登录账户',
        content: '支持微信快速登录，也可以使用手机号注册新账户...',
        category: '账户管理',
        updateTime: '2024-01-13'
      },
      {
        id: 4,
        title: '个性化设置指南',
        content: '在设置页面可以调整通知、语言、检测精度等个人偏好...',
        category: '设置功能',
        updateTime: '2024-01-12'
      },
      {
        id: 5,
        title: '隐私保护政策',
        content: '我们严格保护用户隐私，检测图片仅用于分析，不会泄露个人信息...',
        category: '隐私安全',
        updateTime: '2024-01-11'
      }
    ]
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    // 如果有传入的问题类型，直接跳转到对应内容
    if (options.type) {
      this.onQuickAction({ currentTarget: { dataset: { type: options.type } } });
    }
  },

  /**
   * 搜索输入
   */
  onSearchInput(e) {
    const keyword = e.detail.value;
    this.setData({
      searchKeyword: keyword
    });
    
    if (keyword.trim()) {
      this.performSearch(keyword);
    } else {
      this.setData({
        searchResults: []
      });
    }
  },

  /**
   * 清除搜索
   */
  onSearchClear() {
    this.setData({
      searchKeyword: '',
      searchResults: []
    });
  },

  /**
   * 执行搜索
   */
  performSearch(keyword) {
    const results = this.data.allArticles.filter(article => {
      return article.title.includes(keyword) || 
             article.content.includes(keyword) ||
             article.category.includes(keyword);
    });
    
    this.setData({
      searchResults: results
    });
  },

  /**
   * 快速操作
   */
  onQuickAction(e) {
    const type = e.currentTarget.dataset.type;
    
    switch (type) {
      case 'detection':
        this.showArticleDetail({
          title: '如何进行食品检测',
          content: `
            <h3>检测步骤</h3>
            <p>1. 打开NutriScan应用</p>
            <p>2. 点击首页的"开始检测"按钮</p>
            <p>3. 选择拍照或从相册选择图片</p>
            <p>4. 等待AI分析处理</p>
            <p>5. 查看详细检测结果</p>
            
            <h3>拍摄技巧</h3>
            <p>• 确保光线充足，避免阴影</p>
            <p>• 食品表面保持清洁</p>
            <p>• 镜头对焦清晰，避免模糊</p>
            <p>• 尽量填满画面，突出主体</p>
            
            <h3>注意事项</h3>
            <p>• 支持常见食品类型检测</p>
            <p>• 检测结果仅供参考</p>
            <p>• 如有疑问可联系客服</p>
          `
        });
        break;
        
      case 'result':
        this.showArticleDetail({
          title: '检测结果说明',
          content: `
            <h3>安全等级</h3>
            <p><span style="color: #52c41a;">🟢 安全</span> - 食品质量良好，可以放心食用</p>
            <p><span style="color: #faad14;">🟡 注意</span> - 存在轻微问题，建议谨慎食用</p>
            <p><span style="color: #ff4d4f;">🔴 风险</span> - 检测到安全隐患，不建议食用</p>
            
            <h3>检测指标</h3>
            <p>• <strong>新鲜度</strong>：食品的新鲜程度</p>
            <p>• <strong>农药残留</strong>：是否检测到农药成分</p>
            <p>• <strong>细菌污染</strong>：微生物污染情况</p>
            <p>• <strong>营养成分</strong>：主要营养元素分析</p>
            
            <h3>建议说明</n            <p>根据检测结果，系统会给出相应的食用建议和处理方法。</p>
          `
        });
        break;
        
      case 'safety':
        this.showArticleDetail({
          title: '安全等级详解',
          content: `
            <h3>等级划分标准</h3>
            <p>我们的AI检测系统基于多项指标综合评估食品安全等级：</p>
            
            <h4>🟢 安全等级（85-100分）</h4>
            <p>• 新鲜度良好</p>
            <p>• 无农药残留或在安全范围内</p>
            <p>• 无细菌污染</p>
            <p>• 营养成分正常</p>
            
            <h4>🟡 注意等级（60-84分）</h4>
            <p>• 新鲜度一般</p>
            <p>• 轻微农药残留</p>
            <p>• 少量细菌但在可接受范围</p>
            <p>• 建议清洗后食用</p>
            
            <h4>🔴 风险等级（0-59分）</h4>
            <p>• 新鲜度差</p>
            <p>• 农药残留超标</p>
            <p>• 细菌污染严重</p>
            <p>• 不建议食用</p>
          `
        });
        break;
        
      case 'contact':
        this.onContactService();
        break;
    }
  },

  /**
   * 分类点击
   */
  onCategoryTap(e) {
    const category = e.currentTarget.dataset.category;
    
    wx.navigateTo({
      url: `/pages/help/category/category?id=${category.id}&title=${category.title}`
    });
  },

  /**
   * FAQ点击
   */
  onFAQTap(e) {
    const faq = e.currentTarget.dataset.faq;
    
    this.showArticleDetail({
      title: faq.question,
      content: `<p>${faq.answer}</p>`
    });
  },

  /**
   * 查看全部FAQ
   */
  onViewAllFAQ() {
    wx.navigateTo({
      url: '/pages/help/faq/faq'
    });
  },

  /**
   * 搜索结果点击
   */
  onResultTap(e) {
    const result = e.currentTarget.dataset.result;
    
    this.showArticleDetail({
      title: result.title,
      content: `<p>${result.content}</p>`
    });
  },

  /**
   * 显示文章详情
   */
  showArticleDetail(article) {
    this.setData({
      showArticle: true,
      currentArticle: {
        ...article,
        liked: false
      }
    });
  },

  /**
   * 关闭文章详情
   */
  onCloseArticle() {
    this.setData({
      showArticle: false
    });
  },

  /**
   * 点赞文章
   */
  onLikeArticle(e) {
    const liked = e.currentTarget.dataset.liked;
    
    this.setData({
      'currentArticle.liked': !liked
    });
    
    wx.showToast({
      title: !liked ? '已点赞' : '已取消点赞',
      icon: 'success'
    });
  },

  /**
   * 分享文章
   */
  onShareArticle() {
    wx.showActionSheet({
      itemList: ['分享给朋友', '分享到朋友圈', '复制链接'],
      success: (res) => {
        const actions = ['friend', 'timeline', 'copy'];
        const action = actions[res.tapIndex];
        
        switch (action) {
          case 'friend':
            // 分享给朋友的逻辑
            wx.showToast({ title: '已分享给朋友', icon: 'success' });
            break;
          case 'timeline':
            // 分享到朋友圈的逻辑
            wx.showToast({ title: '已分享到朋友圈', icon: 'success' });
            break;
          case 'copy':
            // 复制链接的逻辑
            wx.setClipboardData({
              data: `NutriScan帮助：${this.data.currentArticle.title}`,
              success: () => {
                wx.showToast({ title: '链接已复制', icon: 'success' });
              }
            });
            break;
        }
      }
    });
  },

  /**
   * 联系在线客服
   */
  onContactService() {
    wx.showModal({
      title: '联系客服',
      content: '即将跳转到客服聊天页面',
      success: (res) => {
        if (res.confirm) {
          // 这里可以跳转到客服页面或打开客服聊天
          wx.navigateTo({
            url: '/pages/service/service'
          });
        }
      }
    });
  },

  /**
   * 电话咨询
   */
  onContactPhone() {
    wx.showModal({
      title: '电话咨询',
      content: '客服电话：400-123-4567\n服务时间：9:00-21:00',
      confirmText: '拨打',
      success: (res) => {
        if (res.confirm) {
          wx.makePhoneCall({
            phoneNumber: '4001234567',
            fail: () => {
              wx.showToast({
                title: '拨打失败',
                icon: 'error'
              });
            }
          });
        }
      }
    });
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
      title: 'NutriScan帮助中心 - 智能食品安全检测',
      path: '/pages/help/help'
    };
  },

  /**
   * 用户点击右上角分享到朋友圈
   */
  onShareTimeline() {
    return {
      title: 'NutriScan帮助中心 - 智能食品安全检测'
    };
  }
});