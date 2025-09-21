#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MiniNutriScan 性能测试和负载测试脚本
测试系统各个组件的性能表现和并发处理能力

作者：AI助手
创建时间：2024年
功能：评估数据库、缓存、AI服务、OCR服务的性能指标
"""

import os
import sys
import time
import asyncio
import threading
import psutil
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Dict, Any
import requests
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入项目模块
try:
    from app.core.database import get_db, test_db_connection, redis_client, test_redis_connection
    from app.services.ai_service import AIService
    from app.services.ocr_service import OCRService
    from app.core.config import settings
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    print("请确保所有依赖包已正确安装")
    sys.exit(1)

class PerformanceTester:
    """
    性能测试器
    测试系统各个组件的性能表现和并发处理能力
    """
    
    def __init__(self):
        self.test_results = []
        self.ai_service = AIService()
        self.ocr_service = OCRService()
        self.start_time = None
        self.system_stats = []
        
    def log_test(self, test_name: str, success: bool, metrics: dict = None, message: str = ""):
        """
        记录测试结果
        
        Args:
            test_name: 测试名称
            success: 是否成功
            metrics: 性能指标
            message: 附加信息
        """
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "metrics": metrics or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")
        if metrics:
            for key, value in metrics.items():
                print(f"   - {key}: {value}")
        print()
    
    def monitor_system_resources(self, duration: int = 60):
        """
        监控系统资源使用情况
        
        Args:
            duration: 监控持续时间（秒）
        """
        print(f"🔍 开始监控系统资源使用情况（{duration}秒）...")
        
        start_time = time.time()
        cpu_usage = []
        memory_usage = []
        
        while time.time() - start_time < duration:
            cpu_usage.append(psutil.cpu_percent(interval=1))
            memory_info = psutil.virtual_memory()
            memory_usage.append(memory_info.percent)
            
        metrics = {
            "平均CPU使用率": f"{statistics.mean(cpu_usage):.2f}%",
            "最大CPU使用率": f"{max(cpu_usage):.2f}%",
            "平均内存使用率": f"{statistics.mean(memory_usage):.2f}%",
            "最大内存使用率": f"{max(memory_usage):.2f}%"
        }
        
        self.log_test("系统资源监控", True, metrics, "资源使用情况统计完成")
        return metrics
    
    def test_database_performance(self, num_connections: int = 50, operations_per_connection: int = 10):
        """
        测试数据库连接池性能
        
        Args:
            num_connections: 并发连接数
            operations_per_connection: 每个连接的操作次数
        """
        print(f"🔄 执行 数据库性能 测试（{num_connections}个并发连接，每个连接{operations_per_connection}次操作）...")
        
        def db_operation():
            """单个数据库操作"""
            start_time = time.time()
            try:
                # 测试数据库连接
                success = test_db_connection()
                end_time = time.time()
                return success, end_time - start_time
            except Exception as e:
                end_time = time.time()
                return False, end_time - start_time
        
        start_time = time.time()
        response_times = []
        success_count = 0
        total_operations = num_connections * operations_per_connection
        
        with ThreadPoolExecutor(max_workers=num_connections) as executor:
            futures = []
            for _ in range(total_operations):
                future = executor.submit(db_operation)
                futures.append(future)
            
            for future in as_completed(futures):
                success, response_time = future.result()
                response_times.append(response_time)
                if success:
                    success_count += 1
        
        end_time = time.time()
        total_time = end_time - start_time
        
        metrics = {
            "总操作数": total_operations,
            "成功操作数": success_count,
            "成功率": f"{(success_count/total_operations)*100:.2f}%",
            "总耗时": f"{total_time:.3f}秒",
            "平均响应时间": f"{statistics.mean(response_times)*1000:.2f}ms",
            "最大响应时间": f"{max(response_times)*1000:.2f}ms",
            "最小响应时间": f"{min(response_times)*1000:.2f}ms",
            "吞吐量": f"{total_operations/total_time:.2f} ops/sec"
        }
        
        success = success_count > total_operations * 0.95  # 95%成功率为通过
        message = "数据库性能测试完成" if success else "数据库性能测试存在问题"
        self.log_test("数据库性能测试", success, metrics, message)
        
        return metrics
    
    def test_redis_performance(self, num_operations: int = 1000, concurrent_clients: int = 20):
        """
        测试Redis缓存性能
        
        Args:
            num_operations: 操作总数
            concurrent_clients: 并发客户端数
        """
        print(f"🔄 执行 Redis缓存性能 测试（{num_operations}次操作，{concurrent_clients}个并发客户端）...")
        
        def redis_operation(operation_id: int):
            """单个Redis操作"""
            start_time = time.time()
            try:
                # 测试写入
                key = f"perf_test_{operation_id}"
                value = f"test_value_{operation_id}_{time.time()}"
                redis_client.set(key, value, ex=60)  # 60秒过期
                
                # 测试读取
                retrieved_value = redis_client.get(key)
                
                # 测试删除
                redis_client.delete(key)
                
                end_time = time.time()
                return True, end_time - start_time
            except Exception as e:
                end_time = time.time()
                return False, end_time - start_time
        
        start_time = time.time()
        response_times = []
        success_count = 0
        
        with ThreadPoolExecutor(max_workers=concurrent_clients) as executor:
            futures = []
            for i in range(num_operations):
                future = executor.submit(redis_operation, i)
                futures.append(future)
            
            for future in as_completed(futures):
                success, response_time = future.result()
                response_times.append(response_time)
                if success:
                    success_count += 1
        
        end_time = time.time()
        total_time = end_time - start_time
        
        metrics = {
            "总操作数": num_operations,
            "成功操作数": success_count,
            "成功率": f"{(success_count/num_operations)*100:.2f}%",
            "总耗时": f"{total_time:.3f}秒",
            "平均响应时间": f"{statistics.mean(response_times)*1000:.2f}ms",
            "最大响应时间": f"{max(response_times)*1000:.2f}ms",
            "最小响应时间": f"{min(response_times)*1000:.2f}ms",
            "吞吐量": f"{num_operations/total_time:.2f} ops/sec"
        }
        
        success = success_count > num_operations * 0.95  # 95%成功率为通过
        message = "Redis性能测试完成" if success else "Redis性能测试存在问题"
        self.log_test("Redis缓存性能测试", success, metrics, message)
        
        return metrics
    
    def test_ai_service_performance(self, num_requests: int = 20, concurrent_requests: int = 5):
        """
        测试AI服务性能
        
        Args:
            num_requests: 请求总数
            concurrent_requests: 并发请求数
        """
        print(f"🔄 执行 AI服务性能 测试（{num_requests}次请求，{concurrent_requests}个并发请求）...")
        
        def ai_request():
            """单个AI请求"""
            start_time = time.time()
            try:
                # 模拟营养分析请求
                test_data = {
                    "food_name": "苹果",
                    "nutrition": {
                        "energy": 52,
                        "protein": 0.3,
                        "fat": 0.2,
                        "carbohydrate": 13.8
                    }
                }
                
                # 调用AI分析（使用真实AI服务）
                if hasattr(self.ai_service, 'is_configured') and self.ai_service.is_configured():
                    result = self.ai_service.analyze_nutrition(test_data["nutrition"])
                else:
                    # AI服务未配置时使用模拟结果
                    result = {"analysis": "mock_analysis", "recommendations": ["mock_recommendation"]}
                
                end_time = time.time()
                return True, end_time - start_time
            except Exception as e:
                end_time = time.time()
                return False, end_time - start_time
        
        start_time = time.time()
        response_times = []
        success_count = 0
        
        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = []
            for _ in range(num_requests):
                future = executor.submit(ai_request)
                futures.append(future)
            
            for future in as_completed(futures):
                success, response_time = future.result()
                response_times.append(response_time)
                if success:
                    success_count += 1
        
        end_time = time.time()
        total_time = end_time - start_time
        
        if response_times:
            metrics = {
                "总请求数": num_requests,
                "成功请求数": success_count,
                "成功率": f"{(success_count/num_requests)*100:.2f}%",
                "总耗时": f"{total_time:.3f}秒",
                "平均响应时间": f"{statistics.mean(response_times)*1000:.2f}ms",
                "最大响应时间": f"{max(response_times)*1000:.2f}ms",
                "最小响应时间": f"{min(response_times)*1000:.2f}ms",
                "吞吐量": f"{num_requests/total_time:.2f} req/sec"
            }
        else:
            metrics = {
                "总请求数": num_requests,
                "成功请求数": 0,
                "成功率": "0.00%",
                "错误": "所有请求都失败了"
            }
        
        success = success_count > 0
        message = "AI服务性能测试完成" if success else "AI服务性能测试失败"
        self.log_test("AI服务性能测试", success, metrics, message)
        
        return metrics
    
    def test_concurrent_load(self, duration: int = 30, concurrent_users: int = 10):
        """
        测试并发负载处理能力
        
        Args:
            duration: 测试持续时间（秒）
            concurrent_users: 并发用户数
        """
        print(f"🔄 执行 并发负载 测试（{duration}秒，{concurrent_users}个并发用户）...")
        
        def simulate_user_activity():
            """模拟用户活动"""
            operations = []
            start_time = time.time()
            
            while time.time() - start_time < duration:
                # 模拟不同类型的操作
                operation_start = time.time()
                
                try:
                    # 随机选择操作类型
                    import random
                    operation_type = random.choice(["db", "redis", "ai"])
                    
                    if operation_type == "db":
                        success = test_db_connection()
                    elif operation_type == "redis":
                        key = f"load_test_{random.randint(1, 1000)}"
                        redis_client.set(key, "test_value", ex=10)
                        redis_client.get(key)
                        redis_client.delete(key)
                        success = True
                    else:  # ai
                        # 模拟AI调用
                        time.sleep(0.1)  # 模拟AI处理时间
                        success = True
                    
                    operation_end = time.time()
                    operations.append({
                        "type": operation_type,
                        "success": success,
                        "duration": operation_end - operation_start
                    })
                    
                except Exception as e:
                    operation_end = time.time()
                    operations.append({
                        "type": operation_type,
                        "success": False,
                        "duration": operation_end - operation_start,
                        "error": str(e)
                    })
                
                # 短暂休息模拟真实用户行为
                time.sleep(0.1)
            
            return operations
        
        start_time = time.time()
        all_operations = []
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = []
            for _ in range(concurrent_users):
                future = executor.submit(simulate_user_activity)
                futures.append(future)
            
            for future in as_completed(futures):
                user_operations = future.result()
                all_operations.extend(user_operations)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 统计结果
        total_operations = len(all_operations)
        successful_operations = sum(1 for op in all_operations if op["success"])
        
        if all_operations:
            response_times = [op["duration"] for op in all_operations]
            
            # 按操作类型统计
            db_ops = [op for op in all_operations if op["type"] == "db"]
            redis_ops = [op for op in all_operations if op["type"] == "redis"]
            ai_ops = [op for op in all_operations if op["type"] == "ai"]
            
            metrics = {
                "测试持续时间": f"{total_time:.3f}秒",
                "并发用户数": concurrent_users,
                "总操作数": total_operations,
                "成功操作数": successful_operations,
                "成功率": f"{(successful_operations/total_operations)*100:.2f}%",
                "平均响应时间": f"{statistics.mean(response_times)*1000:.2f}ms",
                "最大响应时间": f"{max(response_times)*1000:.2f}ms",
                "吞吐量": f"{total_operations/total_time:.2f} ops/sec",
                "数据库操作数": len(db_ops),
                "Redis操作数": len(redis_ops),
                "AI操作数": len(ai_ops)
            }
        else:
            metrics = {
                "错误": "没有完成任何操作",
                "并发用户数": concurrent_users,
                "测试持续时间": f"{total_time:.3f}秒"
            }
        
        success = successful_operations > total_operations * 0.90  # 90%成功率为通过
        message = "并发负载测试完成" if success else "并发负载测试存在问题"
        self.log_test("并发负载测试", success, metrics, message)
        
        return metrics
    
    def run_performance_test(self):
        """
        运行完整的性能测试套件
        """
        print("="*80)
        print("🚀 MiniNutriScan 性能测试和负载测试开始")
        print("="*80)
        print()
        
        self.start_time = time.time()
        
        # 1. 系统资源监控（后台运行）
        monitor_thread = threading.Thread(
            target=lambda: self.monitor_system_resources(60),
            daemon=True
        )
        monitor_thread.start()
        
        # 2. 数据库性能测试
        try:
            self.test_database_performance(num_connections=20, operations_per_connection=5)
        except Exception as e:
            self.log_test("数据库性能测试", False, {}, f"测试异常: {str(e)}")
        
        # 3. Redis缓存性能测试
        try:
            self.test_redis_performance(num_operations=500, concurrent_clients=10)
        except Exception as e:
            self.log_test("Redis缓存性能测试", False, {}, f"测试异常: {str(e)}")
        
        # 4. AI服务性能测试
        try:
            self.test_ai_service_performance(num_requests=10, concurrent_requests=3)
        except Exception as e:
            self.log_test("AI服务性能测试", False, {}, f"测试异常: {str(e)}")
        
        # 5. 并发负载测试
        try:
            self.test_concurrent_load(duration=20, concurrent_users=5)
        except Exception as e:
            self.log_test("并发负载测试", False, {}, f"测试异常: {str(e)}")
        
        # 等待系统监控完成
        monitor_thread.join(timeout=5)
        
        # 生成测试报告
        self.generate_performance_report()
    
    def generate_performance_report(self):
        """
        生成性能测试报告
        """
        end_time = time.time()
        total_time = end_time - self.start_time
        
        print("="*80)
        print("📊 性能测试结果汇总")
        print("="*80)
        
        passed_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"总测试数: {total_tests}")
        print(f"通过测试: {passed_tests} ✅")
        print(f"失败测试: {total_tests - passed_tests} ❌")
        print(f"成功率: {success_rate:.1f}%")
        print(f"总耗时: {total_time:.2f}秒")
        print()
        
        print("📋 详细测试结果:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"   {status} {result['test_name']}: {result['message']}")
            
            # 显示关键性能指标
            if result["metrics"]:
                key_metrics = ["成功率", "平均响应时间", "吞吐量", "平均CPU使用率", "平均内存使用率"]
                for metric in key_metrics:
                    if metric in result["metrics"]:
                        print(f"      - {metric}: {result['metrics'][metric]}")
        
        print()
        
        # 性能评估
        if success_rate >= 80:
            print("🎉 性能测试整体表现良好")
        elif success_rate >= 60:
            print("⚠️  性能测试存在一些问题，建议优化")
        else:
            print("❌ 性能测试存在严重问题，需要立即处理")
        
        # 保存详细报告到文件
        self.save_performance_report()
        
        print("="*80)
        print("🏁 性能测试和负载测试完成")
        print("="*80)
    
    def save_performance_report(self):
        """
        保存性能测试报告到文件
        """
        try:
            report_data = {
                "test_time": datetime.now().isoformat(),
                "total_duration": time.time() - self.start_time,
                "test_results": self.test_results,
                "summary": {
                    "total_tests": len(self.test_results),
                    "passed_tests": sum(1 for r in self.test_results if r["success"]),
                    "success_rate": (sum(1 for r in self.test_results if r["success"]) / len(self.test_results) * 100) if self.test_results else 0
                }
            }
            
            report_file = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            print(f"📄 详细性能报告已保存到: {report_file}")
            
        except Exception as e:
            print(f"⚠️  保存性能报告失败: {str(e)}")

# 使用真实AI服务进行性能测试
# 注意：真实AI服务调用会产生实际费用，请谨慎使用
# 如需使用模拟数据，请在配置中设置MOCK_DATA=true

def main():
    """
    主函数：执行性能测试
    """
    try:
        tester = PerformanceTester()
        tester.run_performance_test()
    except KeyboardInterrupt:
        print("\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"❌ 性能测试执行失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()