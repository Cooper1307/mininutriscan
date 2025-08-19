# app/api/detection.py
# 营养检测API路由

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import uuid
import os
import base64
import io
from PIL import Image

from ..core.database import get_db
from ..core.config import get_settings
from ..models.user import User
from ..models.detection import Detection, DetectionType, DetectionStatus
from ..services.ai_service import AIService
from ..services.ocr_service import OCRService
from ..api.auth import get_current_user, get_current_user_optional

# 创建路由器
router = APIRouter()
settings = get_settings()

# Pydantic模型定义
class DetectionRequest(BaseModel):
    """
    检测请求模型
    """
    detection_type: str = Field(..., description="检测类型: image_ocr, manual_input, barcode")
    raw_text: Optional[str] = Field(None, description="原始文本（手动输入或OCR结果）")
    barcode: Optional[str] = Field(None, description="条形码")
    product_name: Optional[str] = Field(None, description="产品名称")
    brand: Optional[str] = Field(None, description="品牌")
    category: Optional[str] = Field(None, description="分类")

class NutritionData(BaseModel):
    """
    营养数据模型
    """
    energy_kj: Optional[float] = Field(None, description="能量(kJ)")
    energy_kcal: Optional[float] = Field(None, description="能量(kcal)")
    protein: Optional[float] = Field(None, description="蛋白质(g)")
    fat: Optional[float] = Field(None, description="脂肪(g)")
    saturated_fat: Optional[float] = Field(None, description="饱和脂肪(g)")
    carbohydrates: Optional[float] = Field(None, description="碳水化合物(g)")
    sugars: Optional[float] = Field(None, description="糖(g)")
    dietary_fiber: Optional[float] = Field(None, description="膳食纤维(g)")
    sodium: Optional[float] = Field(None, description="钠(mg)")
    calcium: Optional[float] = Field(None, description="钙(mg)")
    iron: Optional[float] = Field(None, description="铁(mg)")
    vitamin_c: Optional[float] = Field(None, description="维生素C(mg)")
    vitamin_d: Optional[float] = Field(None, description="维生素D(μg)")

class DetectionResponse(BaseModel):
    """
    检测响应模型
    """
    id: int
    detection_type: str
    status: str
    product_name: Optional[str]
    brand: Optional[str]
    category: Optional[str]
    nutrition_data: Optional[Dict[str, Any]]
    ai_analysis: Optional[Dict[str, Any]]
    health_score: Optional[float]
    risk_level: Optional[str]
    created_at: datetime
    processing_time: Optional[float]

class DetectionListResponse(BaseModel):
    """
    检测列表响应模型
    """
    id: int
    detection_type: str
    status: str
    product_name: Optional[str]
    brand: Optional[str]
    health_score: Optional[float]
    risk_level: Optional[str]
    created_at: datetime

# 工具函数
def save_uploaded_file(file: UploadFile) -> str:
    """
    保存上传的文件
    
    Args:
        file: 上传的文件
        
    Returns:
        保存的文件路径
        
    Raises:
        HTTPException: 文件保存失败时抛出异常
    """
    try:
        # 生成唯一文件名
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # 确保上传目录存在
        upload_dir = settings.UPLOAD_DIR
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_dir, unique_filename)
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)
        
        return file_path
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件保存失败: {str(e)}"
        )

def validate_file(file: UploadFile) -> None:
    """
    验证上传的文件
    
    Args:
        file: 上传的文件
        
    Raises:
        HTTPException: 文件验证失败时抛出异常
    """
    # 检查文件大小
    if file.size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"文件大小超过限制 ({settings.MAX_UPLOAD_SIZE} bytes)"
        )
    
    # 检查文件类型
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型，支持的类型: {settings.ALLOWED_EXTENSIONS}"
        )

