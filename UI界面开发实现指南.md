# 🛠️ UI界面开发实现指南

> 基于"社区食安AI小卫士"UI设计图的实际开发指导

## 📋 开发准备

### 1. 技术栈选择

```json
{
  "框架": "微信小程序原生框架",
  "UI库": "WeUI + 自定义组件",
  "样式": "WXSS + Sass预处理",
  "状态管理": "小程序原生 + Mobx（可选）",
  "网络请求": "wx.request + 封装",
  "图标库": "iconfont + 自定义SVG"
}
```

### 2. 项目结构搭建

```
miniprogram/
├── pages/           # 页面文件
│   ├── index/       # 首页
│   ├── detection/   # 检测页面
│   ├── report/      # 举报页面
│   ├── education/   # 科普页面
│   └── profile/     # 个人中心
├── components/      # 自定义组件
│   ├── navigation-bar/
│   ├── detection-card/
│   ├── report-form/
│   └── loading-spinner/
├── utils/           # 工具函数
├── services/        # API服务
├── styles/          # 全局样式
└── assets/          # 静态资源
    ├── images/
    └── icons/
```

## 🎨 设计系统实现

### 1. 全局样式配置

**创建 `styles/variables.wxss`:**

```css
/* 色彩变量 */
:root {
  --primary-color: #2E8B57;      /* 主色调-海绿色 */
  --secondary-color: #4169E1;    /* 辅助色-皇家蓝 */
  --accent-color: #FF6B35;       /* 强调色-橙红色 */
  --background-color: #F8F9FA;   /* 背景色 */
  --text-primary: #2C3E50;       /* 主要文字色 */
  --text-secondary: #7F8C8D;     /* 次要文字色 */
  --border-color: #E9ECEF;       /* 边框色 */
  --shadow-color: rgba(0,0,0,0.1); /* 阴影色 */
}

/* 字体大小 */
.text-title { font-size: 36rpx; font-weight: bold; }
.text-subtitle { font-size: 32rpx; font-weight: 600; }
.text-body { font-size: 28rpx; }
.text-caption { font-size: 24rpx; color: var(--text-secondary); }
.text-small { font-size: 22rpx; color: var(--text-secondary); }

/* 间距系统 */
.spacing-xs { margin: 8rpx; }
.spacing-sm { margin: 16rpx; }
.spacing-md { margin: 24rpx; }
.spacing-lg { margin: 32rpx; }
.spacing-xl { margin: 48rpx; }

/* 圆角系统 */
.radius-sm { border-radius: 8rpx; }
.radius-md { border-radius: 12rpx; }
.radius-lg { border-radius: 16rpx; }
.radius-xl { border-radius: 24rpx; }
```

**创建 `styles/common.wxss`:**

```css
/* 通用布局 */
.container {
  padding: 32rpx;
  background-color: var(--background-color);
  min-height: 100vh;
}

.card {
  background: white;
  border-radius: var(--radius-md);
  box-shadow: 0 4rpx 16rpx var(--shadow-color);
  padding: 32rpx;
  margin-bottom: 24rpx;
}

.flex-row {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.flex-column {
  display: flex;
  flex-direction: column;
}

.flex-center {
  display: flex;
  justify-content: center;
  align-items: center;
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 按钮样式 */
.btn-primary {
  background-color: var(--primary-color);
  color: white;
  border-radius: 16rpx;
  padding: 24rpx 48rpx;
  font-size: 32rpx;
  font-weight: bold;
  border: none;
}

.btn-secondary {
  background-color: transparent;
  color: var(--primary-color);
  border: 2rpx solid var(--primary-color);
  border-radius: 16rpx;
  padding: 22rpx 46rpx;
  font-size: 28rpx;
}

.btn-danger {
  background-color: var(--accent-color);
  color: white;
  border-radius: 16rpx;
  padding: 24rpx 48rpx;
  font-size: 32rpx;
  font-weight: bold;
  border: none;
}
```

