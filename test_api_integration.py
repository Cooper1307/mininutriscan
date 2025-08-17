#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MiniNutriScan API接口集成测试脚本
测试各个API端点之间的数据流转和集成功能

作者：AI助手
创建时间：2024年
功能：验证API接口的集成性和数据流转的完整性
"""

import os
import sys
import json
import time
import asyncio
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入项目模块
# 导入项目模块
try:
    from app.core.database import get_db  # 修复：将 get_db_session 改为 get_db
    from app.models.user import User, UserRole, UserStatus
    from app.models.detection import Detection, DetectionType, DetectionStatus
    from app.models.report import Report
    from app.api.auth import create_access_token
    from app.api.detection import router as detection_router
    from app.api.reports import router as reports_router
    from app.api.users import router as users_router
    from fastapi.testclient import TestClient
    from main import app
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    print("请确保所有依赖包已正确安装")
    sys.exit(1)

class APIIntegrationTester:
    """
    API接口集成测试器
    测试各个API端点之间的数据流转和集成功能
    """
    
    def __init__(self):
        self.test_results = []
        self.client = TestClient(app)
        self.test_user_data = None
        self.access_token = None
        self.test_detection_id = None
        self.test_report_id = None
        self.base_url = "http://127.0.0.1:8000"
        
    def log_test(self, test_name: str, success: bool, message: str = "", details: dict = None):
        """
        记录测试结果
        
        Args:
            test_name: 测试名称
            success: 是否成功
            message: 测试消息
            details: 详细信息
        """
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.test_results.append(result)
        
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")
        
        if details:
            for key, value in details.items():
                print(f"   - {key}: {value}")
    
    def test_health_check(self) -> bool:
        """
        测试健康检查端点
        
        Returns:
            bool: 测试是否成功
        """
        try:
            response = self.client.get("/health")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "健康检查API", 
                    True, 
                    "API服务正常运行",
                    {
                        "状态码": response.status_code,
                        "响应时间": f"{response.elapsed.total_seconds():.3f}秒" if hasattr(response, 'elapsed') else "N/A",
                        "服务状态": data.get('status', 'unknown')
                    }
                )
                return True
            else:
                self.log_test("健康检查API", False, f"API响应异常，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("健康检查API", False, f"请求失败: {str(e)}")
            return False
    
    def test_user_registration(self) -> bool:
        """
        测试用户注册API
        
        Returns:
            bool: 测试是否成功
        """
        try:
            # 准备测试用户数据
            test_openid = f"test_api_user_{int(time.time())}"
            user_data = {
                "openid": test_openid,
                "nickname": "API测试用户",
                "avatar_url": "https://example.com/avatar.jpg",
                "gender": 1,
                "country": "中国",
                "province": "北京",
                "city": "北京市"
            }
            
            # 发送注册请求
            response = self.client.post("/api/users/register", json=user_data)
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.test_user_data = data
                
                self.log_test(
                    "用户注册API", 
                    True, 
                    "用户注册成功",
                    {
                        "用户ID": data.get('id'),
                        "OpenID": data.get('openid'),
                        "昵称": data.get('nickname'),
                        "状态码": response.status_code
                    }
                )
                return True
            else:
                self.log_test("用户注册API", False, f"注册失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("用户注册API", False, f"请求失败: {str(e)}")
            return False
    
    def test_user_authentication(self) -> bool:
        """
        测试用户认证API
        
        Returns:
            bool: 测试是否成功
        """
        try:
            if not self.test_user_data:
                self.log_test("用户认证API", False, "缺少测试用户数据")
                return False
            
            # 准备认证数据
            auth_data = {
                "openid": self.test_user_data.get('openid'),
                "session_key": "test_session_key"
            }
            
            # 发送认证请求
            response = self.client.post("/api/auth/login", json=auth_data)
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                
                self.log_test(
                    "用户认证API", 
                    True, 
                    "用户认证成功",
                    {
                        "令牌类型": data.get('token_type'),
                        "令牌长度": len(self.access_token) if self.access_token else 0,
                        "过期时间": data.get('expires_in'),
                        "状态码": response.status_code
                    }
                )
                return True
            else:
                self.log_test("用户认证API", False, f"认证失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("用户认证API", False, f"请求失败: {str(e)}")
            return False
    
    def test_image_upload_detection(self) -> bool:
        """
        测试图像上传检测API
        
        Returns:
            bool: 测试是否成功
        """
        try:
            if not self.access_token:
                self.log_test("图像上传检测API", False, "缺少访问令牌")
                return False
            
            # 准备请求头
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # 准备检测数据（模拟图像上传）
            detection_data = {
                "image_data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
                "detection_type": "ocr_scan",
                "user_notes": "API集成测试图像"
            }
            
            # 发送检测请求
            response = self.client.post("/api/detection/upload-image", json=detection_data, headers=headers)
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.test_detection_id = data.get('id')
                
                self.log_test(
                    "图像上传检测API", 
                    True, 
                    "图像检测请求成功",
                    {
                        "检测ID": self.test_detection_id,
                        "检测类型": data.get('detection_type'),
                        "状态": data.get('status'),
                        "状态码": response.status_code
                    }
                )
                return True
            else:
                self.log_test("图像上传检测API", False, f"检测请求失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("图像上传检测API", False, f"请求失败: {str(e)}")
            return False
    
    def test_detection_status(self) -> bool:
        """
        测试检测状态查询API
        
        Returns:
            bool: 测试是否成功
        """
        try:
            if not self.access_token or not self.test_detection_id:
                self.log_test("检测状态查询API", False, "缺少访问令牌或检测ID")
                return False
            
            # 准备请求头
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
            # 发送状态查询请求
            response = self.client.get(f"/api/detection/{self.test_detection_id}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                self.log_test(
                    "检测状态查询API", 
                    True, 
                    "检测状态查询成功",
                    {
                        "检测ID": data.get('id'),
                        "状态": data.get('status'),
                        "产品名称": data.get('product_name', '未识别'),
                        "营养评分": data.get('nutrition_score', '未评分'),
                        "状态码": response.status_code
                    }
                )
                return True
            else:
                self.log_test("检测状态查询API", False, f"状态查询失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("检测状态查询API", False, f"请求失败: {str(e)}")
            return False
    
    def test_report_generation(self) -> bool:
        """
        测试报告生成API
        
        Returns:
            bool: 测试是否成功
        """
        try:
            if not self.access_token or not self.test_detection_id:
                self.log_test("报告生成API", False, "缺少访问令牌或检测ID")
                return False
            
            # 准备请求头
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # 准备报告生成数据
            report_data = {
                "detection_ids": [self.test_detection_id],
                "report_type": "daily",
                "title": "API集成测试报告",
                "include_recommendations": True
            }
            
            # 发送报告生成请求
            response = self.client.post("/api/reports/generate", json=report_data, headers=headers)
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.test_report_id = data.get('id')
                
                self.log_test(
                    "报告生成API", 
                    True, 
                    "报告生成成功",
                    {
                        "报告ID": self.test_report_id,
                        "报告类型": data.get('report_type'),
                        "标题": data.get('title'),
                        "状态": data.get('status'),
                        "状态码": response.status_code
                    }
                )
                return True
            else:
                self.log_test("报告生成API", False, f"报告生成失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("报告生成API", False, f"请求失败: {str(e)}")
            return False
    
    def test_report_retrieval(self) -> bool:
        """
        测试报告获取API
        
        Returns:
            bool: 测试是否成功
        """
        try:
            if not self.access_token or not self.test_report_id:
                self.log_test("报告获取API", False, "缺少访问令牌或报告ID")
                return False
            
            # 准备请求头
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
            # 发送报告获取请求
            response = self.client.get(f"/api/reports/{self.test_report_id}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                self.log_test(
                    "报告获取API", 
                    True, 
                    "报告获取成功",
                    {
                        "报告ID": data.get('id'),
                        "标题": data.get('title'),
                        "生成时间": data.get('created_at'),
                        "内容长度": len(str(data.get('content', ''))),
                        "状态码": response.status_code
                    }
                )
                return True
            else:
                self.log_test("报告获取API", False, f"报告获取失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("报告获取API", False, f"请求失败: {str(e)}")
            return False
    
    def test_user_history(self) -> bool:
        """
        测试用户历史记录API
        
        Returns:
            bool: 测试是否成功
        """
        try:
            if not self.access_token:
                self.log_test("用户历史记录API", False, "缺少访问令牌")
                return False
            
            # 准备请求头
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
            # 发送历史记录查询请求
            response = self.client.get("/api/detection/history", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                self.log_test(
                    "用户历史记录API", 
                    True, 
                    "历史记录查询成功",
                    {
                        "记录数量": len(data.get('items', [])),
                        "总数": data.get('total', 0),
                        "页码": data.get('page', 1),
                        "状态码": response.status_code
                    }
                )
                return True
            else:
                self.log_test("用户历史记录API", False, f"历史记录查询失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("用户历史记录API", False, f"请求失败: {str(e)}")
            return False
    
    def test_data_flow_integrity(self) -> bool:
        """
        测试数据流转完整性
        
        Returns:
            bool: 测试是否成功
        """
        try:
            # 验证数据流转的完整性
            integrity_checks = {
                "用户数据": self.test_user_data is not None,
                "访问令牌": self.access_token is not None,
                "检测ID": self.test_detection_id is not None,
                "报告ID": self.test_report_id is not None
            }
            
            all_checks_passed = all(integrity_checks.values())
            
            self.log_test(
                "数据流转完整性", 
                all_checks_passed, 
                "数据流转完整性检查完成" if all_checks_passed else "数据流转存在缺失",
                integrity_checks
            )
            
            return all_checks_passed
            
        except Exception as e:
            self.log_test("数据流转完整性", False, f"检查失败: {str(e)}")
            return False
    
    def cleanup_test_data(self):
        """
        清理测试数据
        """
        try:
            cleanup_results = []
            
            # 清理测试用户（如果需要）
            if self.test_user_data and self.access_token:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                # 注意：实际项目中可能不提供删除用户的API，这里仅作演示
                cleanup_results.append("用户数据保留（正常业务需求）")
            
            # 清理测试检测记录（如果需要）
            if self.test_detection_id and self.access_token:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                try:
                    response = self.client.delete(f"/api/detection/{self.test_detection_id}", headers=headers)
                    if response.status_code in [200, 204]:
                        cleanup_results.append("检测记录已删除")
                    else:
                        cleanup_results.append(f"检测记录删除失败: {response.status_code}")
                except:
                    cleanup_results.append("检测记录删除接口不可用")
            
            # 清理测试报告（如果需要）
            if self.test_report_id and self.access_token:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                try:
                    response = self.client.delete(f"/api/reports/{self.test_report_id}", headers=headers)
                    if response.status_code in [200, 204]:
                        cleanup_results.append("报告已删除")
                    else:
                        cleanup_results.append(f"报告删除失败: {response.status_code}")
                except:
                    cleanup_results.append("报告删除接口不可用")
            
            self.log_test(
                "清理测试数据", 
                True, 
                "测试数据清理完成",
                {"清理结果": cleanup_results}
            )
            
        except Exception as e:
            self.log_test("清理测试数据", False, f"清理失败: {str(e)}")
    
    def run_api_integration_test(self):
        """
        运行完整的API接口集成测试
        """
        print("\n" + "="*60)
        print("🔗 MiniNutriScan API接口集成测试开始")
        print("="*60)
        
        start_time = time.time()
        
        # 测试序列
        test_sequence = [
            ("健康检查", self.test_health_check),
            ("用户注册", self.test_user_registration),
            ("用户认证", self.test_user_authentication),
            ("图像上传检测", self.test_image_upload_detection),
            ("检测状态查询", self.test_detection_status),
            ("报告生成", self.test_report_generation),
            ("报告获取", self.test_report_retrieval),
            ("用户历史记录", self.test_user_history),
            ("数据流转完整性", self.test_data_flow_integrity)
        ]
        
        # 执行测试序列
        for test_name, test_func in test_sequence:
            print(f"\n🔄 执行 {test_name} 测试...")
            try:
                success = test_func()
                if not success:
                    print(f"⚠️  {test_name} 测试失败，继续执行后续测试")
            except Exception as e:
                print(f"❌ {test_name} 测试异常: {str(e)}")
                self.log_test(test_name, False, f"测试异常: {str(e)}")
        
        # 清理测试数据
        print("\n🧹 清理测试数据...")
        self.cleanup_test_data()
        
        # 计算总耗时
        total_time = time.time() - start_time
        
        # 统计测试结果
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "="*60)
        print("📊 API接口集成测试结果汇总")
        print("="*60)
        print(f"总测试数: {total_tests}")
        print(f"通过测试: {passed_tests} ✅")
        print(f"失败测试: {failed_tests} ❌")
        print(f"成功率: {(passed_tests/total_tests)*100:.1f}%")
        print(f"总耗时: {total_time:.2f}秒")
        
        # 详细结果分析
        print("\n📋 详细测试结果:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"   {status} {result['test_name']}: {result['message']}")
        
        if failed_tests == 0:
            print("\n🎉 所有API接口集成测试均已通过！")
            print("✅ API端点响应正常")
            print("✅ 数据流转完整")
            print("✅ 用户认证有效")
            print("✅ 业务流程集成正常")
        else:
            print("\n⚠️  部分API集成测试失败，请检查以下问题：")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   - {result['test_name']}: {result['message']}")
        
        print("\n" + "="*60)
        print("🏁 API接口集成测试完成")
        print("="*60)

def main():
    """
    主函数
    """
    try:
        tester = APIIntegrationTester()
        tester.run_api_integration_test()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()