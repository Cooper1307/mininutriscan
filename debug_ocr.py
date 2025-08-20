#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试OCR服务和营养信息提取功能
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ocr_service import OCRService

async def test_ocr_service():
    """
    测试OCR服务的完整流程
    """
    print("🔬 开始测试OCR服务...")
    
    # 初始化OCR服务
    ocr_service = OCRService()
    
    # 测试图片路径
    test_image = "uploads/test_nutrition_label.png"
    
    if not os.path.exists(test_image):
        print(f"❌ 测试图片不存在: {test_image}")
        return
    
    print(f"📷 测试图片: {test_image}")
    
    try:
        # 步骤1: OCR识别
        print("\n🔍 步骤1: 执行OCR识别...")
        ocr_result = await ocr_service.recognize_nutrition_label(test_image)
        print(f"OCR结果: {ocr_result}")
        
        if not ocr_result.get("success"):
            print(f"❌ OCR识别失败: {ocr_result.get('error')}")
            return
        
        # 步骤2: 提取营养信息
        print("\n🥗 步骤2: 提取营养信息...")
        nutrition_result = ocr_service.extract_nutrition_info(ocr_result)
        print(f"营养信息提取结果: {nutrition_result}")
        
        if nutrition_result.get("success"):
            nutrition_info = nutrition_result.get("nutrition_info", {})
            print("\n📊 提取到的营养成分:")
            for nutrient, data in nutrition_info.items():
                print(f"   {nutrient}: {data['value']} {data['unit']}")
        else:
            print(f"❌ 营养信息提取失败: {nutrition_result.get('error')}")
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ocr_service())