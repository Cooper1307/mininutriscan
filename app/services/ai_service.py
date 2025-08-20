# app/services/ai_service.py
# AI服务模块 - 集成Qwen3大语言模型

import json
import aiohttp
from typing import Dict, Any, Optional
from ..core.config import settings

class AIService:
    """
    AI服务类 - 负责与Qwen3 API进行交互
    提供智能问答、营养分析、健康建议等功能
    """
    
    def __init__(self):
        """
        初始化AI服务
        注意：不再在初始化时强制检查API密钥，而是在实际使用时检查
        """
        self.api_key = settings.QWEN_API_KEY
        self.api_url = settings.QWEN_API_URL
        self.model = settings.QWEN_MODEL
        
        # 记录配置状态但不抛出异常
        if not self.api_key or self.api_key == "your-qwen-api-key-here":
            print("⚠️  警告: Qwen API密钥未正确配置，AI功能将不可用")
            print("💡 请在.env文件中设置QWEN_API_KEY以启用AI功能")
    
    async def _make_request(self, messages: list, temperature: float = 0.7) -> Dict[str, Any]:
        """
        向Qwen3 API发送请求
        
        Args:
            messages: 对话消息列表
            temperature: 生成温度，控制回答的随机性
            
        Returns:
            API响应结果
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "input": {
                "messages": messages
            },
            "parameters": {
                "temperature": temperature,
                "max_tokens": 1500,
                "top_p": 0.8
            }
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=30.0)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                ) as response:
                    response.raise_for_status()
                    return await response.json()
                
        except aiohttp.ClientError as e:
            raise Exception(f"API请求失败: {str(e)}")
        except Exception as e:
            raise Exception(f"AI服务调用异常: {str(e)}")
    
    async def analyze_nutrition(self, nutrition_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析营养成分数据，提供健康建议
        
        Args:
            nutrition_data: 营养成分数据字典
            
        Returns:
            包含分析结果和建议的字典
        """
        # 构建营养分析的提示词
        nutrition_text = json.dumps(nutrition_data, ensure_ascii=False, indent=2)
        
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的营养师AI助手。请分析用户提供的食品营养成分数据，给出专业的营养评估和健康建议。回答要简洁明了，适合普通消费者理解。"
            },
            {
                "role": "user",
                "content": f"请分析以下食品的营养成分数据，并给出健康建议：\n{nutrition_text}"
            }
        ]
        
        try:
            response = await self._make_request(messages)
            
            # 解析响应
            if "output" in response and "text" in response["output"]:
                analysis_result = response["output"]["text"]
                
                # 基于营养数据计算健康评分（简单算法）
                health_score = self._calculate_health_score(nutrition_data)
                
                # 基于评分确定风险等级
                risk_level = self._determine_risk_level(health_score)
                
                # 提取建议（从分析文本中提取或生成简短建议）
                advice = self._extract_advice(analysis_result)
                
                return {
                    "success": True,
                    "analysis": analysis_result,
                    "health_score": health_score,
                    "advice": advice,
                    "risk_level": risk_level,
                    "nutrition_data": nutrition_data,
                    "timestamp": json.dumps({"timestamp": "now"}, default=str)
                }
            else:
                raise Exception("API响应格式异常")
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "nutrition_data": nutrition_data
            }
    
    def _calculate_health_score(self, nutrition_data: Dict[str, Any]) -> float:
        """
        基于营养数据计算健康评分（0-100分）
        
        Args:
            nutrition_data: 营养数据字典
            
        Returns:
            健康评分（0-100）
        """
        score = 70.0  # 基础分数
        
        try:
            # 提取营养数值
            energy = self._extract_nutrition_value(nutrition_data, 'energy')
            protein = self._extract_nutrition_value(nutrition_data, 'protein')
            fat = self._extract_nutrition_value(nutrition_data, 'fat')
            carbohydrate = self._extract_nutrition_value(nutrition_data, 'carbohydrate')
            sodium = self._extract_nutrition_value(nutrition_data, 'sodium')
            
            # 能量评估（以每100g为基准）
            if energy:
                if energy < 1000:  # 低热量
                    score += 5
                elif energy > 2500:  # 高热量
                    score -= 10
            
            # 蛋白质评估
            if protein:
                if protein >= 10:  # 高蛋白
                    score += 10
                elif protein >= 5:  # 中等蛋白
                    score += 5
            
            # 脂肪评估
            if fat:
                if fat > 20:  # 高脂肪
                    score -= 15
                elif fat > 10:  # 中等脂肪
                    score -= 5
                elif fat < 3:  # 低脂肪
                    score += 5
            
            # 钠含量评估
            if sodium:
                if sodium > 600:  # 高钠
                    score -= 15
                elif sodium > 300:  # 中等钠
                    score -= 5
                elif sodium < 100:  # 低钠
                    score += 5
            
            # 确保分数在0-100范围内
            score = max(0, min(100, score))
            
        except Exception:
            # 如果计算出错，返回中等分数
            score = 60.0
        
        return round(score, 1)
    
    def _extract_nutrition_value(self, nutrition_data: Dict[str, Any], key: str) -> Optional[float]:
        """
        从营养数据中提取数值
        
        Args:
            nutrition_data: 营养数据字典
            key: 营养成分键名
            
        Returns:
            营养成分数值
        """
        if key in nutrition_data:
            value = nutrition_data[key]
            if isinstance(value, dict) and 'value' in value:
                return float(value['value'])
            elif isinstance(value, (int, float)):
                return float(value)
        return None
    
    def _determine_risk_level(self, health_score: float) -> str:
        """
        基于健康评分确定风险等级
        
        Args:
            health_score: 健康评分
            
        Returns:
            风险等级字符串
        """
        if health_score >= 80:
            return "LOW"
        elif health_score >= 60:
            return "MEDIUM"
        elif health_score >= 40:
            return "HIGH"
        else:
            return "VERY_HIGH"
    
    def _extract_advice(self, analysis_text: str) -> str:
        """
        从分析文本中提取简短建议
        
        Args:
            analysis_text: AI分析文本
            
        Returns:
            简短建议
        """
        # 简单的建议提取逻辑
        if "建议" in analysis_text:
            # 尝试提取建议部分
            lines = analysis_text.split('\n')
            advice_lines = []
            for line in lines:
                if "建议" in line or "推荐" in line or "应该" in line:
                    advice_lines.append(line.strip())
                    if len(advice_lines) >= 3:  # 最多3条建议
                        break
            
            if advice_lines:
                return " ".join(advice_lines)
        
        # 如果没有找到具体建议，返回通用建议
        return "建议均衡饮食，适量运动，关注营养成分标签。"
    
    async def answer_question(self, question: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        回答用户关于食品安全的问题
        
        Args:
            question: 用户问题
            context: 可选的上下文信息
            
        Returns:
            包含回答的字典
        """
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的食品安全AI助手。请回答用户关于食品安全、营养健康的问题。回答要准确、专业但易懂，适合普通消费者。如果涉及严重的食品安全问题，请建议用户咨询专业机构或就医。"
            }
        ]
        
        # 如果有上下文，先添加上下文
        if context:
            messages.append({
                "role": "user",
                "content": f"背景信息：{context}"
            })
        
        messages.append({
            "role": "user",
            "content": question
        })
        
        try:
            response = await self._make_request(messages)
            
            if "output" in response and "text" in response["output"]:
                answer = response["output"]["text"]
                
                return {
                    "success": True,
                    "question": question,
                    "answer": answer,
                    "context": context
                }
            else:
                raise Exception("API响应格式异常")
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "question": question
            }
    
    async def generate_health_tips(self, user_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        根据用户画像生成个性化健康建议
        
        Args:
            user_profile: 用户画像数据（年龄、性别、健康状况等）
            
        Returns:
            包含健康建议的字典
        """
        profile_text = ""
        if user_profile:
            profile_text = f"用户信息：{json.dumps(user_profile, ensure_ascii=False)}"
        
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的营养健康AI助手。请根据用户信息生成个性化的食品安全和营养健康建议。建议要实用、具体，适合日常生活应用。"
            },
            {
                "role": "user",
                "content": f"请为用户生成个性化的健康饮食建议。{profile_text if profile_text else '请提供通用的健康饮食建议。'}"
            }
        ]
        
        try:
            response = await self._make_request(messages, temperature=0.8)
            
            if "output" in response and "text" in response["output"]:
                tips = response["output"]["text"]
                
                return {
                    "success": True,
                    "tips": tips,
                    "user_profile": user_profile
                }
            else:
                raise Exception("API响应格式异常")
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "user_profile": user_profile
            }
    
    def is_configured(self) -> bool:
        """
        检查AI服务是否正确配置
        
        Returns:
            配置状态
        """
        return bool(self.api_key and self.api_key != "your-qwen-api-key-here")
    
    async def generate_health_advice(self, user_profile: dict, nutrition_data: dict) -> dict:
        """
        生成个性化健康建议
        
        Args:
            user_profile: 用户档案信息
            nutrition_data: 营养数据
            
        Returns:
            健康建议结果
        """
        try:
            if not self.api_key:
                return {
                    "success": False,
                    "error": "Qwen API未配置",
                    "advice": "请配置AI服务以获取个性化建议"
                }
            
            # 构建提示词
            prompt = f"""
            基于以下用户信息和营养数据，生成个性化健康建议：
            
            用户信息：
            - 年龄：{user_profile.get('age', '未知')}
            - 健康状况：{user_profile.get('health_conditions', '无')}
            - 饮食偏好：{user_profile.get('dietary_preferences', '无')}
            - 过敏信息：{user_profile.get('allergies', '无')}
            
            营养数据：
            - 能量：{nutrition_data.get('energy_kcal', 0)} kcal
            - 蛋白质：{nutrition_data.get('protein', 0)} g
            - 脂肪：{nutrition_data.get('fat', 0)} g
            - 碳水化合物：{nutrition_data.get('carbohydrates', 0)} g
            - 钠：{nutrition_data.get('sodium', 0)} mg
            
            请提供：
            1. 营养评估
            2. 健康建议
            3. 注意事项
            4. 改善建议
            
            请以JSON格式返回，包含assessment、advice、precautions、improvements字段。
            """
            
            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的营养师AI助手。请分析用户提供的信息，给出专业的营养评估和健康建议。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # 调用AI API
            response = await self._make_request(messages)
            
            if "output" in response and "text" in response["output"]:
                try:
                    # 尝试解析JSON响应
                    advice_data = json.loads(response["output"]["text"])
                    return {
                        "success": True,
                        "assessment": advice_data.get("assessment", "营养成分分析完成"),
                        "advice": advice_data.get("advice", "建议保持均衡饮食"),
                        "precautions": advice_data.get("precautions", "注意适量摄入"),
                        "improvements": advice_data.get("improvements", "可适当调整饮食结构")
                    }
                except json.JSONDecodeError:
                    # 如果不是JSON格式，直接返回文本
                    return {
                        "success": True,
                        "assessment": "营养成分分析完成",
                        "advice": response["output"]["text"],
                        "precautions": "请根据个人情况调整",
                        "improvements": "建议咨询专业营养师"
                    }
            else:
                return {
                    "success": False,
                    "error": "API响应格式异常",
                    "advice": "暂时无法生成个性化建议"
                }
                
        except Exception as e:
            print(f"生成健康建议失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "advice": "生成建议时发生错误"
            }
    
    async def generate_nutrition_report(self, detections_data: list, user_profile: dict, stats: dict, time_range: str) -> dict:
        """
        生成营养分析报告
        
        Args:
            detections_data: 检测数据列表
            user_profile: 用户档案信息
            stats: 统计数据
            time_range: 时间范围
            
        Returns:
            营养报告结果
        """
        try:
            if not self.api_key:
                return {
                    "success": False,
                    "error": "Qwen API未配置",
                    "summary": "请配置AI服务以生成详细报告",
                    "recommendations": ["建议保持均衡饮食", "注意营养搭配"]
                }
            
            # 构建提示词
            prompt = f"""
            基于以下用户信息和营养检测数据，生成详细的营养分析报告：
            
            时间范围：{time_range}
            
            用户信息：
            - 年龄：{user_profile.get('age', '未知')}
            - 健康状况：{user_profile.get('health_conditions', '无')}
            - 饮食偏好：{user_profile.get('dietary_preferences', '无')}
            - 过敏信息：{user_profile.get('allergies', '无')}
            
            统计数据：
            - 总检测次数：{stats.get('total_detections', 0)}
            - 平均营养评分：{stats.get('avg_health_score', 0)}
            - 平均营养摄入：{stats.get('avg_nutrition', {})}
            - 分类分布：{stats.get('category_distribution', {})}
            
            检测数据样本（前5条）：
            {str(detections_data[:5]) if detections_data else '无数据'}
            
            请生成包含以下内容的营养分析报告：
            1. 营养摄入总结
            2. 健康风险评估
            3. 营养均衡分析
            4. 个性化建议
            5. 改善方案
            
            请以JSON格式返回，包含summary和recommendations字段，其中recommendations为字符串数组。
            """
            
            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的营养师AI助手。请根据用户的营养数据生成详细的分析报告。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # 调用AI API
            response = await self._make_request(messages)
            
            if "output" in response and "text" in response["output"]:
                try:
                    # 尝试解析JSON响应
                    report_data = json.loads(response["output"]["text"])
                    return {
                        "success": True,
                        "summary": report_data.get("summary", "营养分析报告生成完成"),
                        "recommendations": report_data.get("recommendations", ["建议保持均衡饮食", "注意营养搭配"])
                    }
                except json.JSONDecodeError:
                    # 如果不是JSON格式，处理文本响应
                    content = response["output"]["text"]
                    # 简单分割为总结和建议
                    lines = content.split('\n')
                    summary_lines = []
                    recommendations = []
                    
                    current_section = "summary"
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        if "建议" in line or "推荐" in line or "改善" in line:
                            current_section = "recommendations"
                        
                        if current_section == "summary":
                            summary_lines.append(line)
                        else:
                            if line.startswith(('-', '•', '1.', '2.', '3.', '4.', '5.')):
                                recommendations.append(line)
                    
                    return {
                        "success": True,
                        "summary": '\n'.join(summary_lines) if summary_lines else content,
                        "recommendations": recommendations if recommendations else ["建议保持均衡饮食", "注意营养搭配"]
                    }
            else:
                return {
                    "success": False,
                    "error": "API响应格式异常",
                    "summary": "暂时无法生成详细报告",
                    "recommendations": ["建议保持均衡饮食", "注意营养搭配"]
                }
                
        except Exception as e:
            print(f"生成营养报告失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "summary": "生成报告时发生错误",
                "recommendations": ["建议咨询专业营养师"]
            }
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        获取服务信息
        
        Returns:
            服务配置信息
        """
        return {
            "service_name": "Qwen3 AI Service",
            "model": self.model,
            "api_url": self.api_url,
            "configured": self.is_configured(),
            "features": [
                "营养成分分析",
                "智能问答",
                "健康建议生成",
                "个性化推荐",
                "营养报告生成"
            ]
        }

# 创建全局AI服务实例
# 现在初始化不会抛出异常，而是在使用时检查配置
ai_service = AIService()