#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Dify API 交互模块
提供与Dify AI平台的API交互功能
"""

import requests
import json
from typing import Dict, Any, Optional
import sys
import os

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import DIFY_CONFIG

class DifyAPI:
    def __init__(self):
        """初始化Dify API客户端"""
        self.api_key = DIFY_CONFIG["API_KEY"]
        self.base_url = DIFY_CONFIG["API_URL"]
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def send_chat_message(self, 
                           query: str, 
                           inputs: Dict = None, 
                           response_mode: str = "streaming", 
                           conversation_id: str = "", 
                           user: str = "default_user") -> Dict[str, Any]:
        """
        发送聊天消息到Dify API
        
        参数:
            query: 用户查询文本
            inputs: 输入参数字典，默认为空字典
            response_mode: 响应模式，可选 "streaming" 或 "blocking"
            conversation_id: 对话ID，用于继续已有对话
            user: 用户标识
            
        返回:
            API响应结果
        """
        if inputs is None:
            inputs = {}
            
        url = f"{self.base_url}/chat-messages"
        
        payload = {
            "inputs": inputs,
            "query": query,
            "response_mode": response_mode,
            "conversation_id": conversation_id,
            "user": user
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            if response_mode == "blocking":
                return response.json()
            else:
                # 处理流式响应
                return {"status": "streaming", "response": response}
                
        except requests.exceptions.RequestException as e:
            print(f"API请求错误: {e}")
            return {"error": str(e)}
    
    def get_streaming_response(self, response) -> str:
        """
        处理流式响应数据
        
        参数:
            response: 流式响应对象
            
        返回:
            完整的响应文本
        """
        full_response = ""
        
        try:
            for line in response.iter_lines():
                if line:
                    # 移除"data: "前缀并解析JSON
                    line_text = line.decode('utf-8')
                    if line_text.startswith("data: "):
                        data = json.loads(line_text[6:])
                        if "answer" in data:
                            chunk = data.get("answer", "")
                            full_response += chunk
                            # 可在此处添加实时处理逻辑
            
            return full_response
        except Exception as e:
            print(f"处理流式响应时出错: {e}")
            return f"错误: {str(e)}"

# 使用示例
if __name__ == "__main__":
    dify_client = DifyAPI()
    
    # 发送聊天消息示例
    response = dify_client.send_chat_message(
        query="What are the specs of the iPhone 13 Pro Max?",
        user="test_user"
    )
    
    if "error" not in response:
        if response.get("status") == "streaming":
            result = dify_client.get_streaming_response(response["response"])
            print("流式响应结果:", result)
        else:
            print("响应结果:", response)
    else:
        print("错误:", response["error"])
