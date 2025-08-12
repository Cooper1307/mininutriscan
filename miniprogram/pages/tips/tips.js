// 营养贴士页面
Page({
  /**
   * 页面的初始数据
   */
  data: {
    // 搜索相关
    searchKeyword: '',
    
    // 分类数据
    categories: [
      { id: 'all', name: '全部' },
      { id: 'nutrition', name: '营养知识' },
      { id: 'health', name: '健康饮食' },
      { id: 'weight', name: '体重管理' },
      { id: 'disease', name: '疾病预防' },
      { id: 'cooking', name: '烹饪技巧' },
      { id: 'supplement', name: '营养补充' },
      { id: 'lifestyle', name: '生活方式' }
    ],
    currentCategory: 'all',
    
    // 所有贴士数据
    allTips: [
      {
        id: 1,
        icon: '🌈',
        title: '彩虹饮食法：营养均衡的秘密',
        summary: '通过摄入不同颜色的蔬果，确保获得全面的营养素。每种颜色代表不同的植物化学物质，对健康有独特的益处。',
        content: '<p>彩虹饮食法是一种简单而有效的营养指导原则，通过食用不同颜色的天然食物来确保营养的多样性和均衡性。</p><h3>各种颜色的营养价值：</h3><p><strong>红色食物：</strong>富含番茄红素和花青素，如西红柿、红椒、草莓等，有助于心血管健康。</p><p><strong>橙黄色食物：</strong>含有β-胡萝卜素和维生素C，如胡萝卜、橙子、南瓜等，支持免疫系统。</p><p><strong>绿色食物：</strong>富含叶绿素、叶酸和维生素K，如菠菜、西兰花、猕猴桃等，促进细胞健康。</p><p><strong>蓝紫色食物：</strong>含有花青素和白藜芦醇，如蓝莓、紫甘蓝、茄子等，具有抗氧化作用。</p><p><strong>白色食物：</strong>含有硫化物和黄酮类化合物，如大蒜、洋葱、白萝卜等，有抗菌消炎功效。</p><h3>实践建议：</h3><p>每天尝试摄入至少5种不同颜色的蔬果，可以通过制作彩虹沙拉、果蔬汁或搭配不同颜色的配菜来实现。</p>',
        categoryId: 'nutrition',
        categoryName: '营养知识',
        tags: ['均衡饮食', '蔬果', '抗氧化', '维生素'],
        readTime: 3,
        likeCount: 128,
        liked: false,
        collected: false,
        references: [
          '《营养学基础》- 中国营养学会',
          '《植物化学物质与健康》- 美国营养协会',
          '《彩虹饮食指南》- 世界卫生组织'
        ]
      },
      {
        id: 2,
        icon: '⏰',
        title: '间歇性断食：科学的饮食时间管理',
        summary: '间歇性断食不仅有助于体重管理，还能改善代谢健康、增强细胞修复能力，是一种科学的饮食模式。',
        content: '<p>间歇性断食（Intermittent Fasting, IF）是一种饮食模式，通过控制进食时间窗口来获得健康益处。</p><h3>常见的间歇性断食方法：</h3><p><strong>16:8方法：</strong>每天断食16小时，在8小时内完成所有进食，是最受欢迎的方法。</p><p><strong>5:2方法：</strong>一周中5天正常饮食，2天限制热量摄入（约500-600卡路里）。</p><p><strong>24小时断食：</strong>每周进行1-2次24小时的完全断食。</p><h3>健康益处：</h3><p>• 促进细胞自噬，清除受损细胞</p><p>• 改善胰岛素敏感性</p><p>• 支持体重管理</p><p>• 可能延缓衰老过程</p><p>• 改善心血管健康指标</p><h3>注意事项：</h3><p>孕妇、哺乳期女性、糖尿病患者等特殊人群应在医生指导下进行。初学者应循序渐进，从较短的断食时间开始。</p>',
        categoryId: 'weight',
        categoryName: '体重管理',
        tags: ['断食', '代谢', '减重', '健康'],
        readTime: 5,
        likeCount: 95,
        liked: false,
        collected: false,
        references: [
          '《间歇性断食研究》- 新英格兰医学杂志',
          '《断食与健康》- 细胞代谢期刊',
          '《营养时间学》- 营养学年鉴'
        ]
      },
      {
        id: 3,
        icon: '💧',
        title: '水的重要性：每天8杯水的科学依据',
        summary: '充足的水分摄入对维持身体各项生理功能至关重要，了解正确的饮水方法和时机，让健康从每一滴水开始。',
        content: '<p>水是生命之源，占人体重量的60-70%，参与几乎所有的生理过程。</p><h3>水在人体中的作用：</h3><p>• 调节体温</p><p>• 运输营养物质和氧气</p><p>• 排除代谢废物</p><p>• 润滑关节</p><p>• 维持血压稳定</p><p>• 支持消化过程</p><h3>每日饮水建议：</h3><p><strong>成年男性：</strong>约2.7升（11杯）</p><p><strong>成年女性：</strong>约2.2升（9杯）</p><p><strong>孕妇：</strong>约2.3升（10杯）</p><p><strong>哺乳期：</strong>约3.1升（13杯）</p><h3>最佳饮水时机：</h3><p>• 起床后：补充夜间流失的水分</p><p>• 餐前30分钟：促进消化</p><p>• 运动前后：维持水电解质平衡</p><p>• 睡前1小时：避免夜间频繁起夜</p><h3>饮水质量：</h3><p>选择清洁的饮用水，可以适量饮用柠檬水、绿茶等，但避免过多含糖饮料。</p>',
        categoryId: 'health',
        categoryName: '健康饮食',
        tags: ['饮水', '代谢', '健康', '生理'],
        readTime: 4,
        likeCount: 156,
        liked: true,
        collected: false,
        references: [
          '《人体水分平衡》- 生理学教科书',
          '《饮水与健康指南》- 世界卫生组织',
          '《水合作用研究》- 运动医学杂志'
        ]
      },
      {
        id: 4,
        icon: '🥗',
        title: '蛋白质搭配指南：植物蛋白的完美组合',
        summary: '了解如何通过合理搭配植物性食物来获得完整的氨基酸谱，为素食者和减少肉类摄入的人群提供营养保障。',
        content: '<p>蛋白质是构成人体的重要营养素，由20种氨基酸组成，其中9种为必需氨基酸，必须通过食物获得。</p><h3>完整蛋白质 vs 不完整蛋白质：</h3><p><strong>完整蛋白质：</strong>含有所有必需氨基酸，主要来源于动物性食品。</p><p><strong>不完整蛋白质：</strong>缺少一种或多种必需氨基酸，多数植物性食品属于此类。</p><h3>经典植物蛋白搭配：</h3><p><strong>豆类 + 谷物：</strong>如红豆饭、豆浆配面包</p><p><strong>坚果 + 种子：</strong>如杏仁配南瓜籽</p><p><strong>豆类 + 坚果：</strong>如鹰嘴豆配芝麻酱</p><p><strong>谷物 + 坚果：</strong>如燕麦配核桃</p><h3>每日蛋白质需求：</h3><p>• 成年人：0.8-1.0克/公斤体重</p><p>• 运动员：1.2-2.0克/公斤体重</p><p>• 老年人：1.0-1.2克/公斤体重</p><h3>优质植物蛋白来源：</h3><p>藜麦、大豆、螺旋藻、奇亚籽等含有完整氨基酸谱的植物性食品。</p>',
        categoryId: 'nutrition',
        categoryName: '营养知识',
        tags: ['蛋白质', '氨基酸', '植物性', '搭配'],
        readTime: 4,
        likeCount: 89,
        liked: false,
        collected: true,
        references: [
          '《蛋白质营养学》- 营养学会期刊',
          '《植物性饮食指南》- 美国饮食协会',
          '《氨基酸代谢》- 生物化学教科书'
        ]
      },
      {
        id: 5,
        icon: '🔥',
        title: '烹饪方式对营养的影响',
        summary: '不同的烹饪方法会显著影响食物的营养价值，掌握正确的烹饪技巧，最大化保留食物中的营养成分。',
        content: '<p>烹饪是食物制备的重要环节，不同的烹饪方式对营养素的保留有很大影响。</p><h3>各种烹饪方式的营养影响：</h3><p><strong>蒸煮：</strong>最大程度保留水溶性维生素，是最健康的烹饪方式之一。</p><p><strong>炒制：</strong>时间短，营养流失少，但要控制油温和用油量。</p><p><strong>烘烤：</strong>能保留大部分营养，但高温可能产生有害物质。</p><p><strong>油炸：</strong>营养流失最多，且增加热量和有害物质。</p><p><strong>生食：</strong>完全保留营养，但要注意食品安全。</p><h3>营养保护技巧：</h3><p>• 缩短烹饪时间</p><p>• 降低烹饪温度</p><p>• 减少水的使用量</p><p>• 保留蔬菜皮</p><p>• 切块要大</p><p>• 现切现炒</p><h3>特殊营养素的处理：</h3><p><strong>维生素C：</strong>易被热和光破坏，适合生食或轻微加热。</p><p><strong>β-胡萝卜素：</strong>加热和加油能提高吸收率。</p><p><strong>番茄红素：</strong>加热后更容易被人体吸收。</p>',
        categoryId: 'cooking',
        categoryName: '烹饪技巧',
        tags: ['烹饪', '营养保留', '维生素', '技巧'],
        readTime: 3,
        likeCount: 112,
        liked: false,
        collected: false,
        references: [
          '《食品营养学》- 食品科学期刊',
          '《烹饪与营养》- 营养研究杂志',
          '《食物加工技术》- 食品工程手册'
        ]
      },
      {
        id: 6,
        icon: '🧠',
        title: '大脑健康饮食：提升认知功能的营养策略',
        summary: '特定的营养素和饮食模式能够支持大脑健康，改善记忆力、注意力和整体认知功能。',
        content: '<p>大脑虽然只占体重的2%，但消耗全身20%的能量，需要特定的营养支持来维持最佳功能。</p><h3>大脑健康的关键营养素：</h3><p><strong>Omega-3脂肪酸：</strong>DHA是大脑细胞膜的重要组成部分，来源包括深海鱼、亚麻籽、核桃等。</p><p><strong>抗氧化剂：</strong>保护大脑免受自由基损害，富含于蓝莓、黑巧克力、绿茶中。</p><p><strong>B族维生素：</strong>支持神经传导，来源包括全谷物、绿叶蔬菜、蛋类。</p><p><strong>胆碱：</strong>合成神经递质的原料，存在于鸡蛋、大豆、坚果中。</p><h3>地中海饮食模式：</h3><p>研究表明，地中海饮食模式对大脑健康最为有益：</p><p>• 大量蔬果和全谷物</p><p>• 适量鱼类和坚果</p><p>• 使用橄榄油</p><p>• 限制红肉和加工食品</p><h3>日常实践建议：</h3><p>• 每周至少吃2次深海鱼</p><p>• 每天一把坚果</p><p>• 多吃深色蔬果</p><p>• 选择全谷物食品</p><p>• 适量饮用绿茶</p>',
        categoryId: 'health',
        categoryName: '健康饮食',
        tags: ['大脑健康', 'Omega-3', '认知', '地中海饮食'],
        readTime: 5,
        likeCount: 203,
        liked: true,
        collected: true,
        references: [
          '《神经营养学》- 神经科学期刊',
          '《大脑与饮食》- 认知科学研究',
          '《地中海饮食研究》- 营养学年鉴'
        ]
      }
    ],
    
    // 过滤后的贴士列表
    filteredTips: [],
    
    // 推荐贴士
    recommendTips: [],
    
    // 每日贴士
    dailyTip: null,
    todayDate: '',
    
    // 贴士详情弹窗
    showTipDetail: false,
    currentTip: {}
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    // 初始化数据
    this.initializeData();
    
    // 处理快捷操作跳转
    if (options.action) {
      this.handleQuickAction(options.action);
    }
  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {
    // 刷新数据
    this.loadTipsData();
  },

  /**
   * 初始化数据
   */
  initializeData() {
    // 设置今日日期
    const today = new Date();
    const todayDate = `${today.getMonth() + 1}月${today.getDate()}日`;
    
    // 随机选择每日贴士
    const randomIndex = Math.floor(Math.random() * this.data.allTips.length);
    const dailyTip = this.data.allTips[randomIndex];
    
    // 选择推荐贴士（排除每日贴士）
    const recommendTips = this.data.allTips
      .filter(tip => tip.id !== dailyTip.id)
      .sort((a, b) => b.likeCount - a.likeCount)
      .slice(0, 3);
    
    this.setData({
      todayDate,
      dailyTip,
      recommendTips
    });
    
    // 初始化过滤列表
    this.filterTips();
  },

  /**
   * 处理快捷操作
   */
  handleQuickAction(action) {
    switch (action) {
      case 'search':
        // 聚焦搜索框
        setTimeout(() => {
          this.selectComponent('.search-input').focus();
        }, 500);
        break;
      case 'category':
        // 显示特定分类
        if (options.category) {
          this.setData({ currentCategory: options.category });
          this.filterTips();
        }
        break;
    }
  },

  /**
   * 加载贴士数据
   */
  loadTipsData() {
    // 这里可以调用API获取最新的贴士数据
    // 目前使用模拟数据
    console.log('加载营养贴士数据');
  },

  /**
   * 搜索输入处理
   */
  onSearchInput(e) {
    const keyword = e.detail.value;
    this.setData({ searchKeyword: keyword });
    
    if (keyword.trim()) {
      this.searchTips(keyword);
    } else {
      this.setData({ currentCategory: 'all' });
      this.filterTips();
    }
  },

  /**
   * 搜索确认
   */
  onSearchConfirm(e) {
    const keyword = e.detail.value;
    if (keyword.trim()) {
      this.searchTips(keyword);
    }
  },

  /**
   * 清除搜索
   */
  onSearchClear() {
    this.setData({ 
      searchKeyword: '',
      currentCategory: 'all'
    });
    this.filterTips();
  },

  /**
   * 搜索贴士
   */
  searchTips(keyword) {
    const filtered = this.data.allTips.filter(tip => 
      tip.title.includes(keyword) || 
      tip.summary.includes(keyword) ||
      tip.tags.some(tag => tag.includes(keyword)) ||
      tip.categoryName.includes(keyword)
    );
    
    this.setData({ 
      filteredTips: filtered,
      currentCategory: 'search'
    });
  },

  /**
   * 分类点击
   */
  onCategoryTap(e) {
    const category = e.currentTarget.dataset.category;
    this.setData({ 
      currentCategory: category.id,
      searchKeyword: ''
    });
    this.filterTips();
  },

  /**
   * 过滤贴士
   */
  filterTips() {
    let filtered = this.data.allTips;
    
    if (this.data.currentCategory !== 'all') {
      filtered = this.data.allTips.filter(tip => 
        tip.categoryId === this.data.currentCategory
      );
    }
    
    // 添加分类名称
    filtered = filtered.map(tip => ({
      ...tip,
      categoryName: this.getCategoryName(tip.categoryId)
    }));
    
    this.setData({ filteredTips: filtered });
  },

  /**
   * 获取分类名称
   */
  getCategoryName(categoryId) {
    const category = this.data.categories.find(cat => cat.id === categoryId);
    return category ? category.name : '未知分类';
  },

  /**
   * 贴士点击
   */
  onTipTap(e) {
    const tip = e.currentTarget.dataset.tip;
    this.setData({ 
      currentTip: tip,
      showTipDetail: true
    });
  },

  /**
   * 关闭贴士详情
   */
  onCloseTipDetail() {
    this.setData({ showTipDetail: false });
  },

  /**
   * 阻止事件冒泡
   */
  stopPropagation() {
    // 阻止事件冒泡
  },

  /**
   * 点赞贴士（列表中）
   */
  onLikeTip(e) {
    const tip = e.currentTarget.dataset.tip;
    this.toggleLike(tip.id);
  },

  /**
   * 点赞贴士（详情中）
   */
  onLikeTipDetail() {
    this.toggleLike(this.data.currentTip.id);
  },

  /**
   * 切换点赞状态
   */
  toggleLike(tipId) {
    const allTips = this.data.allTips.map(tip => {
      if (tip.id === tipId) {
        const liked = !tip.liked;
        const likeCount = liked ? tip.likeCount + 1 : tip.likeCount - 1;
        return { ...tip, liked, likeCount };
      }
      return tip;
    });
    
    // 更新当前贴士
    const currentTip = allTips.find(tip => tip.id === tipId);
    
    this.setData({ 
      allTips,
      currentTip: this.data.showTipDetail ? currentTip : this.data.currentTip
    });
    
    // 重新过滤
    this.filterTips();
    
    wx.showToast({
      title: currentTip.liked ? '点赞成功' : '取消点赞',
      icon: 'success'
    });
    
    // 调用API保存点赞状态
    this.saveLikeStatus(tipId, currentTip.liked);
  },

  /**
   * 收藏贴士
   */
  onCollectTip() {
    const tipId = this.data.currentTip.id;
    const allTips = this.data.allTips.map(tip => {
      if (tip.id === tipId) {
        return { ...tip, collected: !tip.collected };
      }
      return tip;
    });
    
    const currentTip = allTips.find(tip => tip.id === tipId);
    
    this.setData({ 
      allTips,
      currentTip
    });
    
    // 重新过滤
    this.filterTips();
    
    wx.showToast({
      title: currentTip.collected ? '收藏成功' : '取消收藏',
      icon: 'success'
    });
    
    // 调用API保存收藏状态
    this.saveCollectionStatus(tipId, currentTip.collected);
  },

  /**
   * 分享贴士
   */
  onShareTip() {
    const tip = this.data.currentTip;
    
    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage', 'shareTimeline']
    });
    
    wx.showToast({
      title: '分享成功',
      icon: 'success'
    });
  },

  /**
   * 保存点赞状态
   */
  saveLikeStatus(tipId, liked) {
    // 模拟API调用
    console.log('保存点赞状态:', tipId, liked);
    // 实际项目中这里应该调用后端API
  },

  /**
   * 保存收藏状态
   */
  saveCollectionStatus(tipId, collected) {
    // 模拟API调用
    console.log('保存收藏状态:', tipId, collected);
    // 实际项目中这里应该调用后端API
  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh() {
    this.loadTipsData();
    this.initializeData();
    
    setTimeout(() => {
      wx.stopPullDownRefresh();
    }, 1000);
  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom() {
    // 可以实现分页加载更多贴士
    console.log('加载更多贴士数据');
  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {
    if (this.data.showTipDetail) {
      const tip = this.data.currentTip;
      return {
        title: tip.title,
        path: `/pages/tips/tips?tipId=${tip.id}`,
        imageUrl: '/images/share/tip.jpg'
      };
    }
    
    return {
      title: '营养贴士 - 健康生活从这里开始',
      path: '/pages/tips/tips',
      imageUrl: '/images/share/tips.jpg'
    };
  },

  /**
   * 用户点击右上角分享到朋友圈
   */
  onShareTimeline() {
    if (this.data.showTipDetail) {
      const tip = this.data.currentTip;
      return {
        title: tip.title,
        imageUrl: '/images/share/tip.jpg'
      };
    }
    
    return {
      title: '营养贴士 - 健康生活从这里开始',
      imageUrl: '/images/share/tips.jpg'
    };
  }
});