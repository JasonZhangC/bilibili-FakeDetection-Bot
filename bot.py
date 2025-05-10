#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
B站自动检测和回复机器人主程序
会定期检查新的@信息，并使用Dify API回复
"""

import os
import time
import json
import logging
import re
import sys
from typing import Dict, Any, List, Set
from urllib.parse import urlparse, parse_qs
import requests

# 导入API模块
from src.api.bilibili import get_at_messages, parse_at_messages, send_reply_comment
from src.api.dify import DifyAPI

# 导入配置
from config import BILIBILI_CONFIG, DIFY_CONFIG, SYSTEM_CONFIG, LOG_CONFIG

# 设置日志
def setup_logging():
    """设置日志配置"""
    log_level = getattr(logging, LOG_CONFIG.get("LOG_LEVEL", "INFO"))
    
    # 确保日志目录存在
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 设置日志文件名，包含日期
    log_file = os.path.join(log_dir, f"bot_{time.strftime('%Y%m%d')}.log")
    
    # 配置日志
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("FakeDetectionBot")

# 已处理的消息ID存储
def load_processed_messages() -> Set[int]:
    """加载已处理的消息ID列表"""
    processed_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log/processed_messages.json")
    if os.path.exists(processed_file):
        try:
            with open(processed_file, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception as e:
            logging.error(f"加载已处理消息列表出错: {e}")
            return set()
    else:
        return set()

def save_processed_messages(message_ids: Set[int]):
    """保存已处理的消息ID列表"""
    processed_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log/processed_messages.json")
    try:
        with open(processed_file, "w", encoding="utf-8") as f:
            json.dump(list(message_ids), f)
    except Exception as e:
        logging.error(f"保存已处理消息列表出错: {e}")

def extract_video_oid(uri: str) -> int:
    """
    从视频URI中提取视频OID（用于评论API）
    B站的视频评论API使用AV号（数字ID）作为oid参数
    
    Args:
        uri: 视频链接
    
    Returns:
        视频的OID (AV号)
    """
    try:
        # 直接提取所有可能的数字ID格式
        # 尝试从subject_id参数提取
        if "subject_id=" in uri:
            subject_id_match = re.search(r'subject_id=(\d+)', uri)
            if subject_id_match:
                return int(subject_id_match.group(1))
        
        # 尝试从路径中提取AV号
        av_match = re.search(r'/av(\d+)', uri) or re.search(r'av(\d+)', uri)
        if av_match:
            return int(av_match.group(1))
            
        # 尝试从URL中提取数字ID
        numeric_id_match = re.search(r'/video/(\d+)', uri)
        if numeric_id_match:
            return int(numeric_id_match.group(1))

        # 尝试提取B站特有的numeric_id
        business_id = None
        # 如果URI包含business_id字段，可能是评论区ID
        if "business_id" in uri:
            business_id = re.search(r'business_id=(\d+)', uri)
            if business_id:
                return int(business_id.group(1))
        
        # 解析URL
        parsed_url = urlparse(uri)
        path_parts = parsed_url.path.strip('/').split('/')
        
        # 如果是BV号格式，需要从B站API获取av号
        if path_parts and len(path_parts) >= 2 and path_parts[0] == 'video' and path_parts[1].startswith('BV'):
            bv_id = path_parts[1]
            # 调用B站API将BV号转为av号
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Referer": "https://www.bilibili.com/",
                }
                view_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bv_id}"
                response = requests.get(view_url, headers=headers)
                response.raise_for_status()
                result = response.json()
                if result.get("code") == 0 and "data" in result and "aid" in result["data"]:
                    logging.info(f"成功将BV号 {bv_id} 转换为av号: {result['data']['aid']}")
                    return result["data"]["aid"]
            except Exception as e:
                logging.error(f"BV号转av号失败: {e}, BV: {bv_id}")
                
        # 如果是BV号格式但未从API获取成功，尝试从查询参数中获取相关ID
        if path_parts and any(part.startswith('BV') for part in path_parts):
            query_params = parse_qs(parsed_url.query)
            if 'oid' in query_params:
                return int(query_params['oid'][0])
        
        # 最后手段：从URI中提取任何看起来像ID的数字
        # 优先检查以下模式:
        # 1. video/{number}
        # 2. 任何包含数字ID的路径段
        for pattern in [r'/video/(\d+)', r'/(\d+)']:
            id_match = re.search(pattern, uri)
            if id_match:
                return int(id_match.group(1))
        
        # 如果URI中包含"oid="参数
        oid_match = re.search(r'oid=(\d+)', uri)
        if oid_match:
            return int(oid_match.group(1))
            
        # 如果所有方法都失败，返回0表示无法提取
        return 0
    except Exception as e:
        logging.error(f"从URI提取视频OID失败: {e}, URI: {uri}")
        return 0

def process_at_message(message: Dict[str, Any], dify_client: DifyAPI, logger: logging.Logger) -> bool:
    """
    处理单条@消息
    
    Args:
        message: 解析后的@消息
        dify_client: Dify API客户端
        logger: 日志记录器
    
    Returns:
        bool: 处理是否成功
    """
    try:
        # 获取视频标题作为查询内容
        title = message["item"]["title"]
        if not title:
            logger.warning(f"消息 {message['id']} 没有标题，跳过处理")
            return False
        
        logger.info(f"处理@消息 ID:{message['id']}, 标题: {title}")
        
        # 调用Dify API进行查询
        logger.info(f"向Dify API发送查询: {title}")
        response = dify_client.send_chat_message(query=title)
        
        if "error" in response:
            logger.error(f"Dify API返回错误: {response['error']}")
            return False
        
        # 处理响应
        if response.get("status") == "streaming":
            result = dify_client.get_streaming_response(response["response"])
        else:
            result = response.get("answer", "无法获取回复内容")
        
        logger.info(f"Dify API返回结果: {result[:100]}...")
        
        # 根据用户提供的正确映射关系修改参数
        # subject_id对应oid
        oid = message["item"].get("subject_id", 0)
        
        # 如果没有subject_id，尝试提取
        if not oid:
            logger.debug("尝试从URI提取subject_id")
            # 尝试从URI提取subject_id
            uri = message["item"]["uri"]
            if "subject_id=" in uri:
                try:
                    subject_id_match = re.search(r'subject_id=(\d+)', uri)
                    if subject_id_match:
                        oid = int(subject_id_match.group(1))
                        logger.info(f"从URI提取到subject_id: {oid}")
                except Exception as e:
                    logger.error(f"从URI提取subject_id失败: {e}")
            
            # 如果还是无法获取oid，尝试使用business_id
            if not oid:
                oid = message["item"].get("business_id", 0)
                logger.info(f"使用business_id作为oid: {oid}")
        
        # 如果仍然获取不到有效的oid，则无法回复
        if not oid:
            logger.error("无法获取有效的oid，无法回复评论")
            return False
        
        # 判断评论类型
        type_id = 1  # 默认为视频评论类型
        item_type = message["item"].get("type", "")
        if item_type == "dynamic":
            type_id = 17  # 动态评论区类型
        elif item_type == "article":
            type_id = 12  # 文章评论区类型
        
        logger.info(f"评论类型: {item_type}, type_id: {type_id}")
        
        # target_id对应root (评论根ID)
        root_id = message["item"].get("target_id", 0)
        if root_id == 0 and "comment_root_id" in message["item"]["uri"]:
            try:
                root_id = int(message["item"]["uri"].split("comment_root_id=")[1].split("&")[0])
            except Exception:
                logger.warning("无法从URI提取评论根ID")
        
        # source_id对应parent (回复评论的ID)
        parent_id = message["item"].get("source_id", 0)
        
        # 回复评论
        logger.info(f"回复评论, OID: {oid}, type_id: {type_id}, root_id: {root_id}, parent_id: {parent_id}")
        
        # 限制回复字数，B站评论一般有字数限制
        if len(result) > 2000:
            result = result[:1997] + "..."
            
        # 发送回复
        retry_count = 0
        while retry_count < BILIBILI_CONFIG.get("RETRY_TIMES", 3):
            try:
                reply_result = send_reply_comment(
                    oid=oid,
                    message=result,
                    root=root_id,
                    parent=parent_id,
                    type_id=type_id
                )
                
                if reply_result.get("code") == 0:
                    logger.info(f"成功回复评论, 回复ID: {reply_result.get('data', {}).get('rpid', 'unknown')}")
                    return True
                else:
                    logger.warning(f"回复评论失败, 错误码: {reply_result.get('code')}, 消息: {reply_result.get('message')}")
                    
                    # 错误码12002表示评论区已关闭，尝试其他评论类型
                    if reply_result.get("code") == 12002 and type_id == 1:
                        logger.info("尝试使用动态评论类型...")
                        type_id = 17
                        continue
                    
                    retry_count += 1
                    time.sleep(BILIBILI_CONFIG.get("RETRY_INTERVAL", 60))
            except Exception as e:
                logger.error(f"回复评论时发生异常: {str(e)}")
                retry_count += 1
                time.sleep(BILIBILI_CONFIG.get("RETRY_INTERVAL", 60))
        
        logger.error(f"回复评论失败，已达到最大重试次数")
        return False
                
    except Exception as e:
        logger.error(f"处理@消息时发生异常: {str(e)}")
        return False

def main():
    """主函数，运行机器人"""
    # 设置日志
    logger = setup_logging()
    logger.info("FakeDetection机器人启动")
    
    # 创建Dify API客户端
    dify_client = DifyAPI()
    
    # 加载已处理消息列表
    processed_messages = load_processed_messages()
    logger.info(f"已加载 {len(processed_messages)} 条已处理消息记录")
    
    # 首次获取消息，用于标记现有消息为已处理
    try:
        logger.info("初始化：获取当前所有@消息并标记为已处理...")
        initial_response = get_at_messages(page_size=50, page_num=1)
        initial_messages = parse_at_messages(initial_response)
        
        # 将所有现有消息标记为已处理
        initial_ids = set()
        for msg in initial_messages:
            initial_ids.add(msg["id"])
        
        # 更新已处理消息集合
        processed_messages.update(initial_ids)
        save_processed_messages(processed_messages)
        
        logger.info(f"已将 {len(initial_ids)} 条现有消息标记为已处理，将只响应新消息")
    except Exception as e:
        logger.error(f"初始化过程中出错: {str(e)}")
    
    # 主循环
    try:
        while True:
            try:
                # 获取最新@信息
                logger.debug("正在获取最新@信息...")
                at_response = get_at_messages(page_size=20, page_num=1)
                
                # 保存原始响应到日志文件（调试用）
                if SYSTEM_CONFIG.get("DEBUG_MODE", False):
                    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "log/response.json"), "w", encoding="utf-8") as f:
                        json.dump(at_response, f, ensure_ascii=False)
                
                # 解析@信息
                messages = parse_at_messages(at_response)
                logger.debug(f"获取到 {len(messages)} 条@信息")
                
                # 处理未处理的消息
                new_messages = 0
                for message in messages:
                    message_id = message["id"]
                    
                    # 跳过已处理的消息
                    if message_id in processed_messages:
                        continue
                    
                    new_messages += 1
                    logger.info(f"发现新@消息: ID={message_id}, 用户={message['user']['uname']}")
                    
                    # 处理消息并记录
                    success = process_at_message(message, dify_client, logger)
                    
                    # 无论成功与否都标记为已处理，防止重复处理
                    processed_messages.add(message_id)
                    
                    # 处理完一条消息后保存，确保即使程序中断也能记住已处理的消息
                    save_processed_messages(processed_messages)
                
                if new_messages > 0:
                    logger.info(f"本次处理了 {new_messages} 条新@消息")
                
            except Exception as e:
                logger.error(f"处理@信息时发生异常: {str(e)}")
            
            # 等待下一次检查
            logger.debug(f"等待 {BILIBILI_CONFIG.get('CHECK_INTERVAL', 10)} 秒后进行下一次检查...")
            time.sleep(BILIBILI_CONFIG.get("CHECK_INTERVAL", 10))
            
    except KeyboardInterrupt:
        logger.info("接收到终止信号，机器人停止运行")
    except Exception as e:
        logger.critical(f"机器人运行时发生严重错误: {str(e)}")
    finally:
        # 保存已处理消息记录
        save_processed_messages(processed_messages)
        logger.info("已保存处理记录，机器人停止运行")

if __name__ == "__main__":
    main()
