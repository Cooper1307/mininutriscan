# app/api/community.py
# 社区数据API路由

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from typing import Dict, Any, List

# 创建路由器
router = APIRouter()

@router.get("/news")
async def get_community_news(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    获取社区新闻和动态
    返回最新的社区新闻、公告和活动信息
    """
    try:
        # 模拟社区新闻数据（实际项目中应该从数据库获取）
        news_data = [
            {
                "id": 1,
                "title": "食品安全知识科普周活动开始啦！",
                "summary": "本周我们将为大家带来丰富的食品安全知识，包括食品标签解读、营养成分分析等内容。",
                "content": "详细的活动内容和参与方式...",
                "author": "社区管理员",
                "publish_time": (datetime.now() - timedelta(hours=2)).isoformat(),
                "category": "活动公告",
                "tags": ["食品安全", "科普", "活动"],
                "read_count": 156,
                "like_count": 23,
                "image_url": "/uploads/news/food_safety_week.jpg"
            },
            {
                "id": 2,
                "title": "新增营养检测功能：AI智能识别食品成分",
                "summary": "我们的AI检测功能再次升级，现在可以更准确地识别食品成分和营养信息。",
                "content": "功能详细介绍和使用方法...",
                "author": "技术团队",
                "publish_time": (datetime.now() - timedelta(days=1)).isoformat(),
                "category": "功能更新",
                "tags": ["AI检测", "功能更新", "营养分析"],
                "read_count": 89,
                "like_count": 15,
                "image_url": "/uploads/news/ai_detection.jpg"
            },
            {
                "id": 3,
                "title": "社区用户突破1000人！感谢大家的支持",
                "summary": "感谢所有用户的信任和支持，我们将继续努力提供更好的食品安全服务。",
                "content": "里程碑庆祝和未来规划...",
                "author": "社区管理员",
                "publish_time": (datetime.now() - timedelta(days=3)).isoformat(),
                "category": "社区动态",
                "tags": ["里程碑", "感谢", "社区"],
                "read_count": 234,
                "like_count": 67,
                "image_url": "/uploads/news/milestone_1000.jpg"
            },
            {
                "id": 4,
                "title": "食品安全小贴士：如何正确阅读营养标签",
                "summary": "学会阅读营养标签是选择健康食品的重要技能，让我们一起来学习吧！",
                "content": "营养标签阅读指南...",
                "author": "营养专家",
                "publish_time": (datetime.now() - timedelta(days=5)).isoformat(),
                "category": "健康科普",
                "tags": ["营养标签", "健康", "科普"],
                "read_count": 178,
                "like_count": 34,
                "image_url": "/uploads/news/nutrition_label.jpg"
            }
        ]
        
        return {
            "success": True,
            "data": {
                "news": news_data,
                "total_count": len(news_data),
                "last_updated": datetime.now().isoformat()
            },
            "message": "社区新闻获取成功"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取社区新闻失败: {str(e)}"
        )

@router.get("/announcements")
async def get_community_announcements(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    获取社区公告
    返回重要的社区公告和通知
    """
    try:
        # 模拟公告数据
        announcements = [
            {
                "id": 1,
                "title": "系统维护通知",
                "content": "为了提供更好的服务，系统将于本周日凌晨2:00-4:00进行维护升级。",
                "type": "maintenance",
                "priority": "high",
                "publish_time": (datetime.now() - timedelta(hours=6)).isoformat(),
                "expire_time": (datetime.now() + timedelta(days=2)).isoformat(),
                "is_active": True
            },
            {
                "id": 2,
                "title": "新用户注册奖励活动",
                "content": "新用户注册即可获得10次免费AI检测机会，邀请好友还有额外奖励！",
                "type": "promotion",
                "priority": "medium",
                "publish_time": (datetime.now() - timedelta(days=2)).isoformat(),
                "expire_time": (datetime.now() + timedelta(days=30)).isoformat(),
                "is_active": True
            }
        ]
        
        return {
            "success": True,
            "data": {
                "announcements": announcements,
                "active_count": len([a for a in announcements if a["is_active"]]),
                "last_updated": datetime.now().isoformat()
            },
            "message": "社区公告获取成功"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取社区公告失败: {str(e)}"
        )

@router.get("/activities")
async def get_community_activities(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    获取社区活动
    返回正在进行和即将开始的社区活动
    """
    try:
        # 模拟活动数据
        activities = [
            {
                "id": 1,
                "title": "食品安全知识竞赛",
                "description": "参与答题赢取精美奖品，提升食品安全意识！",
                "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
                "end_time": (datetime.now() + timedelta(days=7)).isoformat(),
                "status": "upcoming",
                "participants_count": 45,
                "max_participants": 100,
                "rewards": ["优质食品券", "健康检测套餐", "营养咨询服务"],
                "image_url": "/uploads/activities/quiz_contest.jpg"
            },
            {
                "id": 2,
                "title": "健康饮食分享会",
                "description": "营养专家在线分享健康饮食经验，欢迎大家参与讨论！",
                "start_time": (datetime.now() + timedelta(days=3)).isoformat(),
                "end_time": (datetime.now() + timedelta(days=3, hours=2)).isoformat(),
                "status": "upcoming",
                "participants_count": 23,
                "max_participants": 50,
                "rewards": ["专家咨询机会", "健康食谱"],
                "image_url": "/uploads/activities/health_sharing.jpg"
            }
        ]
        
        return {
            "success": True,
            "data": {
                "activities": activities,
                "upcoming_count": len([a for a in activities if a["status"] == "upcoming"]),
                "last_updated": datetime.now().isoformat()
            },
            "message": "社区活动获取成功"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取社区活动失败: {str(e)}"
        )

@router.get("/stats")
async def get_community_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    获取社区统计信息
    返回社区的基本统计数据
    """
    try:
        # 模拟社区统计数据
        stats = {
            "total_members": 1247,
            "active_members_today": 89,
            "total_posts": 156,
            "total_comments": 423,
            "total_likes": 1089,
            "new_members_this_week": 34,
            "popular_topics": [
                {"name": "食品安全", "count": 45},
                {"name": "营养健康", "count": 38},
                {"name": "AI检测", "count": 29},
                {"name": "健康饮食", "count": 22}
            ]
        }
        
        return {
            "success": True,
            "data": stats,
            "message": "社区统计信息获取成功"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取社区统计信息失败: {str(e)}"
        )