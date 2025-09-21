#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速API测试脚本
"""

import requests
import base64
import json
from io import BytesIO
from PIL import Image

def create_test_image():
    """创建一个简单的测试图片"""
    # 创建一个1x1像素的白色图片
    img = Image.new('RGB', (1, 1), color='white')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def test_health():
    """测试健康检查接口"""
    try:
        response = requests.get('http://127.0.0.1:8000/health', timeout=5)
        print(f"健康检查: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"健康检查失败: {e}")
        return False

def test_image_analysis():
    """测试图片分析接口"""
    try:
        # 创建测试图片
        test_image_b64 = create_test_image()
        
        # 准备请求数据
        data = {
            "image_data": test_image_b64
        }
        
        print("发送图片分析请求...")
        response = requests.post(
            'http://127.0.0.1:8000/api/v1/detection/analyze-base64',
            json=data,
            timeout=10
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 图片分析成功: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return True
        else:
            print(f"❌ 图片分析失败: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 图片分析异常: {e}")
        return False

if __name__ == "__main__":
    print("=== 快速API测试 ===")
    
    # 测试健康检查
    if test_health():
        print("✅ 健康检查通过")
    else:
        print("❌ 健康检查失败")
        exit(1)
    
    # 测试图片分析
    if test_image_analysis():
        print("✅ 图片分析测试通过")
    else:
        print("❌ 图片分析测试失败")
    
    print("=== 测试完成 ===")