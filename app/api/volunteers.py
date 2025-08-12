# app/api/volunteers.py
# 志愿者API路由

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import json

from ..core.database import get_db
from ..models.user import User
from ..models.volunteer import Volunteer
from ..api.auth import get_current_user

# 创建路由器
router = APIRouter()

# Pydantic模型定义
class VolunteerApplicationRequest(BaseModel):
    """
    志愿者申请请求模型
    """
    real_name: str = Field(..., description="真实姓名")
    phone: str = Field(..., description="联系电话")
    email: Optional[str] = Field(None, description="邮箱地址")
    education: str = Field(..., description="学历")
    profession: str = Field(..., description="职业")
    work_unit: Optional[str] = Field(None, description="工作单位")
    specialties: List[str] = Field(..., description="专业特长")
    certifications: List[str] = Field(default_factory=list, description="相关证书")
    experience: Optional[str] = Field(None, description="相关经验")
    motivation: str = Field(..., description="申请动机")
    available_time: List[str] = Field(..., description="可服务时间")
    service_areas: List[str] = Field(..., description="服务领域")
    introduction: Optional[str] = Field(None, description="个人介绍")

class VolunteerResponse(BaseModel):
    """
    志愿者响应模型
    """
    id: int
    user_id: int
    status: str
    real_name: str
    phone: str
    email: Optional[str]
    education: str
    profession: str
    work_unit: Optional[str]
    specialties: List[str]
    certifications: List[str]
    experience: Optional[str]
    service_areas: List[str]
    available_time: List[str]
    total_service_hours: float
    total_service_count: int
    avg_rating: Optional[float]
    rating_count: int
    current_level: str
    total_points: int
    badges: List[str]
    created_at: datetime
    approved_at: Optional[datetime]
    last_service_at: Optional[datetime]

class VolunteerListResponse(BaseModel):
    """
    志愿者列表响应模型
    """
    id: int
    user_id: int
    status: str
    real_name: str
    profession: str
    specialties: List[str]
    service_areas: List[str]
    total_service_hours: float
    avg_rating: Optional[float]
    current_level: str
    created_at: datetime
    last_service_at: Optional[datetime]

class VolunteerStatsResponse(BaseModel):
    """
    志愿者统计响应模型
    """
    total_volunteers: int
    active_volunteers: int
    total_service_hours: float
    total_service_count: int
    avg_rating: Optional[float]
    top_volunteers: List[VolunteerListResponse]
    service_area_distribution: Dict[str, int]
    level_distribution: Dict[str, int]

class ServiceRecordRequest(BaseModel):
    """
    服务记录请求模型
    """
    service_type: str = Field(..., description="服务类型")
    service_date: date = Field(..., description="服务日期")
    duration_hours: float = Field(..., gt=0, description="服务时长（小时）")
    description: str = Field(..., description="服务描述")
    beneficiary_count: int = Field(default=1, ge=1, description="受益人数")
    location: Optional[str] = Field(None, description="服务地点")
    notes: Optional[str] = Field(None, description="备注")

class VolunteerRatingRequest(BaseModel):
    """
    志愿者评价请求模型
    """
    rating: int = Field(..., ge=1, le=5, description="评分 1-5")
    comment: Optional[str] = Field(None, description="评价内容")
    service_quality: int = Field(..., ge=1, le=5, description="服务质量")
    communication: int = Field(..., ge=1, le=5, description="沟通能力")
    professionalism: int = Field(..., ge=1, le=5, description="专业性")

# 工具函数
def calculate_volunteer_level(total_hours: float, total_points: int):
    """
    计算志愿者等级
    
    Args:
        total_hours: 总服务时长
        total_points: 总积分
        
    Returns:
        志愿者等级
    """
    if total_hours >= 500 and total_points >= 1000:
        return "钻石志愿者"
    elif total_hours >= 200 and total_points >= 500:
        return "金牌志愿者"
    elif total_hours >= 100 and total_points >= 200:
        return "银牌志愿者"
    elif total_hours >= 50 and total_points >= 100:
        return "铜牌志愿者"
    elif total_hours >= 10:
        return "注册志愿者"
    else:
        return "新手志愿者"

