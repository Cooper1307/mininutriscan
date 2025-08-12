#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QWEN API密钥配置工具
帮助用户快速配置QWEN API密钥
"""

import os
import re
from pathlib import Path

def print_header(title):
    """打印标题"""
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")

def print_info():
    """打印QWEN API信息"""
    print("\n🤖 关于QWEN API:")
    print("   QWEN是阿里云推出的大语言模型服务")
    print("   用于食品安全AI检测和智能问答功能")
    print("\n🔑 获取API密钥:")
    print("   1. 访问阿里云官网: https://www.aliyun.com/")
    print("   2. 注册/登录阿里云账号")
    print("   3. 开通通义千问服务")
    print("   4. 在控制台获取API密钥")
    print("\n💡 注意事项:")
    print("   - API密钥是敏感信息，请妥善保管")
    print("   - 不要将密钥提交到代码仓库")
    print("   - 如果暂时没有密钥，可以跳过此配置")

def read_env_file():
    """读取.env文件内容"""
    env_path = Path(".env")
    if not env_path.exists():
        return None, []
    
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    return env_path, lines

def update_qwen_key(lines, api_key):
    """更新QWEN API密钥"""
    updated = False
    new_lines = []
    
    for line in lines:
        if line.strip().startswith('QWEN_API_KEY=') or line.strip().startswith('#QWEN_API_KEY='):
            new_lines.append(f'QWEN_API_KEY={api_key}\n')
            updated = True
        else:
            new_lines.append(line)
    
    # 如果没有找到QWEN_API_KEY行，添加到文件末尾
    if not updated:
        new_lines.append(f'\n# QWEN API配置\nQWEN_API_KEY={api_key}\n')
    
    return new_lines

def validate_api_key(api_key):
    """验证API密钥格式"""
    if not api_key:
        return False, "API密钥不能为空"
    
    if len(api_key) < 10:
        return False, "API密钥长度太短，请检查是否完整"
    
    # 简单的格式检查
    if not re.match(r'^[a-zA-Z0-9_-]+$', api_key):
        return False, "API密钥格式不正确，只能包含字母、数字、下划线和连字符"
    
    return True, "格式正确"

def main():
    """主函数"""
    print("🤖 QWEN API密钥配置工具")
    print("=" * 50)
    
    # 检查是否在项目目录
    if not os.path.exists("main.py"):
        print("❌ 请在项目根目录运行此脚本")
        print(f"当前目录: {os.getcwd()}")
        input("\n按回车键退出...")
        return 1
    
    # 读取.env文件
    env_path, lines = read_env_file()
    if env_path is None:
        print("❌ 未找到.env文件")
        print("\n💡 请先运行 '快速设置开发环境.bat' 创建配置文件")
        input("\n按回车键退出...")
        return 1
    
    print_info()
    
    print_header("配置QWEN API密钥")
    
    # 检查当前配置
    current_key = None
    for line in lines:
        if line.strip().startswith('QWEN_API_KEY='):
            current_key = line.split('=', 1)[1].strip()
            break
    
    if current_key and current_key != "your_qwen_api_key_here":
        print(f"\n🔍 当前配置: {current_key[:10]}...{current_key[-4:] if len(current_key) > 14 else current_key}")
        print("\n选择操作:")
        print("   1. 更新API密钥")
        print("   2. 保持当前配置")
        print("   3. 清除API密钥")
        
        while True:
            choice = input("\n请选择 (1-3): ").strip()
            if choice in ['1', '2', '3']:
                break
            print("❌ 请输入有效选项 (1-3)")
        
        if choice == '2':
            print("\n✅ 保持当前配置")
            input("\n按回车键退出...")
            return 0
        elif choice == '3':
            # 清除API密钥
            new_lines = update_qwen_key(lines, "")
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print("\n✅ API密钥已清除")
            input("\n按回车键退出...")
            return 0
    else:
        print("\n🔍 当前状态: 未配置QWEN API密钥")
    
    print("\n📝 请输入QWEN API密钥:")
    print("   (直接回车跳过配置)")
    
    while True:
        api_key = input("\nAPI密钥: ").strip()
        
        if not api_key:
            print("\n⏭️  跳过QWEN API密钥配置")
            print("\n💡 提示: 没有API密钥将无法使用AI检测功能")
            print("   可以稍后重新运行此脚本进行配置")
            input("\n按回车键退出...")
            return 0
        
        # 验证API密钥格式
        is_valid, message = validate_api_key(api_key)
        if is_valid:
            break
        else:
            print(f"❌ {message}")
            print("\n请重新输入或直接回车跳过:")
    
    # 确认配置
    print(f"\n🔍 确认配置:")
    print(f"   API密钥: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else api_key}")
    
    while True:
        confirm = input("\n确认配置? (y/n): ").strip().lower()
        if confirm in ['y', 'yes', 'n', 'no']:
            break
        print("❌ 请输入 y 或 n")
    
    if confirm in ['n', 'no']:
        print("\n❌ 配置已取消")
        input("\n按回车键退出...")
        return 0
    
    try:
        # 更新.env文件
        new_lines = update_qwen_key(lines, api_key)
        
        # 备份原文件
        backup_path = Path(".env.backup")
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        # 写入新配置
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print("\n✅ QWEN API密钥配置成功！")
        print(f"\n📁 配置文件: {env_path.absolute()}")
        print(f"📁 备份文件: {backup_path.absolute()}")
        
        print("\n🚀 下一步操作:")
        print("   1. 运行 '检查项目状态.bat' 验证配置")
        print("   2. 运行 '启动所有服务.bat' 启动服务")
        print("   3. 测试AI检测功能")
        
    except Exception as e:
        print(f"\n❌ 配置失败: {e}")
        print("\n🔧 故障排除:")
        print("   1. 检查文件权限")
        print("   2. 确保.env文件未被其他程序占用")
        print("   3. 手动编辑.env文件")
        input("\n按回车键退出...")
        return 1
    
    input("\n按回车键退出...")
    return 0

if __name__ == "__main__":
    exit(main())