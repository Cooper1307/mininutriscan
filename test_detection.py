#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检测功能测试脚本
用于测试图片检测API的性能和响应时间
"""

import requests
import base64
import time
import json
from pathlib import Path

def encode_image_to_base64(image_path: str) -> str:
    """
    将图片文件编码为base64字符串
    
    Args:
        image_path: 图片文件路径
        
    Returns:
        base64编码的图片字符串（带data URI前缀）
    """
    # 获取文件扩展名
    file_ext = Path(image_path).suffix.lower()
    
    # 确定MIME类型
    if file_ext == '.svg':
        mime_type = 'image/svg+xml'
    elif file_ext in ['.jpg', '.jpeg']:
        mime_type = 'image/jpeg'
    elif file_ext == '.png':
        mime_type = 'image/png'
    elif file_ext == '.gif':
        mime_type = 'image/gif'
    else:
        mime_type = 'image/jpeg'  # 默认
    
    # 读取文件并编码
    with open(image_path, 'rb') as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
    
    # 返回带data URI前缀的格式
    return f"data:{mime_type};base64,{image_data}"

def test_detection_api(image_path: str, api_url: str = "http://127.0.0.1:8000/api/v1/detection/analyze-base64"):
    """
    测试检测API
    
    Args:
        image_path: 测试图片路径
        api_url: API端点URL
    """
    print(f"🧪 开始测试检测API...")
    print(f"📷 测试图片: {image_path}")
    print(f"🌐 API地址: {api_url}")
    print("-" * 50)
    
    try:
        # 检查图片文件是否存在
        if not Path(image_path).exists():
            print(f"❌ 错误: 图片文件不存在 - {image_path}")
            return
        
        # 编码图片
        print("📤 正在编码图片...")
        start_encode = time.time()
        image_base64 = encode_image_to_base64(image_path)
        encode_time = time.time() - start_encode
        print(f"✅ 图片编码完成，耗时: {encode_time:.2f}秒")
        
        # 准备请求数据
        request_data = {
            "image_data": image_base64,
            "user_id": "test_user"
        }
        
        # 发送请求
        print("🚀 正在发送检测请求...")
        start_request = time.time()
        
        response = requests.post(
            api_url,
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=60  # 60秒超时
        )
        
        request_time = time.time() - start_request
        print(f"📡 请求完成，耗时: {request_time:.2f}秒")
        
        # 检查响应状态
        if response.status_code == 200:
            print("✅ 请求成功!")
            result = response.json()
            
            # 打印结果摘要
            print("\n📊 检测结果摘要:")
            print(f"   检测ID: {result.get('detection_id', 'N/A')}")
            print(f"   状态: {result.get('status', 'N/A')}")
            print(f"   处理时间: {result.get('processing_time', 'N/A')}秒")
            
            # 营养数据
            nutrition_data = result.get('nutrition_data', {})
            if nutrition_data:
                print("\n🥗 营养成分数据:")
                print(f"   能量: {nutrition_data.get('energy_kj', 'N/A')} kJ")
                print(f"   蛋白质: {nutrition_data.get('protein', 'N/A')} g")
                print(f"   脂肪: {nutrition_data.get('fat', 'N/A')} g")
                print(f"   碳水化合物: {nutrition_data.get('carbohydrate', 'N/A')} g")
            
            # AI分析
            ai_analysis = result.get('ai_analysis', {})
            if ai_analysis:
                print("\n🤖 AI分析结果:")
                print(f"   健康评分: {ai_analysis.get('health_score', 'N/A')}")
                recommendations = ai_analysis.get('recommendations', [])
                if recommendations:
                    print("   建议:")
                    for i, rec in enumerate(recommendations[:3], 1):
                        print(f"     {i}. {rec}")
            
            print(f"\n⏱️  总耗时: {encode_time + request_time:.2f}秒")
            
        else:
            print(f"❌ 请求失败! 状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时! API响应时间过长")
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误! 请检查API服务是否正常运行")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

def main():
    """
    主函数
    """
    print("🔬 MiniNutriScan 检测功能性能测试")
    print("=" * 50)
    
    # 测试图片路径（使用项目中的示例图片）
    test_images = [
        "uploads/test_nutrition_label.png",  # PNG格式测试图片
        "uploads/test_nutrition_label.svg",
        "uploads/nutrition_label_sample.svg",
        "uploads/food_sample.svg"
    ]
    
    for image_path in test_images:
        if Path(image_path).exists():
            test_detection_api(image_path)
            print("\n" + "=" * 50 + "\n")
            break
    else:
        print("❌ 没有找到测试图片文件")
        print("请确保以下文件存在:")
        for img in test_images:
            print(f"   - {img}")

if __name__ == "__main__":
    main()