def calculate_service_points(duration_hours: float, service_type: str, beneficiary_count: int):
    """
    计算服务积分
    
    Args:
        duration_hours: 服务时长
        service_type: 服务类型
        beneficiary_count: 受益人数
        
    Returns:
        积分
    """
    base_points = duration_hours * 2  # 基础积分：每小时2分
    
    # 服务类型加权
    type_multiplier = {
        "营养咨询": 1.5,
        "健康讲座": 2.0,
        "社区服务": 1.2,
        "在线答疑": 1.0,
        "内容审核": 1.0,
        "其他": 1.0
    }
    
    multiplier = type_multiplier.get(service_type, 1.0)
    
    # 受益人数加权
    if beneficiary_count > 10:
        multiplier *= 1.5
    elif beneficiary_count > 5:
        multiplier *= 1.2
    
    return int(base_points * multiplier)

# API端点
@router.post("/apply", summary="申请成为志愿者")
async def apply_volunteer(
    application: VolunteerApplicationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    申请成为志愿者
    
    Args:
        application: 申请信息
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        申请结果
    """
    try:
        # 检查是否已经申请过
        existing_volunteer = db.query(Volunteer).filter(
            Volunteer.user_id == current_user.id
        ).first()
        
        if existing_volunteer:
            if existing_volunteer.status == "approved":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="您已经是志愿者了"
                )
            elif existing_volunteer.status == "pending":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="您的申请正在审核中"
                )
            elif existing_volunteer.status == "rejected":
                # 允许重新申请
                db.delete(existing_volunteer)
                db.commit()
        
        # 创建志愿者申请
        volunteer = Volunteer(
            user_id=current_user.id,
            status="pending",
            real_name=application.real_name,
            phone=application.phone,
            email=application.email,
            education=application.education,
            profession=application.profession,
            work_unit=application.work_unit,
            specialties=application.specialties,
            certifications=application.certifications,
            experience=application.experience,
            motivation=application.motivation,
            available_time=application.available_time,
            service_areas=application.service_areas,
            introduction=application.introduction,
            application_date=datetime.now()
        )
        
        db.add(volunteer)
        db.commit()
        db.refresh(volunteer)
        
        return {"message": "志愿者申请提交成功，请等待审核"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"申请提交失败: {str(e)}"
        )

@router.get("/list", response_model=List[VolunteerListResponse], summary="获取志愿者列表")
async def get_volunteers_list(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    status_filter: Optional[str] = Query(None, description="状态筛选"),
    service_area: Optional[str] = Query(None, description="服务领域筛选"),
    specialty: Optional[str] = Query(None, description="专业特长筛选"),
    level: Optional[str] = Query(None, description="等级筛选"),
    sort_by: str = Query("created_at", description="排序字段: created_at, service_hours, rating"),
    sort_order: str = Query("desc", description="排序方向: asc, desc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取志愿者列表
    
    Args:
        skip: 跳过的记录数
        limit: 返回的记录数
        status_filter: 状态筛选
        service_area: 服务领域筛选
        specialty: 专业特长筛选
        level: 等级筛选
        sort_by: 排序字段
        sort_order: 排序方向
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        志愿者列表
    """
    try:
        # 构建查询
        query = db.query(Volunteer)
        
        # 应用筛选条件
        if status_filter:
            query = query.filter(Volunteer.status == status_filter)
        else:
            # 默认只显示已审核通过的志愿者
            query = query.filter(Volunteer.status == "approved")
        
        if service_area:
            query = query.filter(Volunteer.service_areas.contains([service_area]))
        
        if specialty:
            query = query.filter(Volunteer.specialties.contains([specialty]))
        
        if level:
            query = query.filter(Volunteer.current_level == level)
        
        # 排序
        if sort_by == "service_hours":
            order_field = Volunteer.total_service_hours
        elif sort_by == "rating":
            order_field = Volunteer.avg_rating
        else:
            order_field = Volunteer.created_at
        
        if sort_order == "asc":
            query = query.order_by(order_field.asc())
        else:
            query = query.order_by(order_field.desc())
        
        # 分页
        volunteers = query.offset(skip).limit(limit).all()
        
        # 转换为响应模型
        volunteer_list = []
        for volunteer in volunteers:
            volunteer_list.append(VolunteerListResponse(
                id=volunteer.id,
                user_id=volunteer.user_id,
                status=volunteer.status,
                real_name=volunteer.real_name,
                profession=volunteer.profession,
                specialties=volunteer.specialties or [],
                service_areas=volunteer.service_areas or [],
                total_service_hours=volunteer.total_service_hours,
                avg_rating=volunteer.avg_rating,
                current_level=volunteer.current_level,
                created_at=volunteer.created_at,
                last_service_at=volunteer.last_service_at
            ))
        
        return volunteer_list
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取志愿者列表失败: {str(e)}"
        )

