#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小程序API连接测试脚本
测试小程序与后端API的连接状态

作者: AI助手
创建时间: 2024
"""

import requests
import json
import sys
from datetime import datetime

def test_api_connection():
    """
    测试API连接
    """
    print("=" * 50)
    print("🔍 小程序API连接测试")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    # 测试基本连接
    print("\n1. 测试基本连接...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ 基本连接成功")
            print(f"   响应: {response.json()}")
        else:
            print(f"❌ 基本连接失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 基本连接失败: {e}")
        return False
    
    # 测试健康检查
    print("\n2. 测试健康检查...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 健康检查成功")
            health_data = response.json()
            print(f"   API状态: {health_data.get('api')}")
            print(f"   数据库状态: {health_data.get('database')}")
        else:
            print(f"❌ 健康检查失败: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
    
    # 测试API文档
    print("\n3. 测试API文档...")
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API文档可访问")
        else:
            print(f"❌ API文档不可访问: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ API文档访问失败: {e}")
    
    # 测试CORS配置
    print("\n4. 测试CORS配置...")
    try:
        headers = {
            'Origin': 'https://servicewechat.com',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        response = requests.options(f"{base_url}/api/v1/info", headers=headers, timeout=5)
        if response.status_code in [200, 204]:
            print("✅ CORS配置正常")
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            for key, value in cors_headers.items():
                if value:
                    print(f"   {key}: {value}")
        else:
            print(f"❌ CORS配置异常: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ CORS测试失败: {e}")
    
    # 测试API信息接口
    print("\n5. 测试API信息接口...")
    try:
        response = requests.get(f"{base_url}/api/v1/info", timeout=5)
        if response.status_code == 200:
            print("✅ API信息接口正常")
            api_info = response.json()
            print(f"   API名称: {api_info.get('name')}")
            print(f"   API版本: {api_info.get('version')}")
        else:
            print(f"❌ API信息接口异常: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ API信息接口测试失败: {e}")
    
    # 测试图片检测接口（不需要认证的测试）
    print("\n6. 测试图片检测接口...")
    try:
        # 模拟小程序请求头
        headers = {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
        }
        
        # 测试接口是否存在（不发送实际数据）
        response = requests.options(f"{base_url}/api/v1/detection/upload-image", headers=headers, timeout=5)
        if response.status_code in [200, 204, 405]:  # 405表示方法不允许，但接口存在
            print("✅ 图片检测接口存在")
        else:
            print(f"❌ 图片检测接口不存在: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 图片检测接口测试失败: {e}")
    
    return True

def test_miniprogram_config():
    """
    检查小程序配置
    """
    print("\n" + "=" * 50)
    print("📱 小程序配置检查")
    print("=" * 50)
    
    # 检查小程序配置文件
    config_files = [
        "miniprogram/app.json",
        "miniprogram/config/api.js",
        "miniprogram/utils/api.js"
    ]
    
    for config_file in config_files:
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                print(f"✅ {config_file} 存在")
        except FileNotFoundError:
            print(f"❌ {config_file} 不存在")
        except Exception as e:
            print(f"❌ {config_file} 读取失败: {e}")
    
    # 检查图标文件
    print("\n检查导航栏图标...")
    icon_files = [
        "miniprogram/assets/icons/home.png",
        "miniprogram/assets/icons/home-active.png",
        "miniprogram/assets/icons/detection.png",
        "miniprogram/assets/icons/detection-active.png",
        "miniprogram/assets/icons/report.png",
        "miniprogram/assets/icons/report-active.png",
        "miniprogram/assets/icons/education.png",
        "miniprogram/assets/icons/education-active.png",
        "miniprogram/assets/icons/profile.png",
        "miniprogram/assets/icons/profile-active.png"
    ]
    
    missing_icons = []
    for icon_file in icon_files:
        try:
            with open(icon_file, 'rb') as f:
                print(f"✅ {icon_file} 存在")
        except FileNotFoundError:
            missing_icons.append(icon_file)
            print(f"❌ {icon_file} 不存在")
    
    if missing_icons:
        print(f"\n⚠️  发现 {len(missing_icons)} 个缺失的图标文件")
        return False
    else:
        print("\n✅ 所有导航栏图标文件都存在")
        return True

def generate_fix_suggestions():
    """
    生成修复建议
    """
    print("\n" + "=" * 50)
    print("🔧 修复建议")
    print("=" * 50)
    
    print("\n如果小程序显示'服务暂不可用'，请检查:")
    print("1. 后端服务是否正常运行")
    print("   - 运行: uvicorn main:app --reload --host 127.0.0.1 --port 8000")
    print("   - 访问: http://127.0.0.1:8000/health")
    
    print("\n2. 小程序API配置是否正确")
    print("   - 检查 miniprogram/config/api.js 中的 BASE_URL")
    print("   - 确保 CURRENT_ENV 设置为 'development'")
    
    print("\n3. 网络请求权限")
    print("   - 在微信开发者工具中开启'不校验合法域名'")
    print("   - 检查小程序的网络请求配置")
    
    print("\n如果导航栏图标不显示，请检查:")
    print("1. 图标文件路径是否正确")
    print("2. 图标文件是否存在")
    print("3. 图标文件格式是否正确（PNG格式）")
    
    print("\n建议的调试步骤:")
    print("1. 重启后端服务")
    print("2. 重启微信开发者工具")
    print("3. 清除小程序缓存")
    print("4. 检查控制台错误信息")

def main():
    """
    主函数
    """
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试API连接
    api_ok = test_api_connection()
    
    # 检查小程序配置
    config_ok = test_miniprogram_config()
    
    # 生成修复建议
    generate_fix_suggestions()
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试总结")
    print("=" * 50)
    
    if api_ok and config_ok:
        print("✅ 所有测试通过，小程序应该可以正常工作")
        print("\n如果仍有问题，请:")
        print("1. 检查微信开发者工具的控制台错误")
        print("2. 确认网络设置正确")
        print("3. 重启服务和开发工具")
    else:
        print("❌ 发现问题，请根据上述建议进行修复")
    
    print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return api_ok and config_ok

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        sys.exit(1)