async def save_base64_image(image_data: str) -> str:
    """
    保存base64编码的图片数据
    
    Args:
        image_data: base64编码的图片数据（可能包含data:image/xxx;base64,前缀）
        
    Returns:
        保存的文件路径
        
    Raises:
        HTTPException: 文件保存失败时抛出异常
    """
    try:
        # 处理data URI格式
        if image_data.startswith('data:'):
            # 提取base64数据部分
            header, base64_data = image_data.split(',', 1)
            # 从header中提取文件类型
            mime_type = header.split(';')[0].split(':')[1]
            file_extension = '.' + mime_type.split('/')[1]
        else:
            # 纯base64数据，默认为jpeg
            base64_data = image_data
            file_extension = '.jpg'
        
        # 解码base64数据
        image_bytes = base64.b64decode(base64_data)
        
        # 验证图片数据
        try:
            image = Image.open(io.BytesIO(image_bytes))
            image.verify()  # 验证图片完整性
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的图片数据"
            )
        
        # 生成唯一文件名
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # 确保上传目录存在
        upload_dir = settings.UPLOAD_DIR
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_dir, unique_filename)
        with open(file_path, "wb") as buffer:
            buffer.write(image_bytes)
        
        return file_path
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"图片保存失败: {str(e)}"
        )

# 新增base64图片数据模型
class Base64ImageRequest(BaseModel):
    """
    Base64图片检测请求模型
    """
    image_data: str = Field(..., description="Base64编码的图片数据")
    detection_type: str = Field(default="image_ocr", description="检测类型")
    user_notes: Optional[str] = Field(None, description="用户备注")

# API端点
@router.post("/upload-image", response_model=DetectionResponse, summary="上传图片进行OCR检测")
async def upload_image_detection(
    file: UploadFile = File(..., description="营养标签图片"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传图片文件进行OCR营养检测
    """
    return await _process_image_detection(file, None, current_user, db)

@router.post("/analyze-base64", response_model=DetectionResponse, summary="分析Base64图片数据")
async def analyze_base64_image(
    request: Base64ImageRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    分析Base64编码的图片数据进行OCR营养检测
    支持匿名用户访问（不需要登录）
    """
    return await _process_image_detection(None, request, current_user, db)

async def _process_image_detection(
    file: Optional[UploadFile],
    base64_request: Optional[Base64ImageRequest],
    current_user: Optional[User],
    db: Session
):
    """
    处理图片检测（支持文件上传和base64数据）
    
    Args:
        file: 上传的图片文件（可选）
        base64_request: base64图片请求（可选）
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        检测结果
        
    Raises:
        HTTPException: 检测失败时抛出异常
    """
    start_time = datetime.now()
    file_path = None
    
    try:
        # 处理文件上传或base64数据
        if file:
            # 验证文件
            validate_file(file)
            # 保存文件
            file_path = save_uploaded_file(file)
        elif base64_request:
            # 处理base64数据
            file_path = await save_base64_image(base64_request.image_data)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="必须提供图片文件或base64数据"
            )
        
        # 创建检测记录（支持匿名用户）
        from ..models.detection import DetectionType, DetectionStatus
        detection = Detection(
            user_id=current_user.id if current_user else None,
            detection_type=DetectionType.OCR_SCAN,
            status=DetectionStatus.PROCESSING,
            image_url=file_path
        )
        db.add(detection)
        db.commit()
        db.refresh(detection)
        
        try:
            # 初始化OCR服务
            ocr_service = OCRService()
            
            # 执行OCR识别
            ocr_result = await ocr_service.recognize_nutrition_label(file_path)
            
            if not ocr_result or not ocr_result.get("success"):
                detection.update_status(DetectionStatus.FAILED, "OCR识别失败")
                db.commit()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="图片识别失败，请确保图片清晰且包含营养标签"
                )
            
            # 更新检测记录
            detection.raw_text = ocr_result.get("text", "")
            detection.ocr_confidence = ocr_result.get("confidence", 0)
            
            # 解析营养信息
            nutrition_data = ocr_result.get("nutrition_data", {})
            if nutrition_data:
                detection.set_nutrition_data(nutrition_data)
            
            # 初始化AI服务进行分析
            ai_service = AIService()
            
            # 执行AI分析
            ai_analysis = await ai_service.analyze_nutrition(
                nutrition_data=nutrition_data,
                product_info={
                    "name": detection.product_name,
                    "brand": detection.brand,
                    "category": detection.category
                },
                user_profile={
                    "age": current_user.age,
                    "health_conditions": current_user.health_conditions,
                    "dietary_preferences": current_user.dietary_preferences,
                    "allergies": current_user.allergies
                }
            )
            
            if ai_analysis and ai_analysis.get("success"):
                detection.set_ai_analysis(
                    score=ai_analysis.get("health_score"),
                    advice=ai_analysis.get("advice"),
                    risk_level=ai_analysis.get("risk_level"),
                    analysis_data=ai_analysis.get("analysis")
                )
            
            # 更新处理时间和状态
            processing_time = (datetime.now() - start_time).total_seconds()
            detection.processing_time = processing_time
            detection.update_status(DetectionStatus.COMPLETED)
            
            # 更新用户统计
            current_user.increment_scan_count()
            
            db.commit()
            db.refresh(detection)
            
            return DetectionResponse(
                id=detection.id,
                detection_type=detection.detection_type,
                status=detection.status,
                product_name=detection.product_name,
                brand=detection.brand,
                category=detection.category,
                nutrition_data=detection.nutrition_data,
                ai_analysis=detection.ai_analysis,
                health_score=detection.health_score,
                risk_level=detection.risk_level,
                created_at=detection.created_at,
                processing_time=processing_time
            )
            
        except Exception as e:
            # 更新检测状态为失败
            detection.update_status(DetectionStatus.FAILED, str(e))
            db.commit()
            raise
            
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"检测过程中发生错误: {str(e)}"
        )

