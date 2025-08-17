#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
营养扫描Web应用
基于Flask的简单Web界面
"""

import os
import json
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
from nutrition_scanner import NutritionScanner

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 在生产环境中请使用更安全的密钥

# 配置
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 初始化营养扫描器
try:
    scanner = NutritionScanner()
except ValueError:
    scanner = None
    print("警告: 未设置API密钥，营养分析功能将不可用")


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """处理文件上传和营养分析"""
    if scanner is None:
        return jsonify({
            'error': 'API密钥未配置，请设置DASHSCOPE_API_KEY环境变量'
        }), 500
    
    # 检查是否有文件
    if 'file' not in request.files:
        return jsonify({'error': '没有选择文件'}), 400
    
    file = request.files['file']
    
    # 检查文件名
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    # 检查文件类型
    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的文件类型'}), 400
    
    try:
        # 保存文件
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 获取用户配置
        user_profile = {
            'age': request.form.get('age', type=int),
            'gender': request.form.get('gender'),
            'weight': request.form.get('weight', type=float),
            'height': request.form.get('height', type=float),
            'activity_level': request.form.get('activity_level'),
            'health_goal': request.form.get('health_goal')
        }
        
        # 分析营养信息
        nutrition_result = scanner.analyze_food_image(filepath)
        
        # 获取个性化建议
        advice = ""
        if 'error' not in nutrition_result and any(user_profile.values()):
            advice = scanner.get_nutrition_advice(nutrition_result, user_profile)
        
        # 清理上传的文件
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify({
            'nutrition_result': nutrition_result,
            'advice': advice,
            'success': True
        })
        
    except Exception as e:
        # 清理文件
        try:
            if 'filepath' in locals():
                os.remove(filepath)
        except:
            pass
        
        return jsonify({
            'error': f'处理文件时出现错误: {str(e)}'
        }), 500


@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API接口：分析营养信息"""
    if scanner is None:
        return jsonify({
            'error': 'API密钥未配置'
        }), 500
    
    try:
        data = request.get_json()
        
        if 'image_path' not in data:
            return jsonify({'error': '缺少image_path参数'}), 400
        
        image_path = data['image_path']
        language = data.get('language', '中文')
        
        if not os.path.exists(image_path):
            return jsonify({'error': '图片文件不存在'}), 404
        
        # 分析营养信息
        result = scanner.analyze_food_image(image_path, language)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': f'API调用失败: {str(e)}'
        }), 500


@app.route('/api/advice', methods=['POST'])
def api_advice():
    """API接口：获取营养建议"""
    if scanner is None:
        return jsonify({
            'error': 'API密钥未配置'
        }), 500
    
    try:
        data = request.get_json()
        
        if 'nutrition_data' not in data:
            return jsonify({'error': '缺少nutrition_data参数'}), 400
        
        nutrition_data = data['nutrition_data']
        user_profile = data.get('user_profile')
        
        # 获取建议
        advice = scanner.get_nutrition_advice(nutrition_data, user_profile)
        
        return jsonify({
            'advice': advice,
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'error': f'获取建议失败: {str(e)}'
        }), 500


@app.errorhandler(413)
def too_large(e):
    """文件过大错误处理"""
    return jsonify({'error': '文件过大，请选择小于16MB的图片'}), 413


@app.errorhandler(404)
def not_found(e):
    """404错误处理"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    """500错误处理"""
    return render_template('500.html'), 500


if __name__ == '__main__':
    print("启动营养扫描Web应用...")
    print("请在浏览器中访问: http://localhost:5000")
    
    if scanner is None:
        print("\n警告: API密钥未配置!")
        print("请设置环境变量: set DASHSCOPE_API_KEY=your_api_key")
        print("或在PowerShell中: $env:DASHSCOPE_API_KEY='your_api_key'")
    
    app.run(debug=True, host='0.0.0.0', port=5000)