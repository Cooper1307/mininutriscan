# app/api/education.py
# 教育内容API路由

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import os

from ..core.database import get_db
from ..models.user import User
from ..models.education import EducationContent
from ..api.auth import get_current_user, get_current_user_optional
from ..core.config import settings

# 创建路由器
router = APIRouter()

# Pydantic模型定义
class EducationContentResponse(BaseModel):
    """
    教育内容响应模型
    """
    id: int
    content_type: str
    status: str
    title: str
    summary: Optional[str]
    content: Optional[str]
    image_url: Optional[str]
    video_url: Optional[str]
    audio_url: Optional[str]
    category: str
    tags: List[str]
    target_audience: str
    difficulty_level: str
    author_name: Optional[str]
    author_title: Optional[str]
    reading_time: Optional[int]
    view_count: int
    like_count: int
    share_count: int
    bookmark_count: int
    avg_rating: Optional[float]
    rating_count: int
    created_at: datetime
    updated_at: datetime
    is_liked: bool = False
    is_bookmarked: bool = False
    user_rating: Optional[int] = None

class EducationContentListResponse(BaseModel):
    """
    教育内容列表响应模型
    """
    id: int
    content_type: str
    status: str
    title: str
    summary: Optional[str]
    image_url: Optional[str]
    category: str
    tags: List[str]
    target_audience: str
    difficulty_level: str
    author_name: Optional[str]
    reading_time: Optional[int]
    view_count: int
    like_count: int
    avg_rating: Optional[float]
    created_at: datetime
    is_liked: bool = False
    is_bookmarked: bool = False

class EducationStatsResponse(BaseModel):
    """
    教育内容统计响应模型
    """
    total_content: int
    total_views: int
    total_likes: int
    total_bookmarks: int
    popular_categories: List[Dict[str, Any]]
    recent_content: List[EducationContentListResponse]
    recommended_content: List[EducationContentListResponse]

class ContentInteractionRequest(BaseModel):
    """
    内容交互请求模型
    """
    action: str = Field(..., description="操作类型: like, unlike, bookmark, unbookmark")

class ContentRatingRequest(BaseModel):
    """
    内容评分请求模型
    """
    rating: int = Field(..., ge=1, le=5, description="评分 1-5")
    comment: Optional[str] = Field(None, description="评价内容")

# 工具函数
def get_user_interactions(db: Session, user_id: Optional[int], content_ids: List[int]):
    """
    获取用户对内容的交互状态
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        content_ids: 内容ID列表
        
    Returns:
        交互状态字典
    """
    if not user_id:
        return {}
    
    # 这里应该查询用户交互表，暂时返回空字典
    # TODO: 实现用户交互表查询
    return {}

def calculate_recommendation_score(content: EducationContent, user: Optional[User] = None):
    """
    计算内容推荐分数
    
    Args:
        content: 教育内容
        user: 用户（可选）
        
    Returns:
        推荐分数
    """
    score = 0
    
    # 基础分数：浏览量和点赞数
    score += min(content.view_count * 0.1, 50)
    score += min(content.like_count * 0.5, 30)
    
    # 评分加权
    if content.avg_rating:
        score += content.avg_rating * 4
    
    # 新鲜度加权（最近发布的内容得分更高）
    days_since_publish = (datetime.now() - content.created_at).days
    if days_since_publish <= 7:
        score += 10
    elif days_since_publish <= 30:
        score += 5
    
    # 用户个性化推荐（如果有用户信息）
    if user:
        # 根据用户健康状况推荐相关内容
        if user.health_conditions and content.tags:
            for condition in user.health_conditions:
                if condition.lower() in [tag.lower() for tag in content.tags]:
                    score += 15
        
        # 根据用户饮食偏好推荐
        if user.dietary_preferences and content.tags:
            for preference in user.dietary_preferences:
                if preference.lower() in [tag.lower() for tag in content.tags]:
                    score += 10
    
    return min(score, 100)  # 最高100分

