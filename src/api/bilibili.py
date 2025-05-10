#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Bilibili API接口模块
包含与Bilibili平台交互的各种API函数
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any

# 导入配置信息
from config import BILIBILI_CONFIG

# 设置日志
logger = logging.getLogger(__name__)

def get_at_messages(page_size: int = 20, page_num: int = 1) -> Dict[str, Any]:
    """
    获取Bilibili账号的@信息列表
    
    Args:
        page_size (int, optional): 每页显示的消息数量. 默认为20.
        page_num (int, optional): 页码, 从1开始. 默认为1.
    
    Returns:
        Dict[str, Any]: 包含@信息的字典，格式为:
        {
            "code": int,  # 状态码，0表示成功
            "message": str,  # 状态信息
            "data": {  # 数据
                "items": List[Dict],  # @消息列表
                "last_id": int,  # 最后一条消息ID
                "has_more": bool  # 是否还有更多消息
            }
        }
        
    Raises:
        Exception: 请求失败时抛出异常
    """
    try:
        url = f"https://api.bilibili.com/x/msgfeed/at?ps={page_size}&pn={page_num}"
        
        headers = {
            "Cookie": f"SESSDATA={BILIBILI_CONFIG['SESSDATA']}; bili_jct={BILIBILI_CONFIG['BILI_JCT']}",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.bilibili.com/",
            "Accept": "application/json, text/plain, */*",
            "Connection": "keep-alive"
        }
        
        response = requests.get(url, headers=headers, allow_redirects=True)
        response.raise_for_status()  # 如果状态码不是200, 抛出异常
        
        data = response.json()
        logger.debug(f"成功获取@信息列表, 页码: {page_num}, 每页数量: {page_size}")
        return data
    except Exception as e:
        logger.error(f"获取@信息列表失败: {str(e)}")
        raise e

def parse_at_messages(response_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    解析@信息列表响应，提取关键信息
    
    Args:
        response_data (Dict[str, Any]): get_at_messages函数返回的原始响应数据
    
    Returns:
        List[Dict[str, Any]]: 处理后的@信息列表，每条包含以下字段:
        [
            {
                "id": int,  # 消息ID
                "user": {  # 发送@的用户信息
                    "uid": int,  # 用户UID
                    "uname": str,  # 用户名
                    "face": str  # 头像URL
                },
                "item": {  # @所在的内容项
                    "type": str,  # 类型(如"reply")
                    "business_id": int,  # 业务ID
                    "title": str,  # 标题
                    "content": str,  # 内容
                    "uri": str,  # 链接
                    "subject_id": int,  # 评论区对应的对象ID (oid)
                    "target_id": int,  # 评论根ID (root)
                    "source_id": int   # 父评论ID (parent)
                },
                "at_time": int  # @时间戳
            },
            ...
        ]
    """
    if response_data["code"] != 0:
        logger.warning(f"获取@信息列表返回错误码: {response_data['code']}, 消息: {response_data['message']}")
        return []
    
    result = []
    if "data" in response_data and "items" in response_data["data"]:
        for item in response_data["data"]["items"]:
            # 提取关键信息
            processed_item = {
                "id": item.get("id", 0),
                "user": {
                    "uid": item.get("user", {}).get("mid", 0),
                    "uname": item.get("user", {}).get("nickname", ""),
                    "face": item.get("user", {}).get("avatar", "")
                },
                "item": {
                    "type": item.get("item", {}).get("type", ""),
                    "business_id": item.get("item", {}).get("business_id", 0),
                    "title": item.get("item", {}).get("title", ""),
                    "content": item.get("item", {}).get("content", ""),
                    "uri": item.get("item", {}).get("uri", ""),
                    # 添加重要的新字段
                    "subject_id": item.get("item", {}).get("subject_id", 0),
                    "target_id": item.get("item", {}).get("target_id", 0),
                    "source_id": item.get("item", {}).get("source_id", 0)
                },
                "at_time": item.get("at_time", 0)
            }
            result.append(processed_item)
    
    return result

def send_reply_comment(oid: int, message: str, root: int = 0, parent: int = 0, type_id: int = 1) -> Dict[str, Any]:
    """
    发送评论回复
    
    Args:
        oid (int): 评论区对应的对象ID，如视频、动态的ID
        message (str): 回复内容
        root (int, optional): 根评论ID，如果直接回复视频则为0
        parent (int, optional): 父评论ID，如果直接回复视频则为0
        type_id (int, optional): 评论区类型，1为视频，默认为1
        
    Returns:
        Dict[str, Any]: 包含回复结果的字典，格式为:
        {
            "code": int,  # 状态码，0表示成功
            "message": str,  # 状态信息
            "data": {  # 数据
                "rpid": int,  # 评论ID
                "rpid_str": str,  # 评论ID的字符串形式
                "dialog": int,  # 对话ID
                "dialog_str": str,  # 对话ID的字符串形式
                "success_action": int,  # 成功操作码
                "success_toast": str  # 成功提示
            }
        }
        
    Raises:
        Exception: 请求失败时抛出异常
    """
    try:
        url = "https://api.bilibili.com/x/v2/reply/add"
        
        headers = {
            "Cookie": f"SESSDATA={BILIBILI_CONFIG['SESSDATA']}; bili_jct={BILIBILI_CONFIG['BILI_JCT']}",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.bilibili.com/",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://www.bilibili.com"
        }
        
        data = {
            "oid": oid,
            "type": type_id,
            "message": message,
            "plat": 1,
            "csrf": BILIBILI_CONFIG['BILI_JCT']
        }
        
        # 如果是回复评论而不是视频
        if root != 0:
            data["root"] = root
        if parent != 0:
            data["parent"] = parent
        
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        
        result = response.json()
        
        if result["code"] == 0:
            logger.info(f"成功发送评论回复，评论ID：{result.get('data', {}).get('rpid', 'unknown')}")
        else:
            logger.warning(f"发送评论回复失败，错误码：{result['code']}，消息：{result['message']}")
        
        return result
    except Exception as e:
        logger.error(f"发送评论回复出错: {str(e)}")
        raise e
