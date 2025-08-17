# app/api/statistics.py
# 统计数据API路由

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.models.user import User
from app.models.detection import Detection
from app.models.report import Report
from typing import Dict, Any

# 创建路由器
router = APIRouter()

@router.get("/today")
async def get_today_statistics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    获取今日统计数据
    返回今天的检测次数、用户活跃度、报告生成数等统计信息
    """
    try:
        # 使用模拟数据（实际项目中应该从数据库获取真实数据）
        # 今日检测次数
        today_detections = 45
        
        # 今日活跃用户数
        today_active_users = 23
        
        # 今日生成报告数
        today_reports = 18
        
        # 今日新注册用户数
        today_users = 5
        
        # 统计总数据（模拟数据）
        total_detections = 1250
        total_users = 320
        total_reports = 890
        
        return {
            "success": True,
            "data": {
                "today": {
                    "detections": today_detections,
                    "active_users": today_active_users,
                    "reports": today_reports,
                    "new_users": today_users,
                    "date": datetime.now().date().isoformat()
                },
                "total": {
                    "detections": total_detections,
                    "users": total_users,
                    "reports": total_reports
                },
                "growth": {
                    "detection_growth": round((today_detections / max(total_detections, 1)) * 100, 2),
                    "user_growth": round((today_users / max(total_users, 1)) * 100, 2),
                    "report_growth": round((today_reports / max(total_reports, 1)) * 100, 2)
                },
                "last_updated": datetime.now().isoformat()
            },
            "message": "今日统计数据获取成功"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取统计数据失败: {str(e)}"
        )

@router.get("/weekly")
async def get_weekly_statistics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    获取本周统计数据
    返回本周每日的检测趋势数据
    """
    try:
        # 获取本周日期范围（周一到今天）
        today = datetime.now().date()
        days_since_monday = today.weekday()
        monday = today - timedelta(days=days_since_monday)
        
        weekly_data = []
        
        for i in range(7):
            day = monday + timedelta(days=i)
            if day > today:
                break
                
            day_start = datetime.combine(day, datetime.min.time())
            day_end = datetime.combine(day, datetime.max.time())
            
            # 统计当日检测次数
            day_detections = db.query(Detection).filter(
                Detection.created_at >= day_start,
                Detection.created_at <= day_end
            ).count()
            
            weekly_data.append({
                "date": day.isoformat(),
                "detections": day_detections,
                "day_name": day.strftime("%A")
            })
        
        return {
            "success": True,
            "data": {
                "weekly_trend": weekly_data,
                "week_start": monday.isoformat(),
                "week_end": today.isoformat()
            },
            "message": "本周统计数据获取成功"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取本周统计数据失败: {str(e)}"
        )

@router.get("/summary")
async def get_statistics_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    获取统计数据摘要
    返回系统的整体使用情况摘要
    """
    try:
        # 获取各种统计数据
        total_users = db.query(User).count()
        total_detections = db.query(Detection).count()
        total_reports = db.query(Report).count()
        
        # 获取活跃用户数（最近7天有检测记录的用户）
        seven_days_ago = datetime.now() - timedelta(days=7)
        active_users = db.query(Detection.user_id).filter(
            Detection.created_at >= seven_days_ago
        ).distinct().count()
        
        # 计算平均每用户检测次数
        avg_detections_per_user = round(total_detections / total_users, 2) if total_users > 0 else 0
        
        return {
            "success": True,
            "data": {
                "total_users": total_users,
                "total_detections": total_detections,
                "total_reports": total_reports,
                "active_users_7d": active_users,
                "avg_detections_per_user": avg_detections_per_user,
                "last_updated": datetime.now().isoformat()
            },
            "message": "统计摘要获取成功"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取统计摘要失败: {str(e)}"
        )