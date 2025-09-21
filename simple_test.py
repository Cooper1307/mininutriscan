#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的API测试脚本
"""

import requests
import sys

def test_basic_health():
    """测试基本健康检查"""
    try:
        print("正在测试健康检查接口...")
        response = requests.get('http://127.0.0.1:8000/', timeout=5)
        print(f"根路径响应: {response.status_code}")
        if response.status_code == 200:
            print(f"响应内容: {response.json()}")
            return True
        else:
            print(f"响应失败: {response.text}")
            return False
    except Exception as e:
        print(f"请求异常: {e}")
        return False

def test_health_endpoint():
    """测试详细健康检查"""
    try:
        print("正在测试详细健康检查接口...")
        response = requests.get('http://127.0.0.1:8000/health', timeout=5)
        print(f"健康检查响应: {response.status_code}")
        if response.status_code == 200:
            print(f"响应内容: {response.json()}")
            return True
        else:
            print(f"响应失败: {response.text}")
            return False
    except Exception as e:
        print(f"请求异常: {e}")
        return False

if __name__ == "__main__":
    print("=== 简化API测试 ===")
    
    # 测试根路径
    if test_basic_health():
        print("✅ 根路径测试通过")
    else:
        print("❌ 根路径测试失败")
        sys.exit(1)
    
    # 测试健康检查
    if test_health_endpoint():
        print("✅ 健康检查测试通过")
    else:
        print("❌ 健康检查测试失败")
    
    print("=== 基础测试完成 ===")