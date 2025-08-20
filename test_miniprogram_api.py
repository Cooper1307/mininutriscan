#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试小程序API调用
模拟小程序发送的请求格式
"""

import requests
import base64
import json
from pathlib import Path

def test_miniprogram_api():
    """测试小程序API调用"""
    print("=== 测试小程序API调用 ===")
    
    # API端点
    api_url = "http://127.0.0.1:8000/api/v1/detection/analyze-base64"
    
    # 使用项目根目录下的测试图片
    test_image_path = "test_nutrition_label.png"
    
    # 检查测试图片是否存在
    if not Path(test_image_path).exists():
        print(f"❌ 测试图片不存在: {test_image_path}")
        print("请确保有测试图片文件")
        return
    
    # 读取并转换图片为base64
    with open(test_image_path, 'rb') as f:
        image_data = f.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        test_image_base64 = f"data:image/jpeg;base64,{image_base64}"
    
    # 模拟小程序发送的请求数据
    request_data = {
        "image_data": test_image_base64,
        "detection_type": "image_ocr",
        "user_notes": "小程序图片检测"
    }
    
    try:
        print(f"发送请求到: {api_url}")
        print(f"请求数据: {json.dumps(request_data, indent=2, ensure_ascii=False)}")
        
        # 发送POST请求
        response = requests.post(
            api_url,
            json=request_data,
            headers={
                'Content-Type': 'application/json'
            },
            timeout=30
        )
        
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ API调用成功!")
            print(f"响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # 检查关键字段
            if 'product_name' in result:
                print(f"\n📦 产品名称: {result['product_name']}")
            
            if 'nutrition_data' in result:
                print(f"🥗 营养数据: {result['nutrition_data']}")
            
            if 'ai_analysis' in result and result['ai_analysis']:
                ai_analysis = result['ai_analysis']
                print(f"🤖 AI分析:")
                print(f"  - 健康评分: {ai_analysis.get('health_score', 'N/A')}")
                print(f"  - 风险等级: {ai_analysis.get('risk_level', 'N/A')}")
                print(f"  - 建议: {ai_analysis.get('recommendations', 'N/A')}")
            
        else:
            print(f"\n❌ API调用失败!")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ 连接失败: 无法连接到后端服务")
        print("请确保后端服务正在运行在 http://127.0.0.1:8000")
    except requests.exceptions.Timeout:
        print("\n❌ 请求超时")
    except Exception as e:
        print(f"\n❌ 请求异常: {e}")

if __name__ == "__main__":
    test_miniprogram_api()