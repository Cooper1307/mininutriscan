#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
营养成分解析测试脚本
测试修改后的OCR服务是否能正确解析营养成分表数据
"""

import requests
import base64
import json
from PIL import Image, ImageDraw, ImageFont
import io

def create_test_nutrition_label():
    """
    创建一个包含营养成分表的测试图片
    """
    # 创建一个白色背景的图片
    width, height = 400, 600
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # 尝试使用系统字体，如果没有则使用默认字体
    try:
        font_title = ImageFont.truetype("arial.ttf", 20)
        font_text = ImageFont.truetype("arial.ttf", 16)
    except:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()
    
    # 绘制营养成分表
    y_pos = 20
    
    # 标题
    draw.text((50, y_pos), "营养成分表", fill='black', font=font_title)
    y_pos += 40
    
    # 每份含量
    draw.text((50, y_pos), "每份30g", fill='black', font=font_text)
    y_pos += 30
    
    # 营养成分列表
    nutrition_data = [
        ("能量", "534kJ"),
        ("", "(127kcal)"),
        ("蛋白质", "4.2g"),
        ("脂肪", "5.1g"),
        ("一反式脂肪", "0g"),
        ("胆固醇", "0mg"),
        ("碳水化合物", "15.0g"),
        ("一糖", "1.6g"),
        ("膳食纤维", "2.3g"),
        ("钠", "178mg")
    ]
    
    for name, value in nutrition_data:
        if name:  # 如果有营养成分名称
            draw.text((50, y_pos), f"{name}", fill='black', font=font_text)
            draw.text((200, y_pos), f"{value}", fill='black', font=font_text)
        else:  # 如果是补充信息（如kcal）
            draw.text((200, y_pos), f"{value}", fill='black', font=font_text)
        y_pos += 25
    
    return image

def image_to_base64(image):
    """
    将PIL图片转换为base64字符串
    """
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

def test_nutrition_parsing():
    """
    测试营养成分解析功能
    """
    print("=" * 60)
    print("营养成分解析测试")
    print("=" * 60)
    
    # 创建测试图片
    print("📸 创建测试营养成分表图片...")
    test_image = create_test_nutrition_label()
    
    # 保存测试图片（可选）
    test_image.save("test_nutrition_label_parsing.png")
    print("✅ 测试图片已保存为 test_nutrition_label_parsing.png")
    
    # 转换为base64
    base64_image = image_to_base64(test_image)
    
    # 准备API请求
    url = "http://127.0.0.1:8000/api/v1/detection/analyze-base64"
    
    payload = {
        "image_data": base64_image,
        "detection_type": "ocr_scan"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("🚀 发送API请求进行营养成分解析...")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API调用成功！")
            print(f"🆔 检测ID: {result.get('detection_id')}")
            print(f"📋 检测状态: {result.get('status')}")
            
            # 检查营养信息
            nutrition_info = result.get('nutrition_data', {})
            if nutrition_info:
                print("\n🥗 解析到的营养成分:")
                print("-" * 40)
                
                # 显示所有解析到的营养成分
                for key, value in nutrition_info.items():
                    if value is not None:
                        print(f"  {key}: {value}")
                
                # 检查关键营养成分是否被正确解析
                expected_nutrients = ['energy_kj', 'energy_kcal', 'protein', 'fat', 'carbohydrates', 'sodium']
                found_nutrients = []
                missing_nutrients = []
                
                for nutrient in expected_nutrients:
                    if nutrient in nutrition_info and nutrition_info[nutrient] is not None:
                        found_nutrients.append(nutrient)
                    else:
                        missing_nutrients.append(nutrient)
                
                print(f"\n📈 解析统计:")
                print(f"  ✅ 成功解析: {len(found_nutrients)}/{len(expected_nutrients)} 项")
                print(f"  ✅ 已解析: {', '.join(found_nutrients)}")
                if missing_nutrients:
                    print(f"  ❌ 未解析: {', '.join(missing_nutrients)}")
                
                # 评估解析质量
                success_rate = len(found_nutrients) / len(expected_nutrients) * 100
                print(f"\n🎯 解析成功率: {success_rate:.1f}%")
                
                if success_rate >= 80:
                    print("🎉 营养成分解析质量: 优秀")
                elif success_rate >= 60:
                    print("👍 营养成分解析质量: 良好")
                elif success_rate >= 40:
                    print("⚠️ 营养成分解析质量: 一般")
                else:
                    print("❌ 营养成分解析质量: 需要改进")
                    
            else:
                print("❌ 未解析到任何营养成分信息")
                
            # 检查AI分析结果
            ai_analysis = result.get('ai_analysis')
            if ai_analysis:
                print(f"\n🤖 AI分析结果:")
                print(f"  {ai_analysis[:200]}..." if len(ai_analysis) > 200 else f"  {ai_analysis}")
            
        else:
            print(f"❌ API调用失败")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
    except Exception as e:
        print(f"❌ 未知错误: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_nutrition_parsing()