@router.post("/manual-input", response_model=DetectionResponse, summary="手动输入营养信息")
async def manual_input_detection(
    detection_data: DetectionRequest,
    nutrition_data: NutritionData,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    手动输入营养信息进行检测
    
    Args:
        detection_data: 检测数据
        nutrition_data: 营养数据
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        检测结果
    """
    start_time = datetime.now()
    
    try:
        # 创建检测记录
        detection = Detection(
            user_id=current_user.id,
            detection_type=DetectionType.MANUAL_INPUT,
            status=DetectionStatus.PROCESSING,
            raw_text=detection_data.raw_text,
            product_name=detection_data.product_name,
            brand=detection_data.brand,
            category=detection_data.category
        )
        
        # 设置营养数据
        nutrition_dict = nutrition_data.dict(exclude_unset=True)
        detection.set_nutrition_data(nutrition_dict)
        
        db.add(detection)
        db.commit()
        db.refresh(detection)
        
        try:
            # 初始化AI服务进行分析
            ai_service = AIService()
            
            # 执行AI分析
            ai_analysis = await ai_service.analyze_nutrition(
                nutrition_data=nutrition_dict,
                product_info={
                    "name": detection.product_name,
                    "brand": detection.brand,
                    "category": detection.category
                },
                user_profile={
                    "age": current_user.age,
                    "health_conditions": current_user.health_conditions,
                    "dietary_preferences": current_user.dietary_preferences,
                    "allergies": current_user.allergies
                }
            )
            
            if ai_analysis and ai_analysis.get("success"):
                detection.set_ai_analysis(
                    score=ai_analysis.get("health_score"),
                    advice=ai_analysis.get("advice"),
                    risk_level=ai_analysis.get("risk_level"),
                    analysis_data=ai_analysis.get("analysis")
                )
            
            # 更新处理时间和状态
            processing_time = (datetime.now() - start_time).total_seconds()
            detection.processing_time = processing_time
            detection.update_status(DetectionStatus.COMPLETED)
            
            # 更新用户统计
            current_user.increment_scan_count()
            
            db.commit()
            db.refresh(detection)
            
            return DetectionResponse(
                id=detection.id,
                detection_type=detection.detection_type,
                status=detection.status,
                product_name=detection.product_name,
                brand=detection.brand,
                category=detection.category,
                nutrition_data=detection.nutrition_data,
                ai_analysis=detection.ai_analysis,
                health_score=detection.health_score,
                risk_level=detection.risk_level,
                created_at=detection.created_at,
                processing_time=processing_time
            )
            
        except Exception as e:
            detection.update_status(DetectionStatus.FAILED, str(e))
            db.commit()
            raise
            
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"检测过程中发生错误: {str(e)}"
        )

@router.post("/barcode", response_model=DetectionResponse, summary="条形码检测")
async def barcode_detection(
    barcode: str = Form(..., description="条形码"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    通过条形码进行产品检测
    
    Args:
        barcode: 条形码
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        检测结果
        
    Note:
        这里需要集成第三方产品数据库API，暂时返回模拟数据
    """
    start_time = datetime.now()
    
    try:
        # 创建检测记录
        detection = Detection(
            user_id=current_user.id,
            detection_type=DetectionType.BARCODE_SCAN,
            status=DetectionStatus.PROCESSING,
            barcode=barcode
        )
        db.add(detection)
        db.commit()
        db.refresh(detection)
        
        try:
            # TODO: 集成第三方产品数据库API
            # 这里暂时返回模拟数据
            product_info = {
                "name": f"产品-{barcode[-6:]}",
                "brand": "示例品牌",
                "category": "食品"
            }
            
            # 模拟营养数据
            nutrition_data = {
                "energy_kcal": 250.0,
                "protein": 8.0,
                "fat": 12.0,
                "carbohydrates": 30.0,
                "sodium": 500.0
            }
            
            # 更新检测记录
            detection.product_name = product_info["name"]
            detection.brand = product_info["brand"]
            detection.category = product_info["category"]
            detection.set_nutrition_data(nutrition_data)
            
            # AI分析
            ai_service = AIService()
            ai_analysis = await ai_service.analyze_nutrition(
                nutrition_data=nutrition_data,
                product_info=product_info,
                user_profile={
                    "age": current_user.age,
                    "health_conditions": current_user.health_conditions,
                    "dietary_preferences": current_user.dietary_preferences,
                    "allergies": current_user.allergies
                }
            )
            
            if ai_analysis and ai_analysis.get("success"):
                detection.set_ai_analysis(
                    score=ai_analysis.get("health_score"),
                    advice=ai_analysis.get("advice"),
                    risk_level=ai_analysis.get("risk_level"),
                    analysis_data=ai_analysis.get("analysis")
                )
            
            # 更新处理时间和状态
            processing_time = (datetime.now() - start_time).total_seconds()
            detection.processing_time = processing_time
            detection.update_status(DetectionStatus.COMPLETED)
            
            # 更新用户统计
            current_user.increment_scan_count()
            
            db.commit()
            db.refresh(detection)
            
            return DetectionResponse(
                id=detection.id,
                detection_type=detection.detection_type,
                status=detection.status,
                product_name=detection.product_name,
                brand=detection.brand,
                category=detection.category,
                nutrition_data=detection.nutrition_data,
                ai_analysis=detection.ai_analysis,
                health_score=detection.health_score,
                risk_level=detection.risk_level,
                created_at=detection.created_at,
                processing_time=processing_time
            )
            
        except Exception as e:
            detection.update_status("failed", str(e))
            db.commit()
            raise
            
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"条形码检测失败: {str(e)}"
        )

