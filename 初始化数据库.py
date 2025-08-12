#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
自动创建数据库表结构和初始数据
"""

import os
import sys
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
    print(f"{icon} {item}: {'成功' if status else '失败'}")
    if details:
        print(f"   {details}")

def check_database_connection():
    """检查数据库连接"""
    try:
        from app.database import check_database_connection
        return check_database_connection()
    except Exception as e:
        print(f"数据库连接检查失败: {e}")
        return False

def create_database_tables():
    """创建数据库表"""
    try:
        # 导入所有模型以确保它们被注册
        from app.models.user import User
        from app.models.detection import Detection, NutritionInfo
        from app.models.report import Report, ReportComment
        from app.models.volunteer import Volunteer, VolunteerTask
        from app.models.education import EducationContent, UserProgress
        
        # 导入数据库基础类
        from app.database import Base, engine
        
        print("正在创建数据库表...")
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        
        print("数据库表创建成功")
        return True
        
    except Exception as e:
        print(f"数据库表创建失败: {e}")
        return False

def create_initial_data():
    """创建初始数据"""
    try:
        from app.database import SessionLocal
        from app.models.education import EducationContent
        from app.models.user import User
        from datetime import datetime
        import hashlib
        
        db = SessionLocal()
        
        try:
            # 检查是否已有数据
            existing_content = db.query(EducationContent).first()
            if existing_content:
                print("初始数据已存在，跳过创建")
                return True
            
            # 创建示例教育内容
            education_contents = [
                {
                    "title": "食品标签怎么看？",
                    "content": "学会看食品标签是保障食品安全的第一步。重点关注生产日期、保质期、配料表和营养成分表。",
                    "category": "基础知识",
                    "tags": "食品标签,安全知识",
                    "difficulty_level": 1,
                    "estimated_time": 5
                },
                {
                    "title": "如何识别过期食品？",
                    "content": "过期食品可能存在安全隐患。除了查看保质期，还要注意食品的外观、气味和质地变化。",
                    "category": "安全识别",
                    "tags": "过期食品,安全识别",
                    "difficulty_level": 1,
                    "estimated_time": 3
                },
                {
                    "title": "营养成分表解读",
                    "content": "营养成分表帮助我们了解食品的营养价值。重点关注能量、蛋白质、脂肪、碳水化合物和钠的含量。",
                    "category": "营养知识",
                    "tags": "营养成分,健康饮食",
                    "difficulty_level": 2,
                    "estimated_time": 8
                },
                {
                    "title": "食品添加剂安全吗？",
                    "content": "合规使用的食品添加剂是安全的。了解常见添加剂的作用和安全性，理性看待食品添加剂。",
                    "category": "专业知识",
                    "tags": "食品添加剂,安全性",
                    "difficulty_level": 3,
                    "estimated_time": 10
                }
            ]
            
            for content_data in education_contents:
                content = EducationContent(
                    title=content_data["title"],
                    content=content_data["content"],
                    category=content_data["category"],
                    tags=content_data["tags"],
                    difficulty_level=content_data["difficulty_level"],
                    estimated_time=content_data["estimated_time"],
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db.add(content)
            
            # 创建管理员用户（如果不存在）
            admin_user = db.query(User).filter(User.username == "admin").first()
            if not admin_user:
                # 创建默认管理员账户
                admin_password = "admin123"  # 生产环境中应该使用更安全的密码
                password_hash = hashlib.sha256(admin_password.encode()).hexdigest()
                
                admin_user = User(
                    username="admin",
                    email="admin@mininutriscan.com",
                    password_hash=password_hash,
                    phone="13800138000",
                    role="admin",
                    is_active=True,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db.add(admin_user)
                print("创建默认管理员账户: admin / admin123")
            
            # 提交事务
            db.commit()
            print("初始数据创建成功")
            return True
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
            
    except Exception as e:
        print(f"初始数据创建失败: {e}")
        return False

def main():
    """主函数"""
    print("🛡️ 社区食安AI小卫士 - 数据库初始化工具")
    print("=" * 50)
    
    try:
        # 检查是否在项目目录
        if not os.path.exists("main.py"):
            print("❌ 请在项目根目录运行此脚本")
            print(f"当前目录: {os.getcwd()}")
            return 1
        
        print_header("数据库连接检查")
        
        # 检查数据库连接
        if not check_database_connection():
            print("\n❌ 数据库连接失败，请检查以下配置:")
            print("   1. PostgreSQL服务是否运行")
            print("   2. .env文件中的数据库配置是否正确")
            print("   3. 数据库是否已创建")
            print("\n💡 提示: 可以运行 '检查项目状态.bat' 获取详细诊断")
            return 1
        
        print_status("数据库连接", True, "连接正常")
        
        print_header("创建数据库表")
        
        # 创建数据库表
        tables_created = create_database_tables()
        print_status("数据库表创建", tables_created)
        
        if not tables_created:
            print("\n❌ 数据库表创建失败")
            return 1
        
        print_header("创建初始数据")
        
        # 创建初始数据
        data_created = create_initial_data()
        print_status("初始数据创建", data_created)
        
        if not data_created:
            print("\n⚠️  初始数据创建失败，但数据库表已创建成功")
            print("   可以手动添加数据或稍后重试")
        
        print_header("初始化完成")
        
        if tables_created and data_created:
            print("\n🎉 数据库初始化完成！")
            print("\n📋 已创建的内容:")
            print("   ✅ 所有数据库表")
            print("   ✅ 示例教育内容 (4篇)")
            print("   ✅ 管理员账户 (admin/admin123)")
            print("\n🚀 下一步操作:")
            print("   1. 运行 '启动所有服务.bat' 启动后端服务")
            print("   2. 访问 http://127.0.0.1:8000/docs 查看API文档")
            print("   3. 使用微信开发者工具打开小程序项目")
        elif tables_created:
            print("\n✅ 数据库表创建成功")
            print("\n⚠️  初始数据创建失败，但不影响基本使用")
            print("\n🚀 下一步操作:")
            print("   1. 运行 '启动所有服务.bat' 启动后端服务")
            print("   2. 可以通过API手动添加数据")
        else:
            print("\n❌ 数据库初始化失败")
            print("\n🔧 建议操作:")
            print("   1. 检查数据库配置")
            print("   2. 确保PostgreSQL服务运行")
            print("   3. 运行 '检查项目状态.bat' 获取详细诊断")
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⏹️  初始化被用户中断")
        return 1
    except Exception as e:
        print(f"\n\n💥 初始化过程中发生异常: {e}")
        return 1
    finally:
        print("\n" + "=" * 50)
        input("按回车键退出...")

if __name__ == "__main__":
    sys.exit(main())