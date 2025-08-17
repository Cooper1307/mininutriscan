#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR服务调试脚本
用于诊断OCR服务配置问题
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ocr_service import OCRService, TENCENT_AVAILABLE, ALIBABA_AVAILABLE
from app.core.config import settings

def test_ocr_configuration():
    """
    测试OCR服务配置
    """
    print("=" * 60)
    print("OCR服务配置诊断")
    print("=" * 60)
    
    # 1. 检查SDK可用性
    print("\n1. SDK可用性检查:")
    print(f"   腾讯云SDK可用: {TENCENT_AVAILABLE}")
    print(f"   阿里云SDK可用: {ALIBABA_AVAILABLE}")
    
    # 2. 检查配置项
    print("\n2. 配置项检查:")
    print(f"   腾讯云Secret ID: {'已配置' if settings.TENCENT_SECRET_ID else '未配置'}")
    print(f"   腾讯云Secret Key: {'已配置' if settings.TENCENT_SECRET_KEY else '未配置'}")
    print(f"   阿里云Access Key ID: {'已配置' if settings.ALIBABA_ACCESS_KEY_ID else '未配置'}")
    print(f"   阿里云Access Key Secret: {'已配置' if settings.ALIBABA_ACCESS_KEY_SECRET else '未配置'}")
    
    # 3. 初始化OCR服务
    print("\n3. OCR服务初始化:")
    try:
        ocr_service = OCRService()
        print(f"   腾讯云配置状态: {ocr_service.tencent_configured}")
        print(f"   阿里云配置状态: {ocr_service.alibaba_configured}")
        
        # 4. 获取服务信息
        service_info = ocr_service.get_service_info()
        print("\n4. 服务信息:")
        for key, value in service_info.items():
            print(f"   {key}: {value}")
            
    except Exception as e:
        print(f"   ❌ OCR服务初始化失败: {str(e)}")
        return False
    
    # 5. 检查具体配置问题
    print("\n5. 详细配置检查:")
    
    if TENCENT_AVAILABLE:
        if settings.TENCENT_SECRET_ID == "your-tencent-secret-id":
            print("   ⚠️  腾讯云Secret ID使用默认值，需要配置真实密钥")
        elif not settings.TENCENT_SECRET_ID:
            print("   ⚠️  腾讯云Secret ID为空")
        else:
            print(f"   ✅ 腾讯云Secret ID已配置: {settings.TENCENT_SECRET_ID[:10]}...")
            
        if not settings.TENCENT_SECRET_KEY:
            print("   ⚠️  腾讯云Secret Key为空")
        else:
            print(f"   ✅ 腾讯云Secret Key已配置: {settings.TENCENT_SECRET_KEY[:10]}...")
    else:
        print("   ❌ 腾讯云SDK未安装")
    
    if ALIBABA_AVAILABLE:
        if settings.ALIBABA_ACCESS_KEY_ID == "your-ali-access-key-id":
            print("   ⚠️  阿里云Access Key ID使用默认值，需要配置真实密钥")
        elif not settings.ALIBABA_ACCESS_KEY_ID:
            print("   ⚠️  阿里云Access Key ID为空")
        else:
            print(f"   ✅ 阿里云Access Key ID已配置: {settings.ALIBABA_ACCESS_KEY_ID[:10]}...")
            
        if not settings.ALIBABA_ACCESS_KEY_SECRET:
            print("   ⚠️  阿里云Access Key Secret为空")
        else:
            print(f"   ✅ 阿里云Access Key Secret已配置: {settings.ALIBABA_ACCESS_KEY_SECRET[:10]}...")
    else:
        print("   ❌ 阿里云SDK未安装")
    
    # 6. 总结和建议
    print("\n6. 诊断结果:")
    if not (ocr_service.tencent_configured or ocr_service.alibaba_configured):
        print("   ❌ 没有可用的OCR服务配置")
        print("\n修复建议:")
        if not TENCENT_AVAILABLE:
            print("   1. 安装腾讯云SDK: pip install tencentcloud-sdk-python")
        if not ALIBABA_AVAILABLE:
            print("   2. 安装阿里云SDK: pip install alibabacloud-ocr-api20210707")
        print("   3. 在.env文件中配置正确的API密钥")
        print("   4. 确保密钥不是默认的占位符值")
        return False
    else:
        print("   ✅ OCR服务配置正常")
        return True

if __name__ == "__main__":
    success = test_ocr_configuration()
    if success:
        print("\n🎉 OCR服务配置检查通过！")
    else:
        print("\n❌ OCR服务配置存在问题，请根据建议进行修复。")