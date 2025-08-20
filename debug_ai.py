#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI服务调试脚本
用于测试AI营养分析功能
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_service import AIService

async def test_ai_service():
    """
    测试AI服务的营养分析功能
    """
    print("🤖 开始测试AI服务...")
    
    # 初始化AI服务
    ai_service = AIService()
    
    # 准备测试营养数据（使用OCR提取的格式）
    nutrition_data = {
        'energy': {'value': 1850.0, 'unit': 'kJ', 'keyword': '能量'},
        'protein': {'value': 12.5, 'unit': 'g', 'keyword': '蛋白质'},
        'fat': {'value': 8.2, 'unit': 'g', 'keyword': '脂肪'},
        'carbohydrate': {'value': 65.3, 'unit': 'g', 'keyword': '碳水化合物'},
        'sodium': {'value': 420.0, 'unit': 'mg', 'keyword': '钠'}
    }
    
    print("📊 测试营养数据:")
    for key, value in nutrition_data.items():
        if isinstance(value, dict):
            print(f"   {key}: {value['value']} {value['unit']}")
        else:
            print(f"   {key}: {value}")
    
    print("\n🔍 开始AI分析...")
    
    try:
        # 执行AI分析
        result = await ai_service.analyze_nutrition(nutrition_data=nutrition_data)
        
        print("\n✅ AI分析完成!")
        
        if result and result.get("success"):
            print("\n🎯 AI分析成功!")
            print(f"   健康评分: {result.get('health_score', 'N/A')}")
            print(f"   风险等级: {result.get('risk_level', 'N/A')}")
            print(f"   建议: {result.get('advice', 'N/A')}")
            if 'analysis' in result:
                print(f"   分析内容: {result['analysis'][:200]}...")  # 只显示前200字符
        else:
            print("❌ AI分析失败或返回无效结果")
            print(f"   错误信息: {result.get('error', '未知错误') if result else '无返回结果'}")
    
    except Exception as e:
        print(f"❌ AI分析过程中发生异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ai_service())