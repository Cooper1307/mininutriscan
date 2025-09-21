# app/services/ai_service.py
# AI服务模块 - 集成Qwen3大语言模型

import json
import httpx
from typing import Dict, Any, Optional
from ..core.config import settings
# from .validators import AIAnalysisValidator  # 暂时注释掉用于测试

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
        if not self.api_key:
            print("❌ AI服务错误: Qwen API密钥未配置")
            raise Exception("Qwen API密钥未配置")
        
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
        
        print(f"🔄 AI服务: 发送请求到 {self.api_url}")
        print(f"📝 请求数据: {json.dumps(payload, ensure_ascii=False)}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                )
                
                print(f"📡 AI服务响应状态: {response.status_code}")
                response_text = response.text
                print(f"📄 AI服务响应内容: {response_text[:500]}..." if len(response_text) > 500 else f"📄 AI服务响应内容: {response_text}")
                
                if response.status_code != 200:
                    print(f"❌ AI服务API请求失败: {response.status_code}")
                    try:
                        error_data = response.json()
                        print(f"❌ 错误详情: {error_data}")
                        raise Exception(f"API请求失败: {response.status_code} - {error_data}")
                    except json.JSONDecodeError:
                        print(f"❌ 无法解析错误响应: {response_text}")
                        raise Exception(f"API请求失败: {response.status_code} - {response_text}")
                
                try:
                    response_data = response.json()
                    print(f"✅ AI服务请求成功")
                    return response_data
                except json.JSONDecodeError as e:
                    print(f"❌ AI服务响应JSON解析失败: {e}")
                    raise Exception(f"响应JSON解析失败: {e}")
                
        except httpx.TimeoutException:
            print("❌ AI服务请求超时")
            raise Exception("AI服务请求超时")
        except httpx.HTTPError as e:
            print(f"❌ AI服务HTTP错误: {e}")
            raise Exception(f"Qwen API请求失败: {str(e)}")
        except Exception as e:
            print(f"❌ AI服务请求异常: {e}")
            raise Exception(f"AI服务调用异常: {str(e)}")
    
    async def analyze_nutrition(self, nutrition_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析营养成分数据，提供健康建议
        
        Args:
            nutrition_data: 营养成分数据字典
            
        Returns:
            包含分析结果和建议的字典
        """
        # 计算健康评分
        health_score = 80  # 基础分
        
        # 检查各项营养成分是否在合理范围内
        try:
            # 能量
            energy_kj = float(nutrition_data.get('energy_kj', {}).get('value', 0))
            if 1500 <= energy_kj <= 2000:  # 假设这是一餐的合理能量范围
                health_score += 5
            elif energy_kj > 2500 or energy_kj < 1000:
                health_score -= 5
            
            # 蛋白质
            protein = float(nutrition_data.get('protein', {}).get('value', 0))
            if 10 <= protein <= 15:  # 假设这是一餐的合理蛋白质范围
                health_score += 5
            elif protein < 5 or protein > 20:
                health_score -= 5
            
            # 脂肪
            fat = float(nutrition_data.get('fat', {}).get('value', 0))
            if 5 <= fat <= 10:  # 假设这是一餐的合理脂肪范围
                health_score += 5
            elif fat > 15:
                health_score -= 5
            
            # 碳水化合物
            carbs = float(nutrition_data.get('carbohydrate', {}).get('value', 0))
            if 50 <= carbs <= 70:  # 假设这是一餐的合理碳水范围
                health_score += 5
            elif carbs > 90:
                health_score -= 5
            
            # 确保评分在0-100之间
            health_score = max(0, min(100, health_score))
            
        except (TypeError, ValueError) as e:
            print(f"计算健康评分时出错: {e}")
            health_score = 60  # 默认评分
        
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
                
                result = {
                    "success": True,
                    "analysis": analysis_result,
                    "nutrition_data": nutrition_data,
                    "health_score": health_score,
                    "timestamp": json.dumps({"timestamp": "now"}, default=str)
                }
                
                # 数据验证 - 暂时禁用
                # validator = AIAnalysisValidator()
                # validation_result = validator.validate(result)
                # if not validation_result.is_valid:
                #     print(f"AI分析结果验证失败: {validation_result.errors}")
                
                return result
            else:
                raise Exception("API响应格式异常")
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "nutrition_data": nutrition_data,
                "health_score": health_score
            }
    
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
                    result = {
                        "success": True,
                        "assessment": advice_data.get("assessment", "营养成分分析完成"),
                        "advice": advice_data.get("advice", "建议保持均衡饮食"),
                        "precautions": advice_data.get("precautions", "注意适量摄入"),
                        "improvements": advice_data.get("improvements", "可适当调整饮食结构")
                    }
                except json.JSONDecodeError:
                    # 如果不是JSON格式，直接返回文本
                    result = {
                        "success": True,
                        "assessment": "营养成分分析完成",
                        "advice": response["output"]["text"],
                        "precautions": "请根据个人情况调整",
                        "improvements": "建议咨询专业营养师"
                    }
                
                # 数据验证 - 暂时禁用
                # validator = AIAnalysisValidator()
                # validation_result = validator.validate(result)
                # if not validation_result.is_valid:
                #     print(f"健康建议结果验证失败: {validation_result.errors}")
                
                return result
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
                    result = {
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
                    
                    result = {
                        "success": True,
                        "summary": '\n'.join(summary_lines) if summary_lines else content,
                        "recommendations": recommendations if recommendations else ["建议保持均衡饮食", "注意营养搭配"]
                    }
                
                # 数据验证 - 暂时禁用
                # validator = AIAnalysisValidator()
                # validation_result = validator.validate(result)
                # if not validation_result.is_valid:
                #     print(f"营养报告结果验证失败: {validation_result.errors}")
                
                return result
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