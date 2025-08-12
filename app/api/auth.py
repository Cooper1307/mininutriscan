# app/api/auth.py
# 用户认证API路由

from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import jwt
from datetime import datetime, timedelta

from ..core.config import get_settings
from ..core.database import get_db
from ..models.user import User
from ..services.wechat_service import WeChatService

# 创建路由器
router = APIRouter()
security = HTTPBearer()
settings = get_settings()

# Pydantic模型定义
class WeChatLoginRequest(BaseModel):
    """
    微信登录请求模型
    """
    code: str  # 微信授权码
    encrypted_data: Optional[str] = None  # 加密的用户信息
    iv: Optional[str] = None  # 初始向量
    signature: Optional[str] = None  # 数据签名

class LoginResponse(BaseModel):
    """
    登录响应模型
    """
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_info: dict
    is_new_user: bool

class TokenRefreshRequest(BaseModel):
    """
    令牌刷新请求模型
    """
    refresh_token: str

class UserInfoUpdateRequest(BaseModel):
    """
    用户信息更新请求模型
    """
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    gender: Optional[int] = None
    city: Optional[str] = None
    province: Optional[str] = None
    country: Optional[str] = None

# JWT工具函数
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    创建访问令牌
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量
        
    Returns:
        JWT令牌字符串
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """
    创建刷新令牌
    
    Args:
        data: 要编码的数据
        
    Returns:
        JWT刷新令牌字符串
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    验证JWT令牌
    
    Args:
        credentials: HTTP认证凭据
        
    Returns:
        解码后的令牌数据
        
    Raises:
        HTTPException: 令牌无效时抛出异常
    """
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证凭据",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(db: Session = Depends(get_db), token_data: dict = Depends(verify_token)):
    """
    获取当前用户
    
    Args:
        db: 数据库会话
        token_data: 令牌数据
        
    Returns:
        当前用户对象
        
    Raises:
        HTTPException: 用户不存在时抛出异常
    """
    user_id = token_data.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )
    return user

def get_current_user_optional(db: Session = Depends(get_db), authorization: str = Header(None)):
    """
    获取当前用户（可选）
    
    如果提供了有效的认证令牌，返回用户对象；否则返回None
    用于不强制要求登录的接口
    
    Args:
        db: 数据库会话
        authorization: 认证头
        
    Returns:
        当前用户对象或None
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
        
        user = db.query(User).filter(User.id == user_id).first()
        return user
    except (JWTError, IndexError):
        return None

# API端点
@router.post("/wechat/login", response_model=LoginResponse, summary="微信小程序登录")
async def wechat_login(
    login_data: WeChatLoginRequest,
    db: Session = Depends(get_db)
):
    """
    微信小程序登录接口
    
    Args:
        login_data: 微信登录数据
        db: 数据库会话
        
    Returns:
        登录响应，包含访问令牌和用户信息
        
    Raises:
        HTTPException: 登录失败时抛出异常
    """
    try:
        # 初始化微信服务
        wechat_service = WeChatService()
        
        # 通过code获取session_key和openid
        session_info = await wechat_service.code2session(login_data.code)
        if not session_info or "openid" not in session_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="微信登录失败，无效的授权码"
            )
        
        openid = session_info["openid"]
        session_key = session_info.get("session_key")
        unionid = session_info.get("unionid")
        
        # 查找或创建用户
        user = db.query(User).filter(User.wechat_openid == openid).first()
        is_new_user = False
        
        if not user:
            # 创建新用户
            user = User(
                wechat_openid=openid,
                wechat_unionid=unionid,
                nickname=f"用户{openid[-6:]}",  # 默认昵称
                status="active"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            is_new_user = True
        else:
            # 更新登录信息
            user.update_login()
            if unionid and not user.wechat_unionid:
                user.wechat_unionid = unionid
            db.commit()
        
        # 解密用户信息（如果提供）
        if login_data.encrypted_data and login_data.iv and session_key:
            try:
                user_info = wechat_service.decrypt_user_info(
                    login_data.encrypted_data,
                    session_key,
                    login_data.iv
                )
                
                # 更新用户信息
                if user_info:
                    user.nickname = user_info.get("nickName", user.nickname)
                    user.avatar_url = user_info.get("avatarUrl", user.avatar_url)
                    user.gender = user_info.get("gender", user.gender)
                    user.city = user_info.get("city", user.city)
                    user.province = user_info.get("province", user.province)
                    user.country = user_info.get("country", user.country)
                    db.commit()
            except Exception as e:
                # 解密失败不影响登录，只记录日志
                print(f"用户信息解密失败: {e}")
        
        # 生成JWT令牌
        access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "openid": openid},
            expires_delta=access_token_expires
        )
        
        refresh_token = create_refresh_token(
            data={"sub": str(user.id), "type": "refresh"}
        )
        
        return LoginResponse(
            access_token=access_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_info=user.to_dict(),
            is_new_user=is_new_user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录过程中发生错误: {str(e)}"
        )

@router.post("/refresh", response_model=dict, summary="刷新访问令牌")
async def refresh_token(
    refresh_data: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    """
    刷新访问令牌
    
    Args:
        refresh_data: 刷新令牌数据
        db: 数据库会话
        
    Returns:
        新的访问令牌
        
    Raises:
        HTTPException: 刷新失败时抛出异常
    """
    try:
        # 验证刷新令牌
        payload = jwt.decode(
            refresh_data.refresh_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        user_id = payload.get("sub")
        token_type = payload.get("type")
        
        if not user_id or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的刷新令牌"
            )
        
        # 验证用户存在
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在"
            )
        
        # 生成新的访问令牌
        access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = create_access_token(
            data={"sub": user_id, "openid": user.wechat_openid},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"令牌刷新失败: {str(e)}"
        )

@router.get("/me", response_model=dict, summary="获取当前用户信息")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户信息
    
    Args:
        current_user: 当前用户
        
    Returns:
        用户信息字典
    """
    return current_user.to_dict()

@router.put("/me", response_model=dict, summary="更新当前用户信息")
async def update_current_user_info(
    user_update: UserInfoUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新当前用户信息
    
    Args:
        user_update: 用户更新数据
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        更新后的用户信息
    """
    try:
        # 更新用户信息
        update_data = user_update.dict(exclude_unset=True)
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
            detail=f"用户信息更新失败: {str(e)}"
        )

@router.post("/logout", summary="用户登出")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    用户登出
    
    Args:
        current_user: 当前用户
        
    Returns:
        登出成功消息
        
    Note:
        由于JWT是无状态的，实际的登出需要在客户端删除令牌
        这里主要用于记录登出日志或执行其他清理操作
    """
    return {"message": "登出成功"}

@router.get("/check", summary="检查令牌有效性")
async def check_token(
    current_user: User = Depends(get_current_user)
):
    """
    检查令牌有效性
    
    Args:
        current_user: 当前用户
        
    Returns:
        令牌有效性信息
    """
    return {
        "valid": True,
        "user_id": current_user.id,
        "message": "令牌有效"
    }