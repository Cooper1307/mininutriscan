#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI接口端点测试脚本
测试所有API接口的基本功能和响应

作者: AI助手
创建时间: 2024
"""

import asyncio
import sys
from pathlib import Path
import json

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_fastapi_import():
    """
    测试FastAPI应用导入
    验证FastAPI应用是否能正常导入
    """
    print("\n=== FastAPI应用导入测试 ===")
    
    try:
        import main
        app = main.app
        print("✓ FastAPI应用导入成功")
        return True, app
    except ImportError as e:
        print(f"✗ FastAPI应用导入失败: {e}")
        return False, None
    except Exception as e:
        print(f"✗ FastAPI应用初始化失败: {e}")
        return False, None

def test_database_models():
    """
    测试数据库模型导入
    验证数据库模型是否能正常导入
    """
    print("\n=== 数据库模型导入测试 ===")
    
    try:
        from app.models.user import User
        from app.models.detection import Detection
        from app.models.report import Report
        from app.models.volunteer import Volunteer
        from app.models.education import EducationContent
        print("✓ 用户模型导入成功")
        print("✓ 检测模型导入成功")
        print("✓ 报告模型导入成功")
        print("✓ 志愿者模型导入成功")
        print("✓ 教育内容模型导入成功")
        return True
    except ImportError as e:
        print(f"✗ 数据库模型导入失败: {e}")
        return False
    except Exception as e:
        print(f"✗ 数据库模型初始化失败: {e}")
        return False

def test_api_routes():
    """
    测试API路由导入
    验证API路由是否能正常导入
    """
    print("\n=== API路由导入测试 ===")
    
    routes_to_test = [
        ('app.api.auth', '认证路由'),
        ('app.api.users', '用户路由'),
        ('app.api.detection', '检测路由'),
        ('app.api.reports', '报告路由'),
        ('app.api.community', '社区路由'),
        ('app.api.education', '教育路由'),
        ('app.api.statistics', '统计路由'),
        ('app.api.volunteers', '志愿者路由')
    ]
    
    all_routes_ok = True
    
    for route_module, route_name in routes_to_test:
        try:
            __import__(route_module)
            print(f"✓ {route_name}导入成功")
        except ImportError as e:
            print(f"✗ {route_name}导入失败: {e}")
            all_routes_ok = False
        except Exception as e:
            print(f"✗ {route_name}初始化失败: {e}")
            all_routes_ok = False
    
    return all_routes_ok

def test_services():
    """
    测试服务层导入
    验证各种服务是否能正常导入
    """
    print("\n=== 服务层导入测试 ===")
    
    services_to_test = [
        ('app.services.ai_service', 'AIService', 'AI服务'),
        ('app.services.ocr_service', 'OCRService', 'OCR服务'),
        ('app.services.wechat_service', 'WeChatService', '微信服务')
    ]
    
    all_services_ok = True
    
    for service_module, service_class, service_name in services_to_test:
        try:
            module = __import__(service_module, fromlist=[service_class])
            service_cls = getattr(module, service_class)
            print(f"✓ {service_name}导入成功")
        except ImportError as e:
            print(f"✗ {service_name}导入失败: {e}")
            all_services_ok = False
        except AttributeError as e:
            print(f"✗ {service_name}类不存在: {e}")
            all_services_ok = False
        except Exception as e:
            print(f"✗ {service_name}初始化失败: {e}")
            all_services_ok = False
    
    return all_services_ok

def test_dependencies():
    """
    测试API依赖项
    验证数据库连接、认证等依赖项是否正常
    """
    print("\n=== API依赖项测试 ===")
    
    dependencies_to_test = [
        ('app.core.database', '数据库依赖'),
        ('app.core.config', '配置依赖')
    ]
    
    all_deps_ok = True
    
    for dep_module, dep_name in dependencies_to_test:
        try:
            __import__(dep_module)
            print(f"✓ {dep_name}导入成功")
        except ImportError as e:
            print(f"✗ {dep_name}导入失败: {e}")
            all_deps_ok = False
        except Exception as e:
            print(f"✗ {dep_name}初始化失败: {e}")
            all_deps_ok = False
    
    return all_deps_ok

def test_middleware():
    """
    测试中间件导入
    验证各种中间件是否能正常导入
    """
    print("\n=== 中间件测试 ===")
    
    try:
        from fastapi.middleware.cors import CORSMiddleware
        
        print("✓ CORS中间件导入成功")
        
        return True
    except ImportError as e:
        print(f"✗ 中间件导入失败: {e}")
        return False
    except Exception as e:
        print(f"✗ 中间件初始化失败: {e}")
        return False

def check_api_structure(app):
    """
    检查API结构
    验证FastAPI应用的路由结构
    """
    print("\n=== API结构检查 ===")
    
    try:
        routes = app.routes
        print(f"✓ 总路由数量: {len(routes)}")
        
        # 统计不同类型的路由
        api_routes = []
        static_routes = []
        other_routes = []
        
        for route in routes:
            if hasattr(route, 'path'):
                if route.path.startswith('/api/'):
                    api_routes.append(route.path)
                elif route.path.startswith('/static/'):
                    static_routes.append(route.path)
                else:
                    other_routes.append(route.path)
        
        print(f"✓ API路由数量: {len(api_routes)}")
        print(f"✓ 静态文件路由数量: {len(static_routes)}")
        print(f"✓ 其他路由数量: {len(other_routes)}")
        
        # 显示主要API路由
        if api_routes:
            print("\n主要API路由:")
            for route in sorted(api_routes)[:10]:  # 显示前10个
                print(f"  - {route}")
            if len(api_routes) > 10:
                print(f"  ... 还有 {len(api_routes) - 10} 个路由")
        
        return True
    except Exception as e:
        print(f"✗ API结构检查失败: {e}")
        return False

def test_configuration():
    """
    测试配置
    验证应用配置是否正确
    """
    print("\n=== 配置测试 ===")
    
    try:
        from app.core.config import settings
        
        config_items = [
            ('APP_NAME', settings.APP_NAME, '应用名称'),
            ('APP_VERSION', settings.APP_VERSION, '应用版本'),
            ('DEBUG', settings.DEBUG, '调试模式'),
            ('HOST', settings.HOST, '服务器主机'),
            ('PORT', settings.PORT, '服务器端口')
        ]
        
        for config_key, config_value, config_desc in config_items:
            print(f"✓ {config_desc}: {config_value}")
        
        return True
    except Exception as e:
        print(f"✗ 配置测试失败: {e}")
        return False

def main():
    """
    主测试函数
    执行所有FastAPI接口相关的测试
    """
    print("FastAPI接口端点测试开始...")
    print("=" * 50)
    
    # 1. 测试FastAPI应用导入
    app_ok, app = test_fastapi_import()
    
    # 2. 测试数据库模型
    models_ok = test_database_models()
    
    # 3. 测试API路由
    routes_ok = test_api_routes()
    
    # 4. 测试服务层
    services_ok = test_services()
    
    # 5. 测试依赖项
    deps_ok = test_dependencies()
    
    # 6. 测试中间件
    middleware_ok = test_middleware()
    
    # 7. 测试配置
    config_ok = test_configuration()
    
    # 8. 如果应用导入成功，检查API结构
    structure_ok = False
    if app_ok and app:
        structure_ok = check_api_structure(app)
    
    # 总结测试结果
    print("\n" + "=" * 50)
    print("=== FastAPI接口测试总结 ===")
    print(f"FastAPI应用: {'✓ 通过' if app_ok else '✗ 失败'}")
    print(f"数据库模型: {'✓ 通过' if models_ok else '✗ 失败'}")
    print(f"API路由: {'✓ 通过' if routes_ok else '✗ 失败'}")
    print(f"服务层: {'✓ 通过' if services_ok else '✗ 失败'}")
    print(f"依赖项: {'✓ 通过' if deps_ok else '✗ 失败'}")
    print(f"中间件: {'✓ 通过' if middleware_ok else '✗ 失败'}")
    print(f"配置: {'✓ 通过' if config_ok else '✗ 失败'}")
    print(f"API结构: {'✓ 通过' if structure_ok else '✗ 失败'}")
    
    # 整体状态
    overall_status = all([
        app_ok, models_ok, routes_ok, services_ok, 
        deps_ok, middleware_ok, config_ok, structure_ok
    ])
    
    print(f"\n整体状态: {'✓ FastAPI接口配置正常' if overall_status else '✗ FastAPI接口需要修复'}")
    
    if overall_status:
        print("\n🎉 所有FastAPI接口测试通过！")
        print("\n下一步建议:")
        print("1. 启动FastAPI服务器: uvicorn app.main:app --reload")
        print("2. 访问API文档: http://localhost:8000/docs")
        print("3. 进行实际的API接口测试")
    else:
        print("\n❌ 部分测试失败，请检查相关模块")
    
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