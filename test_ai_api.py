#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试AI API连接
用于验证Qwen3 API配置是否正确
"""

import asyncio
import json
import os
from dotenv import load_dotenv
import aiohttp

# 加载环境变量
load_dotenv()

class AIAPITester:
    def __init__(self):
        self.api_key = os.getenv("QWEN_API_KEY", "")
        self.api_url = os.getenv("QWEN_API_URL", "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation")
        self.model = os.getenv("QWEN_MODEL", "qwen-turbo")
        
    def check_config(self):
        """检查配置"""
        print("=== AI API 配置检查 ===")
        print(f"API Key: {'已配置' if self.api_key else '未配置'}")
        print(f"API URL: {self.api_url}")
        print(f"Model: {self.model}")
        print()
        
        if not self.api_key:
            print("❌ 错误: QWEN_API_KEY 未配置")
            return False
        
        if self.api_key == "your-qwen-api-key-here":
            print("❌ 错误: QWEN_API_KEY 使用默认值，请配置真实的API密钥")
            return False
            
        print("✅ 配置检查通过")
        return True
    
    async def test_api_connection(self):
        """测试API连接"""
        print("=== 测试API连接 ===")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "input": {
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个营养健康AI助手。"
                    },
                    {
                        "role": "user",
                        "content": "请简单介绍一下苹果的营养价值。"
                    }
                ]
            },
            "parameters": {
                "temperature": 0.7,
                "max_tokens": 100
            }
        }
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                print(f"发送请求到: {self.api_url}")
                print(f"请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
                print()
                
                async with session.post(self.api_url, headers=headers, json=data) as response:
                    print(f"响应状态码: {response.status}")
                    
                    response_text = await response.text()
                    print(f"响应内容: {response_text}")
                    print()
                    
                    if response.status == 200:
                        try:
                            response_data = json.loads(response_text)
                            if "output" in response_data and "text" in response_data["output"]:
                                print("✅ API连接成功!")
                                print(f"AI回复: {response_data['output']['text']}")
                                return True
                            else:
                                print("❌ API响应格式异常")
                                print(f"响应数据: {response_data}")
                                return False
                        except json.JSONDecodeError as e:
                            print(f"❌ JSON解析失败: {e}")
                            return False
                    else:
                        print(f"❌ API请求失败，状态码: {response.status}")
                        try:
                            error_data = json.loads(response_text)
                            print(f"错误信息: {error_data}")
                        except:
                            print(f"错误响应: {response_text}")
                        return False
                        
        except asyncio.TimeoutError:
            print("❌ 请求超时")
            return False
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False
    
    async def run_test(self):
        """运行完整测试"""
        print("开始AI API测试...")
        print()
        
        # 检查配置
        if not self.check_config():
            return False
        
        print()
        
        # 测试API连接
        result = await self.test_api_connection()
        
        print()
        print("=== 测试结果 ===")
        if result:
            print("✅ AI API测试通过，配置正确")
        else:
            print("❌ AI API测试失败，请检查配置")
        
        return result

async def main():
    tester = AIAPITester()
    await tester.run_test()

if __name__ == "__main__":
    asyncio.run(main())