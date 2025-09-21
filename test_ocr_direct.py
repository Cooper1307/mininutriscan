#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试OCR服务的营养成分解析功能
不依赖API服务器，直接调用OCR服务
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ocr_service import ocr_service
from PIL import Image, ImageDraw, ImageFont
import base64
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

def test_ocr_direct():
    """
    直接测试OCR服务的营养成分解析功能
    """
    print("=" * 60)
    print("直接OCR营养成分解析测试")
    print("=" * 60)
    
    # 创建测试图片
    print("📸 创建测试营养成分表图片...")
    test_image = create_test_nutrition_label()
    
    # 保存测试图片
    test_image.save("test_nutrition_label_direct.png")
    print("✅ 测试图片已保存为 test_nutrition_label_direct.png")
    
    # 模拟OCR结果（匹配extract_nutrition_info函数期望的格式）
    mock_ocr_result = {
        "success": True,
        "provider": "mock",
        "texts": [
            {"text": "营养成分表"},
            {"text": "每份30g"},
            {"text": "能量 534kJ"},
            {"text": "(127kcal)"},
            {"text": "蛋白质 4.2g"},
            {"text": "脂肪 5.1g"},
            {"text": "一反式脂肪 0g"},
            {"text": "胆固醇 0mg"},
            {"text": "碳水化合物 15.0g"},
            {"text": "一糖 1.6g"},
            {"text": "膳食纤维 2.3g"},
            {"text": "钠 178mg"}
        ],
        "text": "营养成分表 每份30g 能量 534kJ (127kcal) 蛋白质 4.2g 脂肪 5.1g 一反式脂肪 0g 胆固醇 0mg 碳水化合物 15.0g 一糖 1.6g 膳食纤维 2.3g 钠 178mg"
    }
    
    print("🔍 模拟OCR识别结果:")
    for item in mock_ocr_result["texts"]:
        print(f"  - {item['text']}")
    print(f"\n📝 完整文本: {mock_ocr_result['text']}")
    
    print("\n🧠 开始营养成分解析...")
    
    try:
        # 调用营养成分提取函数
        nutrition_result = ocr_service.extract_nutrition_info(mock_ocr_result)
        
        print(f"\n📊 解析结果:")
        print(f"  成功: {nutrition_result['success']}")
        
        if nutrition_result['success']:
            nutrition_info = nutrition_result.get('nutrition_info', {})
            
            if nutrition_info:
                print("\n🥗 解析到的营养成分:")
                print("-" * 40)
                
                # 显示所有解析到的营养成分
                for key, value in nutrition_info.items():
                    if isinstance(value, dict) and 'value' in value:
                        unit = value.get('unit', '')
                        keyword = value.get('keyword', key)
                        print(f"  {keyword}: {value['value']} {unit}")
                    else:
                        print(f"  {key}: {value}")
                
                # 检查关键营养成分是否被正确解析
                expected_nutrients = ['energy_kj', 'energy_kcal', 'protein', 'fat', 'carbohydrates', 'sodium']
                found_nutrients = []
                missing_nutrients = []
                
                for nutrient in expected_nutrients:
                    if nutrient in nutrition_info and nutrition_info[nutrient].get('value'):
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
                
        else:
            print(f"❌ 解析失败: {nutrition_result.get('error', '未知错误')}")
            
    except Exception as e:
        print(f"❌ 解析过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_ocr_direct()