#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
营养扫描应用示例
使用Qwen API分析食物营养信息
"""

import os
import json
import base64
from typing import Dict, List, Optional
from http import HTTPStatus
from dashscope import MultiModalConversation


class NutritionScanner:
    """营养扫描器类"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化营养扫描器
        
        Args:
            api_key: API密钥，如果不提供则从环境变量获取
        """
        self.api_key = api_key or os.getenv('DASHSCOPE_API_KEY')
        if not self.api_key:
            raise ValueError("请设置DASHSCOPE_API_KEY环境变量或提供api_key参数")
    
    def encode_image(self, image_path: str) -> str:
        """
        将图片编码为base64格式
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            base64编码的图片字符串
        """
        try:
            with open(image_path, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            raise FileNotFoundError(f"无法读取图片文件 {image_path}: {e}")
    
    def analyze_food_image(self, image_path: str, language: str = "中文") -> Dict:
        """
        分析食物图片的营养信息
        
        Args:
            image_path: 图片文件路径
            language: 分析结果语言，默认中文
            
        Returns:
            包含营养分析结果的字典
        """
        # 编码图片
        image_base64 = self.encode_image(image_path)
        
        # 构建系统提示
        system_prompt = f"""
你是一个专业的营养分析师。请分析图片中的食物，并用{language}提供详细的营养信息。

请按照以下JSON格式返回结果：
{{
    "food_items": [
        {{
            "name": "食物名称",
            "estimated_weight": "估计重量(克)",
            "calories_per_100g": "每100克热量(千卡)",
            "total_calories": "总热量(千卡)",
            "macronutrients": {{
                "protein": "蛋白质(克)",
                "carbohydrates": "碳水化合物(克)",
                "fat": "脂肪(克)",
                "fiber": "膳食纤维(克)"
            }},
            "micronutrients": {{
                "vitamin_c": "维生素C(毫克)",
                "calcium": "钙(毫克)",
                "iron": "铁(毫克)"
            }},
            "health_score": "健康评分(1-10)",
            "health_notes": "健康建议"
        }}
    ],
    "total_nutrition": {{
        "total_calories": "总热量",
        "total_protein": "总蛋白质",
        "total_carbs": "总碳水化合物",
        "total_fat": "总脂肪"
    }},
    "dietary_recommendations": "饮食建议"
}}

请确保返回的是有效的JSON格式。
"""
        
        # 构建消息
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "image": f"data:image/jpeg;base64,{image_base64}"
                    },
                    {
                        "text": "请分析这张图片中的食物营养信息"
                    }
                ]
            }
        ]
        
        try:
            # 调用API
            responses = MultiModalConversation.call(
                model='qwen-vl-plus',  # 使用视觉语言模型
                api_key=self.api_key,
                messages=messages,
                stream=False,
                result_format='message',
                temperature=0.1,  # 较低的温度以获得更准确的结果
                top_p=0.8
            )
            
            # 处理响应
            if responses.status_code == HTTPStatus.OK:
                content = responses.output.choices[0].message.content
                
                # 尝试解析JSON
                try:
                    # 提取JSON部分（可能包含其他文本）
                    start_idx = content.find('{')
                    end_idx = content.rfind('}') + 1
                    if start_idx != -1 and end_idx != 0:
                        json_str = content[start_idx:end_idx]
                        result = json.loads(json_str)
                        result['raw_response'] = content
                        return result
                    else:
                        return {
                            'error': '无法解析JSON格式',
                            'raw_response': content
                        }
                except json.JSONDecodeError:
                    return {
                        'error': 'JSON解析失败',
                        'raw_response': content
                    }
            else:
                return {
                    'error': f'API调用失败: {responses.code} - {responses.message}',
                    'request_id': responses.request_id
                }
                
        except Exception as e:
            return {
                'error': f'分析过程中出现错误: {str(e)}'
            }
    
    def get_nutrition_advice(self, nutrition_data: Dict, user_profile: Dict = None) -> str:
        """
        基于营养数据提供个性化建议
        
        Args:
            nutrition_data: 营养分析数据
            user_profile: 用户信息（年龄、性别、体重、身高、活动水平等）
            
        Returns:
            个性化营养建议
        """
        if 'error' in nutrition_data:
            return "无法提供建议，营养分析数据有误"
        
        # 构建用户信息提示
        user_info = ""
        if user_profile:
            user_info = f"""
用户信息：
- 年龄：{user_profile.get('age', '未知')}
- 性别：{user_profile.get('gender', '未知')}
- 体重：{user_profile.get('weight', '未知')}kg
- 身高：{user_profile.get('height', '未知')}cm
- 活动水平：{user_profile.get('activity_level', '未知')}
- 健康目标：{user_profile.get('health_goal', '未知')}
"""
        
        # 构建营养建议提示
        prompt = f"""
作为专业营养师，请基于以下营养分析数据{user_info and '和用户信息'}，提供详细的营养建议：

营养分析数据：
{json.dumps(nutrition_data, ensure_ascii=False, indent=2)}

{user_info}

请提供：
1. 这餐食物的营养评价
2. 优点和不足
3. 改进建议
4. 搭配建议
5. 注意事项
"""
        
        try:
            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            responses = MultiModalConversation.call(
                model='qwen-plus',
                api_key=self.api_key,
                messages=messages,
                stream=False,
                result_format='message',
                temperature=0.3,
                top_p=0.9
            )
            
            if responses.status_code == HTTPStatus.OK:
                return responses.output.choices[0].message.content
            else:
                return f"获取建议失败: {responses.code} - {responses.message}"
                
        except Exception as e:
            return f"获取建议时出现错误: {str(e)}"


def main():
    """主函数示例"""
    # 初始化扫描器
    try:
        scanner = NutritionScanner()
        print("营养扫描器初始化成功！")
    except ValueError as e:
        print(f"初始化失败: {e}")
        return
    
    # 示例：分析食物图片
    image_path = "food_image.jpg"  # 替换为实际图片路径
    
    if os.path.exists(image_path):
        print(f"正在分析图片: {image_path}")
        
        # 分析营养信息
        nutrition_result = scanner.analyze_food_image(image_path)
        
        if 'error' in nutrition_result:
            print(f"分析失败: {nutrition_result['error']}")
        else:
            print("\n=== 营养分析结果 ===")
            print(json.dumps(nutrition_result, ensure_ascii=False, indent=2))
            
            # 获取个性化建议
            user_profile = {
                'age': 30,
                'gender': '男',
                'weight': 70,
                'height': 175,
                'activity_level': '中等',
                'health_goal': '保持健康'
            }
            
            print("\n=== 个性化营养建议 ===")
            advice = scanner.get_nutrition_advice(nutrition_result, user_profile)
            print(advice)
    else:
        print(f"图片文件不存在: {image_path}")
        print("请将要分析的食物图片命名为 'food_image.jpg' 并放在当前目录下")


if __name__ == '__main__':
    main()