#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户认证API端点测试脚本
测试新添加的用户注册和登录功能
"""

import requests
import json
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class AuthEndpointTester:
    """
    认证端点测试器
    """
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_user = {
            "username": f"testuser_{int(datetime.now().timestamp())}",
            "email": f"test_{int(datetime.now().timestamp())}@example.com",
            "password": "testpassword123",
            "nickname": "测试用户"
        }
        
    def test_server_connection(self):
        """
        测试服务器连接
        """
        try:
            response = self.session.get(f"{self.base_url}/docs")
            if response.status_code == 200:
                print("✅ 服务器连接正常")
                return True
            else:
                print(f"❌ 服务器连接失败，状态码: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 服务器连接异常: {e}")
            return False
    
    def test_user_registration(self):
        """
        测试用户注册
        """
        print("\n🔍 测试用户注册...")
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/register",
                json=self.test_user,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 用户注册成功")
                print(f"   - 用户ID: {data['user_info']['id']}")
                print(f"   - 用户名: {data['user_info']['nickname']}")
                print(f"   - 访问令牌: {data['access_token'][:20]}...")
                print(f"   - 令牌类型: {data['token_type']}")
                print(f"   - 过期时间: {data['expires_in']}秒")
                print(f"   - 新用户标识: {data['is_new_user']}")
                return True, data['access_token']
            else:
                print(f"❌ 用户注册失败，状态码: {response.status_code}")
                print(f"   错误信息: {response.text}")
                return False, None
                
        except Exception as e:
            print(f"❌ 用户注册异常: {e}")
            return False, None
    
    def test_duplicate_registration(self):
        """
        测试重复注册（应该失败）
        """
        print("\n🔍 测试重复注册...")
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/register",
                json=self.test_user,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 400:
                print("✅ 重复注册正确被拒绝")
                print(f"   错误信息: {response.json()['detail']}")
                return True
            else:
                print(f"❌ 重复注册未被正确拒绝，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 重复注册测试异常: {e}")
            return False
    
    def test_user_login(self):
        """
        测试用户登录
        """
        print("\n🔍 测试用户登录...")
        
        login_data = {
            "username_or_email": self.test_user["username"],
            "password": self.test_user["password"]
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 用户登录成功")
                print(f"   - 用户ID: {data['user_info']['id']}")
                print(f"   - 用户名: {data['user_info']['nickname']}")
                print(f"   - 访问令牌: {data['access_token'][:20]}...")
                print(f"   - 新用户标识: {data['is_new_user']}")
                return True, data['access_token']
            else:
                print(f"❌ 用户登录失败，状态码: {response.status_code}")
                print(f"   错误信息: {response.text}")
                return False, None
                
        except Exception as e:
            print(f"❌ 用户登录异常: {e}")
            return False, None
    
    def test_email_login(self):
        """
        测试邮箱登录
        """
        print("\n🔍 测试邮箱登录...")
        
        login_data = {
            "username_or_email": self.test_user["email"],
            "password": self.test_user["password"]
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 邮箱登录成功")
                print(f"   - 用户ID: {data['user_info']['id']}")
                return True, data['access_token']
            else:
                print(f"❌ 邮箱登录失败，状态码: {response.status_code}")
                return False, None
                
        except Exception as e:
            print(f"❌ 邮箱登录异常: {e}")
            return False, None
    
    def test_wrong_password(self):
        """
        测试错误密码（应该失败）
        """
        print("\n🔍 测试错误密码...")
        
        login_data = {
            "username_or_email": self.test_user["username"],
            "password": "wrongpassword"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 401:
                print("✅ 错误密码正确被拒绝")
                print(f"   错误信息: {response.json()['detail']}")
                return True
            else:
                print(f"❌ 错误密码未被正确拒绝，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 错误密码测试异常: {e}")
            return False
    
    def test_token_validation(self, token):
        """
        测试令牌验证
        """
        print("\n🔍 测试令牌验证...")
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/auth/check",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 令牌验证成功")
                print(f"   - 有效性: {data['valid']}")
                print(f"   - 用户ID: {data['user_id']}")
                print(f"   - 消息: {data['message']}")
                return True
            else:
                print(f"❌ 令牌验证失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 令牌验证异常: {e}")
            return False
    
    def test_user_info(self, token):
        """
        测试获取用户信息
        """
        print("\n🔍 测试获取用户信息...")
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 获取用户信息成功")
                print(f"   - 用户ID: {data['id']}")
                print(f"   - 用户名: {data.get('username', 'N/A')}")
                print(f"   - 邮箱: {data.get('email', 'N/A')}")
                print(f"   - 昵称: {data.get('nickname', 'N/A')}")
                print(f"   - 角色: {data.get('role', 'N/A')}")
                print(f"   - 状态: {data.get('status', 'N/A')}")
                return True
            else:
                print(f"❌ 获取用户信息失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 获取用户信息异常: {e}")
            return False
    
    def run_all_tests(self):
        """
        运行所有测试
        """
        print("🚀 开始认证API端点测试")
        print(f"测试用户: {self.test_user['username']}")
        print(f"测试邮箱: {self.test_user['email']}")
        
        results = []
        token = None
        
        # 1. 测试服务器连接
        results.append(self.test_server_connection())
        
        if not results[-1]:
            print("\n❌ 服务器连接失败，请确保FastAPI服务正在运行")
            print("   启动命令: python main.py 或 uvicorn main:app --reload")
            return
        
        # 2. 测试用户注册
        success, token = self.test_user_registration()
        results.append(success)
        
        if success:
            # 3. 测试重复注册
            results.append(self.test_duplicate_registration())
            
            # 4. 测试用户名登录
            success, login_token = self.test_user_login()
            results.append(success)
            
            # 5. 测试邮箱登录
            results.append(self.test_email_login()[0])
            
            # 6. 测试错误密码
            results.append(self.test_wrong_password())
            
            # 7. 测试令牌验证
            if token:
                results.append(self.test_token_validation(token))
                
                # 8. 测试获取用户信息
                results.append(self.test_user_info(token))
        
        # 输出测试结果
        print("\n" + "="*50)
        print("📊 测试结果汇总")
        print("="*50)
        
        test_names = [
            "服务器连接",
            "用户注册",
            "重复注册拒绝",
            "用户名登录",
            "邮箱登录",
            "错误密码拒绝",
            "令牌验证",
            "获取用户信息"
        ]
        
        passed = 0
        for i, result in enumerate(results):
            if i < len(test_names):
                status = "✅ 通过" if result else "❌ 失败"
                print(f"{test_names[i]}: {status}")
                if result:
                    passed += 1
        
        print(f"\n总计: {passed}/{len(results)} 项测试通过")
        
        if passed == len(results):
            print("🎉 所有认证API端点测试通过！")
        else:
            print("⚠️  部分测试失败，请检查相关功能")

def main():
    """
    主函数
    """
    print("用户认证API端点测试工具")
    print("=" * 30)
    
    # 创建测试器并运行测试
    tester = AuthEndpointTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()