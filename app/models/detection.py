# app/models/detection.py
# 检测记录数据模型

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
import json
from app.core.database import Base

class DetectionStatus(enum.Enum):
    """
    检测状态枚举
    """
    PENDING = "pending"        # 待处理
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"    # 已完成
    FAILED = "failed"          # 失败
    CANCELLED = "cancelled"    # 已取消

class DetectionType(enum.Enum):
    """
    检测类型枚举
    """
    OCR_SCAN = "ocr_scan"          # OCR文字识别
    IMAGE_ANALYSIS = "image_analysis"  # 图像分析
    MANUAL_INPUT = "manual_input"      # 手动输入
    BARCODE_SCAN = "barcode_scan"      # 条码扫描

class RiskLevel(enum.Enum):
    """
    风险等级枚举
    """
    LOW = "low"        # 低风险
    MEDIUM = "medium"  # 中风险
    HIGH = "high"      # 高风险
    UNKNOWN = "unknown" # 未知

class Detection(Base):
    """
    检测记录数据模型
    存储用户的食品营养检测记录和分析结果
    """
    __tablename__ = "detections"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True, comment="检测记录ID")
    
    # 关联用户（支持匿名用户）
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True, comment="用户ID（匿名用户时为空）")
    
    # 检测基本信息
    detection_type = Column(Enum(DetectionType), nullable=False, comment="检测类型")
    status = Column(Enum(DetectionStatus), default=DetectionStatus.PENDING, comment="检测状态")
    
    # 输入数据
    image_url = Column(String(500), nullable=True, comment="上传图片URL")
    image_path = Column(String(500), nullable=True, comment="图片存储路径")
    raw_text = Column(Text, nullable=True, comment="OCR识别原始文本")
    manual_input = Column(Text, nullable=True, comment="用户手动输入内容")
    barcode = Column(String(50), nullable=True, comment="条码信息")
    
    # 产品信息
    product_name = Column(String(200), nullable=True, comment="产品名称")
    brand = Column(String(100), nullable=True, comment="品牌")
    category = Column(String(100), nullable=True, comment="产品类别")
    manufacturer = Column(String(200), nullable=True, comment="生产厂家")
    production_date = Column(String(50), nullable=True, comment="生产日期")
    expiry_date = Column(String(50), nullable=True, comment="保质期")
    net_weight = Column(String(50), nullable=True, comment="净含量")
    
    # 营养成分信息（每100g/ml）
    energy_kj = Column(Float, nullable=True, comment="能量(kJ)")
    energy_kcal = Column(Float, nullable=True, comment="能量(kcal)")
    protein = Column(Float, nullable=True, comment="蛋白质(g)")
    fat = Column(Float, nullable=True, comment="脂肪(g)")
    saturated_fat = Column(Float, nullable=True, comment="饱和脂肪(g)")
    carbohydrate = Column(Float, nullable=True, comment="碳水化合物(g)")
    sugar = Column(Float, nullable=True, comment="糖(g)")
    dietary_fiber = Column(Float, nullable=True, comment="膳食纤维(g)")
    sodium = Column(Float, nullable=True, comment="钠(mg)")
    
    # 其他营养成分（JSON格式存储）
    vitamins = Column(JSON, nullable=True, comment="维生素含量")
    minerals = Column(JSON, nullable=True, comment="矿物质含量")
    other_nutrients = Column(JSON, nullable=True, comment="其他营养成分")
    
    # 配料表
    ingredients = Column(Text, nullable=True, comment="配料表")
    additives = Column(JSON, nullable=True, comment="添加剂列表")
    allergens = Column(JSON, nullable=True, comment="过敏原信息")
    
    # AI分析结果
    ai_analysis = Column(JSON, nullable=True, comment="AI分析结果")
    nutrition_score = Column(Float, nullable=True, comment="营养评分(0-100)")
    health_advice = Column(Text, nullable=True, comment="健康建议")
    risk_level = Column(Enum(RiskLevel), default=RiskLevel.UNKNOWN, comment="风险等级")
    risk_factors = Column(JSON, nullable=True, comment="风险因素")
    
    # 处理信息
    processing_time = Column(Float, nullable=True, comment="处理耗时(秒)")
    error_message = Column(Text, nullable=True, comment="错误信息")
    confidence_score = Column(Float, nullable=True, comment="识别置信度(0-1)")
    
    # 用户反馈
    user_rating = Column(Integer, nullable=True, comment="用户评分(1-5)")
    user_feedback = Column(Text, nullable=True, comment="用户反馈")
    is_accurate = Column(Boolean, nullable=True, comment="识别是否准确")
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    
    # 其他标记
    is_favorite = Column(Boolean, default=False, comment="是否收藏")
    is_shared = Column(Boolean, default=False, comment="是否分享")
    tags = Column(JSON, nullable=True, comment="用户标签")
    
    def __repr__(self):
        return f"<Detection(id={self.id}, user_id={self.user_id}, product_name={self.product_name}, status={self.status})>"
    
    @property
    def nutrition_data(self):
        """
        获取营养数据字典
        
        Returns:
            营养数据字典
        """
        return {
            "energy_kj": self.energy_kj,
            "energy_kcal": self.energy_kcal,
            "protein": self.protein,
            "fat": self.fat,
            "saturated_fat": self.saturated_fat,
            "carbohydrate": self.carbohydrate,
            "sugar": self.sugar,
            "dietary_fiber": self.dietary_fiber,
            "sodium": self.sodium,
            "vitamins": self.vitamins,
            "minerals": self.minerals,
            "other_nutrients": self.other_nutrients
        }
    
    @property
    def health_score(self):
        """
        获取健康评分（nutrition_score的别名）
        
        Returns:
            健康评分
        """
        return self.nutrition_score
    
    def to_dict(self, include_details=True):
        """
        转换为字典格式
        
        Args:
            include_details: 是否包含详细信息
            
        Returns:
            检测记录字典
        """
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "detection_type": self.detection_type.value if self.detection_type else None,
            "status": self.status.value if self.status else None,
            "product_name": self.product_name,
            "brand": self.brand,
            "category": self.category,
            "nutrition_score": self.nutrition_score,
            "risk_level": self.risk_level.value if self.risk_level else None,
            "user_rating": self.user_rating,
            "is_favorite": self.is_favorite,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
        
        if include_details:
            data.update({
                "image_url": self.image_url,
                "raw_text": self.raw_text,
                "manual_input": self.manual_input,
                "barcode": self.barcode,
                "manufacturer": self.manufacturer,
                "production_date": self.production_date,
                "expiry_date": self.expiry_date,
                "net_weight": self.net_weight,
                "energy_kj": self.energy_kj,
                "energy_kcal": self.energy_kcal,
                "protein": self.protein,
                "fat": self.fat,
                "saturated_fat": self.saturated_fat,
                "carbohydrate": self.carbohydrate,
                "sugar": self.sugar,
                "dietary_fiber": self.dietary_fiber,
                "sodium": self.sodium,
                "vitamins": self.vitamins,
                "minerals": self.minerals,
                "other_nutrients": self.other_nutrients,
                "ingredients": self.ingredients,
                "additives": self.additives,
                "allergens": self.allergens,
                "ai_analysis": self.ai_analysis,
                "health_advice": self.health_advice,
                "risk_factors": self.risk_factors,
                "processing_time": self.processing_time,
                "error_message": self.error_message,
                "confidence_score": self.confidence_score,
                "user_feedback": self.user_feedback,
                "is_accurate": self.is_accurate,
                "updated_at": self.updated_at.isoformat() if self.updated_at else None,
                "is_shared": self.is_shared,
                "tags": self.tags
            })
        
        return data
    
    def update_status(self, status: DetectionStatus, error_message=None):
        """
        更新检测状态
        
        Args:
            status: 新状态
            error_message: 错误信息（如果有）
        """
        self.status = status
        self.updated_at = datetime.now()
        
        if status == DetectionStatus.COMPLETED:
            self.completed_at = datetime.now()
        elif status == DetectionStatus.FAILED and error_message:
            self.error_message = error_message
    
    def set_nutrition_data(self, nutrition_data: dict):
        """
        设置营养成分数据
        
        Args:
            nutrition_data: 营养成分字典
        """
        # 基础营养成分
        self.energy_kj = nutrition_data.get('energy_kj')
        self.energy_kcal = nutrition_data.get('energy_kcal')
        self.protein = nutrition_data.get('protein')
        self.fat = nutrition_data.get('fat')
        self.saturated_fat = nutrition_data.get('saturated_fat')
        self.carbohydrate = nutrition_data.get('carbohydrate')
        self.sugar = nutrition_data.get('sugar')
        self.dietary_fiber = nutrition_data.get('dietary_fiber')
        self.sodium = nutrition_data.get('sodium')
        
        # 其他营养成分
        self.vitamins = nutrition_data.get('vitamins')
        self.minerals = nutrition_data.get('minerals')
        self.other_nutrients = nutrition_data.get('other_nutrients')
    
    def set_ai_analysis(self, score=None, advice=None, risk_level=None, analysis_data=None):
        """
        设置AI分析结果
        
        Args:
            score: 健康评分
            advice: 健康建议
            risk_level: 风险等级
            analysis_data: 详细分析数据
        """
        # 构建AI分析结果字典
        analysis_result = {
            "health_score": score,
            "advice": advice,
            "risk_level": risk_level,
            "analysis": analysis_data,
            "timestamp": datetime.now().isoformat()
        }
        
        self.ai_analysis = analysis_result
        self.nutrition_score = score
        self.health_advice = advice
        
        # 设置风险等级
        if risk_level:
            try:
                self.risk_level = RiskLevel(risk_level)
            except ValueError:
                self.risk_level = RiskLevel.UNKNOWN
        else:
            self.risk_level = RiskLevel.UNKNOWN
        
        # 从分析数据中提取风险因素
        if analysis_data and isinstance(analysis_data, dict):
            self.risk_factors = analysis_data.get('risk_factors')
        
        self.updated_at = datetime.now()
    
    def add_user_feedback(self, rating: int, feedback: str = None, is_accurate: bool = None):
        """
        添加用户反馈
        
        Args:
            rating: 评分(1-5)
            feedback: 反馈文本
            is_accurate: 识别是否准确
        """
        self.user_rating = max(1, min(5, rating))  # 确保评分在1-5范围内
        self.user_feedback = feedback
        self.is_accurate = is_accurate
        self.updated_at = datetime.now()
    
    def toggle_favorite(self):
        """
        切换收藏状态
        """
        self.is_favorite = not self.is_favorite
        self.updated_at = datetime.now()
    
    def add_tag(self, tag: str):
        """
        添加标签
        
        Args:
            tag: 标签名称
        """
        if self.tags is None:
            self.tags = []
        
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now()
    
    def remove_tag(self, tag: str):
        """
        移除标签
        
        Args:
            tag: 标签名称
        """
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now()
    
    def calculate_nutrition_density(self):
        """
        计算营养密度（营养素/能量比）
        
        Returns:
            营养密度字典
        """
        if not self.energy_kcal or self.energy_kcal <= 0:
            return None
        
        density = {}
        
        if self.protein is not None:
            density['protein_density'] = round(self.protein / self.energy_kcal * 100, 2)
        
        if self.dietary_fiber is not None:
            density['fiber_density'] = round(self.dietary_fiber / self.energy_kcal * 100, 2)
        
        if self.sodium is not None:
            density['sodium_density'] = round(self.sodium / self.energy_kcal, 2)
        
        return density if density else None
    
    def is_high_sodium(self, threshold=600):
        """
        判断是否为高钠食品
        
        Args:
            threshold: 钠含量阈值(mg/100g)
            
        Returns:
            是否为高钠食品
        """
        return self.sodium is not None and self.sodium > threshold
    
    def is_high_sugar(self, threshold=15):
        """
        判断是否为高糖食品
        
        Args:
            threshold: 糖含量阈值(g/100g)
            
        Returns:
            是否为高糖食品
        """
        return self.sugar is not None and self.sugar > threshold
    
    def is_high_fat(self, threshold=20):
        """
        判断是否为高脂食品
        
        Args:
            threshold: 脂肪含量阈值(g/100g)
            
        Returns:
            是否为高脂食品
        """
        return self.fat is not None and self.fat > threshold