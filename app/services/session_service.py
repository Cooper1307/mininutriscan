# app/services/session_service.py
# 会话管理服务 - 处理用户会话的创建、存储、验证和清理

import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status
import redis
from ..core.database import redis_client
from ..core.config import settings
import logging

# 配置日志
logger = logging.getLogger(__name__)

class SessionService:
    """
    会话管理服务类
    负责用户会话的完整生命周期管理
    """
    
    def __init__(self):
        """
        初始化会话服务
        """
        self.redis_client = redis_client
        self.session_prefix = "session:"
        self.user_session_prefix = "user_sessions:"
        # 默认会话过期时间（秒）
        self.default_expire_time = getattr(settings, 'SESSION_EXPIRE_MINUTES', 60) * 60
        
    def generate_session_id(self, user_id: int, ip_address: str = None) -> str:
        """
        生成唯一的会话ID
        
        Args:
            user_id: 用户ID
            ip_address: 用户IP地址
            
        Returns:
            生成的会话ID
        """
        timestamp = str(time.time())
        random_str = str(hash(f"{user_id}_{timestamp}_{ip_address or ''}"))
        session_data = f"user_{user_id}_{timestamp}_{random_str}"
        return hashlib.md5(session_data.encode()).hexdigest()
    
    async def create_session(self, user_id: int, user_data: Dict[str, Any], 
                           ip_address: str = None, expire_minutes: int = None) -> str:
        """
        创建新的用户会话
        
        Args:
            user_id: 用户ID
            user_data: 用户数据
            ip_address: 用户IP地址
            expire_minutes: 会话过期时间（分钟）
            
        Returns:
            会话ID
            
        Raises:
            HTTPException: 会话创建失败时抛出异常
        """
        try:
            # 生成会话ID
            session_id = self.generate_session_id(user_id, ip_address)
            
            # 准备会话数据
            session_data = {
                "user_id": user_id,
                "user_data": user_data,
                "created_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "ip_address": ip_address,
                "is_active": True
            }
            
            # 计算过期时间
            expire_time = (expire_minutes or (self.default_expire_time // 60)) * 60
            
            # 存储会话数据到Redis
            session_key = f"{self.session_prefix}{session_id}"
            self.redis_client.setex(
                session_key, 
                expire_time, 
                json.dumps(session_data, ensure_ascii=False)
            )
            
            # 将会话ID添加到用户会话列表
            user_sessions_key = f"{self.user_session_prefix}{user_id}"
            self.redis_client.sadd(user_sessions_key, session_id)
            self.redis_client.expire(user_sessions_key, expire_time)
            
            logger.info(f"会话创建成功: 用户ID={user_id}, 会话ID={session_id}")
            return session_id
            
        except redis.RedisError as e:
            logger.error(f"Redis错误 - 会话创建失败: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="会话创建失败，请稍后重试"
            )
        except Exception as e:
            logger.error(f"会话创建失败: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="会话创建失败"
            )
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取会话数据
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话数据字典，如果会话不存在或已过期则返回None
        """
        try:
            session_key = f"{self.session_prefix}{session_id}"
            session_data = self.redis_client.get(session_key)
            
            if session_data:
                # 处理Redis返回的数据类型（可能是bytes或str）
                if isinstance(session_data, bytes):
                    data = json.loads(session_data.decode('utf-8'))
                else:
                    data = json.loads(session_data)
                # 更新最后活动时间
                data["last_activity"] = datetime.now().isoformat()
                self.redis_client.setex(
                    session_key, 
                    self.default_expire_time, 
                    json.dumps(data, ensure_ascii=False)
                )
                return data
            return None
            
        except (redis.RedisError, json.JSONDecodeError) as e:
            logger.error(f"获取会话失败: {e}")
            return None
    
    async def validate_session(self, session_id: str) -> bool:
        """
        验证会话是否有效
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话是否有效
        """
        session_data = await self.get_session(session_id)
        return session_data is not None and session_data.get("is_active", False)
    
    async def update_session(self, session_id: str, update_data: Dict[str, Any]) -> bool:
        """
        更新会话数据
        
        Args:
            session_id: 会话ID
            update_data: 要更新的数据
            
        Returns:
            更新是否成功
        """
        try:
            session_data = await self.get_session(session_id)
            if not session_data:
                return False
            
            # 更新数据
            session_data.update(update_data)
            session_data["last_activity"] = datetime.now().isoformat()
            
            # 保存更新后的数据
            session_key = f"{self.session_prefix}{session_id}"
            self.redis_client.setex(
                session_key, 
                self.default_expire_time, 
                json.dumps(session_data, ensure_ascii=False)
            )
            
            return True
            
        except Exception as e:
            logger.error(f"更新会话失败: {e}")
            return False
    
    async def delete_session(self, session_id: str) -> bool:
        """
        删除会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            删除是否成功
        """
        try:
            # 获取会话数据以获取用户ID
            session_data = await self.get_session(session_id)
            
            # 删除会话数据
            session_key = f"{self.session_prefix}{session_id}"
            result = self.redis_client.delete(session_key)
            
            # 从用户会话列表中移除
            if session_data and "user_id" in session_data:
                user_sessions_key = f"{self.user_session_prefix}{session_data['user_id']}"
                self.redis_client.srem(user_sessions_key, session_id)
            
            logger.info(f"会话删除: 会话ID={session_id}")
            return result > 0
            
        except Exception as e:
            logger.error(f"删除会话失败: {e}")
            return False
    
    async def delete_user_sessions(self, user_id: int) -> int:
        """
        删除用户的所有会话
        
        Args:
            user_id: 用户ID
            
        Returns:
            删除的会话数量
        """
        try:
            user_sessions_key = f"{self.user_session_prefix}{user_id}"
            session_ids = self.redis_client.smembers(user_sessions_key)
            
            deleted_count = 0
            for session_id in session_ids:
                session_key = f"{self.session_prefix}{session_id.decode('utf-8')}"
                if self.redis_client.delete(session_key):
                    deleted_count += 1
            
            # 删除用户会话列表
            self.redis_client.delete(user_sessions_key)
            
            logger.info(f"用户会话清理: 用户ID={user_id}, 删除数量={deleted_count}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"删除用户会话失败: {e}")
            return 0
    
    async def get_user_sessions(self, user_id: int) -> List[Dict[str, Any]]:
        """
        获取用户的所有活跃会话
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户会话列表
        """
        try:
            user_sessions_key = f"{self.user_session_prefix}{user_id}"
            session_ids = self.redis_client.smembers(user_sessions_key)
            
            sessions = []
            for session_id in session_ids:
                # 处理Redis返回的数据类型（可能是bytes或str）
                if isinstance(session_id, bytes):
                    session_id_str = session_id.decode('utf-8')
                else:
                    session_id_str = session_id
                    
                session_data = await self.get_session(session_id_str)
                if session_data:
                    sessions.append({
                        "session_id": session_id_str,
                        "created_at": session_data.get("created_at"),
                        "last_activity": session_data.get("last_activity"),
                        "ip_address": session_data.get("ip_address")
                    })
            
            return sessions
            
        except Exception as e:
            logger.error(f"获取用户会话失败: {e}")
            return []
    
    async def cleanup_expired_sessions(self) -> int:
        """
        清理过期的会话
        
        Returns:
            清理的会话数量
        """
        try:
            # Redis的过期机制会自动清理过期的键
            # 这里主要是清理用户会话列表中的无效引用
            
            # 获取所有用户会话键
            pattern = f"{self.user_session_prefix}*"
            user_session_keys = self.redis_client.keys(pattern)
            
            cleaned_count = 0
            for user_sessions_key in user_session_keys:
                session_ids = self.redis_client.smembers(user_sessions_key)
                
                for session_id in session_ids:
                    session_key = f"{self.session_prefix}{session_id.decode('utf-8')}"
                    if not self.redis_client.exists(session_key):
                        # 会话已过期，从用户会话列表中移除
                        self.redis_client.srem(user_sessions_key, session_id)
                        cleaned_count += 1
            
            logger.info(f"会话清理完成: 清理数量={cleaned_count}")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"会话清理失败: {e}")
            return 0
    
    async def get_session_stats(self) -> Dict[str, Any]:
        """
        获取会话统计信息
        
        Returns:
            会话统计数据
        """
        try:
            # 获取所有会话键
            session_pattern = f"{self.session_prefix}*"
            session_keys = self.redis_client.keys(session_pattern)
            
            # 获取所有用户会话键
            user_session_pattern = f"{self.user_session_prefix}*"
            user_session_keys = self.redis_client.keys(user_session_pattern)
            
            return {
                "total_sessions": len(session_keys),
                "active_users": len(user_session_keys),
                "redis_connected": self.redis_client.ping(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取会话统计失败: {e}")
            return {
                "total_sessions": 0,
                "active_users": 0,
                "redis_connected": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# 创建全局会话服务实例
session_service = SessionService()

# 便捷函数
async def create_user_session(user_id: int, user_data: Dict[str, Any], 
                            ip_address: str = None) -> str:
    """
    创建用户会话的便捷函数
    
    Args:
        user_id: 用户ID
        user_data: 用户数据
        ip_address: 用户IP地址
        
    Returns:
        会话ID
    """
    return await session_service.create_session(user_id, user_data, ip_address)

async def get_user_session(session_id: str) -> Optional[Dict[str, Any]]:
    """
    获取用户会话的便捷函数
    
    Args:
        session_id: 会话ID
        
    Returns:
        会话数据
    """
    return await session_service.get_session(session_id)

async def validate_user_session(session_id: str) -> bool:
    """
    验证用户会话的便捷函数
    
    Args:
        session_id: 会话ID
        
    Returns:
        会话是否有效
    """
    return await session_service.validate_session(session_id)

async def logout_user(session_id: str) -> bool:
    """
    用户登出的便捷函数
    
    Args:
        session_id: 会话ID
        
    Returns:
        登出是否成功
    """
    return await session_service.delete_session(session_id)

async def logout_all_user_sessions(user_id: int) -> int:
    """
    用户全部登出的便捷函数
    
    Args:
        user_id: 用户ID
        
    Returns:
        删除的会话数量
    """
    return await session_service.delete_user_sessions(user_id)