# app/api/users.py
# 用户管理API路由

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date

from ..core.database import get_db
from ..models.user import User
from ..api.auth import get_current_user

# 创建路由器
router = APIRouter()

# Pydantic模型定义
class HealthInfoUpdate(BaseModel):
    """
    健康信息更新模型
    """
    age: Optional[int] = Field(None, ge=1, le=120, description="年龄")
    height: Optional[float] = Field(None, ge=50, le=250, description="身高(cm)")
    weight: Optional[float] = Field(None, ge=20, le=300, description="体重(kg)")
    health_conditions: Optional[List[str]] = Field(None, description="健康状况列表")
    dietary_preferences: Optional[List[str]] = Field(None, description="饮食偏好")
    allergies: Optional[List[str]] = Field(None, description="过敏信息")

class UserProfileUpdate(BaseModel):
    """
    用户档案更新模型
    """
    nickname: Optional[str] = Field(None, min_length=1, max_length=50, description="昵称")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    gender: Optional[int] = Field(None, ge=0, le=2, description="性别(0:未知,1:男,2:女)")
    city: Optional[str] = Field(None, max_length=50, description="城市")
    province: Optional[str] = Field(None, max_length=50, description="省份")
    country: Optional[str] = Field(None, max_length=50, description="国家")

class UserStatsResponse(BaseModel):
    """
    用户统计响应模型
    """
    total_scans: int
    total_reports: int
    days_active: int
    avg_scans_per_day: float
    last_scan_date: Optional[datetime]
    health_score: Optional[float]
    bmi: Optional[float]
    bmi_category: Optional[str]

class UserListResponse(BaseModel):
    """
    用户列表响应模型
    """
    id: int
    nickname: str
    avatar_url: Optional[str]
    role: str
    status: str
    total_scans: int
    total_reports: int
    created_at: datetime
    last_login_at: Optional[datetime]

# API端点
@router.get("/profile", response_model=dict, summary="获取用户详细档案")
async def get_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的详细档案信息
    
    Args:
        current_user: 当前用户
        
    Returns:
        用户详细档案信息
    """
    profile = current_user.to_dict()
    
    # 添加计算字段
    profile["bmi"] = current_user.calculate_bmi()
    profile["bmi_category"] = current_user.get_bmi_category()
    profile["account_age_days"] = (datetime.now() - current_user.created_at).days
    
    return profile

@router.put("/profile", response_model=dict, summary="更新用户档案")
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新用户档案信息
    
    Args:
        profile_update: 档案更新数据
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        更新后的用户档案
    """
    try:
        # 更新档案信息
        update_data = profile_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(current_user, field):
                setattr(current_user, field, value)
        
        current_user.updated_at = datetime.now()
        db.commit()
        db.refresh(current_user)
        
        return current_user.to_dict()
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"档案更新失败: {str(e)}"
        )

@router.put("/health-info", response_model=dict, summary="更新健康信息")
async def update_health_info(
    health_update: HealthInfoUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新用户健康信息
    
    Args:
        health_update: 健康信息更新数据
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        更新后的健康信息
    """
    try:
        # 更新健康信息
        update_data = health_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(current_user, field):
                setattr(current_user, field, value)
        
        current_user.updated_at = datetime.now()
        db.commit()
        db.refresh(current_user)
        
        # 返回健康相关信息
        health_info = {
            "age": current_user.age,
            "height": current_user.height,
            "weight": current_user.weight,
            "health_conditions": current_user.health_conditions,
            "dietary_preferences": current_user.dietary_preferences,
            "allergies": current_user.allergies,
            "bmi": current_user.calculate_bmi(),
            "bmi_category": current_user.get_bmi_category(),
            "updated_at": current_user.updated_at
        }
        
        return health_info
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"健康信息更新失败: {str(e)}"
        )

@router.get("/stats", response_model=UserStatsResponse, summary="获取用户统计信息")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户统计信息
    
    Args:
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        用户统计信息
    """
    try:
        # 计算活跃天数
        days_active = (datetime.now() - current_user.created_at).days + 1
        
        # 计算平均每日扫描次数
        avg_scans_per_day = current_user.total_scans / max(1, days_active)
        
        # 获取最后扫描日期（这里需要从detection表查询，暂时使用last_login_at）
        last_scan_date = current_user.last_login_at
        
        # 计算健康评分（简化版本）
        health_score = None
        if current_user.age and current_user.height and current_user.weight:
            bmi = current_user.calculate_bmi()
            if bmi:
                # 简化的健康评分计算
                if 18.5 <= bmi <= 24.9:
                    health_score = 85.0
                elif 25 <= bmi <= 29.9:
                    health_score = 70.0
                elif bmi < 18.5:
                    health_score = 60.0
                else:
                    health_score = 50.0
                
                # 根据年龄调整
                if current_user.age:
                    if 20 <= current_user.age <= 40:
                        health_score += 10
                    elif 41 <= current_user.age <= 60:
                        health_score += 5
        
        return UserStatsResponse(
            total_scans=current_user.total_scans,
            total_reports=current_user.total_reports,
            days_active=days_active,
            avg_scans_per_day=round(avg_scans_per_day, 2),
            last_scan_date=last_scan_date,
            health_score=health_score,
            bmi=current_user.calculate_bmi(),
            bmi_category=current_user.get_bmi_category()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}"
        )

