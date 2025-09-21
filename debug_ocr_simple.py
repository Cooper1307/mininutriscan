#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的OCR调试脚本
"""

import asyncio
import sys
import os
from PIL import Image
import base64
import io

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ocr_service import OCRService

async def test_ocr_with_simple_image():
    """
    使用简单的白色图片测试OCR服务
    """
    print("🔬 开始测试OCR服务...")
    
    # 创建一个简单的白色图片
    image = Image.new('RGB', (100, 100), 'white')
    
    # 保存到临时文件
    temp_path = "temp_test_image.png"
    image.save(temp_path)
    
    try:
        # 初始化OCR服务
        ocr_service = OCRService()
        
        print(f"📷 测试图片: {temp_path}")
        
        # 步骤1: OCR识别
        print("\n🔍 步骤1: 执行OCR识别...")
        ocr_result = await ocr_service.recognize_nutrition_label(temp_path)
        print(f"OCR结果: {ocr_result}")
        
        if not ocr_result.get("success"):
            print(f"❌ OCR识别失败: {ocr_result.get('error')}")
            return False
        
        # 步骤2: 提取营养信息
        print("\n🥗 步骤2: 提取营养信息...")
        nutrition_result = ocr_service.extract_nutrition_info(ocr_result)
        print(f"营养信息提取结果: {nutrition_result}")
        
        if nutrition_result.get("success"):
            nutrition_info = nutrition_result.get("nutrition_info", {})
            print("\n📊 提取到的营养成分:")
            for nutrient, data in nutrition_info.items():
                print(f"   {nutrient}: {data['value']} {data['unit']}")
            return True
        else:
            print(f"❌ 营养信息提取失败: {nutrition_result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    result = asyncio.run(test_ocr_with_simple_image())
    if result:
        print("\n✅ OCR服务测试成功")
    else:
        print("\n❌ OCR服务测试失败")