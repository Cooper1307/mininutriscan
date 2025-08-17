#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
营养扫描Web应用 - 基于FastAPI
使用FastAPI替代Flask，利用项目已有的依赖
"""

import os
import base64
import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# 导入营养扫描器
from nutrition_scanner import NutritionScanner

# 创建FastAPI应用
app = FastAPI(
    title="营养扫描器",
    description="基于AI的食物营养分析工具",
    version="1.0.0"
)

# 配置静态文件和模板
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 创建营养扫描器实例
scanner = NutritionScanner()

# 确保上传目录存在
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# 允许的文件类型
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

class UserProfile(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    activity_level: Optional[str] = None
    health_goal: Optional[str] = None

def allowed_file(filename: str) -> bool:
    """检查文件类型是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """主页"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze")
async def analyze_nutrition(
    file: UploadFile = File(...),
    age: Optional[int] = Form(None),
    gender: Optional[str] = Form(None),
    weight: Optional[float] = Form(None),
    height: Optional[float] = Form(None),
    activity_level: Optional[str] = Form(None),
    health_goal: Optional[str] = Form(None)
):
    """分析营养信息"""
    try:
        # 验证文件
        if not file.filename:
            raise HTTPException(status_code=400, detail="未选择文件")
        
        if not allowed_file(file.filename):
            raise HTTPException(status_code=400, detail="不支持的文件类型")
        
        # 读取文件内容
        file_content = await file.read()
        
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="文件大小超过限制")
        
        # 保存文件
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # 分析营养信息
        nutrition_result = await scanner.analyze_food_image(str(file_path))
        
        if not nutrition_result:
            raise HTTPException(status_code=500, detail="营养分析失败")
        
        # 构建用户档案
        user_profile = {
            "age": age,
            "gender": gender,
            "weight": weight,
            "height": height,
            "activity_level": activity_level,
            "health_goal": health_goal
        }
        
        # 获取个性化建议
        advice = None
        if any(user_profile.values()):
            advice = await scanner.get_personalized_advice(nutrition_result, user_profile)
        
        # 清理临时文件
        try:
            os.remove(file_path)
        except:
            pass
        
        return JSONResponse({
            "success": True,
            "nutrition": nutrition_result,
            "advice": advice
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析过程中发生错误: {str(e)}")

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "message": "营养扫描器运行正常"}

if __name__ == "__main__":
    import uvicorn
    
    print("🍎 营养扫描器启动中...")
    print("📱 访问地址: http://localhost:8000")
    print("📋 API文档: http://localhost:8000/docs")
    
    uvicorn.run(
        "web_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )