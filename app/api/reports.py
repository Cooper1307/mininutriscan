# app/api/reports.py
# 报告系统API路由

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, date
import json

from ..core.database import get_db
from ..models.user import User
from ..models.report import Report
from ..models.detection import Detection
from ..services.ai_service import AIService
from ..api.auth import get_current_user

# 创建路由器
router = APIRouter()

# Pydantic模型定义
class ReportGenerateRequest(BaseModel):
    """
    报告生成请求模型
    """
    report_type: str = Field(..., description="报告类型: daily, weekly, monthly, custom")
    title: Optional[str] = Field(None, description="报告标题")
    description: Optional[str] = Field(None, description="报告描述")
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    detection_ids: Optional[List[int]] = Field(None, description="指定检测记录ID列表")
    include_trends: bool = Field(True, description="是否包含趋势分析")
    include_recommendations: bool = Field(True, description="是否包含建议")

class ReportResponse(BaseModel):
    """
    报告响应模型
    """
    id: int
    report_type: str
    status: str
    title: str
    description: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    total_detections: int
    total_products: int
    avg_nutrition_score: Optional[float]
    risk_analysis: Optional[Dict[str, Any]]
    ai_summary: Optional[str]
    ai_recommendations: Optional[List[str]]
    created_at: datetime
    updated_at: datetime
    view_count: int
    is_favorite: bool

class ReportListResponse(BaseModel):
    """
    报告列表响应模型
    """
    id: int
    report_type: str
    status: str
    title: str
    start_date: Optional[date]
    end_date: Optional[date]
    total_detections: int
    avg_nutrition_score: Optional[float]
    created_at: datetime
    view_count: int
    is_favorite: bool

class ReportStatsResponse(BaseModel):
    """
    报告统计响应模型
    """
    total_reports: int
    completed_reports: int
    favorite_reports: int
    avg_nutrition_score: Optional[float]
    most_scanned_category: Optional[str]
    health_trend: Optional[str]  # improving, stable, declining
    last_report_date: Optional[datetime]

# 工具函数
def calculate_date_range(report_type: str, custom_start: Optional[date] = None, custom_end: Optional[date] = None):
    """
    计算报告日期范围
    
    Args:
        report_type: 报告类型
        custom_start: 自定义开始日期
        custom_end: 自定义结束日期
        
    Returns:
        (start_date, end_date) 元组
    """
    today = date.today()
    
    if report_type == "daily":
        return today, today
    elif report_type == "weekly":
        start_date = today - timedelta(days=today.weekday())  # 本周一
        end_date = start_date + timedelta(days=6)  # 本周日
        return start_date, end_date
    elif report_type == "monthly":
        start_date = today.replace(day=1)  # 本月第一天
        next_month = start_date.replace(month=start_date.month + 1) if start_date.month < 12 else start_date.replace(year=start_date.year + 1, month=1)
        end_date = next_month - timedelta(days=1)  # 本月最后一天
        return start_date, end_date
    elif report_type == "custom":
        if custom_start and custom_end:
            return custom_start, custom_end
        else:
            # 默认最近30天
            return today - timedelta(days=29), today
    else:
        # 默认最近7天
        return today - timedelta(days=6), today

def get_detections_in_range(db: Session, user_id: int, start_date: date, end_date: date, detection_ids: Optional[List[int]] = None):
    """
    获取指定日期范围内的检测记录
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        start_date: 开始日期
        end_date: 结束日期
        detection_ids: 指定的检测ID列表
        
    Returns:
        检测记录列表
    """
    query = db.query(Detection).filter(
        Detection.user_id == user_id,
        Detection.status == "completed",
        func.date(Detection.created_at) >= start_date,
        func.date(Detection.created_at) <= end_date
    )
    
    if detection_ids:
        query = query.filter(Detection.id.in_(detection_ids))
    
    return query.order_by(Detection.created_at.desc()).all()

