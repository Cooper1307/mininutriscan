# app/models/volunteer.py
# 志愿者数据模型

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.core.database import Base

class VolunteerStatus(enum.Enum):
    """
    志愿者状态枚举
    """
    PENDING = "pending"      # 待审核
    ACTIVE = "active"        # 活跃
    INACTIVE = "inactive"    # 非活跃
    SUSPENDED = "suspended"  # 暂停
    RETIRED = "retired"      # 退休

class ServiceType(enum.Enum):
    """
    服务类型枚举
    """
    CONSULTATION = "consultation"    # 营养咨询
    EDUCATION = "education"          # 健康教育
    COMMUNITY = "community"          # 社区服务
    TRAINING = "training"            # 培训指导
    RESEARCH = "research"            # 调研活动
    OTHER = "other"                  # 其他

class Volunteer(Base):
    """
    志愿者数据模型
    存储志愿者的基本信息、资质和服务记录
    """
    __tablename__ = "volunteers"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, comment="志愿者ID")
    
    # 关联用户（志愿者也是用户）
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True, comment="用户ID")
    
    # 志愿者基本信息
    volunteer_id = Column(String(20), unique=True, nullable=False, index=True, comment="志愿者编号")
    real_name = Column(String(50), nullable=False, comment="真实姓名")
    id_number = Column(String(18), nullable=True, comment="身份证号")
    phone = Column(String(20), nullable=False, comment="联系电话")
    email = Column(String(100), nullable=True, comment="邮箱地址")
    
    # 地址信息
    province = Column(String(50), nullable=True, comment="省份")
    city = Column(String(50), nullable=True, comment="城市")
    district = Column(String(50), nullable=True, comment="区县")
    address = Column(String(200), nullable=True, comment="详细地址")
    
    # 专业背景
    education_level = Column(String(20), nullable=True, comment="学历水平")
    major = Column(String(100), nullable=True, comment="专业")
    work_experience = Column(Text, nullable=True, comment="工作经历")
    professional_skills = Column(JSON, nullable=True, comment="专业技能")
    
    # 资质认证
    certifications = Column(JSON, nullable=True, comment="资质证书")
    training_records = Column(JSON, nullable=True, comment="培训记录")
    qualification_level = Column(String(20), default="初级", comment="资质等级")
    
    # 志愿者状态
    status = Column(Enum(VolunteerStatus), default=VolunteerStatus.PENDING, comment="志愿者状态")
    approval_date = Column(DateTime, nullable=True, comment="审核通过时间")
    approved_by = Column(Integer, nullable=True, comment="审核人ID")
    
    # 服务能力
    service_types = Column(JSON, nullable=True, comment="服务类型")
    service_areas = Column(JSON, nullable=True, comment="服务区域")
    available_time = Column(JSON, nullable=True, comment="可服务时间")
    max_weekly_hours = Column(Integer, default=10, comment="每周最大服务小时数")
    
    # 服务统计
    total_service_hours = Column(Float, default=0.0, comment="总服务小时数")
    total_consultations = Column(Integer, default=0, comment="总咨询次数")
    total_users_helped = Column(Integer, default=0, comment="帮助用户总数")
    current_month_hours = Column(Float, default=0.0, comment="本月服务小时数")
    
    # 评价统计
    average_rating = Column(Float, nullable=True, comment="平均评分")
    total_ratings = Column(Integer, default=0, comment="评价总数")
    positive_feedback_rate = Column(Float, nullable=True, comment="好评率")
    
    # 个人简介
    bio = Column(Text, nullable=True, comment="个人简介")
    specialties = Column(JSON, nullable=True, comment="专长领域")
    languages = Column(JSON, nullable=True, comment="语言能力")
    
    # 联系偏好
    preferred_contact_method = Column(String(20), default="phone", comment="首选联系方式")
    contact_hours = Column(String(100), nullable=True, comment="可联系时间")
    
    # 激励机制
    points = Column(Integer, default=0, comment="积分")
    level = Column(String(20), default="新手", comment="等级")
    badges = Column(JSON, nullable=True, comment="徽章")
    achievements = Column(JSON, nullable=True, comment="成就")
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    last_active_at = Column(DateTime, nullable=True, comment="最后活跃时间")
    last_service_at = Column(DateTime, nullable=True, comment="最后服务时间")
    
    # 其他设置
    is_featured = Column(Boolean, default=False, comment="是否为推荐志愿者")
    is_available = Column(Boolean, default=True, comment="是否可接受服务")
    auto_accept_requests = Column(Boolean, default=False, comment="是否自动接受请求")
    
    def __repr__(self):
        return f"<Volunteer(id={self.id}, volunteer_id={self.volunteer_id}, real_name={self.real_name}, status={self.status})>"
    
    def to_dict(self, include_sensitive=False):
        """
        转换为字典格式
        
        Args:
            include_sensitive: 是否包含敏感信息
            
        Returns:
            志愿者信息字典
        """
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "volunteer_id": self.volunteer_id,
            "real_name": self.real_name,
            "status": self.status.value if self.status else None,
            "qualification_level": self.qualification_level,
            "service_types": self.service_types,
            "service_areas": self.service_areas,
            "total_service_hours": self.total_service_hours,
            "total_consultations": self.total_consultations,
            "total_users_helped": self.total_users_helped,
            "average_rating": self.average_rating,
            "total_ratings": self.total_ratings,
            "positive_feedback_rate": self.positive_feedback_rate,
            "bio": self.bio,
            "specialties": self.specialties,
            "languages": self.languages,
            "points": self.points,
            "level": self.level,
            "badges": self.badges,
            "is_featured": self.is_featured,
            "is_available": self.is_available,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_active_at": self.last_active_at.isoformat() if self.last_active_at else None
        }
        
        if include_sensitive:
            data.update({
                "phone": self.phone,
                "email": self.email,
                "id_number": self.id_number,
                "province": self.province,
                "city": self.city,
                "district": self.district,
                "address": self.address,
                "education_level": self.education_level,
                "major": self.major,
                "work_experience": self.work_experience,
                "professional_skills": self.professional_skills,
                "certifications": self.certifications,
                "training_records": self.training_records,
                "available_time": self.available_time,
                "max_weekly_hours": self.max_weekly_hours,
                "current_month_hours": self.current_month_hours,
                "preferred_contact_method": self.preferred_contact_method,
                "contact_hours": self.contact_hours,
                "achievements": self.achievements,
                "approval_date": self.approval_date.isoformat() if self.approval_date else None,
                "approved_by": self.approved_by,
                "updated_at": self.updated_at.isoformat() if self.updated_at else None,
                "last_service_at": self.last_service_at.isoformat() if self.last_service_at else None,
                "auto_accept_requests": self.auto_accept_requests
            })
        
        return data
    
    def update_status(self, status: VolunteerStatus, approved_by=None):
        """
        更新志愿者状态
        
        Args:
            status: 新状态
            approved_by: 审核人ID（如果是审核操作）
        """
        self.status = status
        self.updated_at = datetime.now()
        
        if status == VolunteerStatus.ACTIVE and not self.approval_date:
            self.approval_date = datetime.now()
            if approved_by:
                self.approved_by = approved_by
    
    def add_service_hours(self, hours: float, service_type: ServiceType = None):
        """
        添加服务小时数
        
        Args:
            hours: 服务小时数
            service_type: 服务类型
        """
        self.total_service_hours += hours
        self.current_month_hours += hours
        self.last_service_at = datetime.now()
        self.last_active_at = datetime.now()
        self.updated_at = datetime.now()
        
        # 根据服务类型增加相应统计
        if service_type == ServiceType.CONSULTATION:
            self.total_consultations += 1
    
    def add_rating(self, rating: float):
        """
        添加评分
        
        Args:
            rating: 评分(1-5)
        """
        if self.average_rating is None:
            self.average_rating = rating
            self.total_ratings = 1
        else:
            total_score = self.average_rating * self.total_ratings + rating
            self.total_ratings += 1
            self.average_rating = round(total_score / self.total_ratings, 2)
        
        # 计算好评率（4分以上为好评）
        if self.total_ratings > 0:
            # 这里简化处理，实际应该统计所有评分
            self.positive_feedback_rate = round(
                (self.average_rating - 1) / 4 * 100, 1
            )
        
        self.updated_at = datetime.now()
    
    def add_points(self, points: int, reason: str = None):
        """
        添加积分
        
        Args:
            points: 积分数
            reason: 获得积分的原因
        """
        self.points += points
        self.updated_at = datetime.now()
        
        # 检查是否需要升级
        self._check_level_upgrade()
    
    def _check_level_upgrade(self):
        """
        检查等级升级
        """
        level_thresholds = {
            "新手": 0,
            "初级": 100,
            "中级": 500,
            "高级": 1500,
            "专家": 3000,
            "大师": 6000
        }
        
        for level, threshold in reversed(level_thresholds.items()):
            if self.points >= threshold:
                if self.level != level:
                    self.level = level
                    # 可以在这里添加升级奖励逻辑
                break
    
    def add_badge(self, badge_name: str, badge_description: str = None):
        """
        添加徽章
        
        Args:
            badge_name: 徽章名称
            badge_description: 徽章描述
        """
        if self.badges is None:
            self.badges = []
        
        badge = {
            "name": badge_name,
            "description": badge_description,
            "earned_at": datetime.now().isoformat()
        }
        
        # 检查是否已有该徽章
        if not any(b["name"] == badge_name for b in self.badges):
            self.badges.append(badge)
            self.updated_at = datetime.now()
    
    def is_available_now(self):
        """
        检查当前是否可提供服务
        
        Returns:
            是否可提供服务
        """
        if not self.is_available or self.status != VolunteerStatus.ACTIVE:
            return False
        
        # 检查本月服务时间是否已达上限
        if self.current_month_hours >= self.max_weekly_hours * 4:
            return False
        
        return True
    
    def get_service_capacity(self):
        """
        获取服务容量信息
        
        Returns:
            服务容量字典
        """
        max_monthly_hours = self.max_weekly_hours * 4
        remaining_hours = max(0, max_monthly_hours - self.current_month_hours)
        
        return {
            "max_weekly_hours": self.max_weekly_hours,
            "max_monthly_hours": max_monthly_hours,
            "current_month_hours": self.current_month_hours,
            "remaining_hours": remaining_hours,
            "capacity_percentage": round(
                (max_monthly_hours - remaining_hours) / max_monthly_hours * 100, 1
            ) if max_monthly_hours > 0 else 0
        }
    
    def reset_monthly_hours(self):
        """
        重置月度服务小时数（每月初调用）
        """
        self.current_month_hours = 0.0
        self.updated_at = datetime.now()
    
    def get_performance_summary(self):
        """
        获取绩效摘要
        
        Returns:
            绩效摘要字典
        """
        return {
            "total_service_hours": self.total_service_hours,
            "total_consultations": self.total_consultations,
            "total_users_helped": self.total_users_helped,
            "average_rating": self.average_rating,
            "positive_feedback_rate": self.positive_feedback_rate,
            "points": self.points,
            "level": self.level,
            "badge_count": len(self.badges) if self.badges else 0,
            "service_capacity": self.get_service_capacity()
        }
    
    def can_provide_service(self, service_type: ServiceType):
        """
        检查是否能提供特定类型的服务
        
        Args:
            service_type: 服务类型
            
        Returns:
            是否能提供该服务
        """
        if not self.is_available_now():
            return False
        
        if not self.service_types:
            return False
        
        return service_type.value in self.service_types
    
    def update_last_active(self):
        """
        更新最后活跃时间
        """
        self.last_active_at = datetime.now()
        self.updated_at = datetime.now()