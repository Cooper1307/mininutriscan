#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试匿名用户API接口
验证analyze-base64接口是否支持匿名访问
"""

import requests
import json
import base64
from PIL import Image
import io

def create_test_image():
    """
    创建一个简单的测试图片并转换为base64
    """
    # 创建一个简单的白色图片
    img = Image.new('RGB', (100, 100), color='white')
    
    # 转换为base64
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    img_data = buffer.getvalue()
    
    # 编码为base64
    base64_data = base64.b64encode(img_data).decode('utf-8')
    return f"data:image/jpeg;base64,{base64_data}"

def test_anonymous_api():
    """
    测试匿名用户API访问
    """
    print("开始测试匿名用户API访问...")
    
    # API端点
    url = "http://127.0.0.1:8000/api/v1/detection/analyze-base64"
    
    # 创建测试图片
    test_image = create_test_image()
    
    # 请求数据
    data = {
        "image_data": test_image,
        "detection_type": "image_ocr",
        "user_notes": "匿名用户测试"
    }
    
    # 发送请求（不包含认证头）
    try:
        print("发送API请求...")
        response = requests.post(
            url,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API调用成功！")
            print(f"检测ID: {result.get('id')}")
            print(f"检测状态: {result.get('status')}")
            print(f"检测类型: {result.get('detection_type')}")
            return True
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

def test_with_auth():
    """
    测试带认证的API访问（对比测试）
    """
    print("\n开始测试带认证的API访问...")
    
    url = "http://127.0.0.1:8000/api/v1/detection/analyze-base64"
    test_image = create_test_image()
    
    data = {
        "image_data": test_image,
        "detection_type": "image_ocr",
        "user_notes": "认证用户测试"
    }
    
    # 使用无效的token测试
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer invalid_token"
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        print(f"带无效token的响应状态码: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ 无效token正确返回401")
        else:
            print(f"⚠️ 无效token返回: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 带认证测试错误: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("匿名用户API测试")
    print("=" * 50)
    
    # 测试匿名访问
    success = test_anonymous_api()
    
    # 测试带认证访问
    test_with_auth()
    
    print("\n=" * 50)
    if success:
        print("✅ 匿名用户API测试通过！")
    else:
        print("❌ 匿名用户API测试失败！")
    print("=" * 50)