@router.get("/stats", response_model=VolunteerStatsResponse, summary="获取志愿者统计")
async def get_volunteer_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取志愿者统计信息
    
    Args:
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        志愿者统计信息
    """
    try:
        # 基础统计
        total_volunteers = db.query(Volunteer).filter(
            Volunteer.status == "approved"
        ).count()
        
        # 活跃志愿者（最近30天有服务记录）
        from datetime import timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        active_volunteers = db.query(Volunteer).filter(
            Volunteer.status == "approved",
            Volunteer.last_service_at >= thirty_days_ago
        ).count()
        
        # 总服务时长和次数
        total_service_hours = db.query(func.sum(Volunteer.total_service_hours)).filter(
            Volunteer.status == "approved"
        ).scalar() or 0
        
        total_service_count = db.query(func.sum(Volunteer.total_service_count)).filter(
            Volunteer.status == "approved"
        ).scalar() or 0
        
        # 平均评分
        avg_rating_result = db.query(func.avg(Volunteer.avg_rating)).filter(
            Volunteer.status == "approved",
            Volunteer.avg_rating.isnot(None)
        ).scalar()
        avg_rating = round(avg_rating_result, 2) if avg_rating_result else None
        
        # 优秀志愿者（按服务时长排序）
        top_volunteers_query = db.query(Volunteer).filter(
            Volunteer.status == "approved"
        ).order_by(Volunteer.total_service_hours.desc()).limit(10).all()
        
        top_volunteers = []
        for volunteer in top_volunteers_query:
            top_volunteers.append(VolunteerListResponse(
                id=volunteer.id,
                user_id=volunteer.user_id,
                status=volunteer.status,
                real_name=volunteer.real_name,
                profession=volunteer.profession,
                specialties=volunteer.specialties or [],
                service_areas=volunteer.service_areas or [],
                total_service_hours=volunteer.total_service_hours,
                avg_rating=volunteer.avg_rating,
                current_level=volunteer.current_level,
                created_at=volunteer.created_at,
                last_service_at=volunteer.last_service_at
            ))
        
        # 服务领域分布
        volunteers = db.query(Volunteer).filter(
            Volunteer.status == "approved",
            Volunteer.service_areas.isnot(None)
        ).all()
        
        service_area_counts = {}
        for volunteer in volunteers:
            if volunteer.service_areas:
                for area in volunteer.service_areas:
                    service_area_counts[area] = service_area_counts.get(area, 0) + 1
        
        # 等级分布
        level_distribution = {}
        level_stats = db.query(
            Volunteer.current_level,
            func.count(Volunteer.id).label("count")
        ).filter(
            Volunteer.status == "approved"
        ).group_by(Volunteer.current_level).all()
        
        for stat in level_stats:
            level_distribution[stat.current_level] = stat.count
        
        return VolunteerStatsResponse(
            total_volunteers=total_volunteers,
            active_volunteers=active_volunteers,
            total_service_hours=total_service_hours,
            total_service_count=total_service_count,
            avg_rating=avg_rating,
            top_volunteers=top_volunteers,
            service_area_distribution=service_area_counts,
            level_distribution=level_distribution
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取志愿者统计失败: {str(e)}"
        )

@router.get("/my-profile", response_model=VolunteerResponse, summary="获取我的志愿者档案")
async def get_my_volunteer_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的志愿者档案
    
    Args:
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        志愿者档案
    """
    # 查找志愿者记录
    volunteer = db.query(Volunteer).filter(
        Volunteer.user_id == current_user.id
    ).first()
    
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="您还不是志愿者"
        )
    
    return VolunteerResponse(
        id=volunteer.id,
        user_id=volunteer.user_id,
        status=volunteer.status,
        real_name=volunteer.real_name,
        phone=volunteer.phone,
        email=volunteer.email,
        education=volunteer.education,
        profession=volunteer.profession,
        work_unit=volunteer.work_unit,
        specialties=volunteer.specialties or [],
        certifications=volunteer.certifications or [],
        experience=volunteer.experience,
        service_areas=volunteer.service_areas or [],
        available_time=volunteer.available_time or [],
        total_service_hours=volunteer.total_service_hours,
        total_service_count=volunteer.total_service_count,
        avg_rating=volunteer.avg_rating,
        rating_count=volunteer.rating_count,
        current_level=volunteer.current_level,
        total_points=volunteer.total_points,
        badges=volunteer.badges or [],
        created_at=volunteer.created_at,
        approved_at=volunteer.approved_at,
        last_service_at=volunteer.last_service_at
    )