# API端点
@router.get("/list", response_model=List[EducationContentListResponse], summary="获取教育内容列表")
async def get_education_content_list(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    category: Optional[str] = Query(None, description="分类筛选"),
    content_type: Optional[str] = Query(None, description="内容类型筛选"),
    difficulty_level: Optional[str] = Query(None, description="难度级别筛选"),
    target_audience: Optional[str] = Query(None, description="目标受众筛选"),
    tags: Optional[str] = Query(None, description="标签筛选，多个标签用逗号分隔"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    sort_by: str = Query("created_at", description="排序字段: created_at, view_count, like_count, rating"),
    sort_order: str = Query("desc", description="排序方向: asc, desc"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    获取教育内容列表
    
    Args:
        skip: 跳过的记录数
        limit: 返回的记录数
        category: 分类筛选
        content_type: 内容类型筛选
        difficulty_level: 难度级别筛选
        target_audience: 目标受众筛选
        tags: 标签筛选
        search: 搜索关键词
        sort_by: 排序字段
        sort_order: 排序方向
        current_user: 当前用户（可选）
        db: 数据库会话
        
    Returns:
        教育内容列表
    """
    try:
        # 构建查询
        query = db.query(EducationContent).filter(
            EducationContent.status == "published"
        )
        
        # 应用筛选条件
        if category:
            query = query.filter(EducationContent.category == category)
        
        if content_type:
            query = query.filter(EducationContent.content_type == content_type)
        
        if difficulty_level:
            query = query.filter(EducationContent.difficulty_level == difficulty_level)
        
        if target_audience:
            query = query.filter(EducationContent.target_audience == target_audience)
        
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
            for tag in tag_list:
                query = query.filter(EducationContent.tags.contains([tag]))
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    EducationContent.title.ilike(search_term),
                    EducationContent.summary.ilike(search_term),
                    EducationContent.content.ilike(search_term)
                )
            )
        
        # 排序
        if sort_by == "view_count":
            order_field = EducationContent.view_count
        elif sort_by == "like_count":
            order_field = EducationContent.like_count
        elif sort_by == "rating":
            order_field = EducationContent.avg_rating
        else:
            order_field = EducationContent.created_at
        
        if sort_order == "asc":
            query = query.order_by(order_field.asc())
        else:
            query = query.order_by(order_field.desc())
        
        # 分页
        contents = query.offset(skip).limit(limit).all()
        
        # 获取用户交互状态
        user_interactions = {}
        if current_user:
            content_ids = [c.id for c in contents]
            user_interactions = get_user_interactions(db, current_user.id, content_ids)
        
        # 转换为响应模型
        content_list = []
        for content in contents:
            interaction = user_interactions.get(content.id, {})
            content_list.append(EducationContentListResponse(
                id=content.id,
                content_type=content.content_type,
                status=content.status,
                title=content.title,
                summary=content.summary,
                image_url=content.image_url,
                category=content.category,
                tags=content.tags or [],
                target_audience=content.target_audience,
                difficulty_level=content.difficulty_level,
                author_name=content.author_name,
                reading_time=content.reading_time,
                view_count=content.view_count,
                like_count=content.like_count,
                avg_rating=content.avg_rating,
                created_at=content.created_at,
                is_liked=interaction.get("is_liked", False),
                is_bookmarked=interaction.get("is_bookmarked", False)
            ))
        
        return content_list
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取教育内容列表失败: {str(e)}"
        )

@router.get("/stats", response_model=EducationStatsResponse, summary="获取教育内容统计")
async def get_education_stats(
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    获取教育内容统计信息
    
    Args:
        current_user: 当前用户（可选）
        db: 数据库会话
        
    Returns:
        教育内容统计信息
    """
    try:
        # 基础统计
        total_content = db.query(EducationContent).filter(
            EducationContent.status == "published"
        ).count()
        
        total_views = db.query(func.sum(EducationContent.view_count)).filter(
            EducationContent.status == "published"
        ).scalar() or 0
        
        total_likes = db.query(func.sum(EducationContent.like_count)).filter(
            EducationContent.status == "published"
        ).scalar() or 0
        
        total_bookmarks = db.query(func.sum(EducationContent.bookmark_count)).filter(
            EducationContent.status == "published"
        ).scalar() or 0
        
        # 热门分类
        category_stats = db.query(
            EducationContent.category,
            func.count(EducationContent.id).label("count"),
            func.sum(EducationContent.view_count).label("total_views")
        ).filter(
            EducationContent.status == "published"
        ).group_by(EducationContent.category).order_by(desc("total_views")).limit(5).all()
        
        popular_categories = [
            {
                "category": stat.category,
                "count": stat.count,
                "total_views": stat.total_views
            }
            for stat in category_stats
        ]
        
        # 最新内容
        recent_contents = db.query(EducationContent).filter(
            EducationContent.status == "published"
        ).order_by(EducationContent.created_at.desc()).limit(5).all()
        
        recent_content_list = []
        for content in recent_contents:
            recent_content_list.append(EducationContentListResponse(
                id=content.id,
                content_type=content.content_type,
                status=content.status,
                title=content.title,
                summary=content.summary,
                image_url=content.image_url,
                category=content.category,
                tags=content.tags or [],
                target_audience=content.target_audience,
                difficulty_level=content.difficulty_level,
                author_name=content.author_name,
                reading_time=content.reading_time,
                view_count=content.view_count,
                like_count=content.like_count,
                avg_rating=content.avg_rating,
                created_at=content.created_at
            ))
        
        # 推荐内容
        all_contents = db.query(EducationContent).filter(
            EducationContent.status == "published"
        ).all()
        
        # 计算推荐分数并排序
        content_scores = []
        for content in all_contents:
            score = calculate_recommendation_score(content, current_user)
            content_scores.append((content, score))
        
        # 按分数排序并取前5个
        content_scores.sort(key=lambda x: x[1], reverse=True)
        recommended_contents = [item[0] for item in content_scores[:5]]
        
        recommended_content_list = []
        for content in recommended_contents:
            recommended_content_list.append(EducationContentListResponse(
                id=content.id,
                content_type=content.content_type,
                status=content.status,
                title=content.title,
                summary=content.summary,
                image_url=content.image_url,
                category=content.category,
                tags=content.tags or [],
                target_audience=content.target_audience,
                difficulty_level=content.difficulty_level,
                author_name=content.author_name,
                reading_time=content.reading_time,
                view_count=content.view_count,
                like_count=content.like_count,
                avg_rating=content.avg_rating,
                created_at=content.created_at
            ))
        
        return EducationStatsResponse(
            total_content=total_content,
            total_views=total_views,
            total_likes=total_likes,
            total_bookmarks=total_bookmarks,
            popular_categories=popular_categories,
            recent_content=recent_content_list,
            recommended_content=recommended_content_list
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取教育内容统计失败: {str(e)}"
        )

@router.get("/categories", summary="获取内容分类列表")
async def get_content_categories(
    db: Session = Depends(get_db)
):
    """
    获取所有内容分类
    
    Args:
        db: 数据库会话
        
    Returns:
        分类列表
    """
    try:
        categories = db.query(EducationContent.category).filter(
            EducationContent.status == "published"
        ).distinct().all()
        
        category_list = [cat[0] for cat in categories if cat[0]]
        
        return {"categories": sorted(category_list)}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分类列表失败: {str(e)}"
        )

@router.get("/tags", summary="获取热门标签")
async def get_popular_tags(
    limit: int = Query(20, ge=1, le=50, description="返回的标签数量"),
    db: Session = Depends(get_db)
):
    """
    获取热门标签
    
    Args:
        limit: 返回的标签数量
        db: 数据库会话
        
    Returns:
        热门标签列表
    """
    try:
        # 获取所有已发布内容的标签
        contents = db.query(EducationContent.tags).filter(
            EducationContent.status == "published",
            EducationContent.tags.isnot(None)
        ).all()
        
        # 统计标签频次
        tag_counts = {}
        for content in contents:
            if content.tags:
                for tag in content.tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # 按频次排序
        popular_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        return {
            "tags": [
                {"tag": tag, "count": count}
                for tag, count in popular_tags
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取热门标签失败: {str(e)}"
        )

@router.get("/{content_id}", response_model=EducationContentResponse, summary="获取教育内容详情")
async def get_education_content_detail(
    content_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    获取教育内容详情
    
    Args:
        content_id: 内容ID
        current_user: 当前用户（可选）
        db: 数据库会话
        
    Returns:
        教育内容详情
    """
    # 查找内容
    content = db.query(EducationContent).filter(
        EducationContent.id == content_id,
        EducationContent.status == "published"
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="内容不存在或未发布"
        )
    
    # 增加浏览次数
    content.increment_view_count()
    db.commit()
    
    # 获取用户交互状态
    user_interaction = {}
    if current_user:
        user_interaction = get_user_interactions(db, current_user.id, [content.id]).get(content.id, {})
    
    return EducationContentResponse(
        id=content.id,
        content_type=content.content_type,
        status=content.status,
        title=content.title,
        summary=content.summary,
        content=content.content,
        image_url=content.image_url,
        video_url=content.video_url,
        audio_url=content.audio_url,
        category=content.category,
        tags=content.tags or [],
        target_audience=content.target_audience,
        difficulty_level=content.difficulty_level,
        author_name=content.author_name,
        author_title=content.author_title,
        reading_time=content.reading_time,
        view_count=content.view_count,
        like_count=content.like_count,
        share_count=content.share_count,
        bookmark_count=content.bookmark_count,
        avg_rating=content.avg_rating,
        rating_count=content.rating_count,
        created_at=content.created_at,
        updated_at=content.updated_at,
        is_liked=user_interaction.get("is_liked", False),
        is_bookmarked=user_interaction.get("is_bookmarked", False),
        user_rating=user_interaction.get("rating")
    )

@router.post("/{content_id}/interact", summary="内容交互")
async def interact_with_content(
    content_id: int,
    interaction: ContentInteractionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    与内容进行交互（点赞、收藏等）
    
    Args:
        content_id: 内容ID
        interaction: 交互请求
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        交互结果
    """
    try:
        # 查找内容
        content = db.query(EducationContent).filter(
            EducationContent.id == content_id,
            EducationContent.status == "published"
        ).first()
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="内容不存在或未发布"
            )
        
        # 处理交互
        if interaction.action == "like":
            content.increment_like_count()
            message = "点赞成功"
        elif interaction.action == "unlike":
            content.decrement_like_count()
            message = "取消点赞成功"
        elif interaction.action == "bookmark":
            content.increment_bookmark_count()
            message = "收藏成功"
        elif interaction.action == "unbookmark":
            content.decrement_bookmark_count()
            message = "取消收藏成功"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的交互类型"
            )
        
        # TODO: 记录用户交互到用户交互表
        
        db.commit()
        
        return {"message": message}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"交互失败: {str(e)}"
        )

@router.post("/{content_id}/share", summary="分享内容")
async def share_content(
    content_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    分享内容
    
    Args:
        content_id: 内容ID
        current_user: 当前用户（可选）
        db: 数据库会话
        
    Returns:
        分享结果
    """
    try:
        # 查找内容
        content = db.query(EducationContent).filter(
            EducationContent.id == content_id,
            EducationContent.status == "published"
        ).first()
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="内容不存在或未发布"
            )
        
        # 增加分享次数
        content.increment_share_count()
        db.commit()
        
        return {"message": "分享成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分享失败: {str(e)}"
        )

@router.post("/{content_id}/rate", summary="评价内容")
async def rate_content(
    content_id: int,
    rating_request: ContentRatingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    评价内容
    
    Args:
        content_id: 内容ID
        rating_request: 评价请求
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        评价结果
    """
    try:
        # 查找内容
        content = db.query(EducationContent).filter(
            EducationContent.id == content_id,
            EducationContent.status == "published"
        ).first()
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="内容不存在或未发布"
            )
        
        # TODO: 检查用户是否已经评价过，如果是则更新评价
        # TODO: 将评价记录到用户评价表
        
        # 更新内容评分
        content.add_rating(rating_request.rating)
        db.commit()
        
        return {"message": "评价成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"评价失败: {str(e)}"
        )