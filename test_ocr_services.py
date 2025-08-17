#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR服务测试脚本
测试腾讯云和阿里云OCR服务的配置和基本功能

作者: AI助手
创建时间: 2024
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_environment_variables():
    """
    测试环境变量配置
    检查OCR服务所需的环境变量是否已正确设置
    """
    print("\n=== 环境变量检查 ===")
    
    try:
        from app.core.config import settings
        
        # 腾讯云OCR配置
        tencent_secret_id = settings.TENCENT_SECRET_ID
        tencent_secret_key = settings.TENCENT_SECRET_KEY
        
        # 阿里云OCR配置
        aliyun_access_key_id = settings.ALIBABA_ACCESS_KEY_ID
        aliyun_access_key_secret = settings.ALIBABA_ACCESS_KEY_SECRET
        
        print(f"腾讯云 Secret ID: {'✓ 已配置' if tencent_secret_id else '✗ 未配置'}")
        print(f"腾讯云 Secret Key: {'✓ 已配置' if tencent_secret_key else '✗ 未配置'}")
        print(f"阿里云 Access Key ID: {'✓ 已配置' if aliyun_access_key_id else '✗ 未配置'}")
        print(f"阿里云 Access Key Secret: {'✓ 已配置' if aliyun_access_key_secret else '✗ 未配置'}")
        
        return all([tencent_secret_id, tencent_secret_key, aliyun_access_key_id, aliyun_access_key_secret])
    except ImportError as e:
        print(f"✗ 无法导入配置模块: {e}")
        return False

def test_ocr_service_import():
    """
    测试OCR服务模块导入
    验证OCR服务类是否能正常导入和初始化
    """
    print("\n=== OCR服务模块导入测试 ===")
    
    try:
        from app.services.ocr_service import OCRService
        print("✓ OCR服务模块导入成功")
        
        # 尝试初始化OCR服务
        ocr_service = OCRService()
        print("✓ OCR服务初始化成功")
        
        return True, ocr_service
    except ImportError as e:
        print(f"✗ OCR服务模块导入失败: {e}")
        return False, None
    except Exception as e:
        print(f"✗ OCR服务初始化失败: {e}")
        return False, None

def test_required_packages():
    """
    测试OCR服务所需的Python包
    检查腾讯云和阿里云SDK是否已安装
    """
    print("\n=== OCR服务依赖包检查 ===")
    
    packages = {
        'tencentcloud-sdk-python': 'tencentcloud',
        'alibabacloud_ocr_api20210707': 'alibabacloud_ocr_api20210707',
        'alibabacloud_tea_openapi': 'alibabacloud_tea_openapi',
        'Pillow': 'PIL'
    }
    
    all_installed = True
    
    for package_name, import_name in packages.items():
        try:
            __import__(import_name)
            print(f"✓ {package_name}: 已安装")
        except ImportError:
            print(f"✗ {package_name}: 未安装")
            all_installed = False
    
    return all_installed

def test_ocr_service_methods(ocr_service):
    """
    测试OCR服务的基本方法
    验证OCR服务的各个方法是否存在且可调用
    """
    print("\n=== OCR服务方法检查 ===")
    
    methods_to_check = [
        '_preprocess_image',
        'recognize_nutrition_label',
        '_tencent_ocr',
        '_alibaba_ocr',
        'extract_nutrition_info',
        'get_service_info'
    ]
    
    all_methods_exist = True
    
    for method_name in methods_to_check:
        if hasattr(ocr_service, method_name):
            print(f"✓ {method_name}: 方法存在")
        else:
            print(f"✗ {method_name}: 方法不存在")
            all_methods_exist = False
    
    return all_methods_exist

def create_test_image():
    """
    创建一个简单的测试图像
    用于测试OCR服务的图像处理功能
    """
    print("\n=== 创建测试图像 ===")
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # 创建一个简单的测试图像
        img = Image.new('RGB', (400, 300), color='white')
        draw = ImageDraw.Draw(img)
        
        # 添加一些测试文本（模拟营养标签）
        test_text = [
            "营养成分表",
            "每100g含有:",
            "能量: 2000kJ",
            "蛋白质: 10g",
            "脂肪: 5g",
            "碳水化合物: 60g",
            "钠: 500mg"
        ]
        
        y_position = 30
        for text in test_text:
            draw.text((20, y_position), text, fill='black')
            y_position += 30
        
        # 保存测试图像
        test_image_path = project_root / 'test_nutrition_label.png'
        img.save(test_image_path)
        print(f"✓ 测试图像已创建: {test_image_path}")
        
        return str(test_image_path)
    except ImportError:
        print("✗ Pillow包未安装，无法创建测试图像")
        return None
    except Exception as e:
        print(f"✗ 创建测试图像失败: {e}")
        return None

def main():
    """
    主测试函数
    执行所有OCR服务相关的测试
    """
    print("OCR服务测试开始...")
    print("=" * 50)
    
    # 1. 检查环境变量
    env_ok = test_environment_variables()
    
    # 2. 检查依赖包
    packages_ok = test_required_packages()
    
    # 3. 测试模块导入
    import_ok, ocr_service = test_ocr_service_import()
    
    # 4. 如果导入成功，测试方法
    methods_ok = False
    if import_ok and ocr_service:
        methods_ok = test_ocr_service_methods(ocr_service)
    
    # 5. 创建测试图像（如果Pillow可用）
    test_image_path = create_test_image()
    
    # 总结测试结果
    print("\n" + "=" * 50)
    print("=== OCR服务测试总结 ===")
    print(f"环境变量配置: {'✓ 通过' if env_ok else '✗ 失败'}")
    print(f"依赖包安装: {'✓ 通过' if packages_ok else '✗ 失败'}")
    print(f"模块导入: {'✓ 通过' if import_ok else '✗ 失败'}")
    print(f"方法检查: {'✓ 通过' if methods_ok else '✗ 失败'}")
    print(f"测试图像: {'✓ 已创建' if test_image_path else '✗ 创建失败'}")
    
    # 整体状态
    overall_status = env_ok and import_ok and methods_ok
    print(f"\n整体状态: {'✓ OCR服务配置正常' if overall_status else '✗ OCR服务需要修复'}")
    
    if not packages_ok:
        print("\n建议安装缺失的依赖包:")
        print("pip install tencentcloud-sdk-python")
        print("pip install alibabacloud_ocr_api20210707")
        print("pip install alibabacloud_tea_openapi")
        print("pip install Pillow")
    
    if not env_ok:
        print("请检查并配置以下环境变量:")
        print("- TENCENT_SECRET_ID")
        print("- TENCENT_SECRET_KEY")
        print("- ALIBABA_ACCESS_KEY_ID")
        print("- ALIBABA_ACCESS_KEY_SECRET")
    
    return overall_status

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        sys.exit(1)