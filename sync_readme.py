#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动同步README文档脚本

功能说明:
1. 监控项目文件变化
2. 自动更新README文档内容
3. 提交并推送到远程仓库
4. 记录同步日志

使用方法:
    python sync_readme.py

作者: 陈露
创建时间: 2025年8月
"""

import os
import sys
import subprocess
import datetime
import json
from pathlib import Path
from typing import Dict, List, Optional

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
README_PATH = PROJECT_ROOT / "README.md"
LOG_PATH = PROJECT_ROOT / "sync_readme.log"

# 需要监控的文件类型
MONITORED_EXTENSIONS = {
    '.md', '.py', '.js', '.json', '.yaml', '.yml', 
    '.txt', '.wxml', '.wxss', '.wxs'
}

# 需要排除的目录
EXCLUDED_DIRS = {
    '.git', 'node_modules', '__pycache__', '.trae', 
    'dist', 'build', 'logs'
}

class ReadmeSync:
    """README文档同步管理器"""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.readme_path = README_PATH
        self.log_path = LOG_PATH
        
    def log_message(self, message: str, level: str = "INFO") -> None:
        """记录日志信息"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        # 输出到控制台
        print(log_entry.strip())
        
        # 写入日志文件
        try:
            with open(self.log_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"写入日志失败: {e}")
    
    def get_project_stats(self) -> Dict:
        """获取项目统计信息"""
        stats = {
            'total_files': 0,
            'code_files': 0,
            'doc_files': 0,
            'total_lines': 0,
            'last_modified': None,
            'file_types': {},
            'recent_changes': []
        }
        
        try:
            for root, dirs, files in os.walk(self.project_root):
                # 排除指定目录
                dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
                
                for file in files:
                    file_path = Path(root) / file
                    file_ext = file_path.suffix.lower()
                    
                    # 统计文件数量
                    stats['total_files'] += 1
                    
                    # 按扩展名分类
                    if file_ext in stats['file_types']:
                        stats['file_types'][file_ext] += 1
                    else:
                        stats['file_types'][file_ext] = 1
                    
                    # 分类统计
                    if file_ext in {'.py', '.js', '.wxml', '.wxss', '.wxs'}:
                        stats['code_files'] += 1
                    elif file_ext in {'.md', '.txt'}:
                        stats['doc_files'] += 1
                    
                    # 统计行数（仅文本文件）
                    if file_ext in MONITORED_EXTENSIONS:
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                lines = len(f.readlines())
                                stats['total_lines'] += lines
                        except:
                            pass
                    
                    # 记录最后修改时间
                    try:
                        mtime = file_path.stat().st_mtime
                        if stats['last_modified'] is None or mtime > stats['last_modified']:
                            stats['last_modified'] = mtime
                    except:
                        pass
            
            # 转换时间戳
            if stats['last_modified']:
                stats['last_modified'] = datetime.datetime.fromtimestamp(
                    stats['last_modified']
                ).strftime("%Y-%m-%d %H:%M:%S")
                
        except Exception as e:
            self.log_message(f"获取项目统计信息失败: {e}", "ERROR")
        
        return stats
    
    def get_git_status(self) -> Dict:
        """获取Git状态信息"""
        git_info = {
            'branch': 'unknown',
            'commit_count': 0,
            'last_commit': 'unknown',
            'status': 'unknown',
            'remote_url': 'unknown'
        }
        
        try:
            # 获取当前分支
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                git_info['branch'] = result.stdout.strip()
            
            # 获取提交数量
            result = subprocess.run(
                ['git', 'rev-list', '--count', 'HEAD'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                git_info['commit_count'] = int(result.stdout.strip())
            
            # 获取最后提交信息
            result = subprocess.run(
                ['git', 'log', '-1', '--pretty=format:%h - %s (%cr)'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                git_info['last_commit'] = result.stdout.strip()
            
            # 获取工作区状态
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                if result.stdout.strip():
                    git_info['status'] = 'modified'
                else:
                    git_info['status'] = 'clean'
            
            # 获取远程仓库URL
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                git_info['remote_url'] = result.stdout.strip()
                
        except Exception as e:
            self.log_message(f"获取Git信息失败: {e}", "ERROR")
        
        return git_info
    
    def update_readme_stats(self) -> bool:
        """更新README中的项目统计信息"""
        try:
            # 获取统计信息
            stats = self.get_project_stats()
            git_info = self.get_git_status()
            
            # 读取当前README内容
            if not self.readme_path.exists():
                self.log_message("README.md文件不存在", "ERROR")
                return False
            
            with open(self.readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 更新统计信息（在项目进度部分）
            current_time = datetime.datetime.now().strftime("%Y年%m月%d日 %H:%M")
            
            # 查找并更新"最后更新"时间
            import re
            
            # 更新最后更新时间
            content = re.sub(
                r'\*\*最后更新\*\*: .*',
                f'**最后更新**: {current_time}',
                content
            )
            
            # 在README末尾添加统计信息（如果不存在）
            stats_section = f"""

## 📈 项目统计

> 最后更新: {current_time}

### 代码统计
- 📁 **总文件数**: {stats['total_files']}
- 💻 **代码文件**: {stats['code_files']}
- 📝 **文档文件**: {stats['doc_files']}
- 📏 **总代码行数**: {stats['total_lines']:,}
- 🕒 **最后修改**: {stats['last_modified'] or '未知'}

### Git信息
- 🌿 **当前分支**: {git_info['branch']}
- 📦 **提交数量**: {git_info['commit_count']}
- 🔄 **最后提交**: {git_info['last_commit']}
- 📊 **工作区状态**: {git_info['status']}
- 🔗 **远程仓库**: {git_info['remote_url']}

### 文件类型分布
"""
            
            # 添加文件类型统计
            for ext, count in sorted(stats['file_types'].items()):
                if ext and count > 0:
                    stats_section += f"- `{ext}`: {count} 个文件\n"
            
            # 检查是否已存在统计部分
            if "## 📈 项目统计" in content:
                # 替换现有统计部分
                content = re.sub(
                    r'## 📈 项目统计.*?(?=##|$)',
                    stats_section.strip() + '\n\n',
                    content,
                    flags=re.DOTALL
                )
            else:
                # 在最后更新之前插入统计部分
                insert_pos = content.rfind('**最后更新**')
                if insert_pos != -1:
                    # 找到段落开始
                    paragraph_start = content.rfind('\n\n', 0, insert_pos)
                    if paragraph_start != -1:
                        content = (content[:paragraph_start] + 
                                 stats_section + 
                                 content[paragraph_start:])
            
            # 写回文件
            with open(self.readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log_message("README统计信息更新成功")
            return True
            
        except Exception as e:
            self.log_message(f"更新README统计信息失败: {e}", "ERROR")
            return False
    
    def commit_and_push(self) -> bool:
        """提交并推送更改到远程仓库"""
        try:
            # 检查是否有更改
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self.log_message("检查Git状态失败", "ERROR")
                return False
            
            if not result.stdout.strip():
                self.log_message("没有文件更改，跳过提交")
                return True
            
            # 添加所有更改
            result = subprocess.run(
                ['git', 'add', '.'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self.log_message(f"Git add失败: {result.stderr}", "ERROR")
                return False
            
            # 提交更改
            commit_message = f"docs: 自动同步README文档 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
            result = subprocess.run(
                ['git', 'commit', '-m', commit_message],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self.log_message(f"Git commit失败: {result.stderr}", "ERROR")
                return False
            
            # 推送到远程仓库
            result = subprocess.run(
                ['git', 'push', 'origin', 'master'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self.log_message(f"Git push失败: {result.stderr}", "ERROR")
                return False
            
            self.log_message("成功提交并推送到远程仓库")
            return True
            
        except Exception as e:
            self.log_message(f"提交推送过程失败: {e}", "ERROR")
            return False
    
    def sync(self) -> bool:
        """执行完整的同步流程"""
        self.log_message("开始同步README文档")
        
        # 更新README统计信息
        if not self.update_readme_stats():
            return False
        
        # 提交并推送更改
        if not self.commit_and_push():
            return False
        
        self.log_message("README文档同步完成")
        return True

def main():
    """主函数"""
    print("🛡️ 社区食安AI小卫士 - README自动同步工具")
    print("=" * 50)
    
    # 检查是否在Git仓库中
    if not (PROJECT_ROOT / '.git').exists():
        print("❌ 错误: 当前目录不是Git仓库")
        sys.exit(1)
    
    # 创建同步管理器
    sync_manager = ReadmeSync()
    
    # 执行同步
    success = sync_manager.sync()
    
    if success:
        print("\n✅ README文档同步成功！")
        print(f"📝 日志文件: {LOG_PATH}")
        sys.exit(0)
    else:
        print("\n❌ README文档同步失败！")
        print(f"📝 请查看日志文件: {LOG_PATH}")
        sys.exit(1)

if __name__ == "__main__":
    main()