### 2. 组件开发

#### 🧩 导航栏组件 (navigation-bar)

**`components/navigation-bar/navigation-bar.wxml`:**

```xml
<view class="nav-bar">
  <view class="nav-content">
    <view class="nav-left" wx:if="{{showBack}}">
      <view class="nav-back" bindtap="onBack">
        <text class="icon-back">‹</text>
      </view>
    </view>
    
    <view class="nav-center">
      <text class="nav-title">{{title}}</text>
    </view>
    
    <view class="nav-right">
      <slot name="right"></slot>
    </view>
  </view>
</view>
```

**`components/navigation-bar/navigation-bar.wxss`:**

```css
.nav-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: white;
  border-bottom: 1rpx solid var(--border-color);
}

.nav-content {
  display: flex;
  align-items: center;
  height: 88rpx;
  padding: 0 32rpx;
}

.nav-left {
  width: 80rpx;
}

.nav-back {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--background-color);
}

.icon-back {
  font-size: 48rpx;
  color: var(--text-primary);
  font-weight: bold;
}

.nav-center {
  flex: 1;
  text-align: center;
}

.nav-title {
  font-size: 36rpx;
  font-weight: bold;
  color: var(--text-primary);
}

.nav-right {
  width: 80rpx;
  display: flex;
  justify-content: flex-end;
}
```

**`components/navigation-bar/navigation-bar.js`:**

```javascript
Component({
  properties: {
    title: {
      type: String,
      value: ''
    },
    showBack: {
      type: Boolean,
      value: false
    }
  },
  
  methods: {
    onBack() {
      wx.navigateBack()
    }
  }
})
```

#### 🎯 快速功能组件 (quick-actions)

**`components/quick-actions/quick-actions.wxml`:**

```xml
<view class="quick-actions">
  <view class="actions-grid">
    <view 
      class="action-item" 
      wx:for="{{actions}}" 
      wx:key="id"
      bindtap="onActionTap"
      data-action="{{item}}"
    >
      <view class="action-icon">
        <text class="icon">{{item.icon}}</text>
      </view>
      <text class="action-label">{{item.label}}</text>
    </view>
  </view>
</view>
```

**`components/quick-actions/quick-actions.wxss`:**

```css
.quick-actions {
  margin: 32rpx 0;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24rpx;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24rpx 16rpx;
  background: white;
  border-radius: var(--radius-md);
  box-shadow: 0 2rpx 8rpx var(--shadow-color);
  transition: transform 0.2s ease;
}

.action-item:active {
  transform: scale(0.95);
}

.action-icon {
  width: 96rpx;
  height: 96rpx;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16rpx;
}

.icon {
  font-size: 48rpx;
  color: white;
}

.action-label {
  font-size: 24rpx;
  color: var(--text-primary);
  text-align: center;
  font-weight: 500;
}
```

**`components/quick-actions/quick-actions.js`:**

```javascript
Component({
  properties: {
    actions: {
      type: Array,
      value: []
    }
  },
  
  methods: {
    onActionTap(e) {
      const action = e.currentTarget.dataset.action
      this.triggerEvent('actionTap', action)
    }
  }
})
```

## 📱 页面实现

### 🏠 首页实现

**`pages/index/index.wxml`:**