def calculate_nutrition_stats(detections: List[Detection]):
    """
    计算营养统计数据
    
    Args:
        detections: 检测记录列表
        
    Returns:
        营养统计字典
    """
    if not detections:
        return {}
    
    # 统计营养成分
    total_energy = 0
    total_protein = 0
    total_fat = 0
    total_carbs = 0
    total_sodium = 0
    count = 0
    
    health_scores = []
    categories = {}
    brands = {}
    
    for detection in detections:
        if detection.nutrition_data:
            nutrition = detection.nutrition_data
            
            # 累计营养成分
            total_energy += nutrition.get("energy_kcal", 0) or 0
            total_protein += nutrition.get("protein", 0) or 0
            total_fat += nutrition.get("fat", 0) or 0
            total_carbs += nutrition.get("carbohydrates", 0) or 0
            total_sodium += nutrition.get("sodium", 0) or 0
            count += 1
        
        # 健康评分
        if detection.health_score:
            health_scores.append(detection.health_score)
        
        # 分类统计
        if detection.category:
            categories[detection.category] = categories.get(detection.category, 0) + 1
        
        # 品牌统计
        if detection.brand:
            brands[detection.brand] = brands.get(detection.brand, 0) + 1
    
    # 计算平均值
    avg_nutrition = {}
    if count > 0:
        avg_nutrition = {
            "energy_kcal": round(total_energy / count, 2),
            "protein": round(total_protein / count, 2),
            "fat": round(total_fat / count, 2),
            "carbohydrates": round(total_carbs / count, 2),
            "sodium": round(total_sodium / count, 2)
        }
    
    return {
        "total_detections": len(detections),
        "avg_nutrition": avg_nutrition,
        "avg_health_score": round(sum(health_scores) / len(health_scores), 2) if health_scores else None,
        "category_distribution": dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)),
        "brand_distribution": dict(sorted(brands.items(), key=lambda x: x[1], reverse=True)),
        "health_score_distribution": {
            "excellent": len([s for s in health_scores if s >= 80]),
            "good": len([s for s in health_scores if 60 <= s < 80]),
            "fair": len([s for s in health_scores if 40 <= s < 60]),
            "poor": len([s for s in health_scores if s < 40])
        } if health_scores else {}
    }

