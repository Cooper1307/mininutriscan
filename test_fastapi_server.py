#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI服务器自动化测试脚本
验证FastAPI服务器配置、路由、中间件等功能

作者: AI助手
创建时间: 2024
"""

import asyncio
import sys
import os
import json
from pathlib import Path
from typing import Dict, Any, List
import importlib.util

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def print_header(title: str):
    """打印测试标题"""
    print(f"\n{'='*50}")
    print(f"=== {title} ===")
    print(f"{'='*50}")

def print_status(item: str, success: bool, details: str = ""):
    """打印测试状态"""
    status = "✓" if success else "✗"
    print(f"{status} {item}: {details if details else ('通过' if success else '失败')}")

def test_fastapi_app_creation():
    """
    测试FastAPI应用创建
    验证FastAPI应用是否能正常创建和配置
    """
    print_header("FastAPI应用创建测试")
    
    try:
        # 导入main模块
        import main
        app = main.app
        
        # 验证应用基本属性
        print_status("FastAPI应用导入", True)
        print_status("应用标题", app.title == "MiniNutriScan API", f"标题: {app.title}")
        print_status("应用版本", app.version == "1.0.0", f"版本: {app.version}")
        print_status("API文档路径", app.docs_url == "/docs", f"文档: {app.docs_url}")
        
        return True, app
    except Exception as e:
        print_status("FastAPI应用创建", False, f"错误: {e}")
        return False, None

def test_middleware_configuration(app):
    """
    测试中间件配置
    验证CORS和其他中间件是否正确配置
    """
    print_header("中间件配置测试")
    
    try:
        # 检查中间件
        middleware_found = False
        cors_configured = False
        
        for middleware in app.user_middleware:
            if 'CORSMiddleware' in str(middleware.cls):
                middleware_found = True
                cors_configured = True
                break
        
        print_status("中间件注册", middleware_found)
        print_status("CORS配置", cors_configured)
        
        return cors_configured
    except Exception as e:
        print_status("中间件配置", False, f"错误: {e}")
        return False

def test_route_registration(app):
    """
    测试路由注册
    验证所有API路由是否正确注册
    """
    print_header("路由注册测试")
    
    try:
        routes = app.routes
        route_paths = [route.path for route in routes if hasattr(route, 'path')]
        
        # 检查基础路由
        basic_routes = ["/", "/health", "/api/v1/info"]
        api_routes = [path for path in route_paths if path.startswith('/api/v1/')]
        
        print_status("总路由数量", len(routes) > 0, f"共 {len(routes)} 个路由")
        
        for route in basic_routes:
            found = route in route_paths
            print_status(f"基础路由 {route}", found)
        
        print_status("API路由注册", len(api_routes) > 0, f"共 {len(api_routes)} 个API路由")
        
        # 显示前几个API路由
        if api_routes:
            print("\n主要API路由:")
            for route in sorted(api_routes)[:10]:
                print(f"  - {route}")
            if len(api_routes) > 10:
                print(f"  ... 还有 {len(api_routes) - 10} 个路由")
        
        return len(api_routes) > 0
    except Exception as e:
        print_status("路由注册", False, f"错误: {e}")
        return False

def test_static_files_configuration(app):
    """
    测试静态文件配置
    验证静态文件服务是否正确配置
    """
    print_header("静态文件配置测试")
    
    try:
        # 检查uploads目录
        uploads_dir = "uploads"
        uploads_exists = os.path.exists(uploads_dir)
        print_status("uploads目录", uploads_exists)
        
        # 检查静态文件挂载
        static_mounted = False
        for route in app.routes:
            if hasattr(route, 'path') and route.path == '/uploads':
                static_mounted = True
                break
        
        print_status("静态文件挂载", static_mounted)
        
        return uploads_exists and static_mounted
    except Exception as e:
        print_status("静态文件配置", False, f"错误: {e}")
        return False

def test_exception_handlers(app):
    """
    测试异常处理器
    验证异常处理器是否正确配置
    """
    print_header("异常处理器测试")
    
    try:
        # 检查异常处理器
        exception_handlers = app.exception_handlers
        
        # 检查HTTPException处理器
        from fastapi import HTTPException
        http_handler = HTTPException in exception_handlers
        print_status("HTTPException处理器", http_handler)
        
        # 检查通用异常处理器
        general_handler = Exception in exception_handlers
        print_status("通用异常处理器", general_handler)
        
        return http_handler and general_handler
    except Exception as e:
        print_status("异常处理器", False, f"错误: {e}")
        return False

def test_environment_configuration():
    """
    测试环境配置
    验证环境变量和配置是否正确
    """
    print_header("环境配置测试")
    
    try:
        # 检查环境变量
        host = os.getenv("HOST", "127.0.0.1")
        port = int(os.getenv("PORT", "8000"))
        debug = os.getenv("DEBUG", "true").lower() == "true"
        
        print_status("HOST配置", True, f"主机: {host}")
        print_status("PORT配置", True, f"端口: {port}")
        print_status("DEBUG配置", True, f"调试模式: {'开启' if debug else '关闭'}")
        
        # 检查.env文件
        env_file_exists = os.path.exists(".env")
        print_status(".env文件", env_file_exists)
        
        return True
    except Exception as e:
        print_status("环境配置", False, f"错误: {e}")
        return False

def test_database_integration():
    """
    测试数据库集成
    验证数据库连接和表创建
    """
    print_header("数据库集成测试")
    
    try:
        # 导入数据库模块
        from app.database import check_database_connection, create_tables
        
        # 测试数据库连接
        db_connected = check_database_connection()
        print_status("数据库连接", db_connected)
        
        if db_connected:
            # 测试表创建
            try:
                create_tables()
                print_status("数据库表创建", True)
                return True
            except Exception as e:
                print_status("数据库表创建", False, f"错误: {e}")
                return False
        else:
            print_status("数据库表创建", False, "数据库未连接")
            return False
            
    except Exception as e:
        print_status("数据库集成", False, f"错误: {e}")
        return False

def test_api_router_integration():
    """
    测试API路由器集成
    验证API路由器是否正确集成
    """
    print_header("API路由器集成测试")
    
    try:
        # 导入API路由器
        from app.api import api_router
        
        # 检查路由器属性
        router_prefix = getattr(api_router, 'prefix', '')
        router_routes = getattr(api_router, 'routes', [])
        
        print_status("API路由器导入", True)
        print_status("路由器前缀", router_prefix == "/api/v1", f"前缀: {router_prefix}")
        print_status("路由器路由数量", len(router_routes) > 0, f"共 {len(router_routes)} 个路由")
        
        return len(router_routes) > 0
    except Exception as e:
        print_status("API路由器集成", False, f"错误: {e}")
        return False

def test_uvicorn_configuration():
    """
    测试Uvicorn配置
    验证Uvicorn服务器配置
    """
    print_header("Uvicorn配置测试")
    
    try:
        # 检查uvicorn导入
        import uvicorn
        print_status("Uvicorn导入", True, f"版本: {uvicorn.__version__}")
        
        # 检查配置参数
        host = os.getenv("HOST", "127.0.0.1")
        port = int(os.getenv("PORT", "8000"))
        debug = os.getenv("DEBUG", "true").lower() == "true"
        
        print_status("服务器地址", True, f"http://{host}:{port}")
        print_status("热重载配置", True, f"{'启用' if debug else '禁用'}")
        print_status("日志级别", True, f"{'debug' if debug else 'info'}")
        
        return True
    except Exception as e:
        print_status("Uvicorn配置", False, f"错误: {e}")
        return False

def generate_server_startup_guide():
    """
    生成服务器启动指南
    """
    print_header("服务器启动指南")
    
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    
    print("\n🚀 FastAPI服务器启动命令:")
    print(f"   python main.py")
    print(f"\n📍 服务器地址:")
    print(f"   http://{host}:{port}")
    print(f"\n📚 API文档地址:")
    print(f"   http://{host}:{port}/docs")
    print(f"   http://{host}:{port}/redoc")
    print(f"\n🔍 健康检查地址:")
    print(f"   http://{host}:{port}/health")
    print(f"\n💡 其他启动方式:")
    print(f"   uvicorn main:app --host {host} --port {port} --reload")
    print(f"\n⚠️  注意事项:")
    print(f"   1. 确保数据库服务已启动")
    print(f"   2. 确保Redis服务已启动（可选）")
    print(f"   3. 确保.env文件配置正确")
    print(f"   4. 确保所有依赖包已安装")

def main():
    """
    主测试函数
    执行所有FastAPI服务器测试
    """
    print("FastAPI服务器自动化测试开始...")
    print("=" * 60)
    
    # 1. 测试FastAPI应用创建
    app_ok, app = test_fastapi_app_creation()
    
    # 2. 测试中间件配置
    middleware_ok = False
    if app_ok and app:
        middleware_ok = test_middleware_configuration(app)
    
    # 3. 测试路由注册
    routes_ok = False
    if app_ok and app:
        routes_ok = test_route_registration(app)
    
    # 4. 测试静态文件配置
    static_ok = False
    if app_ok and app:
        static_ok = test_static_files_configuration(app)
    
    # 5. 测试异常处理器
    exception_ok = False
    if app_ok and app:
        exception_ok = test_exception_handlers(app)
    
    # 6. 测试环境配置
    env_ok = test_environment_configuration()
    
    # 7. 测试数据库集成
    db_ok = test_database_integration()
    
    # 8. 测试API路由器集成
    api_router_ok = test_api_router_integration()
    
    # 9. 测试Uvicorn配置
    uvicorn_ok = test_uvicorn_configuration()
    
    # 总结测试结果
    print("\n" + "=" * 60)
    print("=== FastAPI服务器测试总结 ===")
    print(f"FastAPI应用创建: {'✓ 通过' if app_ok else '✗ 失败'}")
    print(f"中间件配置: {'✓ 通过' if middleware_ok else '✗ 失败'}")
    print(f"路由注册: {'✓ 通过' if routes_ok else '✗ 失败'}")
    print(f"静态文件配置: {'✓ 通过' if static_ok else '✗ 失败'}")
    print(f"异常处理器: {'✓ 通过' if exception_ok else '✗ 失败'}")
    print(f"环境配置: {'✓ 通过' if env_ok else '✗ 失败'}")
    print(f"数据库集成: {'✓ 通过' if db_ok else '✗ 失败'}")
    print(f"API路由器集成: {'✓ 通过' if api_router_ok else '✗ 失败'}")
    print(f"Uvicorn配置: {'✓ 通过' if uvicorn_ok else '✗ 失败'}")
    
    # 整体状态
    overall_status = all([
        app_ok, middleware_ok, routes_ok, static_ok, 
        exception_ok, env_ok, db_ok, api_router_ok, uvicorn_ok
    ])
    
    print(f"\n整体状态: {'✓ FastAPI服务器配置正常' if overall_status else '✗ FastAPI服务器需要修复'}")
    
    if overall_status:
        print("\n🎉 所有FastAPI服务器测试通过！")
        generate_server_startup_guide()
    else:
        print("\n❌ 部分测试失败，请检查相关配置")
    
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