```xml
<view class="page">
  <!-- 顶部状态栏 -->
  <view class="status-bar">
    <view class="location">
      <text class="icon">📍</text>
      <text class="location-text">{{userLocation}}</text>
    </view>
    <view class="status-right">
      <view class="notification" bindtap="onNotificationTap">
        <text class="icon">🔔</text>
        <text class="badge" wx:if="{{notificationCount > 0}}">{{notificationCount}}</text>
      </view>
      <view class="settings" bindtap="onSettingsTap">
        <text class="icon">⚙️</text>
      </view>
    </view>
  </view>

  <!-- 欢迎横幅 -->
  <view class="welcome-banner">
    <view class="banner-content">
      <view class="banner-title">
        <text class="icon">🏥</text>
        <text class="title-text">社区食安AI小卫士</text>
      </view>
      <text class="banner-subtitle">守护您的餐桌安全 🛡️</text>
      <view class="banner-stats">
        <view class="stat-item">
          <text class="stat-label">今日检测:</text>
          <text class="stat-value">{{todayDetections}}次</text>
        </view>
        <view class="stat-item">
          <text class="stat-label">社区举报:</text>
          <text class="stat-value">{{todayReports}}件</text>
        </view>
      </view>
    </view>
  </view>

  <!-- 快速功能 -->
  <quick-actions 
    actions="{{quickActions}}"
    bind:actionTap="onQuickActionTap"
  ></quick-actions>

  <!-- 社区动态 -->
  <view class="community-news">
    <view class="section-header">
      <text class="section-title">📰 社区动态</text>
    </view>
    <view class="news-list">
      <view 
        class="news-item {{item.urgent ? 'urgent' : ''}}" 
        wx:for="{{communityNews}}" 
        wx:key="id"
        bindtap="onNewsItemTap"
        data-news="{{item}}"
      >
        <view class="news-content">
          <text class="news-title">{{item.title}}</text>
          <view class="news-meta">
            <text class="news-date">📅 {{item.date}}</text>
            <text class="news-views">👁️ 已读 {{item.views}}人</text>
          </view>
        </view>
        <view class="news-indicator" wx:if="{{item.urgent}}">
          <text class="urgent-dot">🔴</text>
        </view>
      </view>
    </view>
  </view>

  <!-- 今日推荐 -->
  <view class="recommendations">
    <view class="section-header">
      <text class="section-title">💡 AI推荐</text>
    </view>
    <view class="recommendation-list">
      <view 
        class="recommendation-item" 
        wx:for="{{recommendations}}" 
        wx:key="id"
        bindtap="onRecommendationTap"
        data-item="{{item}}"
      >
        <text class="recommendation-text">"{{item.title}}"</text>
      </view>
    </view>
    <view class="view-more" bindtap="onViewMoreRecommendations">
      <text class="view-more-text">[查看更多 →]</text>
    </view>
  </view>
</view>
```

**`pages/index/index.wxss`:**

