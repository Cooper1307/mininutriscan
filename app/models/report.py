# app/models/report.py
# 报告数据模型

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import enum
import json
from app.core.database import Base

class ReportType(enum.Enum):
    """
    报告类型枚举
    """
    DAILY = "daily"        # 日报告
    WEEKLY = "weekly"      # 周报告
    MONTHLY = "monthly"    # 月报告
    CUSTOM = "custom"      # 自定义报告
    SINGLE = "single"      # 单次检测报告

class ReportStatus(enum.Enum):
    """
    报告状态枚举
    """
    GENERATING = "generating"  # 生成中
    COMPLETED = "completed"    # 已完成
    FAILED = "failed"          # 生成失败
    ARCHIVED = "archived"      # 已归档

class Report(Base):
    """
    报告数据模型
    存储用户的营养健康分析报告
    """
    __tablename__ = "reports"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, comment="报告ID")
    
    # 关联用户
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    
    # 报告基本信息
    report_type = Column(Enum(ReportType), nullable=False, comment="报告类型")
    status = Column(Enum(ReportStatus), default=ReportStatus.GENERATING, comment="报告状态")
    title = Column(String(200), nullable=False, comment="报告标题")
    description = Column(Text, nullable=True, comment="报告描述")
    
    # 时间范围
    start_date = Column(DateTime, nullable=False, comment="统计开始时间")
    end_date = Column(DateTime, nullable=False, comment="统计结束时间")
    
    # 统计数据
    total_scans = Column(Integer, default=0, comment="总扫描次数")
    total_products = Column(Integer, default=0, comment="总产品数量")
    detection_ids = Column(JSON, nullable=True, comment="包含的检测记录ID列表")
    
    # 营养摄入统计（平均值）
    avg_energy_kcal = Column(Float, nullable=True, comment="平均能量摄入(kcal)")
    avg_protein = Column(Float, nullable=True, comment="平均蛋白质摄入(g)")
    avg_fat = Column(Float, nullable=True, comment="平均脂肪摄入(g)")
    avg_carbohydrate = Column(Float, nullable=True, comment="平均碳水化合物摄入(g)")
    avg_sugar = Column(Float, nullable=True, comment="平均糖摄入(g)")
    avg_sodium = Column(Float, nullable=True, comment="平均钠摄入(mg)")
    avg_dietary_fiber = Column(Float, nullable=True, comment="平均膳食纤维摄入(g)")
    
    # 营养评分
    overall_nutrition_score = Column(Float, nullable=True, comment="整体营养评分(0-100)")
    balance_score = Column(Float, nullable=True, comment="营养均衡评分(0-100)")
    health_score = Column(Float, nullable=True, comment="健康评分(0-100)")
    
    # 风险分析
    high_risk_products = Column(Integer, default=0, comment="高风险产品数量")
    medium_risk_products = Column(Integer, default=0, comment="中风险产品数量")
    low_risk_products = Column(Integer, default=0, comment="低风险产品数量")
    risk_factors = Column(JSON, nullable=True, comment="主要风险因素")
    
    # 产品分类统计
    category_stats = Column(JSON, nullable=True, comment="产品分类统计")
    brand_stats = Column(JSON, nullable=True, comment="品牌统计")
    
    # AI分析结果
    ai_summary = Column(Text, nullable=True, comment="AI生成的报告摘要")
    health_recommendations = Column(JSON, nullable=True, comment="健康建议列表")
    dietary_suggestions = Column(JSON, nullable=True, comment="饮食建议")
    improvement_areas = Column(JSON, nullable=True, comment="需要改进的方面")
    
    # 趋势分析
    nutrition_trends = Column(JSON, nullable=True, comment="营养趋势数据")
    score_trends = Column(JSON, nullable=True, comment="评分趋势")
    consumption_patterns = Column(JSON, nullable=True, comment="消费模式分析")
    
    # 对比数据
    previous_period_comparison = Column(JSON, nullable=True, comment="与上期对比")
    peer_comparison = Column(JSON, nullable=True, comment="同龄人对比")
    standard_comparison = Column(JSON, nullable=True, comment="标准值对比")
    
    # 报告文件
    report_file_path = Column(String(500), nullable=True, comment="报告文件路径")
    report_file_url = Column(String(500), nullable=True, comment="报告文件URL")
    chart_data = Column(JSON, nullable=True, comment="图表数据")
    
    # 生成信息
    generation_time = Column(Float, nullable=True, comment="生成耗时(秒)")
    error_message = Column(Text, nullable=True, comment="错误信息")
    
    # 用户交互
    view_count = Column(Integer, default=0, comment="查看次数")
    is_shared = Column(Boolean, default=False, comment="是否分享")
    is_favorite = Column(Boolean, default=False, comment="是否收藏")
    user_notes = Column(Text, nullable=True, comment="用户备注")
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    last_viewed_at = Column(DateTime, nullable=True, comment="最后查看时间")
    
    def __repr__(self):
        return f"<Report(id={self.id}, user_id={self.user_id}, title={self.title}, type={self.report_type})>"
    
    def to_dict(self, include_details=True):
        """
        转换为字典格式
        
        Args:
            include_details: 是否包含详细信息
            
        Returns:
            报告字典
        """
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "report_type": self.report_type.value if self.report_type else None,
            "status": self.status.value if self.status else None,
            "title": self.title,
            "description": self.description,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "total_scans": self.total_scans,
            "total_products": self.total_products,
            "overall_nutrition_score": self.overall_nutrition_score,
            "balance_score": self.balance_score,
            "health_score": self.health_score,
            "view_count": self.view_count,
            "is_shared": self.is_shared,
            "is_favorite": self.is_favorite,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
        
        if include_details:
            data.update({
                "detection_ids": self.detection_ids,
                "avg_energy_kcal": self.avg_energy_kcal,
                "avg_protein": self.avg_protein,
                "avg_fat": self.avg_fat,
                "avg_carbohydrate": self.avg_carbohydrate,
                "avg_sugar": self.avg_sugar,
                "avg_sodium": self.avg_sodium,
                "avg_dietary_fiber": self.avg_dietary_fiber,
                "high_risk_products": self.high_risk_products,
                "medium_risk_products": self.medium_risk_products,
                "low_risk_products": self.low_risk_products,
                "risk_factors": self.risk_factors,
                "category_stats": self.category_stats,
                "brand_stats": self.brand_stats,
                "ai_summary": self.ai_summary,
                "health_recommendations": self.health_recommendations,
                "dietary_suggestions": self.dietary_suggestions,
                "improvement_areas": self.improvement_areas,
                "nutrition_trends": self.nutrition_trends,
                "score_trends": self.score_trends,
                "consumption_patterns": self.consumption_patterns,
                "previous_period_comparison": self.previous_period_comparison,
                "peer_comparison": self.peer_comparison,
                "standard_comparison": self.standard_comparison,
                "report_file_url": self.report_file_url,
                "chart_data": self.chart_data,
                "generation_time": self.generation_time,
                "error_message": self.error_message,
                "user_notes": self.user_notes,
                "updated_at": self.updated_at.isoformat() if self.updated_at else None,
                "last_viewed_at": self.last_viewed_at.isoformat() if self.last_viewed_at else None
            })
        
        return data
    
    def update_status(self, status: ReportStatus, error_message=None):
        """
        更新报告状态
        
        Args:
            status: 新状态
            error_message: 错误信息（如果有）
        """
        self.status = status
        self.updated_at = datetime.now()
        
        if status == ReportStatus.COMPLETED:
            self.completed_at = datetime.now()
        elif status == ReportStatus.FAILED and error_message:
            self.error_message = error_message
    
    def set_nutrition_stats(self, nutrition_data: dict):
        """
        设置营养统计数据
        
        Args:
            nutrition_data: 营养统计字典
        """
        self.avg_energy_kcal = nutrition_data.get('avg_energy_kcal')
        self.avg_protein = nutrition_data.get('avg_protein')
        self.avg_fat = nutrition_data.get('avg_fat')
        self.avg_carbohydrate = nutrition_data.get('avg_carbohydrate')
        self.avg_sugar = nutrition_data.get('avg_sugar')
        self.avg_sodium = nutrition_data.get('avg_sodium')
        self.avg_dietary_fiber = nutrition_data.get('avg_dietary_fiber')
    
    def set_risk_analysis(self, risk_data: dict):
        """
        设置风险分析数据
        
        Args:
            risk_data: 风险分析字典
        """
        self.high_risk_products = risk_data.get('high_risk_products', 0)
        self.medium_risk_products = risk_data.get('medium_risk_products', 0)
        self.low_risk_products = risk_data.get('low_risk_products', 0)
        self.risk_factors = risk_data.get('risk_factors')
    
    def set_ai_analysis(self, ai_data: dict):
        """
        设置AI分析结果
        
        Args:
            ai_data: AI分析结果字典
        """
        self.ai_summary = ai_data.get('summary')
        self.health_recommendations = ai_data.get('health_recommendations')
        self.dietary_suggestions = ai_data.get('dietary_suggestions')
        self.improvement_areas = ai_data.get('improvement_areas')
    
    def increment_view_count(self):
        """
        增加查看次数
        """
        self.view_count += 1
        self.last_viewed_at = datetime.now()
        self.updated_at = datetime.now()
    
    def toggle_favorite(self):
        """
        切换收藏状态
        """
        self.is_favorite = not self.is_favorite
        self.updated_at = datetime.now()
    
    def add_user_notes(self, notes: str):
        """
        添加用户备注
        
        Args:
            notes: 备注内容
        """
        self.user_notes = notes
        self.updated_at = datetime.now()
    
    def calculate_period_days(self):
        """
        计算报告时间跨度（天数）
        
        Returns:
            天数
        """
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0
    
    def get_risk_distribution(self):
        """
        获取风险分布百分比
        
        Returns:
            风险分布字典
        """
        total = self.high_risk_products + self.medium_risk_products + self.low_risk_products
        
        if total == 0:
            return {"high": 0, "medium": 0, "low": 0}
        
        return {
            "high": round(self.high_risk_products / total * 100, 1),
            "medium": round(self.medium_risk_products / total * 100, 1),
            "low": round(self.low_risk_products / total * 100, 1)
        }
    
    def get_nutrition_balance_analysis(self):
        """
        获取营养均衡分析
        
        Returns:
            营养均衡分析字典
        """
        if not self.avg_energy_kcal:
            return None
        
        # 计算三大营养素比例
        protein_calories = (self.avg_protein or 0) * 4
        fat_calories = (self.avg_fat or 0) * 9
        carb_calories = (self.avg_carbohydrate or 0) * 4
        
        total_calories = protein_calories + fat_calories + carb_calories
        
        if total_calories == 0:
            return None
        
        return {
            "protein_ratio": round(protein_calories / total_calories * 100, 1),
            "fat_ratio": round(fat_calories / total_calories * 100, 1),
            "carbohydrate_ratio": round(carb_calories / total_calories * 100, 1),
            "recommended_protein": "10-15%",
            "recommended_fat": "20-30%",
            "recommended_carbohydrate": "55-65%"
        }
    
    def is_recent(self, days=30):
        """
        判断是否为最近的报告
        
        Args:
            days: 天数阈值
            
        Returns:
            是否为最近报告
        """
        if not self.created_at:
            return False
        
        return (datetime.now() - self.created_at).days <= days
    
    def get_improvement_score(self):
        """
        计算改进评分（相比上期）
        
        Returns:
            改进评分，正数表示改进，负数表示退步
        """
        if not self.previous_period_comparison:
            return None
        
        current_score = self.overall_nutrition_score or 0
        previous_score = self.previous_period_comparison.get('overall_nutrition_score', 0)
        
        return round(current_score - previous_score, 1)