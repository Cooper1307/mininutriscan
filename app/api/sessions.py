# app/api/sessions.py
# 会话管理API路由

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from ..core.database import get_db
from ..models.user import User
from ..api.auth import get_current_user
from ..services.session_service import (
    session_service,
    create_user_session,
    get_user_session,
    validate_user_session,
    logout_user,
    logout_all_user_sessions
)

# 创建路由器
router = APIRouter()

# Pydantic模型定义
class SessionInfo(BaseModel):
    """
    会话信息模型
    """
    session_id: str
    created_at: str
    last_activity: str
    ip_address: Optional[str] = None
    is_current: bool = False

class SessionStats(BaseModel):
    """
    会话统计模型
    """
    total_sessions: int
    active_users: int
    redis_connected: bool
    timestamp: str

class CreateSessionRequest(BaseModel):
    """
    创建会话请求模型
    """
    expire_minutes: Optional[int] = None

class SessionResponse(BaseModel):
    """
    会话响应模型
    """
    session_id: str
    message: str

def get_client_ip(request: Request) -> str:
    """
    获取客户端IP地址
    
    Args:
        request: FastAPI请求对象
        
    Returns:
        客户端IP地址
    """
    # 尝试从各种头部获取真实IP
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # 回退到客户端IP
    return request.client.host if request.client else "unknown"

@router.post("/create", response_model=SessionResponse, summary="创建新会话")
async def create_session(
    request: Request,
    session_request: CreateSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    为当前用户创建新的会话
    
    Args:
        request: HTTP请求对象
        session_request: 会话创建请求
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        创建的会话信息
        
    Raises:
        HTTPException: 会话创建失败时抛出异常
    """
    try:
        # 获取客户端IP
        client_ip = get_client_ip(request)
        
        # 准备用户数据
        user_data = {
            "user_id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "nickname": current_user.nickname,
            "role": current_user.role.value if current_user.role else "user"
        }
        
        # 创建会话
        session_id = await create_user_session(
            user_id=current_user.id,
            user_data=user_data,
            ip_address=client_ip
        )
        
        return SessionResponse(
            session_id=session_id,
            message="会话创建成功"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"会话创建失败: {str(e)}"
        )

@router.get("/current", response_model=dict, summary="获取当前会话信息")
async def get_current_session(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的会话信息
    
    Args:
        request: HTTP请求对象
        current_user: 当前用户
        
    Returns:
        当前会话信息
    """
    try:
        # 从请求头中获取会话ID（如果有的话）
        session_id = request.headers.get("X-Session-ID")
        
        if session_id:
            session_data = await get_user_session(session_id)
            if session_data:
                return {
                    "session_id": session_id,
                    "user_id": session_data.get("user_id"),
                    "created_at": session_data.get("created_at"),
                    "last_activity": session_data.get("last_activity"),
                    "ip_address": session_data.get("ip_address"),
                    "is_active": session_data.get("is_active", False)
                }
        
        return {
            "message": "当前无活跃会话",
            "user_id": current_user.id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取会话信息失败: {str(e)}"
        )

@router.get("/list", response_model=List[SessionInfo], summary="获取用户所有会话")
async def list_user_sessions(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的所有活跃会话
    
    Args:
        current_user: 当前用户
        
    Returns:
        用户会话列表
    """
    try:
        sessions = await session_service.get_user_sessions(current_user.id)
        
        session_list = []
        for session in sessions:
            session_list.append(SessionInfo(
                session_id=session["session_id"],
                created_at=session["created_at"],
                last_activity=session["last_activity"],
                ip_address=session["ip_address"],
                is_current=False  # 这里可以根据实际情况判断
            ))
        
        return session_list
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取会话列表失败: {str(e)}"
        )

@router.delete("/logout/{session_id}", summary="登出指定会话")
async def logout_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    登出指定的会话
    
    Args:
        session_id: 要登出的会话ID
        current_user: 当前用户
        
    Returns:
        登出结果
        
    Raises:
        HTTPException: 会话不存在或登出失败时抛出异常
    """
    try:
        # 验证会话是否属于当前用户
        session_data = await get_user_session(session_id)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在或已过期"
            )
        
        if session_data.get("user_id") != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权限操作此会话"
            )
        
        # 登出会话
        success = await logout_user(session_id)
        if success:
            return {"message": "会话登出成功"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="会话登出失败"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登出会话失败: {str(e)}"
        )

@router.delete("/logout-all", summary="登出所有会话")
async def logout_all_sessions(
    current_user: User = Depends(get_current_user)
):
    """
    登出当前用户的所有会话
    
    Args:
        current_user: 当前用户
        
    Returns:
        登出结果
    """
    try:
        deleted_count = await logout_all_user_sessions(current_user.id)
        
        return {
            "message": f"成功登出 {deleted_count} 个会话",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登出所有会话失败: {str(e)}"
        )

@router.post("/validate/{session_id}", summary="验证会话")
async def validate_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    验证指定会话是否有效
    
    Args:
        session_id: 要验证的会话ID
        current_user: 当前用户
        
    Returns:
        验证结果
    """
    try:
        # 验证会话
        is_valid = await validate_user_session(session_id)
        
        if is_valid:
            session_data = await get_user_session(session_id)
            return {
                "valid": True,
                "message": "会话有效",
                "session_data": {
                    "user_id": session_data.get("user_id"),
                    "last_activity": session_data.get("last_activity")
                }
            }
        else:
            return {
                "valid": False,
                "message": "会话无效或已过期"
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"验证会话失败: {str(e)}"
        )

@router.get("/stats", response_model=SessionStats, summary="获取会话统计")
async def get_session_statistics(
    current_user: User = Depends(get_current_user)
):
    """
    获取会话统计信息（仅管理员可访问）
    
    Args:
        current_user: 当前用户
        
    Returns:
        会话统计信息
        
    Raises:
        HTTPException: 权限不足时抛出异常
    """
    # 检查用户权限
    if not current_user.role or current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，仅管理员可访问"
        )
    
    try:
        stats = await session_service.get_session_stats()
        
        return SessionStats(
            total_sessions=stats.get("total_sessions", 0),
            active_users=stats.get("active_users", 0),
            redis_connected=stats.get("redis_connected", False),
            timestamp=stats.get("timestamp", datetime.now().isoformat())
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取会话统计失败: {str(e)}"
        )

@router.post("/cleanup", summary="清理过期会话")
async def cleanup_expired_sessions(
    current_user: User = Depends(get_current_user)
):
    """
    清理过期的会话（仅管理员可访问）
    
    Args:
        current_user: 当前用户
        
    Returns:
        清理结果
        
    Raises:
        HTTPException: 权限不足时抛出异常
    """
    # 检查用户权限
    if not current_user.role or current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，仅管理员可访问"
        )
    
    try:
        cleaned_count = await session_service.cleanup_expired_sessions()
        
        return {
            "message": f"清理完成，共清理 {cleaned_count} 个过期会话",
            "cleaned_count": cleaned_count,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"清理过期会话失败: {str(e)}"
        )