@router.post("/service-record", summary="记录服务时长")
async def record_service(
    service_record: ServiceRecordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    记录志愿服务时长
    
    Args:
        service_record: 服务记录
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        记录结果
    """
    try:
        # 查找志愿者记录
        volunteer = db.query(Volunteer).filter(
            Volunteer.user_id == current_user.id,
            Volunteer.status == "approved"
        ).first()
        
        if not volunteer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="您还不是已审核的志愿者"
            )
        
        # 计算积分
        points = calculate_service_points(
            service_record.duration_hours,
            service_record.service_type,
            service_record.beneficiary_count
        )
        
        # 更新志愿者统计
        volunteer.add_service_hours(service_record.duration_hours)
        volunteer.add_points(points)
        
        # 更新等级
        new_level = calculate_volunteer_level(volunteer.total_service_hours, volunteer.total_points)
        if new_level != volunteer.current_level:
            volunteer.update_level(new_level)
        
        # TODO: 记录详细的服务记录到服务记录表
        
        db.commit()
        
        return {
            "message": "服务记录添加成功",
            "hours_added": service_record.duration_hours,
            "points_earned": points,
            "current_level": volunteer.current_level,
            "total_hours": volunteer.total_service_hours,
            "total_points": volunteer.total_points
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"记录服务失败: {str(e)}"
        )

@router.get("/{volunteer_id}", response_model=VolunteerResponse, summary="获取志愿者详情")
async def get_volunteer_detail(
    volunteer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取志愿者详情
    
    Args:
        volunteer_id: 志愿者ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        志愿者详情
    """
    # 查找志愿者
    volunteer = db.query(Volunteer).filter(
        Volunteer.id == volunteer_id,
        Volunteer.status == "approved"
    ).first()
    
    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="志愿者不存在或未审核通过"
        )
    
    return VolunteerResponse(
        id=volunteer.id,
        user_id=volunteer.user_id,
        status=volunteer.status,
        real_name=volunteer.real_name,
        phone=volunteer.phone,
        email=volunteer.email,
        education=volunteer.education,
        profession=volunteer.profession,
        work_unit=volunteer.work_unit,
        specialties=volunteer.specialties or [],
        certifications=volunteer.certifications or [],
        experience=volunteer.experience,
        service_areas=volunteer.service_areas or [],
        available_time=volunteer.available_time or [],
        total_service_hours=volunteer.total_service_hours,
        total_service_count=volunteer.total_service_count,
        avg_rating=volunteer.avg_rating,
        rating_count=volunteer.rating_count,
        current_level=volunteer.current_level,
        total_points=volunteer.total_points,
        badges=volunteer.badges or [],
        created_at=volunteer.created_at,
        approved_at=volunteer.approved_at,
        last_service_at=volunteer.last_service_at
    )

@router.post("/{volunteer_id}/rate", summary="评价志愿者")
async def rate_volunteer(
    volunteer_id: int,
    rating_request: VolunteerRatingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    评价志愿者
    
    Args:
        volunteer_id: 志愿者ID
        rating_request: 评价请求
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        评价结果
    """
    try:
        # 查找志愿者
        volunteer = db.query(Volunteer).filter(
            Volunteer.id == volunteer_id,
            Volunteer.status == "approved"
        ).first()
        
        if not volunteer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="志愿者不存在或未审核通过"
            )
        
        # TODO: 检查用户是否有权评价该志愿者（例如是否接受过服务）
        # TODO: 检查用户是否已经评价过
        
        # 更新志愿者评分
        volunteer.add_rating(rating_request.rating)
        
        # TODO: 记录详细评价到评价表
        
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