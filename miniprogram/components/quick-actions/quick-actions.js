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
      
      // 触发自定义事件，传递点击的功能项
      this.triggerEvent('actionTap', action)
      
      // 添加触觉反馈
      wx.vibrateShort({
        type: 'light'
      })
    }
  }
})