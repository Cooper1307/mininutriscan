// 食品百科页面
Page({
  /**
   * 页面的初始数据
   */
  data: {
    // 搜索相关
    searchKeyword: '',
    searchSuggestions: [],
    
    // 分类数据
    categories: [
      { id: 'all', name: '全部', icon: '🍽️' },
      { id: 'fruits', name: '水果', icon: '🍎' },
      { id: 'vegetables', name: '蔬菜', icon: '🥬' },
      { id: 'grains', name: '谷物', icon: '🌾' },
      { id: 'meat', name: '肉类', icon: '🥩' },
      { id: 'seafood', name: '海鲜', icon: '🐟' },
      { id: 'dairy', name: '乳制品', icon: '🥛' },
      { id: 'nuts', name: '坚果', icon: '🥜' },
      { id: 'beverages', name: '饮品', icon: '🥤' }
    ],
    currentCategory: 'all',
    currentCategoryName: '全部食品',
    
    // 推荐食品
    recommendFoods: [
      {
        id: 1,
        name: '蓝莓',
        image: '/images/foods/blueberry.svg',
        benefit: '富含花青素，抗氧化'
      },
      {
        id: 2,
        name: '三文鱼',
        image: '/images/foods/salmon.svg',
        benefit: '优质蛋白，Omega-3'
      },
      {
        id: 3,
        name: '牛油果',
        image: '/images/foods/avocado.svg',
        benefit: '健康脂肪，维生素E'
      },
      {
        id: 4,
        name: '燕麦',
        image: '/images/foods/oats.svg',
        benefit: '膳食纤维，降胆固醇'
      }
    ],
    
    // 所有食品数据
    allFoods: [
      {
        id: 1,
        name: '苹果',
        category: '水果',
        categoryId: 'fruits',
        image: '/images/foods/apple.svg',
        tags: ['维生素C', '膳食纤维', '低热量'],
        nutritionScore: 85,
        latinName: 'Malus domestica',
        nutrition: [
          { name: '热量', value: '52', unit: 'kcal/100g' },
          { name: '维生素C', value: '4.6', unit: 'mg/100g' },
          { name: '膳食纤维', value: '2.4', unit: 'g/100g' },
          { name: '钾', value: '107', unit: 'mg/100g' }
        ],
        benefits: '苹果富含维生素C和膳食纤维，有助于增强免疫力，促进消化，降低胆固醇。其中的果胶有助于调节血糖，抗氧化物质能够延缓衰老。',
        suggestions: '建议每天食用1-2个苹果，最好连皮一起食用以获得更多纤维。可以作为餐间零食，也可以搭配燕麦或酸奶食用。',
        precautions: '糖尿病患者应适量食用，注意血糖变化。苹果籽含有微量氰化物，不宜大量食用。',
        storage: '常温下可保存1-2周，冰箱冷藏可延长至1个月。避免与香蕉等产生乙烯的水果一起存放。',
        collected: false
      },
      {
        id: 2,
        name: '香蕉',
        category: '水果',
        categoryId: 'fruits',
        image: '/images/foods/banana.svg',
        tags: ['钾', '维生素B6', '快速能量'],
        nutritionScore: 78,
        latinName: 'Musa acuminata',
        nutrition: [
          { name: '热量', value: '89', unit: 'kcal/100g' },
          { name: '钾', value: '358', unit: 'mg/100g' },
          { name: '维生素B6', value: '0.4', unit: 'mg/100g' },
          { name: '维生素C', value: '8.7', unit: 'mg/100g' }
        ],
        benefits: '香蕉富含钾元素，有助于维持心脏健康和血压稳定。维生素B6支持神经系统功能，天然糖分提供快速能量补充。',
        suggestions: '运动前后食用效果佳，可以快速补充能量。搭配坚果或酸奶食用营养更均衡。',
        storage: '室温保存，避免阳光直射。成熟后可冷藏延缓过熟，但不宜长期冷藏。',
        collected: false
      },
      {
        id: 3,
        name: '西兰花',
        category: '蔬菜',
        categoryId: 'vegetables',
        image: '/images/foods/broccoli.svg',
        tags: ['维生素K', '叶酸', '抗癌'],
        nutritionScore: 92,
        latinName: 'Brassica oleracea',
        nutrition: [
          { name: '热量', value: '34', unit: 'kcal/100g' },
          { name: '维生素C', value: '89', unit: 'mg/100g' },
          { name: '维生素K', value: '102', unit: 'μg/100g' },
          { name: '叶酸', value: '63', unit: 'μg/100g' }
        ],
        benefits: '西兰花是营养密度极高的蔬菜，富含维生素C、K和叶酸。含有硫化物具有抗癌作用，膳食纤维促进消化健康。',
        suggestions: '建议蒸煮或快炒，避免过度烹饪以保留营养。可搭配胡萝卜、彩椒等制作营养沙拉。',
        storage: '冰箱冷藏可保存3-5天，用保鲜袋包装防止失水。不宜冷冻保存。',
        collected: false
      },
      {
        id: 4,
        name: '三文鱼',
        category: '海鲜',
        categoryId: 'seafood',
        image: '/images/foods/salmon.svg',
        tags: ['Omega-3', '优质蛋白', 'DHA'],
        nutritionScore: 95,
        latinName: 'Salmo salar',
        nutrition: [
          { name: '热量', value: '208', unit: 'kcal/100g' },
          { name: '蛋白质', value: '25.4', unit: 'g/100g' },
          { name: 'Omega-3', value: '2.3', unit: 'g/100g' },
          { name: '维生素D', value: '11', unit: 'μg/100g' }
        ],
        benefits: '三文鱼富含优质蛋白质和Omega-3脂肪酸，有助于心脑血管健康，支持大脑发育，具有抗炎作用。',
        suggestions: '建议每周食用2-3次，可烤制、蒸煮或制作刺身。搭配蔬菜和全谷物营养更均衡。',
        precautions: '孕妇应选择低汞品种，过敏体质者慎食。生食需确保新鲜度和安全性。',
        storage: '新鲜三文鱼应冷藏保存，1-2天内食用。冷冻可保存2-3个月。',
        collected: false
      },
      {
        id: 5,
        name: '燕麦',
        category: '谷物',
        categoryId: 'grains',
        image: '/images/foods/oats.svg',
        tags: ['β-葡聚糖', '膳食纤维', '低GI'],
        nutritionScore: 88,
        latinName: 'Avena sativa',
        nutrition: [
          { name: '热量', value: '389', unit: 'kcal/100g' },
          { name: '蛋白质', value: '16.9', unit: 'g/100g' },
          { name: '膳食纤维', value: '10.6', unit: 'g/100g' },
          { name: 'β-葡聚糖', value: '4', unit: 'g/100g' }
        ],
        benefits: '燕麦含有β-葡聚糖，能够降低胆固醇，稳定血糖。丰富的膳食纤维促进肠道健康，提供持久饱腹感。',
        suggestions: '可制作燕麦粥、燕麦饼干或添加到酸奶中。建议选择无糖原味燕麦，避免即食加糖产品。',
        storage: '密封保存在阴凉干燥处，可保存6-12个月。开封后应尽快食用完毕。',
        collected: false
      }
    ],
    
    // 过滤后的食品列表
    filteredFoods: [],
    
    // 热门搜索
    hotSearches: ['苹果', '香蕉', '西兰花', '三文鱼', '燕麦', '牛油果', '蓝莓', '菠菜'],
    
    // 营养小贴士
    nutritionTips: [
      {
        id: 1,
        icon: '🌈',
        title: '彩虹饮食法',
        description: '每天摄入不同颜色的蔬果，获得全面营养'
      },
      {
        id: 2,
        icon: '⏰',
        title: '规律进餐',
        description: '定时定量进餐，有助于维持血糖稳定'
      },
      {
        id: 3,
        icon: '💧',
        title: '充足饮水',
        description: '每天8杯水，促进新陈代谢和排毒'
      },
      {
        id: 4,
        icon: '🥗',
        title: '均衡搭配',
        description: '蛋白质、碳水化合物、脂肪合理搭配'
      }
    ],
    
    // 食品详情弹窗
    showFoodDetail: false,
    currentFood: {}
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    // 处理快捷操作跳转
    if (options.action) {
      this.handleQuickAction(options.action);
    }
    
    // 初始化食品列表
    this.filterFoods();
  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {
    // 刷新数据
    this.loadEncyclopediaData();
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
        // 显示分类
        this.setData({ currentCategory: 'all' });
        break;
    }
  },

  /**
   * 加载百科数据
   */
  loadEncyclopediaData() {
    // 这里可以调用API获取最新的食品数据
    // 目前使用模拟数据
    console.log('加载食品百科数据');
  },

  /**
   * 搜索输入处理
   */
  onSearchInput(e) {
    const keyword = e.detail.value;
    this.setData({ searchKeyword: keyword });
    
    if (keyword.trim()) {
      this.searchSuggestions(keyword);
      this.searchFoods(keyword);
    } else {
      this.setData({ 
        searchSuggestions: [],
        currentCategory: 'all'
      });
      this.filterFoods();
    }
  },

  /**
   * 搜索确认
   */
  onSearchConfirm(e) {
    const keyword = e.detail.value;
    if (keyword.trim()) {
      this.searchFoods(keyword);
      this.setData({ searchSuggestions: [] });
    }
  },

  /**
   * 清除搜索
   */
  onSearchClear() {
    this.setData({ 
      searchKeyword: '',
      searchSuggestions: [],
      currentCategory: 'all'
    });
    this.filterFoods();
  },

  /**
   * 搜索建议
   */
  searchSuggestions(keyword) {
    const suggestions = this.data.allFoods
      .filter(food => food.name.includes(keyword))
      .slice(0, 5)
      .map(food => ({
        id: food.id,
        name: food.name,
        category: food.category,
        icon: this.getCategoryIcon(food.categoryId)
      }));
    
    this.setData({ searchSuggestions: suggestions });
  },

  /**
   * 获取分类图标
   */
  getCategoryIcon(categoryId) {
    const category = this.data.categories.find(cat => cat.id === categoryId);
    return category ? category.icon : '🍽️';
  },

  /**
   * 建议项点击
   */
  onSuggestionTap(e) {
    const item = e.currentTarget.dataset.item;
    this.setData({ 
      searchKeyword: item.name,
      searchSuggestions: []
    });
    this.searchFoods(item.name);
  },

  /**
   * 搜索食品
   */
  searchFoods(keyword) {
    const filtered = this.data.allFoods.filter(food => 
      food.name.includes(keyword) || 
      food.tags.some(tag => tag.includes(keyword)) ||
      food.category.includes(keyword)
    );
    
    this.setData({ 
      filteredFoods: filtered,
      currentCategory: 'search',
      currentCategoryName: '搜索结果'
    });
  },

  /**
   * 分类点击
   */
  onCategoryTap(e) {
    const category = e.currentTarget.dataset.category;
    this.setData({ 
      currentCategory: category.id,
      currentCategoryName: category.name,
      searchKeyword: ''
    });
    this.filterFoods();
  },

  /**
   * 过滤食品
   */
  filterFoods() {
    let filtered = this.data.allFoods;
    
    if (this.data.currentCategory !== 'all') {
      filtered = this.data.allFoods.filter(food => 
        food.categoryId === this.data.currentCategory
      );
    }
    
    this.setData({ filteredFoods: filtered });
  },

  /**
   * 查看更多推荐
   */
  onViewMore() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    });
  },

  /**
   * 食品项点击
   */
  onFoodTap(e) {
    const food = e.currentTarget.dataset.food;
    this.setData({ 
      currentFood: food,
      showFoodDetail: true
    });
  },

  /**
   * 关闭食品详情
   */
  onCloseFoodDetail() {
    this.setData({ showFoodDetail: false });
  },

  /**
   * 阻止事件冒泡
   */
  stopPropagation() {
    // 阻止事件冒泡
  },

  /**
   * 收藏食品
   */
  onCollectFood() {
    const currentFood = this.data.currentFood;
    const collected = !currentFood.collected;
    
    // 更新当前食品收藏状态
    this.setData({
      'currentFood.collected': collected
    });
    
    // 更新食品列表中的收藏状态
    const allFoods = this.data.allFoods.map(food => {
      if (food.id === currentFood.id) {
        return { ...food, collected };
      }
      return food;
    });
    
    const filteredFoods = this.data.filteredFoods.map(food => {
      if (food.id === currentFood.id) {
        return { ...food, collected };
      }
      return food;
    });
    
    this.setData({ allFoods, filteredFoods });
    
    wx.showToast({
      title: collected ? '收藏成功' : '取消收藏',
      icon: 'success'
    });
    
    // 这里可以调用API保存收藏状态
    this.saveCollectionStatus(currentFood.id, collected);
  },

  /**
   * 保存收藏状态
   */
  saveCollectionStatus(foodId, collected) {
    // 模拟API调用
    console.log('保存收藏状态:', foodId, collected);
    // 实际项目中这里应该调用后端API
  },

  /**
   * 检测此食品
   */
  onDetectFood() {
    const food = this.data.currentFood;
    
    wx.navigateTo({
      url: `/pages/detection/detection?food=${encodeURIComponent(food.name)}`
    });
  },

  /**
   * 热门搜索点击
   */
  onHotSearchTap(e) {
    const keyword = e.currentTarget.dataset.keyword;
    this.setData({ searchKeyword: keyword });
    this.searchFoods(keyword);
  },

  /**
   * 营养贴士点击
   */
  onTipTap(e) {
    const tip = e.currentTarget.dataset.tip;
    
    wx.showModal({
      title: tip.title,
      content: tip.description,
      showCancel: false,
      confirmText: '知道了'
    });
  },

  /**
   * 查看所有贴士
   */
  onViewAllTips() {
    wx.navigateTo({
      url: '/pages/tips/tips'
    });
  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh() {
    this.loadEncyclopediaData();
    
    setTimeout(() => {
      wx.stopPullDownRefresh();
    }, 1000);
  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom() {
    // 可以实现分页加载更多食品
    console.log('加载更多食品数据');
  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {
    return {
      title: '食品百科 - 了解食物营养知识',
      path: '/pages/encyclopedia/encyclopedia',
      imageUrl: '/images/share/encyclopedia.svg'
    };
  },

  /**
   * 用户点击右上角分享到朋友圈
   */
  onShareTimeline() {
    return {
      title: '食品百科 - 了解食物营养知识',
      imageUrl: '/images/share/encyclopedia.jpg'
    };
  }
});