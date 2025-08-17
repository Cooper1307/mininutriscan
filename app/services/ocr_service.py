# app/services/ocr_service.py
# OCR服务模块 - 集成腾讯云和阿里云OCR服务

import base64
import json
from typing import Dict, Any, Optional, List
from PIL import Image
import io

# 腾讯云SDK
try:
    from tencentcloud.common import credential
    from tencentcloud.common.profile.client_profile import ClientProfile
    from tencentcloud.common.profile.http_profile import HttpProfile
    from tencentcloud.ocr.v20181119 import ocr_client, models
    TENCENT_AVAILABLE = True
except ImportError:
    TENCENT_AVAILABLE = False

# 阿里云SDK
try:
    from alibabacloud_ocr_api20210707.client import Client as OcrClient
    from alibabacloud_tea_openapi import models as open_api_models
    from alibabacloud_ocr_api20210707 import models as ocr_models
    ALIBABA_AVAILABLE = True
except ImportError:
    ALIBABA_AVAILABLE = False

from ..core.config import settings

class OCRService:
    """
    OCR服务类 - 负责图像文字识别
    支持腾讯云和阿里云OCR服务
    """
    
    def __init__(self):
        """
        初始化OCR服务
        """
        self.tencent_configured = self._check_tencent_config()
        self.alibaba_configured = self._check_alibaba_config()
        
        if not (self.tencent_configured or self.alibaba_configured):
            print("⚠️  警告: 没有配置任何OCR服务，图像识别功能将不可用")
    
    def _check_tencent_config(self) -> bool:
        """
        检查腾讯云配置
        """
        return (TENCENT_AVAILABLE and 
                settings.TENCENT_SECRET_ID and 
                settings.TENCENT_SECRET_KEY and
                settings.TENCENT_SECRET_ID != "your-tencent-secret-id")
    
    def _check_alibaba_config(self) -> bool:
        """
        检查阿里云配置
        """
        return (ALIBABA_AVAILABLE and 
                settings.ALIBABA_ACCESS_KEY_ID and 
                settings.ALIBABA_ACCESS_KEY_SECRET and
                settings.ALIBABA_ACCESS_KEY_ID != "your-ali-access-key-id")
    
    def _image_to_base64(self, image_path: str) -> str:
        """
        将图片转换为base64编码
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            base64编码的图片数据
        """
        try:
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
                return base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            raise Exception(f"图片读取失败: {str(e)}")
    
    def _preprocess_image(self, image_path: str) -> str:
        """
        预处理图片（压缩、格式转换等）
        
        Args:
            image_path: 原始图片路径
            
        Returns:
            处理后的图片base64数据
        """
        try:
            # 打开图片
            with Image.open(image_path) as img:
                # 转换为RGB模式（如果是RGBA等）
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 压缩图片（如果太大）
                max_size = (1920, 1920)
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # 保存到内存
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                image_data = buffer.getvalue()
                
                return base64.b64encode(image_data).decode('utf-8')
                
        except Exception as e:
            raise Exception(f"图片预处理失败: {str(e)}")
    
    async def recognize_nutrition_label(self, image_path: str, provider: str = "auto") -> Dict[str, Any]:
        """
        识别营养成分表
        
        Args:
            image_path: 图片文件路径
            provider: OCR服务提供商 ("tencent", "alibaba", "auto")
            
        Returns:
            识别结果字典
        """
        # 自动选择可用的服务
        if provider == "auto":
            if self.tencent_configured:
                provider = "tencent"
            elif self.alibaba_configured:
                provider = "alibaba"
            else:
                return {
                    "success": False,
                    "error": "没有可用的OCR服务",
                    "provider": None
                }
        
        try:
            if provider == "tencent" and self.tencent_configured:
                return await self._tencent_ocr(image_path)
            elif provider == "alibaba" and self.alibaba_configured:
                return await self._alibaba_ocr(image_path)
            else:
                return {
                    "success": False,
                    "error": f"OCR服务 {provider} 未配置或不可用",
                    "provider": provider
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": provider
            }
    
    async def _tencent_ocr(self, image_path: str) -> Dict[str, Any]:
        """
        使用腾讯云OCR识别
        
        Args:
            image_path: 图片路径
            
        Returns:
            识别结果
        """
        try:
            # 创建认证对象
            cred = credential.Credential(settings.TENCENT_SECRET_ID, settings.TENCENT_SECRET_KEY)
            
            # 实例化HTTP配置
            httpProfile = HttpProfile()
            httpProfile.endpoint = "ocr.tencentcloudapi.com"
            
            # 实例化客户端配置
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            
            # 实例化OCR客户端
            client = ocr_client.OcrClient(cred, settings.TENCENT_REGION, clientProfile)
            
            # 预处理图片
            image_base64 = self._preprocess_image(image_path)
            
            # 实例化请求对象
            req = models.GeneralBasicOCRRequest()
            params = {
                "ImageBase64": image_base64,
                "LanguageType": "auto"
            }
            req.from_json_string(json.dumps(params))
            
            # 发起请求
            resp = client.GeneralBasicOCR(req)
            result = json.loads(resp.to_json_string())
            
            # 解析结果
            if "TextDetections" in result:
                texts = []
                confidence_sum = 0
                text_parts = []
                
                for detection in result["TextDetections"]:
                    detected_text = detection["DetectedText"]
                    confidence = detection["Confidence"]
                    
                    text_parts.append(detected_text)
                    confidence_sum += confidence
                    
                    texts.append({
                        "text": detected_text,
                        "confidence": confidence,
                        "polygon": detection.get("Polygon", [])
                    })
                
                avg_confidence = confidence_sum / len(texts) if texts else 0
                full_text = ' '.join(text_parts)
                
                return {
                    "success": True,
                    "provider": "tencent",
                    "text": full_text,
                    "confidence": avg_confidence,
                    "texts": texts,
                    "raw_result": result
                }
            else:
                return {
                    "success": False,
                    "error": "未检测到文字",
                    "provider": "tencent"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"腾讯云OCR调用失败: {str(e)}",
                "provider": "tencent"
            }
    
    async def _alibaba_ocr(self, image_path: str) -> Dict[str, Any]:
        """
        使用阿里云OCR识别
        
        Args:
            image_path: 图片路径
            
        Returns:
            识别结果
        """
        try:
            # 配置阿里云客户端
            config = open_api_models.Config(
                access_key_id=settings.ALIBABA_ACCESS_KEY_ID,
                access_key_secret=settings.ALIBABA_ACCESS_KEY_SECRET
            )
            config.endpoint = f'ocr-api.{settings.ALIBABA_REGION}.aliyuncs.com'
            
            # 创建客户端
            client = OcrClient(config)
            
            # 预处理图片
            image_base64 = self._preprocess_image(image_path)
            
            # 创建请求 - 使用正确的API调用方式
            request = ocr_models.RecognizeGeneralRequest()
            # 直接设置body为字典
            request.body = {
                "image": image_base64,
                "configure": {
                    "min_size": 16,
                    "output_char_info": True,
                    "output_table": True
                }
            }
            
            # 发起请求
            response = client.recognize_general(request)
            
            # 解析结果
            if response.body and hasattr(response.body, 'data') and response.body.data:
                texts = []
                confidence_sum = 0
                text_parts = []
                
                for item in response.body.data:
                    if hasattr(item, 'text') and item.text:
                        text_parts.append(item.text)
                        confidence = getattr(item, 'confidence', 0.8)
                        confidence_sum += confidence
                        texts.append({
                            "text": item.text,
                            "confidence": confidence,
                            "polygon": getattr(item, 'text_rectangles', [])
                        })
                
                avg_confidence = confidence_sum / len(texts) if texts else 0
                full_text = ' '.join(text_parts)
                
                return {
                    "success": True,
                    "provider": "alibaba",
                    "text": full_text,
                    "confidence": avg_confidence,
                    "texts": texts,
                    "raw_result": response.body.to_map() if hasattr(response.body, 'to_map') else str(response.body)
                }
            else:
                return {
                    "success": False,
                    "error": "未检测到文字",
                    "provider": "alibaba"
                }
                
        except Exception as e:
            # 如果阿里云OCR失败，返回错误但不中断程序
            print(f"⚠️  阿里云OCR调用失败: {str(e)}")
            return {
                "success": False,
                "error": f"阿里云OCR调用失败: {str(e)}",
                "provider": "alibaba"
            }
    
    def extract_nutrition_info(self, ocr_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        从OCR结果中提取营养成分信息
        
        Args:
            ocr_result: OCR识别结果
            
        Returns:
            提取的营养信息
        """
        if not ocr_result.get("success"):
            return {
                "success": False,
                "error": "OCR识别失败"
            }
        
        try:
            texts = ocr_result.get("texts", [])
            all_text = " ".join([item["text"] for item in texts])
            
            # 营养成分关键词匹配
            nutrition_keywords = {
                "energy": ["能量", "热量", "卡路里", "千焦", "kJ", "kcal"],
                "protein": ["蛋白质", "蛋白"],
                "fat": ["脂肪", "总脂肪"],
                "carbohydrate": ["碳水化合物", "糖类"],
                "sodium": ["钠", "盐"],
                "sugar": ["糖", "添加糖"]
            }
            
            extracted_nutrition = {}
            
            # 简单的关键词匹配和数值提取
            import re
            for nutrient, keywords in nutrition_keywords.items():
                for keyword in keywords:
                    pattern = rf"{keyword}[：:]*\s*(\d+(?:\.\d+)?)\s*([a-zA-Z]+)?"
                    matches = re.findall(pattern, all_text)
                    if matches:
                        value, unit = matches[0]
                        extracted_nutrition[nutrient] = {
                            "value": float(value),
                            "unit": unit or "g",
                            "keyword": keyword
                        }
                        break
            
            return {
                "success": True,
                "nutrition_info": extracted_nutrition,
                "raw_text": all_text,
                "ocr_provider": ocr_result.get("provider")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"营养信息提取失败: {str(e)}"
            }
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        获取OCR服务信息
        
        Returns:
            服务配置信息
        """
        return {
            "service_name": "OCR Service",
            "configured": self.tencent_configured or self.alibaba_configured,
            "tencent_available": self.tencent_configured,
            "alibaba_available": self.alibaba_configured,
            "providers": {
                "tencent": {
                    "available": TENCENT_AVAILABLE,
                    "configured": self.tencent_configured
                },
                "alibaba": {
                    "available": ALIBABA_AVAILABLE,
                    "configured": self.alibaba_configured
                }
            },
            "features": [
                "营养成分表识别",
                "通用文字识别",
                "图片预处理",
                "营养信息提取"
            ]
        }

# 创建全局OCR服务实例
ocr_service = OCRService()