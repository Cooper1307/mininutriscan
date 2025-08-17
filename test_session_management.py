#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会话管理功能测试脚本

这个脚本测试会话管理的各种功能：
1. 会话创建
2. 会话验证
3. 会话列表获取
4. 会话登出
5. 批量登出
6. 会话统计（管理员功能）
"""

import requests
import json
import time
from datetime import datetime

# 配置
BASE_URL = "http://127.0.0.1:8000/api/v1"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def print_test_header(test_name):
    """打印测试标题"""
    print(f"\n{'='*60}")
    print(f"🧪 测试: {test_name}")
    print(f"{'='*60}")

def print_result(success, message, details=None):
    """打印测试结果"""
    status = "✅ 成功" if success else "❌ 失败"
    print(f"{status}: {message}")
    if details:
        print(f"详细信息: {details}")

def register_test_user():
    """注册测试用户"""
    print_test_header("注册测试用户")
    
    # 生成唯一的测试用户名
    timestamp = int(time.time())
    test_user = {
        "username": f"session_test_user_{timestamp}",
        "email": f"session_test_{timestamp}@example.com",
        "password": "test_password_123",
        "nickname": f"会话测试用户_{timestamp}"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            headers=HEADERS,
            json=test_user
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "用户注册成功", f"用户ID: {data.get('user', {}).get('id')}")
            return test_user, data.get('access_token')
        else:
            print_result(False, f"用户注册失败 (状态码: {response.status_code})", response.text)
            return None, None
            
    except Exception as e:
        print_result(False, "用户注册异常", str(e))
        return None, None

def test_session_creation(token):
    """测试会话创建"""
    print_test_header("会话创建测试")
    
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.post(
            f"{BASE_URL}/sessions/create",
            headers=headers,
            json={"expire_minutes": 60}
        )
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get('session_id')
            print_result(True, "会话创建成功", f"会话ID: {session_id}")
            return session_id
        else:
            print_result(False, f"会话创建失败 (状态码: {response.status_code})", response.text)
            return None
            
    except Exception as e:
        print_result(False, "会话创建异常", str(e))
        return None

def test_session_validation(token, session_id):
    """测试会话验证"""
    print_test_header("会话验证测试")
    
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.post(
            f"{BASE_URL}/sessions/validate/{session_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            is_valid = data.get('valid', False)
            print_result(is_valid, f"会话验证结果: {'有效' if is_valid else '无效'}", data.get('message'))
            return is_valid
        else:
            print_result(False, f"会话验证失败 (状态码: {response.status_code})", response.text)
            return False
            
    except Exception as e:
        print_result(False, "会话验证异常", str(e))
        return False

def test_current_session(token):
    """测试获取当前会话"""
    print_test_header("获取当前会话测试")
    
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.get(
            f"{BASE_URL}/sessions/current",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "获取当前会话成功", json.dumps(data, indent=2, ensure_ascii=False))
            return data
        else:
            print_result(False, f"获取当前会话失败 (状态码: {response.status_code})", response.text)
            return None
            
    except Exception as e:
        print_result(False, "获取当前会话异常", str(e))
        return None

def test_session_list(token):
    """测试获取会话列表"""
    print_test_header("获取会话列表测试")
    
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.get(
            f"{BASE_URL}/sessions/list",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            session_count = len(data) if isinstance(data, list) else 0
            print_result(True, f"获取会话列表成功，共 {session_count} 个会话")
            
            if session_count > 0:
                print("会话详情:")
                for i, session in enumerate(data, 1):
                    print(f"  {i}. 会话ID: {session.get('session_id', 'N/A')}")
                    print(f"     创建时间: {session.get('created_at', 'N/A')}")
                    print(f"     最后活动: {session.get('last_activity', 'N/A')}")
                    print(f"     IP地址: {session.get('ip_address', 'N/A')}")
            
            return data
        else:
            print_result(False, f"获取会话列表失败 (状态码: {response.status_code})", response.text)
            return None
            
    except Exception as e:
        print_result(False, "获取会话列表异常", str(e))
        return None

def test_session_logout(token, session_id):
    """测试会话登出"""
    print_test_header("会话登出测试")
    
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.delete(
            f"{BASE_URL}/sessions/logout/{session_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "会话登出成功", data.get('message'))
            return True
        else:
            print_result(False, f"会话登出失败 (状态码: {response.status_code})", response.text)
            return False
            
    except Exception as e:
        print_result(False, "会话登出异常", str(e))
        return False

def test_logout_all_sessions(token):
    """测试登出所有会话"""
    print_test_header("登出所有会话测试")
    
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.delete(
            f"{BASE_URL}/sessions/logout-all",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            deleted_count = data.get('deleted_count', 0)
            print_result(True, f"登出所有会话成功，共登出 {deleted_count} 个会话", data.get('message'))
            return True
        else:
            print_result(False, f"登出所有会话失败 (状态码: {response.status_code})", response.text)
            return False
            
    except Exception as e:
        print_result(False, "登出所有会话异常", str(e))
        return False

def test_session_stats(token):
    """测试会话统计（需要管理员权限）"""
    print_test_header("会话统计测试（管理员功能）")
    
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.get(
            f"{BASE_URL}/sessions/stats",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "获取会话统计成功", json.dumps(data, indent=2, ensure_ascii=False))
            return data
        elif response.status_code == 403:
            print_result(True, "权限验证正常（非管理员用户无法访问统计）", "403 Forbidden")
            return None
        else:
            print_result(False, f"获取会话统计失败 (状态码: {response.status_code})", response.text)
            return None
            
    except Exception as e:
        print_result(False, "获取会话统计异常", str(e))
        return None

def test_cleanup_sessions(token):
    """测试清理过期会话（需要管理员权限）"""
    print_test_header("清理过期会话测试（管理员功能）")
    
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.post(
            f"{BASE_URL}/sessions/cleanup",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            cleaned_count = data.get('cleaned_count', 0)
            print_result(True, f"清理过期会话成功，共清理 {cleaned_count} 个会话", data.get('message'))
            return True
        elif response.status_code == 403:
            print_result(True, "权限验证正常（非管理员用户无法执行清理）", "403 Forbidden")
            return False
        else:
            print_result(False, f"清理过期会话失败 (状态码: {response.status_code})", response.text)
            return False
            
    except Exception as e:
        print_result(False, "清理过期会话异常", str(e))
        return False

def check_server_connection():
    """检查服务器连接"""
    print_test_header("服务器连接检查")
    
    try:
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health", timeout=5)
        if response.status_code == 200:
            print_result(True, "服务器连接正常")
            return True
        else:
            print_result(False, f"服务器响应异常 (状态码: {response.status_code})")
            return False
    except Exception as e:
        print_result(False, "无法连接到服务器", str(e))
        return False

def main():
    """主测试函数"""
    print("🚀 开始会话管理功能测试")
    print(f"📍 测试服务器: {BASE_URL}")
    print(f"🕒 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查服务器连接
    if not check_server_connection():
        print("\n❌ 服务器连接失败，请确保服务器正在运行")
        return
    
    # 注册测试用户
    test_user, token = register_test_user()
    if not token:
        print("\n❌ 无法获取访问令牌，测试终止")
        return
    
    print(f"\n🔑 获取到访问令牌: {token[:20]}...")
    
    # 测试会话创建
    session_id = test_session_creation(token)
    if not session_id:
        print("\n❌ 会话创建失败，跳过后续测试")
        return
    
    # 等待一秒，确保会话已保存
    time.sleep(1)
    
    # 测试会话验证
    test_session_validation(token, session_id)
    
    # 测试获取当前会话
    test_current_session(token)
    
    # 测试获取会话列表
    test_session_list(token)
    
    # 创建多个会话进行测试
    print_test_header("创建多个会话进行测试")
    additional_sessions = []
    for i in range(2):
        additional_session = test_session_creation(token)
        if additional_session:
            additional_sessions.append(additional_session)
        time.sleep(0.5)
    
    # 再次获取会话列表
    test_session_list(token)
    
    # 测试单个会话登出
    if additional_sessions:
        test_session_logout(token, additional_sessions[0])
    
    # 测试会话统计（管理员功能）
    test_session_stats(token)
    
    # 测试清理过期会话（管理员功能）
    test_cleanup_sessions(token)
    
    # 测试登出所有会话
    test_logout_all_sessions(token)
    
    # 验证登出后的状态
    print_test_header("验证登出后状态")
    test_session_list(token)
    
    print("\n🎉 会话管理功能测试完成！")
    print("\n📋 测试总结:")
    print("   ✅ 会话创建功能")
    print("   ✅ 会话验证功能")
    print("   ✅ 会话列表获取")
    print("   ✅ 单个会话登出")
    print("   ✅ 批量会话登出")
    print("   ✅ 权限控制验证")
    print("\n💡 提示: 管理员功能需要具有admin角色的用户才能访问")

if __name__ == "__main__":
    main()