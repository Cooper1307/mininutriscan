#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统连接测试脚本
测试PostgreSQL、Redis和FastAPI服务的连接状态
"""

import sys
import os
import requests
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from app.core.database import test_db_connection, test_redis_connection
    from app.core.config import settings
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    print("请确保已安装所有依赖包")
    sys.exit(1)

def test_fastapi_server():
    """
    测试FastAPI服务器连接
    """
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ FastAPI服务器: 运行正常")
            print(f"   状态: {data.get('status', 'unknown')}")
            print(f"   时间: {data.get('timestamp', 'unknown')}")
            return True
        else:
            print(f"❌ FastAPI服务器: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ FastAPI服务器: 连接失败 (服务器未启动?)")
        return False
    except requests.exceptions.Timeout:
        print("❌ FastAPI服务器: 连接超时")
        return False
    except Exception as e:
        print(f"❌ FastAPI服务器: 测试失败 - {e}")
        return False

def test_api_docs():
    """
    测试API文档页面
    """
    try:
        response = requests.get("http://127.0.0.1:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API文档页面: 可访问")
            print("   地址: http://127.0.0.1:8000/docs")
            return True
        else:
            print(f"❌ API文档页面: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API文档页面: 测试失败 - {e}")
        return False

def main():
    """
    主测试函数
    """
    print("🔍 MiniNutriScan 系统连接测试")
    print("=" * 50)
    
    # 测试结果统计
    results = {
        "postgresql": False,
        "redis": False,
        "fastapi": False,
        "docs": False
    }
    
    # 1. 测试PostgreSQL连接
    print("\n📊 测试数据库连接...")
    try:
        if test_db_connection():
            print("✅ PostgreSQL: 连接成功")
            print(f"   数据库URL: {settings.database_url.split('@')[1] if '@' in settings.database_url else settings.database_url}")
            results["postgresql"] = True
        else:
            print("❌ PostgreSQL: 连接失败")
    except Exception as e:
        print(f"❌ PostgreSQL: 测试异常 - {e}")
    
    # 2. 测试Redis连接
    print("\n🔄 测试Redis连接...")
    try:
        if test_redis_connection():
            print("✅ Redis: 连接成功")
            print(f"   Redis地址: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
            print(f"   数据库: {settings.REDIS_DB}")
            results["redis"] = True
        else:
            print("❌ Redis: 连接失败")
    except Exception as e:
        print(f"❌ Redis: 测试异常 - {e}")
    
    # 3. 测试FastAPI服务器
    print("\n🚀 测试FastAPI服务器...")
    results["fastapi"] = test_fastapi_server()
    
    # 4. 测试API文档
    print("\n📚 测试API文档...")
    results["docs"] = test_api_docs()
    
    # 显示测试总结
    print("\n" + "=" * 50)
    print("📋 测试总结:")
    
    success_count = sum(results.values())
    total_count = len(results)
    
    for service, status in results.items():
        status_icon = "✅" if status else "❌"
        service_name = {
            "postgresql": "PostgreSQL数据库",
            "redis": "Redis缓存",
            "fastapi": "FastAPI服务器",
            "docs": "API文档"
        }[service]
        print(f"   {status_icon} {service_name}: {'正常' if status else '异常'}")
    
    print(f"\n🎯 总体状态: {success_count}/{total_count} 服务正常")
    
    if success_count == total_count:
        print("🎉 所有服务运行正常！系统已准备就绪。")
        print("\n🔗 快速链接:")
        print("   • API服务: http://127.0.0.1:8000")
        print("   • API文档: http://127.0.0.1:8000/docs")
        print("   • 健康检查: http://127.0.0.1:8000/health")
    else:
        print("⚠️  部分服务存在问题，请检查配置和服务状态。")
        
        # 提供故障排除建议
        print("\n🔧 故障排除建议:")
        if not results["postgresql"]:
            print("   • PostgreSQL: 检查数据库服务是否启动，用户名密码是否正确")
        if not results["redis"]:
            print("   • Redis: 检查Redis服务是否启动 (redis-server.exe)")
        if not results["fastapi"]:
            print("   • FastAPI: 检查服务器是否启动 (python main.py)")
        if not results["docs"]:
            print("   • API文档: 检查FastAPI服务器状态")
    
    return success_count == total_count

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 测试过程中发生异常: {e}")
        sys.exit(1)