# MiniNutriScan Android App

## 项目简介

MiniNutriScan是一款基于Android平台的营养成分扫描应用，使用现代化的Jetpack Compose UI框架构建。该应用能够通过相机扫描食品包装上的营养标签，并提供智能的营养成分分析功能。

## 主要功能

### 🔍 核心功能
- **相机扫描**: 使用CameraX库实现高质量的相机预览和拍照功能
- **图像处理**: 集成图像处理功能，优化扫描效果
- **营养分析**: 智能识别和解析营养标签信息
- **历史记录**: 保存扫描历史，方便用户查看过往记录

### 📱 用户界面
- **现代化设计**: 采用Material Design 3设计规范
- **响应式布局**: 支持不同屏幕尺寸的设备
- **直观导航**: 简洁明了的导航结构
- **用户友好**: 优化的用户体验和交互设计

## 技术架构

### 开发环境
- **开发语言**: Kotlin
- **UI框架**: Jetpack Compose
- **最低SDK版本**: API 24 (Android 7.0)
- **目标SDK版本**: API 34 (Android 14)
- **构建工具**: Gradle with Kotlin DSL

### 核心依赖
```kotlin
// UI框架
implementation("androidx.compose.ui:ui")
implementation("androidx.compose.material3:material3")
implementation("androidx.activity:activity-compose")

// 相机功能
implementation("androidx.camera:camera-camera2")
implementation("androidx.camera:camera-lifecycle")
implementation("androidx.camera:camera-view")

// 导航
implementation("androidx.navigation:navigation-compose")

// 权限处理
implementation("com.google.accompanist:accompanist-permissions")

// 网络请求
implementation("com.squareup.retrofit2:retrofit")
implementation("com.squareup.retrofit2:converter-gson")

// 图像处理
implementation("com.github.bumptech.glide:compose")
```

## 项目结构

```
app/src/main/java/com/mininutriscan/app/
├── MainActivity.kt          # 主活动，应用入口点
├── ui/
│   ├── screens/
│   │   ├── HomeScreen.kt    # 主页面，功能导航
│   │   └── CameraScreen.kt  # 相机扫描页面
│   └── navigation/
│       └── AppNavigation.kt # 应用导航配置
└── theme/
    └── Theme.kt            # 应用主题配置
```

## 功能特性

### 1. 主页面 (HomeScreen)
- 应用标题和欢迎信息
- 主要功能卡片：扫描食物
- 次要功能：历史记录、设置
- 最近扫描记录展示

### 2. 相机页面 (CameraScreen)
- 实时相机预览
- 拍照按钮和功能
- 权限请求处理
- 图像捕获和处理

### 3. 导航系统 (AppNavigation)
- 基于Jetpack Navigation Compose
- 流畅的页面切换动画
- 返回栈管理

## 权限配置

应用需要以下权限：
- `CAMERA`: 相机访问权限
- `INTERNET`: 网络访问权限
- `READ_EXTERNAL_STORAGE`: 读取外部存储权限
- `WRITE_EXTERNAL_STORAGE`: 写入外部存储权限

## 安装和运行

### 环境要求
- Android Studio Hedgehog | 2023.1.1 或更高版本
- JDK 17 或更高版本
- Android SDK API 34
- 支持相机的Android设备或模拟器

### 构建步骤
1. 克隆项目到本地
```bash
git clone <repository-url>
cd android-app
```

2. 在Android Studio中打开项目

3. 同步Gradle依赖
```bash
./gradlew build
```

4. 连接Android设备或启动模拟器

5. 运行应用
```bash
./gradlew installDebug
```

## 开发指南

### 代码规范
- 遵循Kotlin官方编码规范
- 使用Jetpack Compose最佳实践
- 保持代码简洁和可读性
- 添加必要的注释和文档

### 测试
- 单元测试：使用JUnit和Mockito
- UI测试：使用Compose Testing
- 集成测试：使用Espresso

### 版本控制
- 使用Git进行版本控制
- 遵循Git Flow工作流
- 提交信息使用规范格式

## 后续开发计划

### 短期目标
- [ ] 完善相机功能实现
- [ ] 集成OCR文字识别
- [ ] 添加营养数据解析
- [ ] 实现本地数据存储

### 长期目标
- [ ] 云端数据同步
- [ ] AI智能推荐
- [ ] 社交分享功能
- [ ] 多语言支持

## 贡献指南

欢迎提交Issue和Pull Request来改进项目。请确保：
1. 代码符合项目规范
2. 添加适当的测试
3. 更新相关文档
4. 提交前进行充分测试

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 项目Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 邮箱: your-email@example.com

---

**最后更新**: 2025年1月21日
**版本**: v1.0.0-alpha
**状态**: 开发中