# API端点
@router.post("/generate", response_model=ReportResponse, summary="生成营养报告")
async def generate_report(
    report_request: ReportGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    生成营养分析报告
    
    Args:
        report_request: 报告生成请求
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        生成的报告
    """
    try:
        # 计算日期范围
        start_date, end_date = calculate_date_range(
            report_request.report_type,
            report_request.start_date,
            report_request.end_date
        )
        
        # 获取检测记录
        detections = get_detections_in_range(
            db, current_user.id, start_date, end_date, report_request.detection_ids
        )
        
        if not detections:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="指定时间范围内没有检测记录"
            )
        
        # 计算统计数据
        stats = calculate_nutrition_stats(detections)
        
        # 生成报告标题
        if not report_request.title:
            title = f"{current_user.nickname}的{report_request.report_type}营养报告"
        else:
            title = report_request.title
        
        # 创建报告记录
        report = Report(
            user_id=current_user.id,
            report_type=report_request.report_type,
            status="generating",
            title=title,
            description=report_request.description,
            start_date=start_date,
            end_date=end_date,
            total_detections=stats["total_detections"],
            total_products=len(set(d.product_name for d in detections if d.product_name)),
            detection_ids=[d.id for d in detections],
            avg_nutrition_intake=stats["avg_nutrition"],
            avg_nutrition_score=stats["avg_health_score"],
            category_stats=stats["category_distribution"],
            brand_stats=stats["brand_distribution"],
            generation_started_at=datetime.now()
        )
        
        db.add(report)
        db.commit()
        db.refresh(report)
        
        try:
            # 风险分析
            risk_analysis = {
                "high_sodium": len([d for d in detections if d.nutrition_data and d.nutrition_data.get("sodium", 0) > 600]),
                "high_sugar": len([d for d in detections if d.nutrition_data and d.nutrition_data.get("sugars", 0) > 15]),
                "high_fat": len([d for d in detections if d.nutrition_data and d.nutrition_data.get("fat", 0) > 20]),
                "low_protein": len([d for d in detections if d.nutrition_data and d.nutrition_data.get("protein", 0) < 5])
            }
            
            # AI分析（如果启用）
            ai_summary = None
            ai_recommendations = []
            
            if report_request.include_recommendations:
                try:
                    ai_service = AIService()
                    ai_analysis = await ai_service.generate_nutrition_report(
                        detections_data=[d.to_dict() for d in detections],
                        user_profile={
                            "age": current_user.age,
                            "health_conditions": current_user.health_conditions,
                            "dietary_preferences": current_user.dietary_preferences,
                            "allergies": current_user.allergies
                        },
                        stats=stats,
                        time_range=f"{start_date} 至 {end_date}"
                    )
                    
                    if ai_analysis and ai_analysis.get("success"):
                        ai_summary = ai_analysis.get("summary")
                        ai_recommendations = ai_analysis.get("recommendations", [])
                        
                except Exception as e:
                    print(f"AI分析失败: {e}")
                    ai_summary = "AI分析暂时不可用"
                    ai_recommendations = ["建议保持均衡饮食", "注意控制钠的摄入量"]
            
            # 更新报告
            report.set_risk_analysis(risk_analysis)
            report.set_ai_analysis(ai_summary, ai_recommendations)
            report.update_status("completed")
            
            # 更新用户统计
            current_user.increment_report_count()
            
            db.commit()
            db.refresh(report)
            
            return ReportResponse(
                id=report.id,
                report_type=report.report_type,
                status=report.status,
                title=report.title,
                description=report.description,
                start_date=report.start_date,
                end_date=report.end_date,
                total_detections=report.total_detections,
                total_products=report.total_products,
                avg_nutrition_score=report.avg_nutrition_score,
                risk_analysis=report.risk_analysis,
                ai_summary=report.ai_summary,
                ai_recommendations=report.ai_recommendations,
                created_at=report.created_at,
                updated_at=report.updated_at,
                view_count=report.view_count,
                is_favorite=report.is_favorite
            )
            
        except Exception as e:
            report.update_status("failed", str(e))
            db.commit()
            raise
            
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"报告生成失败: {str(e)}"
        )

@router.get("/list", response_model=List[ReportListResponse], summary="获取报告列表")
async def get_reports_list(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    report_type: Optional[str] = Query(None, description="报告类型筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    is_favorite: Optional[bool] = Query(None, description="是否只显示收藏"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户的报告列表
    
    Args:
        skip: 跳过的记录数
        limit: 返回的记录数
        report_type: 报告类型筛选
        status: 状态筛选
        is_favorite: 是否只显示收藏
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        报告列表
    """
    try:
        # 构建查询
        query = db.query(Report).filter(Report.user_id == current_user.id)
        
        # 应用筛选条件
        if report_type:
            query = query.filter(Report.report_type == report_type)
        
        if status:
            query = query.filter(Report.status == status)
        
        if is_favorite is not None:
            query = query.filter(Report.is_favorite == is_favorite)
        
        # 排序和分页
        reports = query.order_by(Report.created_at.desc()).offset(skip).limit(limit).all()
        
        # 转换为响应模型
        report_list = []
        for report in reports:
            report_list.append(ReportListResponse(
                id=report.id,
                report_type=report.report_type,
                status=report.status,
                title=report.title,
                start_date=report.start_date,
                end_date=report.end_date,
                total_detections=report.total_detections,
                avg_nutrition_score=report.avg_nutrition_score,
                created_at=report.created_at,
                view_count=report.view_count,
                is_favorite=report.is_favorite
            ))
        
        return report_list
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取报告列表失败: {str(e)}"
        )