```css
@import '/styles/variables.wxss';
@import '/styles/common.wxss';

.page {
  background-color: var(--background-color);
  min-height: 100vh;
  padding-bottom: 120rpx; /* 为底部导航留空间 */
}

/* 顶部状态栏 */
.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 32rpx;
  background: white;
  border-bottom: 1rpx solid var(--border-color);
}

.location {
  display: flex;
  align-items: center;
}

.location .icon {
  margin-right: 8rpx;
  font-size: 28rpx;
}

.location-text {
  font-size: 28rpx;
  color: var(--text-primary);
}

.status-right {
  display: flex;
  align-items: center;
  gap: 24rpx;
}

.notification {
  position: relative;
  padding: 8rpx;
}

.notification .icon {
  font-size: 32rpx;
}

.badge {
  position: absolute;
  top: 0;
  right: 0;
  background: var(--accent-color);
  color: white;
  font-size: 20rpx;
  padding: 4rpx 8rpx;
  border-radius: 20rpx;
  min-width: 32rpx;
  text-align: center;
}

.settings .icon {
  font-size: 32rpx;
}

/* 欢迎横幅 */
.welcome-banner {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  margin: 24rpx 32rpx;
  border-radius: var(--radius-lg);
  padding: 48rpx 32rpx;
  color: white;
}

.banner-title {
  display: flex;
  align-items: center;
  margin-bottom: 16rpx;
}

.banner-title .icon {
  font-size: 48rpx;
  margin-right: 16rpx;
}

.title-text {
  font-size: 40rpx;
  font-weight: bold;
}

.banner-subtitle {
  font-size: 28rpx;
  opacity: 0.9;
  margin-bottom: 32rpx;
}

.banner-stats {
  display: flex;
  gap: 48rpx;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.stat-label {
  font-size: 24rpx;
  opacity: 0.8;
}

.stat-value {
  font-size: 28rpx;
  font-weight: bold;
}

/* 社区动态 */
.community-news {
  margin: 32rpx;
}

.section-header {
  margin-bottom: 24rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: bold;
  color: var(--text-primary);
}

.news-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.news-item {
  background: white;
  border-radius: var(--radius-md);
  padding: 32rpx;
  box-shadow: 0 2rpx 8rpx var(--shadow-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: transform 0.2s ease;
}

.news-item:active {
  transform: scale(0.98);
}

.news-item.urgent {
  border-left: 8rpx solid var(--accent-color);
}

.news-content {
  flex: 1;
}

.news-title {
  font-size: 28rpx;
  color: var(--text-primary);
  font-weight: 500;
  margin-bottom: 12rpx;
  display: block;
}

.news-meta {
  display: flex;
  gap: 24rpx;
}

.news-date,
.news-views {
  font-size: 24rpx;
  color: var(--text-secondary);
}

.urgent-dot {
  font-size: 24rpx;
}

/* 今日推荐 */
.recommendations {
  margin: 32rpx;
}

.recommendation-list {
  background: white;
  border-radius: var(--radius-md);
  padding: 32rpx;
  box-shadow: 0 2rpx 8rpx var(--shadow-color);
}

.recommendation-item {
  padding: 16rpx 0;
  border-bottom: 1rpx solid var(--border-color);
}

.recommendation-item:last-child {
  border-bottom: none;
}

.recommendation-text {
  font-size: 28rpx;
  color: var(--text-primary);
  line-height: 1.5;
}

.view-more {
  text-align: center;
  margin-top: 24rpx;
}

.view-more-text {
  font-size: 28rpx;
  color: var(--primary-color);
  font-weight: 500;
}
```

**`pages/index/index.js`:**