@router.get("/history", response_model=List[DetectionListResponse], summary="获取检测历史")
async def get_detection_history(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    detection_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户的检测历史记录
    
    Args:
        skip: 跳过的记录数
        limit: 返回的记录数
        status: 状态筛选
        detection_type: 检测类型筛选
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        检测历史列表
    """
    try:
        # 构建查询
        query = db.query(Detection).filter(Detection.user_id == current_user.id)
        
        # 应用筛选条件
        if status:
            # 将字符串状态转换为枚举类型
            try:
                status_enum = DetectionStatus(status)
                query = query.filter(Detection.status == status_enum)
            except ValueError:
                # 如果状态值无效，返回空结果
                return []
        
        if detection_type:
            # 将字符串检测类型转换为枚举类型
            try:
                detection_type_enum = DetectionType(detection_type)
                query = query.filter(Detection.detection_type == detection_type_enum)
            except ValueError:
                # 如果检测类型值无效，返回空结果
                return []
        
        # 排序和分页
        detections = query.order_by(Detection.created_at.desc()).offset(skip).limit(limit).all()
        
        # 转换为响应模型
        detection_list = []
        for detection in detections:
            detection_list.append(DetectionListResponse(
                id=detection.id,
                detection_type=detection.detection_type,
                status=detection.status,
                product_name=detection.product_name,
                brand=detection.brand,
                health_score=detection.health_score,
                risk_level=detection.risk_level,
                created_at=detection.created_at
            ))
        
        return detection_list
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取检测历史失败: {str(e)}"
        )

@router.get("/{detection_id}", response_model=DetectionResponse, summary="获取检测详情")
async def get_detection_detail(
    detection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取检测详情
    
    Args:
        detection_id: 检测ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        检测详情
        
    Raises:
        HTTPException: 检测不存在或无权访问时抛出异常
    """
    # 查找检测记录
    detection = db.query(Detection).filter(
        Detection.id == detection_id,
        Detection.user_id == current_user.id
    ).first()
    
    if not detection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="检测记录不存在或无权访问"
        )
    
    return DetectionResponse(
        id=detection.id,
        detection_type=detection.detection_type,
        status=detection.status,
        product_name=detection.product_name,
        brand=detection.brand,
        category=detection.category,
        nutrition_data=detection.nutrition_data,
        ai_analysis=detection.ai_analysis,
        health_score=detection.health_score,
        risk_level=detection.risk_level,
        created_at=detection.created_at,
        processing_time=detection.processing_time
    )

@router.post("/{detection_id}/feedback", summary="提交检测反馈")
async def submit_detection_feedback(
    detection_id: int,
    rating: int = Form(..., ge=1, le=5, description="评分(1-5)"),
    feedback_text: Optional[str] = Form(None, description="反馈文本"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    提交检测反馈
    
    Args:
        detection_id: 检测ID
        rating: 评分
        feedback_text: 反馈文本
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        反馈提交确认
    """
    try:
        # 查找检测记录
        detection = db.query(Detection).filter(
            Detection.id == detection_id,
            Detection.user_id == current_user.id
        ).first()
        
        if not detection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="检测记录不存在或无权访问"
            )
        
        # 提交反馈
        detection.submit_feedback(rating, feedback_text)
        db.commit()
        
        return {"message": "反馈提交成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"反馈提交失败: {str(e)}"
        )

@router.delete("/{detection_id}", summary="删除检测记录")
async def delete_detection(
    detection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除检测记录
    
    Args:
        detection_id: 检测ID
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        删除确认
    """
    try:
        # 查找检测记录
        detection = db.query(Detection).filter(
            Detection.id == detection_id,
            Detection.user_id == current_user.id
        ).first()
        
        if not detection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="检测记录不存在或无权访问"
            )
        
        # 删除文件（如果存在）
        if detection.image_url and os.path.exists(detection.image_url):
            try:
                os.remove(detection.image_url)
            except Exception as e:
                print(f"删除文件失败: {e}")
        
        # 删除记录
        db.delete(detection)
        db.commit()
        
        return {"message": "检测记录删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除检测记录失败: {str(e)}"
        )