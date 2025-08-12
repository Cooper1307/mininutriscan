#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目状态检查脚本
检查项目配置、服务状态和开发环境
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def print_header(title):
    """打印标题"""
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")

def print_status(item, status, details=""):
    """打印状态信息"""
    icon = "✅" if status else "❌"
    print(f"{icon} {item}: {'正常' if status else '异常'}")
    if details:
        print(f"   {details}")

def check_python_environment():
    """检查Python环境"""
    print_header("Python环境检查")
    
    # Python版本
    python_version = sys.version_info
    version_ok = python_version >= (3, 8)
    print_status("Python版本", version_ok, 
                f"当前版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 虚拟环境
    venv_active = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    print_status("虚拟环境", venv_active, "建议使用虚拟环境" if not venv_active else "已激活")
    
    # 依赖包检查
    required_packages = ['fastapi', 'uvicorn', 'sqlalchemy', 'pydantic']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    packages_ok = len(missing_packages) == 0
    print_status("依赖包", packages_ok, 
                f"缺少: {', '.join(missing_packages)}" if missing_packages else "所有依赖已安装")
    
    return version_ok and packages_ok

def check_project_structure():
    """检查项目结构"""
    print_header("项目结构检查")
    
    required_files = [
        'main.py',
        'requirements.txt',
        '.env',
        'app/database.py',
        'miniprogram/app.json',
        'miniprogram/app.js'
    ]
    
    required_dirs = [
        'app',
        'app/api',
        'app/models',
        'app/services',
        'miniprogram',
        'miniprogram/pages',
        'miniprogram/utils'
    ]
    
    # 检查文件
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    files_ok = len(missing_files) == 0
    print_status("核心文件", files_ok, 
                f"缺少: {', '.join(missing_files)}" if missing_files else "所有核心文件存在")
    
    # 检查目录
    missing_dirs = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    dirs_ok = len(missing_dirs) == 0
    print_status("目录结构", dirs_ok, 
                f"缺少: {', '.join(missing_dirs)}" if missing_dirs else "目录结构完整")
    
    return files_ok and dirs_ok

def check_configuration():
    """检查配置文件"""
    print_header("配置文件检查")
    
    # 检查.env文件
    env_exists = os.path.exists('.env')
    print_status(".env文件", env_exists)
    
    if not env_exists:
        return False
    
    # 检查关键配置项
    config_items = {
        'DATABASE_URL': os.getenv('DATABASE_URL'),
        'SECRET_KEY': os.getenv('SECRET_KEY'),
        'QWEN_API_KEY': os.getenv('QWEN_API_KEY'),
        'WECHAT_APP_ID': os.getenv('WECHAT_APP_ID')
    }
    
    configured_items = 0
    total_items = len(config_items)
    
    for key, value in config_items.items():
        is_configured = value and value != f'your-{key.lower().replace("_", "-")}-here'
        print_status(key, is_configured, 
                    "已配置" if is_configured else "需要配置")
        if is_configured:
            configured_items += 1
    
    # 检查小程序配置
    miniprogram_config_path = 'miniprogram/config/api.js'
    miniprogram_config_exists = os.path.exists(miniprogram_config_path)
    print_status("小程序API配置", miniprogram_config_exists)
    
    print(f"\n📊 配置完成度: {configured_items}/{total_items} ({configured_items/total_items*100:.1f}%)")
    
    return configured_items >= 2  # 至少需要数据库和密钥配置

def check_services():
    """检查服务状态"""
    print_header("服务状态检查")
    
    try:
        import requests
        
        # 检查FastAPI服务
        try:
            response = requests.get('http://127.0.0.1:8000/health', timeout=5)
            fastapi_ok = response.status_code == 200
            print_status("FastAPI服务", fastapi_ok, 
                        "运行正常" if fastapi_ok else f"HTTP {response.status_code}")
        except requests.exceptions.ConnectionError:
            print_status("FastAPI服务", False, "未启动")
            fastapi_ok = False
        except Exception as e:
            print_status("FastAPI服务", False, f"检查失败: {e}")
            fastapi_ok = False
        
        # 检查API文档
        try:
            response = requests.get('http://127.0.0.1:8000/docs', timeout=5)
            docs_ok = response.status_code == 200
            print_status("API文档", docs_ok, 
                        "可访问" if docs_ok else "无法访问")
        except:
            print_status("API文档", False, "无法访问")
            docs_ok = False
        
        return fastapi_ok
        
    except ImportError:
        print_status("服务检查", False, "缺少requests包")
        return False

def check_database():
    """检查数据库连接"""
    print_header("数据库检查")
    
    try:
        from app.database import check_database_connection
        
        db_ok = check_database_connection()
        print_status("数据库连接", db_ok, 
                    "连接正常" if db_ok else "连接失败")
        
        return db_ok
        
    except Exception as e:
        print_status("数据库连接", False, f"检查失败: {e}")
        return False

def generate_report():
    """生成检查报告"""
    print_header("项目状态报告")
    
    # 执行所有检查
    checks = {
        "Python环境": check_python_environment(),
        "项目结构": check_project_structure(),
        "配置文件": check_configuration(),
        "数据库": check_database(),
        "服务状态": check_services()
    }
    
    # 统计结果
    passed = sum(checks.values())
    total = len(checks)
    
    print(f"\n📋 检查结果汇总:")
    for check_name, result in checks.items():
        icon = "✅" if result else "❌"
        print(f"   {icon} {check_name}")
    
    print(f"\n🎯 总体状态: {passed}/{total} 项检查通过 ({passed/total*100:.1f}%)")
    
    # 给出建议
    if passed == total:
        print("\n🎉 恭喜！项目配置完整，可以开始开发了！")
        print("\n📱 下一步操作:")
        print("   1. 双击运行 启动服务.bat 启动后端服务")
        print("   2. 打开微信开发者工具导入小程序项目")
        print("   3. 参考 小程序开发指南.md 进行开发")
    elif passed >= 3:
        print("\n⚠️  项目基本配置完成，但还有一些问题需要解决")
        print("\n🔧 建议操作:")
        if not checks["配置文件"]:
            print("   1. 参考 配置指南.md 完成环境配置")
        if not checks["服务状态"]:
            print("   2. 运行 启动服务.bat 启动后端服务")
        if not checks["数据库"]:
            print("   3. 检查数据库配置和连接")
    else:
        print("\n❌ 项目配置不完整，需要先解决基础问题")
        print("\n🚨 紧急操作:")
        if not checks["Python环境"]:
            print("   1. 安装Python 3.8+和项目依赖")
        if not checks["项目结构"]:
            print("   2. 检查项目文件是否完整")
        if not checks["配置文件"]:
            print("   3. 创建并配置.env文件")
    
    print("\n📚 参考文档:")
    print("   - 配置指南.md")
    print("   - 小程序开发指南.md")
    print("   - 快速使用指南.md")
    
    return passed >= 3

def main():
    """主函数"""
    print("🛡️ 社区食安AI小卫士 - 项目状态检查工具")
    print("=" * 50)
    
    try:
        success = generate_report()
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n⏹️  检查被用户中断")
        return 1
    except Exception as e:
        print(f"\n\n💥 检查过程中发生异常: {e}")
        return 1
    finally:
        print("\n" + "=" * 50)
        input("按回车键退出...")

if __name__ == "__main__":
    sys.exit(main())