```javascript
Page({
  data: {
    userLocation: '普陀区长风街道',
    notificationCount: 3,
    todayDetections: 23,
    todayReports: 2,
    quickActions: [
      { id: 1, icon: '🔍', label: 'AI检测', action: 'detection' },
      { id: 2, icon: '📷', label: '拍照识别', action: 'camera' },
      { id: 3, icon: '📢', label: '举报问题', action: 'report' },
      { id: 4, icon: '📚', label: '学习科普', action: 'education' }
    ],
    communityNews: [
      {
        id: 1,
        title: '🔴 紧急通知: XX超市食品召回',
        date: '2024-01-15',
        views: 156,
        urgent: true
      },
      {
        id: 2,
        title: '✅ 志愿者活动: 食品安全宣传周',
        date: '2024-01-12',
        views: 89,
        urgent: false
      }
    ],
    recommendations: [
      { id: 1, title: '冬季养生食谱推荐' },
      { id: 2, title: '如何识别过期食品' }
    ]
  },

  onLoad() {
    this.loadUserData()
    this.loadCommunityData()
  },

  // 快速功能点击
  onQuickActionTap(e) {
    const action = e.detail
    switch (action.action) {
      case 'detection':
        wx.navigateTo({ url: '/pages/detection/detection' })
        break
      case 'camera':
        this.openCamera()
        break
      case 'report':
        wx.navigateTo({ url: '/pages/report/report' })
        break
      case 'education':
        wx.navigateTo({ url: '/pages/education/education' })
        break
    }
  },

  // 打开相机
  openCamera() {
    wx.chooseImage({
      count: 1,
      sourceType: ['camera'],
      success: (res) => {
        const imagePath = res.tempFilePaths[0]
        wx.navigateTo({
          url: `/pages/detection/result?image=${encodeURIComponent(imagePath)}`
        })
      }
    })
  },

  // 通知点击
  onNotificationTap() {
    wx.navigateTo({ url: '/pages/notifications/notifications' })
  },

  // 设置点击
  onSettingsTap() {
    wx.navigateTo({ url: '/pages/settings/settings' })
  },

  // 新闻项点击
  onNewsItemTap(e) {
    const news = e.currentTarget.dataset.news
    wx.navigateTo({
      url: `/pages/news/detail?id=${news.id}`
    })
  },

  // 推荐项点击
  onRecommendationTap(e) {
    const item = e.currentTarget.dataset.item
    wx.navigateTo({
      url: `/pages/education/article?id=${item.id}`
    })
  },

  // 查看更多推荐
  onViewMoreRecommendations() {
    wx.switchTab({ url: '/pages/education/education' })
  },

  // 加载用户数据
  loadUserData() {
    // 获取用户位置
    wx.getLocation({
      type: 'gcj02',
      success: (res) => {
        // 根据经纬度获取地址信息
        this.reverseGeocode(res.latitude, res.longitude)
      }
    })
  },

  // 加载社区数据
  loadCommunityData() {
    // 从服务器获取社区动态和推荐内容
    wx.request({
      url: 'https://your-api.com/community/news',
      success: (res) => {
        this.setData({
          communityNews: res.data.news,
          recommendations: res.data.recommendations
        })
      }
    })
  },

  // 逆地理编码
  reverseGeocode(lat, lng) {
    // 调用地图API获取地址
    // 这里使用腾讯地图API示例
    wx.request({
      url: `https://apis.map.qq.com/ws/geocoder/v1/?location=${lat},${lng}&key=YOUR_KEY`,
      success: (res) => {
        if (res.data.status === 0) {
          const address = res.data.result.formatted_addresses.recommend
          this.setData({ userLocation: address })
        }
      }
    })
  }
})
```

### 🔍 检测页面实现

**`pages/detection/detection.wxml`:**

```xml
<view class="page">
  <navigation-bar title="🔍 AI智能检测" show-back="{{true}}">
    <view slot="right">
      <text class="ai-icon">🤖</text>
    </view>
  </navigation-bar>

  <view class="content">
    <!-- 检测方式选择 -->
    <view class="detection-methods">
      <view class="method-card {{selectedMethod === 'camera' ? 'active' : ''}}" 
            bindtap="selectMethod" data-method="camera">
        <view class="method-icon">📷</view>
        <view class="method-title">拍照检测</view>
        <view class="method-desc">识别食品信息</view>
        <button class="method-btn" wx:if="{{selectedMethod === 'camera'}}">点击拍照</button>
      </view>
      
      <view class="method-card {{selectedMethod === 'text' ? 'active' : ''}}" 
            bindtap="selectMethod" data-method="text">
        <view class="method-icon">📝</view>
        <view class="method-title">文字咨询</view>
        <view class="method-desc">AI智能问答</view>
        <button class="method-btn" wx:if="{{selectedMethod === 'text'}}">开始咨询</button>
      </view>
    </view>

    <!-- 拍照检测区域 -->
    <view class="camera-section" wx:if="{{selectedMethod === 'camera'}}">
      <view class="camera-preview">
        <camera 
          device-position="back" 
          flash="off" 
          binderror="onCameraError"
          style="width: 100%; height: 400rpx;"
          wx:if="{{showCamera}}"
        ></camera>
        <view class="camera-placeholder" wx:else>
          <text class="placeholder-icon">📷</text>
          <text class="placeholder-text">相机预览区域</text>
        </view>
      </view>
      
      <view class="camera-controls">
        <button class="control-btn" bindtap="takePhoto">点击拍照</button>
        <button class="control-btn secondary" bindtap="chooseFromAlbum">从相册选择</button>
      </view>
      
      <view class="photo-tips">
        <view class="tips-title">💡 拍照提示:</view>
        <view class="tips-list">
          <text class="tip-item">• 确保食品标签清晰可见</text>
          <text class="tip-item">• 光线充足，避免反光</text>
          <text class="tip-item">• 包含生产日期和保质期</text>
        </view>
      </view>
    </view>

    <!-- 文字咨询区域 -->
    <view class="chat-section" wx:if="{{selectedMethod === 'text'}}">
      <view class="chat-messages">
        <view class="message {{msg.type}}" wx:for="{{messages}}" wx:key="id">
          <view class="message-avatar">
            <text class="avatar-icon">{{msg.type === 'user' ? '👤' : '🤖'}}</text>
          </view>
          <view class="message-content">
            <text class="message-text">{{msg.content}}</text>
            <text class="message-time">{{msg.time}}</text>
          </view>
        </view>
      </view>
      
      <view class="chat-input">
        <input 
          class="input-field" 
          placeholder="请输入您的食品安全问题..."
          value="{{inputText}}"
          bindinput="onInputChange"
          confirm-type="send"
          bindconfirm="sendMessage"
        />
        <button class="send-btn" bindtap="sendMessage" disabled="{{!inputText.trim()}}">
          发送
        </button>
      </view>
    </view>

    <!-- 检测历史 -->
    <view class="history-section">
      <view class="section-header">
        <text class="section-title">📊 最近检测记录</text>
        <text class="view-all" bindtap="viewAllHistory">[查看全部 →]</text>
      </view>
      
      <view class="history-list">
        <view class="history-item" wx:for="{{recentHistory}}" wx:key="id" 
              bindtap="viewHistoryDetail" data-item="{{item}}">
          <view class="history-icon">
            <text class="food-icon">{{item.icon}}</text>
          </view>
          <view class="history-content">
            <text class="history-title">{{item.name}} - {{item.status}}</text>
            <text class="history-time">📅 {{item.time}}</text>
          </view>
          <view class="history-status">
            <text class="status-icon">{{item.statusIcon}}</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</view>
