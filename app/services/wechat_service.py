# app/services/wechat_service.py
# 微信服务模块 - 处理微信小程序相关功能

import httpx
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from ..core.config import settings

class WeChatService:
    """
    微信服务类 - 负责微信小程序用户认证和相关功能
    """
    
    def __init__(self):
        """
        初始化微信服务
        """
        self.app_id = settings.WECHAT_APP_ID
        self.app_secret = settings.WECHAT_APP_SECRET
        
        # 微信API端点
        self.auth_url = "https://api.weixin.qq.com/sns/jscode2session"
        self.access_token_url = "https://api.weixin.qq.com/cgi-bin/token"
        
        # 检查配置
        if not self.is_configured():
            print("⚠️  警告: 微信小程序配置未完成，微信登录功能将不可用")
    
    def is_configured(self) -> bool:
        """
        检查微信服务是否正确配置
        
        Returns:
            配置状态
        """
        return (bool(self.app_id and self.app_id != "your-wechat-app-id") and
                bool(self.app_secret and self.app_secret != "your-wechat-app-secret"))
    
    async def code2session(self, js_code: str) -> Dict[str, Any]:
        """
        通过微信登录凭证code获取session_key和openid
        
        Args:
            js_code: 微信小程序wx.login()获取的code
            
        Returns:
            包含openid、session_key等信息的字典
        """
        if not self.is_configured():
            return {
                "success": False,
                "error": "微信服务未配置"
            }
        
        params = {
            "appid": self.app_id,
            "secret": self.app_secret,
            "js_code": js_code,
            "grant_type": "authorization_code"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.auth_url, params=params)
                response.raise_for_status()
                
                result = response.json()
                
                # 检查是否有错误
                if "errcode" in result:
                    error_messages = {
                        40029: "js_code无效",
                        45011: "频率限制，每个用户每分钟100次",
                        40013: "不合法的AppID",
                        40125: "不合法的密钥"
                    }
                    error_msg = error_messages.get(result["errcode"], f"微信API错误: {result.get('errmsg', '未知错误')}")
                    
                    return {
                        "success": False,
                        "error": error_msg,
                        "errcode": result["errcode"]
                    }
                
                # 成功获取用户信息
                if "openid" in result:
                    return {
                        "success": True,
                        "openid": result["openid"],
                        "session_key": result.get("session_key"),
                        "unionid": result.get("unionid"),  # 如果绑定了开放平台
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "error": "微信API返回数据异常"
                    }
                    
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": f"网络请求失败: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"微信认证异常: {str(e)}"
            }
    
    async def get_access_token(self) -> Dict[str, Any]:
        """
        获取微信小程序的access_token
        用于调用其他微信API
        
        Returns:
            包含access_token的字典
        """
        if not self.is_configured():
            return {
                "success": False,
                "error": "微信服务未配置"
            }
        
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.access_token_url, params=params)
                response.raise_for_status()
                
                result = response.json()
                
                if "access_token" in result:
                    return {
                        "success": True,
                        "access_token": result["access_token"],
                        "expires_in": result["expires_in"],
                        "expires_at": (datetime.now() + timedelta(seconds=result["expires_in"])).isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "error": f"获取access_token失败: {result.get('errmsg', '未知错误')}",
                        "errcode": result.get("errcode")
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"获取access_token异常: {str(e)}"
            }
    
    def decrypt_user_info(self, encrypted_data: str, iv: str, session_key: str) -> Dict[str, Any]:
        """
        解密微信用户敏感数据
        
        Args:
            encrypted_data: 加密数据
            iv: 初始向量
            session_key: 会话密钥
            
        Returns:
            解密后的用户信息
        """
        try:
            import base64
            from Crypto.Cipher import AES
            
            # Base64解码
            session_key = base64.b64decode(session_key)
            encrypted_data = base64.b64decode(encrypted_data)
            iv = base64.b64decode(iv)
            
            # AES解密
            cipher = AES.new(session_key, AES.MODE_CBC, iv)
            decrypted = cipher.decrypt(encrypted_data)
            
            # 去除填充
            decrypted = decrypted[:-decrypted[-1]]
            
            # 解析JSON
            user_info = json.loads(decrypted.decode('utf-8'))
            
            return {
                "success": True,
                "user_info": user_info
            }
            
        except ImportError:
            return {
                "success": False,
                "error": "缺少加密库，请安装pycryptodome: pip install pycryptodome"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"用户信息解密失败: {str(e)}"
            }
    
    async def send_template_message(self, access_token: str, openid: str, template_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送模板消息（需要模板消息权限）
        
        Args:
            access_token: 访问令牌
            openid: 用户openid
            template_id: 模板ID
            data: 模板数据
            
        Returns:
            发送结果
        """
        url = f"https://api.weixin.qq.com/cgi-bin/message/wxopen/template/send?access_token={access_token}"
        
        payload = {
            "touser": openid,
            "template_id": template_id,
            "data": data
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                
                if result.get("errcode") == 0:
                    return {
                        "success": True,
                        "msgid": result.get("msgid")
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get("errmsg", "发送失败"),
                        "errcode": result.get("errcode")
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"发送模板消息异常: {str(e)}"
            }
    
    def validate_signature(self, signature: str, timestamp: str, nonce: str, token: str) -> bool:
        """
        验证微信服务器签名
        
        Args:
            signature: 微信签名
            timestamp: 时间戳
            nonce: 随机数
            token: 验证令牌
            
        Returns:
            验证结果
        """
        try:
            import hashlib
            
            # 将token、timestamp、nonce三个参数进行字典序排序
            tmp_list = [token, timestamp, nonce]
            tmp_list.sort()
            
            # 将三个参数字符串拼接成一个字符串进行sha1加密
            tmp_str = ''.join(tmp_list)
            hash_obj = hashlib.sha1(tmp_str.encode('utf-8'))
            hash_str = hash_obj.hexdigest()
            
            # 开发者获得加密后的字符串可与signature对比，标识该请求来源于微信
            return hash_str == signature
            
        except Exception:
            return False
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        获取微信服务信息
        
        Returns:
            服务配置信息
        """
        return {
            "service_name": "WeChat Mini Program Service",
            "app_id": self.app_id if self.is_configured() else "未配置",
            "configured": self.is_configured(),
            "features": [
                "用户登录认证",
                "获取用户信息",
                "模板消息推送",
                "签名验证"
            ],
            "endpoints": {
                "auth": self.auth_url,
                "access_token": self.access_token_url
            }
        }

# 创建全局微信服务实例
wechat_service = WeChatService()