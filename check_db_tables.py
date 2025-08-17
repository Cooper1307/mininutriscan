#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库中的表
"""

from app.database import engine
from sqlalchemy import text

def check_tables():
    """检查数据库中的所有表"""
    try:
        with engine.connect() as conn:
            # 查询所有表
            result = conn.execute(text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
            ))
            
            tables = [row[0] for row in result]
            
            print("数据库中的表:")
            if tables:
                for table in tables:
                    print(f"- {table}")
            else:
                print("没有找到任何表")
                
            return tables
            
    except Exception as e:
        print(f"检查数据库表时出错: {e}")
        return []

if __name__ == "__main__":
    check_tables()