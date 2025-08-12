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
      // 触发自定义事件，允许父组件处理返回逻辑
      this.triggerEvent('back')
      
      // 默认行为：返回上一页
      wx.navigateBack({
        fail: () => {
          // 如果无法返回，则跳转到首页
          wx.switchTab({
            url: '/pages/index/index'
          })
        }
      })
    }
  }
})