@router.delete("/account", summary="删除用户账户")
async def delete_user_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除用户账户（软删除）
    
    Args:
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        删除确认信息
    """
    try:
        # 软删除：更新状态为deleted
        current_user.status = "deleted"
        current_user.updated_at = datetime.now()
        
        # 清除敏感信息
        current_user.nickname = f"已删除用户{current_user.id}"
        current_user.avatar_url = None
        current_user.city = None
        current_user.province = None
        current_user.country = None
        
        db.commit()
        
        return {"message": "账户删除成功"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"账户删除失败: {str(e)}"
        )

@router.post("/deactivate", summary="停用用户账户")
async def deactivate_user_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    停用用户账户
    
    Args:
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        停用确认信息
    """
    try:
        current_user.status = "inactive"
        current_user.updated_at = datetime.now()
        db.commit()
        
        return {"message": "账户已停用"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"账户停用失败: {str(e)}"
        )

@router.post("/reactivate", summary="重新激活用户账户")
async def reactivate_user_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    重新激活用户账户
    
    Args:
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        激活确认信息
    """
    try:
        current_user.status = "active"
        current_user.updated_at = datetime.now()
        db.commit()
        
        return {"message": "账户已重新激活"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"账户激活失败: {str(e)}"
        )

# 管理员专用接口
@router.get("/list", response_model=List[UserListResponse], summary="获取用户列表（管理员）")
async def get_users_list(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    role: Optional[str] = Query(None, description="角色筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户列表（仅管理员可访问）
    
    Args:
        skip: 跳过的记录数
        limit: 返回的记录数
        role: 角色筛选
        status: 状态筛选
        search: 搜索关键词
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        用户列表
        
    Raises:
        HTTPException: 权限不足时抛出异常
    """
    # 检查管理员权限
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，仅管理员可访问"
        )
    
    try:
        # 构建查询
        query = db.query(User)
        
        # 应用筛选条件
        if role:
            query = query.filter(User.role == role)
        
        if status:
            query = query.filter(User.status == status)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    User.nickname.ilike(search_pattern),
                    User.wechat_openid.ilike(search_pattern)
                )
            )
        
        # 排序和分页
        users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
        
        # 转换为响应模型
        user_list = []
        for user in users:
            user_list.append(UserListResponse(
                id=user.id,
                nickname=user.nickname,
                avatar_url=user.avatar_url,
                role=user.role,
                status=user.status,
                total_scans=user.total_scans,
                total_reports=user.total_reports,
                created_at=user.created_at,
                last_login_at=user.last_login_at
            ))
        
        return user_list
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户列表失败: {str(e)}"
        )

@router.get("/{user_id}", response_model=dict, summary="获取指定用户信息（管理员）")
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取指定用户信息（仅管理员可访问）
    
    Args:
        user_id: 用户ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        指定用户信息
        
    Raises:
        HTTPException: 权限不足或用户不存在时抛出异常
    """
    # 检查管理员权限
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，仅管理员可访问"
        )
    
    # 查找用户
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return user.to_dict()

@router.put("/{user_id}/role", summary="更新用户角色（管理员）")
async def update_user_role(
    user_id: int,
    new_role: str = Query(..., description="新角色"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新用户角色（仅管理员可访问）
    
    Args:
        user_id: 用户ID
        new_role: 新角色
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        更新确认信息
        
    Raises:
        HTTPException: 权限不足或用户不存在时抛出异常
    """
    # 检查管理员权限
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，仅管理员可访问"
        )
    
    # 验证角色
    valid_roles = ["user", "volunteer", "admin"]
    if new_role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的角色，有效角色: {valid_roles}"
        )
    
    try:
        # 查找用户
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 更新角色
        old_role = user.role
        user.role = new_role
        user.updated_at = datetime.now()
        db.commit()
        
        return {
            "message": f"用户角色已从 {old_role} 更新为 {new_role}",
            "user_id": user_id,
            "old_role": old_role,
            "new_role": new_role
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"角色更新失败: {str(e)}"
        )