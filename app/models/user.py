# app/models/user.py
# 用户数据模型

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    """
    用户角色枚举
    """
    USER = "user"          # 普通用户
    VOLUNTEER = "volunteer" # 志愿者
    ADMIN = "admin"        # 管理员

class UserStatus(enum.Enum):
    """
    用户状态枚举
    """
    ACTIVE = "active"      # 活跃
    INACTIVE = "inactive"  # 非活跃
    BANNED = "banned"      # 被禁用

class User(Base):
    """
    用户数据模型
    存储微信小程序用户的基本信息和系统相关数据
    """
    __tablename__ = "users"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, comment="用户ID")
    
    # 微信相关字段
    openid = Column(String(64), unique=True, index=True, nullable=False, comment="微信OpenID")
    unionid = Column(String(64), unique=True, index=True, nullable=True, comment="微信UnionID")
    session_key = Column(String(64), nullable=True, comment="微信会话密钥")
    
    # 用户基本信息
    nickname = Column(String(100), nullable=True, comment="用户昵称")
    avatar_url = Column(String(500), nullable=True, comment="头像URL")
    gender = Column(Integer, default=0, comment="性别：0-未知，1-男，2-女")
    country = Column(String(50), nullable=True, comment="国家")
    province = Column(String(50), nullable=True, comment="省份")
    city = Column(String(50), nullable=True, comment="城市")
    language = Column(String(20), default="zh_CN", comment="语言")
    
    # 系统字段
    role = Column(Enum(UserRole), default=UserRole.USER, comment="用户角色")
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, comment="用户状态")
    
    # 个人健康信息（可选）
    age = Column(Integer, nullable=True, comment="年龄")
    height = Column(Integer, nullable=True, comment="身高(cm)")
    weight = Column(Integer, nullable=True, comment="体重(kg)")
    health_conditions = Column(Text, nullable=True, comment="健康状况描述")
    dietary_preferences = Column(Text, nullable=True, comment="饮食偏好")
    allergies = Column(Text, nullable=True, comment="过敏信息")
    
    # 使用统计
    scan_count = Column(Integer, default=0, comment="扫描次数")
    last_scan_time = Column(DateTime, nullable=True, comment="最后扫描时间")
    total_reports = Column(Integer, default=0, comment="生成报告总数")
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    last_login_at = Column(DateTime, nullable=True, comment="最后登录时间")
    
    # 其他设置
    notification_enabled = Column(Boolean, default=True, comment="是否启用通知")
    privacy_agreement = Column(Boolean, default=False, comment="是否同意隐私协议")
    terms_agreement = Column(Boolean, default=False, comment="是否同意使用条款")
    
    def __repr__(self):
        return f"<User(id={self.id}, openid={self.openid}, nickname={self.nickname})>"
    
    def to_dict(self, include_sensitive=False):
        """
        转换为字典格式
        
        Args:
            include_sensitive: 是否包含敏感信息
            
        Returns:
            用户信息字典
        """
        data = {
            "id": self.id,
            "nickname": self.nickname,
            "avatar_url": self.avatar_url,
            "gender": self.gender,
            "country": self.country,
            "province": self.province,
            "city": self.city,
            "language": self.language,
            "role": self.role.value if self.role else None,
            "status": self.status.value if self.status else None,
            "age": self.age,
            "height": self.height,
            "weight": self.weight,
            "health_conditions": self.health_conditions,
            "dietary_preferences": self.dietary_preferences,
            "allergies": self.allergies,
            "scan_count": self.scan_count,
            "last_scan_time": self.last_scan_time.isoformat() if self.last_scan_time else None,
            "total_reports": self.total_reports,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "notification_enabled": self.notification_enabled,
            "privacy_agreement": self.privacy_agreement,
            "terms_agreement": self.terms_agreement
        }
        
        # 包含敏感信息
        if include_sensitive:
            data.update({
                "openid": self.openid,
                "unionid": self.unionid,
                "session_key": self.session_key
            })
        
        return data
    
    def update_login_info(self, session_key=None):
        """
        更新登录信息
        
        Args:
            session_key: 新的会话密钥
        """
        self.last_login_at = datetime.now()
        if session_key:
            self.session_key = session_key
    
    def increment_scan_count(self):
        """
        增加扫描次数
        """
        self.scan_count += 1
        self.last_scan_time = datetime.now()
    
    def increment_report_count(self):
        """
        增加报告数量
        """
        self.total_reports += 1
    
    def is_active(self):
        """
        检查用户是否活跃
        
        Returns:
            用户活跃状态
        """
        return self.status == UserStatus.ACTIVE
    
    def is_volunteer(self):
        """
        检查是否为志愿者
        
        Returns:
            是否为志愿者
        """
        return self.role == UserRole.VOLUNTEER
    
    def is_admin(self):
        """
        检查是否为管理员
        
        Returns:
            是否为管理员
        """
        return self.role == UserRole.ADMIN
    
    def calculate_bmi(self):
        """
        计算BMI指数
        
        Returns:
            BMI值，如果身高体重不完整则返回None
        """
        if self.height and self.weight and self.height > 0:
            height_m = self.height / 100  # 转换为米
            return round(self.weight / (height_m ** 2), 2)
        return None
    
    def get_bmi_category(self):
        """
        获取BMI分类
        
        Returns:
            BMI分类字符串
        """
        bmi = self.calculate_bmi()
        if bmi is None:
            return "未知"
        
        if bmi < 18.5:
            return "偏瘦"
        elif bmi < 24:
            return "正常"
        elif bmi < 28:
            return "偏胖"
        else:
            return "肥胖"