@router.get("/stats", response_model=ReportStatsResponse, summary="获取报告统计")
async def get_reports_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户的报告统计信息
    
    Args:
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        报告统计信息
    """
    try:
        # 基础统计
        total_reports = db.query(Report).filter(Report.user_id == current_user.id).count()
        completed_reports = db.query(Report).filter(
            Report.user_id == current_user.id,
            Report.status == "completed"
        ).count()
        favorite_reports = db.query(Report).filter(
            Report.user_id == current_user.id,
            Report.is_favorite == True
        ).count()
        
        # 平均营养评分
        avg_score_result = db.query(func.avg(Report.avg_nutrition_score)).filter(
            Report.user_id == current_user.id,
            Report.status == "completed",
            Report.avg_nutrition_score.isnot(None)
        ).scalar()
        avg_nutrition_score = round(avg_score_result, 2) if avg_score_result else None
        
        # 最常扫描的分类
        most_scanned_category = None
        recent_detections = db.query(Detection).filter(
            Detection.user_id == current_user.id,
            Detection.status == "completed",
            Detection.category.isnot(None)
        ).limit(100).all()
        
        if recent_detections:
            category_counts = {}
            for detection in recent_detections:
                category = detection.category
                category_counts[category] = category_counts.get(category, 0) + 1
            
            if category_counts:
                most_scanned_category = max(category_counts, key=category_counts.get)
        
        # 健康趋势分析
        health_trend = None
        recent_reports = db.query(Report).filter(
            Report.user_id == current_user.id,
            Report.status == "completed",
            Report.avg_nutrition_score.isnot(None)
        ).order_by(Report.created_at.desc()).limit(5).all()
        
        if len(recent_reports) >= 3:
            scores = [r.avg_nutrition_score for r in reversed(recent_reports)]
            if scores[-1] > scores[0] + 5:
                health_trend = "improving"
            elif scores[-1] < scores[0] - 5:
                health_trend = "declining"
            else:
                health_trend = "stable"
        
        # 最后报告日期
        last_report = db.query(Report).filter(
            Report.user_id == current_user.id
        ).order_by(Report.created_at.desc()).first()
        last_report_date = last_report.created_at if last_report else None
        
        return ReportStatsResponse(
            total_reports=total_reports,
            completed_reports=completed_reports,
            favorite_reports=favorite_reports,
            avg_nutrition_score=avg_nutrition_score,
            most_scanned_category=most_scanned_category,
            health_trend=health_trend,
            last_report_date=last_report_date
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取报告统计失败: {str(e)}"
        )

@router.get("/{report_id}", response_model=ReportResponse, summary="获取报告详情")
async def get_report_detail(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取报告详情
    
    Args:
        report_id: 报告ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        报告详情
    """
    # 查找报告
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="报告不存在或无权访问"
        )
    
    # 增加查看次数
    report.increment_view_count()
    db.commit()
    
    return ReportResponse(
        id=report.id,
        report_type=report.report_type,
        status=report.status,
        title=report.title,
        description=report.description,
        start_date=report.start_date,
        end_date=report.end_date,
        total_detections=report.total_detections,
        total_products=report.total_products,
        avg_nutrition_score=report.avg_nutrition_score,
        risk_analysis=report.risk_analysis,
        ai_summary=report.ai_summary,
        ai_recommendations=report.ai_recommendations,
        created_at=report.created_at,
        updated_at=report.updated_at,
        view_count=report.view_count,
        is_favorite=report.is_favorite
    )

@router.post("/{report_id}/favorite", summary="收藏/取消收藏报告")
async def toggle_report_favorite(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    收藏或取消收藏报告
    
    Args:
        report_id: 报告ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        操作结果
    """
    try:
        # 查找报告
        report = db.query(Report).filter(
            Report.id == report_id,
            Report.user_id == current_user.id
        ).first()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="报告不存在或无权访问"
            )
        
        # 切换收藏状态
        report.toggle_favorite()
        db.commit()
        
        action = "收藏" if report.is_favorite else "取消收藏"
        return {"message": f"报告{action}成功", "is_favorite": report.is_favorite}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"操作失败: {str(e)}"
        )

@router.post("/{report_id}/note", summary="添加报告备注")
async def add_report_note(
    report_id: int,
    note: str = Query(..., description="备注内容"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    为报告添加备注
    
    Args:
        report_id: 报告ID
        note: 备注内容
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        操作结果
    """
    try:
        # 查找报告
        report = db.query(Report).filter(
            Report.id == report_id,
            Report.user_id == current_user.id
        ).first()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="报告不存在或无权访问"
            )
        
        # 添加备注
        report.add_note(note)
        db.commit()
        
        return {"message": "备注添加成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加备注失败: {str(e)}"
        )

@router.delete("/{report_id}", summary="删除报告")
async def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除报告
    
    Args:
        report_id: 报告ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        删除确认
    """
    try:
        # 查找报告
        report = db.query(Report).filter(
            Report.id == report_id,
            Report.user_id == current_user.id
        ).first()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="报告不存在或无权访问"
            )
        
        # 删除报告文件（如果存在）
        if report.report_file_path and os.path.exists(report.report_file_path):
            try:
                os.remove(report.report_file_path)
            except Exception as e:
                print(f"删除报告文件失败: {e}")
        
        # 删除记录
        db.delete(report)
        db.commit()
        
        return {"message": "报告删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除报告失败: {str(e)}"
        )