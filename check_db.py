#!/usr/bin/env python3
# 检查数据库表结构

from app.database import engine
from sqlalchemy import text

def check_reports_table():
    """检查reports表结构"""
    try:
        with engine.connect() as conn:
            # 检查表是否存在
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'reports'
                )
            """))
            table_exists = result.scalar()
            print(f"Reports table exists: {table_exists}")
            
            if table_exists:
                # 获取表结构
                result = conn.execute(text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = 'reports' 
                    ORDER BY ordinal_position
                """))
                
                print("\nReports table columns:")
                for row in result:
                    print(f"  {row[0]}: {row[1]} (nullable: {row[2]})")
            else:
                print("Reports table does not exist!")
                
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    check_reports_table()