```

## 🚀 开发最佳实践

### 1. 性能优化

```javascript
// utils/performance.js
class PerformanceOptimizer {
  // 图片懒加载
  static lazyLoadImages() {
    const observer = wx.createIntersectionObserver()
    observer.relativeToViewport().observe('.lazy-image', (res) => {
      if (res.intersectionRatio > 0) {
        // 加载图片
        const dataset = res.target.dataset
        const src = dataset.src
        // 更新图片源
      }
    })
  }
  
  // 防抖函数
  static debounce(func, wait) {
    let timeout
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout)
        func(...args)
      }
      clearTimeout(timeout)
      timeout = setTimeout(later, wait)
    }
  }
  
  // 节流函数
  static throttle(func, limit) {
    let inThrottle
    return function() {
      const args = arguments
      const context = this
      if (!inThrottle) {
        func.apply(context, args)
        inThrottle = true
        setTimeout(() => inThrottle = false, limit)
      }
    }
  }
}

module.exports = PerformanceOptimizer
```

### 2. 网络请求封装

```javascript
// utils/request.js
class RequestManager {
  static baseURL = 'https://your-api.com'
  
  static request(options) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: this.baseURL + options.url,
        method: options.method || 'GET',
        data: options.data,
        header: {
          'Content-Type': 'application/json',
          'Authorization': wx.getStorageSync('token') || '',
          ...options.header
        },
        success: (res) => {
          if (res.statusCode === 200) {
            resolve(res.data)
          } else {
            this.handleError(res)
            reject(res)
          }
        },
        fail: (err) => {
          this.handleError(err)
          reject(err)
        }
      })
    })
  }
  
  static handleError(error) {
    console.error('Request Error:', error)
    wx.showToast({
      title: '网络请求失败',
      icon: 'none'
    })
  }
  
  // API方法
  static detectFood(imageData) {
    return this.request({
      url: '/api/detection/food',
      method: 'POST',
      data: { image: imageData }
    })
  }
  
  static submitReport(reportData) {
    return this.request({
      url: '/api/reports',
      method: 'POST',
      data: reportData
    })
  }
  
  static getCommunityNews() {
    return this.request({
      url: '/api/community/news'
    })
  }
}

