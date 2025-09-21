#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试图片上传和分析功能
"""

import requests
import base64
import json
import os
from pathlib import Path

def encode_image_to_base64(image_path):
    """将图片文件编码为base64字符串"""
    try:
        with open(image_path, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
    except Exception as e:
        print(f"编码图片失败: {e}")
        return None

def test_base64_upload():
    """测试base64图片上传和分析"""
    print("=== 测试Base64图片上传和分析 ===")
    
    # API端点
    url = "http://127.0.0.1:8000/api/v1/detection/analyze-base64"
    
    # 查找测试图片
    test_image_path = None
    possible_paths = [
        "d:/MyData/projects/mininutriscan/test_image.jpg",
        "d:/MyData/projects/mininutriscan/test_image.png",
        "d:/MyData/projects/mininutriscan/uploads/test.jpg",
        "d:/MyData/projects/mininutriscan/uploads/test.png"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            test_image_path = path
            break
    
    if not test_image_path:
        print("未找到测试图片，创建一个简单的测试图片...")
        # 创建一个简单的测试图片（1x1像素的PNG）
        test_image_path = "d:/MyData/projects/mininutriscan/test_pixel.png"
        # 最小的PNG文件（1x1透明像素）
        png_data = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==')
        with open(test_image_path, 'wb') as f:
            f.write(png_data)
        print(f"创建测试图片: {test_image_path}")
    
    print(f"使用测试图片: {test_image_path}")
    
    # 编码图片
    base64_image = encode_image_to_base64(test_image_path)
    if not base64_image:
        print("图片编码失败")
        return
    
    # 准备请求数据
    data = {
        "image_data": base64_image,
        "user_id": "test_user_123"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("发送请求到API...")
        print(f"请求URL: {url}")
        print(f"图片大小: {len(base64_image)} 字符")
        
        response = requests.post(url, json=data, headers=headers, timeout=60)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 请求成功!")
            print(f"响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"错误响应: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误，请确保后端服务器正在运行")
    except Exception as e:
        print(f"❌ 请求异常: {e}")

def test_health_check():
    """测试健康检查接口"""
    print("=== 测试健康检查接口 ===")
    
    url = "http://127.0.0.1:8000/health"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"健康检查状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"健康检查响应: {response.json()}")
        else:
            print(f"健康检查失败: {response.text}")
    except Exception as e:
        print(f"健康检查异常: {e}")

def main():
    """主函数"""
    print("开始测试图片上传和分析功能...")
    print("="*50)
    
    # 测试健康检查
    test_health_check()
    print()
    
    # 测试图片上传
    test_base64_upload()
    
    print("\n测试完成!")

if __name__ == "__main__":
    main()