#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据持久化测试脚本
测试Detection模型的数据保存、更新和查询功能
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from sqlalchemy.orm import Session
    from app.core.database import get_db, create_tables, test_db_connection
    from app.models.detection import Detection, DetectionType, DetectionStatus, RiskLevel
    from app.models.user import User
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  依赖模块导入失败: {e}")
    DEPENDENCIES_AVAILABLE = False

class DataPersistenceTest:
    """
    数据持久化测试类
    """
    
    def __init__(self):
        self.test_results = {}
        self.test_data = {}
        self.db_session = None
        
    def print_header(self):
        """打印测试标题"""
        print("\n" + "="*60)
        print("🧪 数据持久化测试")
        print("="*60)
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
    
    def print_step(self, step_name: str, description: str = ""):
        """打印测试步骤"""
        print(f"\n📋 {step_name}")
        if description:
            print(f"   {description}")
        print("-" * 40)
    
    def print_status(self, item: str, success: bool, details: str = ""):
        """打印状态信息"""
        status_icon = "✅" if success else "❌"
        print(f"   {status_icon} {item}: {'成功' if success else '失败'}")
        if details:
            print(f"      {details}")
    
    def setup_database(self) -> bool:
        """
        设置数据库连接
        """
        self.print_step("数据库设置", "初始化数据库连接和表结构")
        
        try:
            # 测试数据库连接
            db_connected = test_db_connection()
            self.print_status("数据库连接", db_connected)
            
            if not db_connected:
                self.test_results['database_setup'] = False
                return False
            
            # 创建数据库表
            create_tables()
            self.print_status("数据库表创建", True)
            
            # 获取数据库会话
            self.db_session = next(get_db())
            self.print_status("数据库会话", True)
            
            self.test_results['database_setup'] = True
            return True
            
        except Exception as e:
            self.print_status("数据库设置", False, f"错误: {e}")
            self.test_results['database_setup'] = False
            return False
    
    def create_test_user(self) -> Optional[User]:
        """
        创建测试用户
        """
        self.print_step("创建测试用户", "为数据持久化测试创建用户")
        
        try:
            # 检查是否已存在测试用户
            existing_user = self.db_session.query(User).filter(
                User.username == "test_persistence_user"
            ).first()
            
            if existing_user:
                self.print_status("测试用户", True, "使用现有测试用户")
                return existing_user
            
            # 创建新的测试用户
            test_user = User(
                username="test_persistence_user",
                email="test_persistence@example.com",
                password_hash="test_password_hash",
                nickname="数据持久化测试用户",
                age=25,
                gender=0,  # 0-未知，1-男，2-女
                height=170,
                weight=65
            )
            
            self.db_session.add(test_user)
            self.db_session.commit()
            self.db_session.refresh(test_user)
            
            self.print_status("测试用户创建", True, f"用户ID: {test_user.id}")
            self.test_data['user'] = test_user
            return test_user
            
        except Exception as e:
            self.print_status("测试用户创建", False, f"错误: {e}")
            self.db_session.rollback()
            return None
    
    def test_detection_creation(self, user: User) -> Optional[Detection]:
        """
        测试Detection记录创建
        """
        self.print_step("Detection记录创建", "测试基本检测记录的创建")
        
        try:
            # 创建Detection记录
            detection = Detection(
                user_id=user.id,
                detection_type=DetectionType.OCR_SCAN,
                status=DetectionStatus.PENDING,
                image_url="/test/images/test_nutrition_label.jpg",
                raw_text="营养成分表\n能量 2000kJ\n蛋白质 10g\n脂肪 5g\n碳水化合物 50g\n钠 800mg",
                product_name="测试食品",
                brand="测试品牌",
                category="测试类别"
            )
            
            self.db_session.add(detection)
            self.db_session.commit()
            self.db_session.refresh(detection)
            
            self.print_status("Detection创建", True, f"ID: {detection.id}")
            self.print_status("基本信息保存", True, f"产品: {detection.product_name}")
            
            self.test_data['detection'] = detection
            self.test_results['detection_creation'] = True
            return detection
            
        except Exception as e:
            self.print_status("Detection创建", False, f"错误: {e}")
            self.db_session.rollback()
            self.test_results['detection_creation'] = False
            return None
    
    def test_nutrition_data_persistence(self, detection: Detection) -> bool:
        """
        测试营养数据持久化
        """
        self.print_step("营养数据持久化", "测试营养成分数据的保存和更新")
        
        try:
            # 准备营养数据
            nutrition_data = {
                "energy": 2000,
                "protein": 10.0,
                "fat": 5.0,
                "carbohydrate": 50.0,
                "sodium": 800.0,
                "sugar": 15.0,
                "fiber": 3.0,
                "other_nutrients": {
                    "vitamin_c": 60.0,
                    "calcium": 120.0,
                    "iron": 8.0
                }
            }
            
            # 使用set_nutrition_data方法
            detection.set_nutrition_data(nutrition_data)
            self.db_session.commit()
            self.db_session.refresh(detection)
            
            # 验证数据保存
            self.print_status("基础营养成分", True, f"能量: {detection.energy}kJ")
            self.print_status("蛋白质", detection.protein == 10.0, f"{detection.protein}g")
            self.print_status("脂肪", detection.fat == 5.0, f"{detection.fat}g")
            self.print_status("碳水化合物", detection.carbohydrate == 50.0, f"{detection.carbohydrate}g")
            self.print_status("钠", detection.sodium == 800.0, f"{detection.sodium}mg")
            
            # 验证其他营养成分
            other_nutrients = detection.other_nutrients
            if other_nutrients:
                self.print_status("其他营养成分", True, f"维生素C: {other_nutrients.get('vitamin_c')}mg")
            else:
                self.print_status("其他营养成分", False, "数据未保存")
            
            self.test_results['nutrition_persistence'] = True
            return True
            
        except Exception as e:
            self.print_status("营养数据持久化", False, f"错误: {e}")
            self.db_session.rollback()
            self.test_results['nutrition_persistence'] = False
            return False
    
    def test_ai_analysis_persistence(self, detection: Detection) -> bool:
        """
        测试AI分析结果持久化
        """
        self.print_step("AI分析结果持久化", "测试AI分析数据的保存和更新")
        
        try:
            # 准备AI分析数据
            analysis_data = {
                "health_assessment": "该产品营养成分较为均衡",
                "recommendations": ["建议适量食用", "注意控制钠的摄入"],
                "risk_factors": ["钠含量偏高"],
                "nutritional_highlights": ["蛋白质含量适中", "能量密度合理"]
            }
            
            # 使用set_ai_analysis方法
            detection.set_ai_analysis(
                score=75.5,
                advice="该产品营养成分较为均衡，建议适量食用，注意控制钠的摄入。",
                risk_level="medium",
                analysis_data=analysis_data
            )
            
            self.db_session.commit()
            self.db_session.refresh(detection)
            
            # 验证AI分析数据保存
            self.print_status("健康评分", detection.nutrition_score == 75.5, f"{detection.nutrition_score}分")
            self.print_status("健康建议", bool(detection.health_advice), "已保存")
            self.print_status("风险等级", detection.risk_level == RiskLevel.MEDIUM, f"{detection.risk_level.value}")
            
            # 验证AI分析详细数据
            ai_analysis = detection.ai_analysis
            if ai_analysis:
                self.print_status("AI分析详情", True, f"包含 {len(analysis_data)} 个分析项")
                self.print_status("时间戳", 'timestamp' in ai_analysis, "已记录分析时间")
            else:
                self.print_status("AI分析详情", False, "数据未保存")
            
            self.test_results['ai_analysis_persistence'] = True
            return True
            
        except Exception as e:
            self.print_status("AI分析结果持久化", False, f"错误: {e}")
            self.db_session.rollback()
            self.test_results['ai_analysis_persistence'] = False
            return False
    
    def test_status_updates(self, detection: Detection) -> bool:
        """
        测试状态更新
        """
        self.print_step("状态更新测试", "测试检测状态的更新和错误处理")
        
        try:
            # 测试状态更新
            original_status = detection.status
            detection.update_status("processing")
            self.db_session.commit()
            self.db_session.refresh(detection)
            
            self.print_status("状态更新", detection.status.value == "processing", f"从 {original_status.value} 更新为 {detection.status.value}")
            
            # 测试完成状态
            detection.update_status("completed")
            self.db_session.commit()
            self.db_session.refresh(detection)
            
            self.print_status("完成状态", detection.status.value == "completed", "状态已更新为完成")
            self.print_status("完成时间", detection.completed_at is not None, "已记录完成时间")
            
            # 测试错误状态
            detection.update_status("failed", "测试错误信息")
            self.db_session.commit()
            self.db_session.refresh(detection)
            
            self.print_status("错误状态", detection.status.value == "failed", "状态已更新为失败")
            self.print_status("错误信息", detection.error_message == "测试错误信息", "错误信息已保存")
            
            self.test_results['status_updates'] = True
            return True
            
        except Exception as e:
            self.print_status("状态更新测试", False, f"错误: {e}")
            self.db_session.rollback()
            self.test_results['status_updates'] = False
            return False
    
    def test_data_retrieval(self, detection: Detection) -> bool:
        """
        测试数据检索
        """
        self.print_step("数据检索测试", "测试从数据库检索完整的检测记录")
        
        try:
            # 通过ID检索记录
            retrieved_detection = self.db_session.query(Detection).filter(
                Detection.id == detection.id
            ).first()
            
            if not retrieved_detection:
                self.print_status("记录检索", False, "未找到记录")
                self.test_results['data_retrieval'] = False
                return False
            
            self.print_status("记录检索", True, f"成功检索ID: {retrieved_detection.id}")
            
            # 验证数据完整性
            data_integrity_checks = [
                ("产品名称", retrieved_detection.product_name == "测试食品"),
                ("营养数据", retrieved_detection.energy is not None),
                ("AI分析", retrieved_detection.ai_analysis is not None),
                ("健康评分", retrieved_detection.nutrition_score is not None),
                ("风险等级", retrieved_detection.risk_level is not None),
                ("创建时间", retrieved_detection.created_at is not None),
                ("更新时间", retrieved_detection.updated_at is not None)
            ]
            
            all_checks_passed = True
            for check_name, check_result in data_integrity_checks:
                self.print_status(check_name, check_result)
                if not check_result:
                    all_checks_passed = False
            
            # 测试to_dict方法
            try:
                detection_dict = retrieved_detection.to_dict()
                self.print_status("字典转换", True, f"包含 {len(detection_dict)} 个字段")
            except Exception as e:
                self.print_status("字典转换", False, f"错误: {e}")
                all_checks_passed = False
            
            self.test_results['data_retrieval'] = all_checks_passed
            return all_checks_passed
            
        except Exception as e:
            self.print_status("数据检索测试", False, f"错误: {e}")
            self.test_results['data_retrieval'] = False
            return False
    
    def cleanup_test_data(self):
        """
        清理测试数据
        """
        self.print_step("清理测试数据", "删除测试过程中创建的数据")
        
        try:
            if 'detection' in self.test_data:
                detection = self.test_data['detection']
                self.db_session.delete(detection)
                self.print_status("删除Detection记录", True)
            
            if 'user' in self.test_data:
                user = self.test_data['user']
                self.db_session.delete(user)
                self.print_status("删除测试用户", True)
            
            self.db_session.commit()
            self.print_status("数据清理", True, "所有测试数据已清理")
            
        except Exception as e:
            self.print_status("数据清理", False, f"错误: {e}")
            self.db_session.rollback()
    
    def generate_report(self):
        """
        生成测试报告
        """
        self.print_step("测试报告", "生成数据持久化测试结果报告")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 测试结果统计:")
        print(f"   总测试数: {total_tests}")
        print(f"   通过测试: {passed_tests}")
        print(f"   失败测试: {total_tests - passed_tests}")
        print(f"   成功率: {success_rate:.1f}%")
        
        print(f"\n📋 详细结果:")
        for test_name, result in self.test_results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"   {test_name}: {status}")
        
        # 保存报告到文件
        report_data = {
            "test_time": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "test_results": self.test_results,
            "summary": {
                "database_setup": self.test_results.get('database_setup', False),
                "detection_creation": self.test_results.get('detection_creation', False),
                "nutrition_persistence": self.test_results.get('nutrition_persistence', False),
                "ai_analysis_persistence": self.test_results.get('ai_analysis_persistence', False),
                "status_updates": self.test_results.get('status_updates', False),
                "data_retrieval": self.test_results.get('data_retrieval', False)
            }
        }
        
        report_filename = f"data_persistence_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            print(f"\n📄 测试报告已保存: {report_filename}")
        except Exception as e:
            print(f"\n⚠️  报告保存失败: {e}")
    
    def run_all_tests(self):
        """
        运行所有数据持久化测试
        """
        self.print_header()
        
        if not DEPENDENCIES_AVAILABLE:
            print("❌ 依赖模块不可用，无法运行测试")
            return
        
        try:
            # 1. 设置数据库
            if not self.setup_database():
                print("❌ 数据库设置失败，终止测试")
                return
            
            # 2. 创建测试用户
            test_user = self.create_test_user()
            if not test_user:
                print("❌ 测试用户创建失败，终止测试")
                return
            
            # 3. 测试Detection记录创建
            detection = self.test_detection_creation(test_user)
            if not detection:
                print("❌ Detection记录创建失败，终止测试")
                return
            
            # 4. 测试营养数据持久化
            self.test_nutrition_data_persistence(detection)
            
            # 5. 测试AI分析结果持久化
            self.test_ai_analysis_persistence(detection)
            
            # 6. 测试状态更新
            self.test_status_updates(detection)
            
            # 7. 测试数据检索
            self.test_data_retrieval(detection)
            
            # 8. 生成测试报告
            self.generate_report()
            
            # 9. 清理测试数据
            self.cleanup_test_data()
            
        except Exception as e:
            print(f"\n❌ 测试过程中发生未预期错误: {e}")
        finally:
            if self.db_session:
                self.db_session.close()

def main():
    """
    主函数
    """
    tester = DataPersistenceTest()
    tester.run_all_tests()

if __name__ == "__main__":
    main()