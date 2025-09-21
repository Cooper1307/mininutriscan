#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片分析API测试脚本
"""

import requests
import base64
import json
from io import BytesIO
from PIL import Image

def create_simple_test_image():
    """创建一个简单的测试图片"""
    # 创建一个10x10像素的白色图片
    img = Image.new('RGB', (10, 10), color='white')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def test_image_analysis():
    """测试图片分析接口"""
    try:
        print("正在创建测试图片...")
        test_image_b64 = create_simple_test_image()
        print(f"测试图片大小: {len(test_image_b64)} 字符")
        
        # 准备请求数据
        data = {
            "image_data": test_image_b64
        }
        
        print("发送图片分析请求...")
        response = requests.post(
            'http://127.0.0.1:8000/api/v1/detection/analyze-base64',
            json=data,
            timeout=30  # 增加超时时间
        )
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 图片分析成功:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return True
        else:
            print(f"❌ 图片分析失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except Exception as e:
        print(f"❌ 图片分析异常: {e}")
        return False

if __name__ == "__main__":
    print("=== 图片分析API测试 ===")
    
    # 先测试健康检查
    try:
        response = requests.get('http://127.0.0.1:8000/', timeout=5)
        if response.status_code == 200:
            print("✅ 服务器运行正常")
        else:
            print("❌ 服务器状态异常")
            exit(1)
    except Exception as e:
        print(f"❌ 无法连接服务器: {e}")
        exit(1)
    
    # 测试图片分析
    if test_image_analysis():
        print("✅ 图片分析测试通过")
    else:
        print("❌ 图片分析测试失败")
    
    print("=== 测试完成 ===")