module.exports = RequestManager
```

### 3. 状态管理

```javascript
// utils/store.js
class Store {
  constructor() {
    this.state = {
      user: null,
      location: null,
      detectionHistory: [],
      notifications: []
    }
    this.listeners = []
  }
  
  setState(newState) {
    this.state = { ...this.state, ...newState }
    this.notify()
  }
  
  getState() {
    return this.state
  }
  
  subscribe(listener) {
    this.listeners.push(listener)
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener)
    }
  }
  
  notify() {
    this.listeners.forEach(listener => listener(this.state))
  }
}

const store = new Store()
module.exports = store
```

## 📱 适配与测试

### 1. 多设备适配

```css
/* 响应式设计 */
@media screen and (max-width: 375px) {
  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .action-item {
    padding: 32rpx 24rpx;
  }
}

@media screen and (min-width: 768px) {
  .container {
    max-width: 750rpx;
    margin: 0 auto;
  }
}
```

### 2. 测试策略

```javascript
// tests/unit/components.test.js
describe('组件测试', () => {
  test('快速功能组件渲染', () => {
    const actions = [
      { id: 1, icon: '🔍', label: 'AI检测', action: 'detection' }
    ]
    // 测试组件渲染和交互
  })
  
  test('导航栏组件功能', () => {
    // 测试返回按钮、标题显示等
  })
})
```

## 🎯 部署与发布

### 1. 构建配置

```json
// project.config.json
{
  "miniprogramRoot": "miniprogram/",
  "cloudfunctionRoot": "cloudfunctions/",
  "setting": {
    "urlCheck": false,
    "es6": true,
    "enhance": true,
    "postcss": true,
    "preloadBackgroundData": false,
    "minified": true,
    "newFeature": false,
    "coverView": true,
    "nodeModules": false,
    "autoAudits": false,
    "showShadowRootInWxmlPanel": true,
    "scopeDataCheck": false,
    "uglifyFileName": false,
    "checkInvalidKey": true,
    "checkSiteMap": true,
    "uploadWithSourceMap": true,
    "compileHotReLoad": false,
    "lazyloadPlaceholderEnable": false,
    "useMultiFrameRuntime": true,
    "useApiHook": true,
    "useApiHostProcess": true,
    "babelSetting": {
      "ignore": [],
      "disablePlugins": [],
      "outputPath": ""
    },
    "enableEngineNative": false,
    "useIsolateContext": true,
    "userConfirmedBundleSwitch": false,
    "packNpmManually": false,
    "packNpmRelationList": [],
    "minifyWXSS": true,
    "disableUseStrict": false,
    "minifyWXML": true,
    "showES6CompileOption": false,
    "useCompilerPlugins": false
  }
}
```

### 2. 发布检查清单

- [ ] 所有页面功能正常
- [ ] 网络请求正确配置
- [ ] 图片资源优化
- [ ] 性能测试通过
- [ ] 多设备适配验证
- [ ] 用户体验测试
- [ ] 安全性检查
- [ ] 小程序审核要求符合

---

## 📚 总结

这份实现指南提供了从设计系统到具体页面开发的完整方案，包括：

1. **🎨 设计系统**: 统一的色彩、字体、间距规范
2. **🧩 组件化开发**: 可复用的UI组件
3. **📱 页面实现**: 详细的页面结构和交互
4. **🚀 性能优化**: 最佳实践和优化策略
5. **📋 测试部署**: 完整的测试和发布流程

按照这个指南，您可以逐步实现一个功能完整、用户体验优秀的"社区食安AI小卫士"小程序！