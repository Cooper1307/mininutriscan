#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR功能测试脚本
测试OCR服务的实际识别能力
"""

import sys
import os
import asyncio
from PIL import Image, ImageDraw, ImageFont

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ocr_service import OCRService

def create_test_nutrition_image(output_path: str) -> str:
    """
    创建一个包含营养成分表的测试图片
    
    Args:
        output_path: 输出图片路径
        
    Returns:
        创建的图片路径
    """
    # 创建一个白色背景的图片
    width, height = 400, 300
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # 尝试使用系统字体，如果没有则使用默认字体
    try:
        # Windows系统字体
        font_large = ImageFont.truetype("arial.ttf", 20)
        font_medium = ImageFont.truetype("arial.ttf", 16)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except:
        try:
            # 备用字体
            font_large = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", 20)
            font_medium = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", 16)
            font_small = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", 14)
        except:
            # 使用默认字体
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
    
    # 绘制营养成分表
    y_offset = 20
    
    # 标题
    draw.text((50, y_offset), "营养成分表", fill='black', font=font_large)
    y_offset += 40
    
    # 每100g含有
    draw.text((50, y_offset), "每100g含有:", fill='black', font=font_medium)
    y_offset += 30
    
    # 营养成分列表
    nutrition_items = [
        "能量        2100kJ (500kcal)",
        "蛋白质      25.0g",
        "脂肪        30.0g",
        "碳水化合物  45.0g",
        "钠          800mg",
        "钙          120mg",
        "铁          15mg"
    ]
    
    for item in nutrition_items:
        draw.text((70, y_offset), item, fill='black', font=font_small)
        y_offset += 25
    
    # 保存图片
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    image.save(output_path)
    print(f"✅ 测试图片已创建: {output_path}")
    
    return output_path

async def test_ocr_recognition(image_path: str):
    """
    测试OCR识别功能
    
    Args:
        image_path: 测试图片路径
    """
    print("=" * 60)
    print("OCR功能测试")
    print("=" * 60)
    
    try:
        # 初始化OCR服务
        print("\n1. 初始化OCR服务...")
        ocr_service = OCRService()
        
        # 获取服务信息
        service_info = ocr_service.get_service_info()
        print(f"   服务状态: {'已配置' if service_info['configured'] else '未配置'}")
        print(f"   腾讯云: {'可用' if service_info['tencent_available'] else '不可用'}")
        print(f"   阿里云: {'可用' if service_info['alibaba_available'] else '不可用'}")
        
        if not service_info['configured']:
            print("   ❌ OCR服务未正确配置，无法进行测试")
            return False
        
        # 测试营养标签识别
        print("\n2. 测试营养标签识别...")
        print(f"   图片路径: {image_path}")
        
        # 使用auto模式（自动选择最佳提供商）
        result = await ocr_service.recognize_nutrition_label(image_path, provider="auto")
        
        if result['success']:
            print("   ✅ OCR识别成功")
            print(f"   识别文本长度: {len(result.get('text', ''))} 字符")
            print(f"   置信度: {result.get('confidence', 0):.2f}")
            print(f"   使用提供商: {result.get('provider', '未知')}")
            
            # 显示识别的文本（前200个字符）
            text = result.get('text', '')
            if text:
                print(f"\n   识别文本预览:")
                print(f"   {text[:200]}{'...' if len(text) > 200 else ''}")
            
            # 测试营养信息提取
            print("\n3. 测试营养信息提取...")
            nutrition_info = ocr_service.extract_nutrition_info(result)
            
            if nutrition_info:
                print("   ✅ 营养信息提取成功")
                print(f"   提取到 {len(nutrition_info)} 项营养数据:")
                for key, value in nutrition_info.items():
                    if value is not None:
                        print(f"     {key}: {value}")
            else:
                print("   ⚠️  未能提取到营养信息")
            
            return True
            
        else:
            print("   ❌ OCR识别失败")
            print(f"   错误信息: {result.get('error', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"   ❌ OCR测试过程中发生错误: {str(e)}")
        import traceback
        print(f"   详细错误信息: {traceback.format_exc()}")
        return False

async def test_different_providers(image_path: str):
    """
    测试不同的OCR提供商
    
    Args:
        image_path: 测试图片路径
    """
    print("\n" + "=" * 60)
    print("不同OCR提供商测试")
    print("=" * 60)
    
    ocr_service = OCRService()
    providers = []
    
    if ocr_service.tencent_configured:
        providers.append("tencent")
    if ocr_service.alibaba_configured:
        providers.append("alibaba")
    
    if not providers:
        print("   ❌ 没有可用的OCR提供商")
        return
    
    for provider in providers:
        print(f"\n测试 {provider.upper()} OCR:")
        try:
            result = await ocr_service.recognize_nutrition_label(image_path, provider=provider)
            
            if result['success']:
                print(f"   ✅ {provider.upper()} 识别成功")
                print(f"   文本长度: {len(result.get('text', ''))} 字符")
                print(f"   置信度: {result.get('confidence', 0):.2f}")
            else:
                print(f"   ❌ {provider.upper()} 识别失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            print(f"   ❌ {provider.upper()} 测试出错: {str(e)}")

async def main():
    """
    主测试函数
    """
    # 创建测试图片
    test_image_path = "uploads/test_nutrition_label.png"
    create_test_nutrition_image(test_image_path)
    
    # 测试OCR功能
    success = await test_ocr_recognition(test_image_path)
    
    # 测试不同提供商
    await test_different_providers(test_image_path)
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 OCR功能测试通过！")
    else:
        print("❌ OCR功能测试失败，请检查配置和网络连接。")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    asyncio.run(main())