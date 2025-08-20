#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建测试图片脚本
用于生成营养成分表测试图片
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_nutrition_label_image():
    """
    创建营养成分表测试图片（PNG格式）
    """
    # 创建白色背景图片
    width, height = 400, 600
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # 尝试使用系统字体，如果没有则使用默认字体
    try:
        # Windows系统字体
        font_large = ImageFont.truetype("arial.ttf", 20)
        font_medium = ImageFont.truetype("arial.ttf", 16)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except:
        # 使用默认字体
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # 绘制边框
    draw.rectangle([10, 10, width-10, height-10], outline='black', width=2)
    
    # 标题
    draw.text((width//2, 40), "营养成分表", font=font_large, fill='black', anchor='mm')
    draw.text((width//2, 65), "Nutrition Facts", font=font_small, fill='black', anchor='mm')
    
    # 分隔线
    draw.line([20, 80, width-20, 80], fill='black', width=2)
    
    # 营养成分数据
    y_pos = 110
    draw.text((30, y_pos), "每100g营养成分", font=font_medium, fill='black')
    
    # 营养成分列表
    nutrients = [
        ("能量", "1850kJ"),
        ("蛋白质", "12.5g"),
        ("脂肪", "8.2g"),
        ("碳水化合物", "65.3g"),
        ("钠", "420mg"),
        ("维生素C", "15mg"),
        ("钙", "120mg"),
        ("铁", "2.5mg")
    ]
    
    y_pos = 140
    for name, value in nutrients:
        draw.text((30, y_pos), name, font=font_small, fill='black')
        draw.text((width-30, y_pos), value, font=font_small, fill='black', anchor='rm')
        y_pos += 30
    
    # 保存图片
    output_path = "uploads/test_nutrition_label.png"
    os.makedirs("uploads", exist_ok=True)
    image.save(output_path, "PNG")
    print(f"✅ 测试图片已创建: {output_path}")
    return output_path

if __name__ == "__main__":
    create_nutrition_label_image()