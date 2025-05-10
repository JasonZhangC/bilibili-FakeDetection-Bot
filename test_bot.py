#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
B站自动检测和回复机器人的测试程序
用于模拟B站@信息，测试机器人的功能
"""

import os
import time
import json
import logging
import sys
from typing import Dict, Any, List
from unittest.mock import patch, MagicMock

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入要测试的模块
from src.api.dify import DifyAPI
from config import BILIBILI_CONFIG, DIFY_CONFIG

# 从bot.py导入需要测试的函数
from bot import extract_video_oid, process_at_message, setup_logging

# 模拟@消息数据
def create_mock_at_message(title: str, user_name: str = "测试用户", video_id: int = 114450023587340, message_id: int = 999999999) -> Dict[str, Any]:
    """
    创建模拟的B站@消息数据
    
    Args:
        title: 视频标题
        user_name: 用户名
        video_id: 视频ID
        message_id: 消息ID
        
    Returns:
        Dict[str, Any]: 模拟的@消息数据
    """
    return {
        "id": message_id,
        "user": {
            "uid": 458118476,
            "uname": user_name,
            "face": "https://i2.hdslb.com/bfs/face/7727a8b5dd7210800415c599e625f53d79e6a58e.jpg"
        },
        "item": {
            "type": "reply",
            "business_id": 1,
            "title": title,
            "content": f"@{BILIBILI_CONFIG['BOT_NAME']} 请分析一下这个视频",
            "uri": f"https://www.bilibili.com/video/BV1hcVPzLEm3?subject_id={video_id}&page=0&comment_root_id=261448306497",
            "source_id": 261448306497
        },
        "at_time": int(time.time())
    }

# 模拟Dify API响应
def mock_dify_response(title: str) -> Dict[str, Any]:
    """
    模拟Dify API的响应
    
    Args:
        title: 查询的视频标题
        
    Returns:
        Dict[str, Any]: 模拟的API响应
    """
    return {
        "status": "success",
        "answer": f"这是对视频《{title}》的分析结果：\n\n根据我的分析，这个视频标题看起来{('可信' if len(title) % 2 == 0 else '可能有误导性')}。"
                 f"\n\n{'视频内容符合常理，未发现明显虚假信息' if len(title) < 20 else '标题过长且夸张，可能存在标题党或虚假宣传的嫌疑'}"
    }

# 测试提取视频ID功能
def test_extract_video_oid():
    """测试从不同格式的URL中提取视频ID的功能"""
    print("\n===== 测试提取视频ID功能 =====")
    
    test_urls = [
        "https://www.bilibili.com/video/BV1hcVPzLEm3?subject_id=114450023587340",
        "https://www.bilibili.com/video/av114450023",
        "https://www.bilibili.com/video/114450023",
        "https://t.bilibili.com/123456?oid=114450023",
        "https://www.bilibili.com/video/BV1hcVPzLEm3?page=0&comment_root_id=261448306497"
    ]
    
    for i, url in enumerate(test_urls, 1):
        oid = extract_video_oid(url)
        print(f"测试 {i}: URL=\"{url}\"")
        print(f"   提取结果: OID = {oid}")
        print()

# 测试处理@消息功能
@patch('bot.send_reply_comment')
def test_process_at_message(mock_send_reply):
    """测试处理@消息的完整流程"""
    print("\n===== 测试处理@消息功能 =====")
    
    # 设置模拟的回复结果
    mock_send_reply.return_value = {"code": 0, "data": {"rpid": 12345678}}
    
    # 创建日志记录器
    logger = setup_logging()
    
    # 创建测试标题列表
    test_titles = [
        "【真实】2023年最新科技突破，人工智能取得重大进展",
        "震惊！这个视频居然能让你一夜暴富，点击就送100万",
        "华为最新5G技术应用，速度提升10倍",
        "普通人如何30天学会编程并找到高薪工作",
        "我花了一个月时间测试各种学习方法，这是最有效的一种"
    ]
    
    # 创建真实的Dify客户端 (也可以使用模拟的)
    try:
        dify_client = DifyAPI()
        
        # 依次测试每个标题
        for i, title in enumerate(test_titles, 1):
            print(f"\n测试 {i}: 标题=\"{title}\"")
            
            # 创建模拟的@消息
            mock_message = create_mock_at_message(title, message_id=1000000 + i)
            
            # 处理模拟的@消息
            # 两种选择:
            # 1. 使用真实的Dify API (可能较慢)
            success = process_at_message(mock_message, dify_client, logger)
            
            # 2. 使用模拟的Dify API (如果需要更快的测试)
            # with patch.object(dify_client, 'send_chat_message', return_value=mock_dify_response(title)):
            #    with patch.object(dify_client, 'get_streaming_response', return_value=mock_dify_response(title)["answer"]):
            #        success = process_at_message(mock_message, dify_client, logger)
            
            print(f"处理结果: {'成功' if success else '失败'}")
            if mock_send_reply.called:
                print(f"已调用send_reply_comment函数，参数:")
                args, kwargs = mock_send_reply.call_args
                print(f"  oid = {kwargs.get('oid')}")
                print(f"  root = {kwargs.get('root')}")
                print(f"  parent = {kwargs.get('parent')}")
                print(f"  消息长度 = {len(kwargs.get('message', ''))}")
            
            # 重置模拟
            mock_send_reply.reset_mock()
    
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")

# 手动测试单个标题
def test_single_title(title: str, video_id: int = 114450023587340):
    """
    手动测试单个标题
    
    Args:
        title: 要测试的视频标题
        video_id: 视频ID
    """
    print(f"\n===== 测试标题: {title} =====")
    
    try:
        # 设置模拟的回复结果
        with patch('bot.send_reply_comment') as mock_send_reply:
            mock_send_reply.return_value = {"code": 0, "data": {"rpid": 12345678}}
            
            # 创建日志记录器
            logger = setup_logging()
            
            # 创建模拟的@消息
            mock_message = create_mock_at_message(title, video_id=video_id)
            
            # 创建Dify客户端
            dify_client = DifyAPI()
            
            # 处理模拟的@消息
            print("开始处理@消息...")
            success = process_at_message(mock_message, dify_client, logger)
            
            print(f"处理结果: {'成功' if success else '失败'}")
            if mock_send_reply.called:
                print(f"已调用send_reply_comment函数，参数:")
                args, kwargs = mock_send_reply.call_args
                print(f"  oid = {kwargs.get('oid')}")
                print(f"  root = {kwargs.get('root')}")
                print(f"  parent = {kwargs.get('parent')}")
                print(f"  消息长度 = {len(kwargs.get('message', ''))}")
                print(f"  消息内容前100字符: {kwargs.get('message', '')[:100]}...")
    
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")

def main():
    """主函数"""
    print("===== B站FakeDetection机器人测试程序 =====")
    print("1. 测试提取视频ID功能")
    print("2. 测试处理@消息功能 (使用预设的测试标题)")
    print("3. 手动输入标题测试")
    
    choice = input("请选择测试类型 (1/2/3): ")
    
    if choice == '1':
        test_extract_video_oid()
    elif choice == '2':
        test_process_at_message()
    elif choice == '3':
        title = input("请输入要测试的视频标题: ")
        video_id = input("请输入视频ID (直接回车使用默认ID): ")
        video_id = int(video_id) if video_id.strip() else 114450023587340
        test_single_title(title, video_id)
    else:
        print("无效的选择!")

if __name__ == "__main__":
    main() 