#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Bilibili API接口的单元测试
使用unittest框架进行测试
"""

import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# 导入待测试的模块
from src.api.bilibili import get_at_messages, parse_at_messages

class MockResponse:
    """模拟HTTP响应对象"""
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code
        
    def json(self):
        return self.json_data
        
    def raise_for_status(self):
        if self.status_code != 200:
            raise Exception(f"HTTP错误: {self.status_code}")


class TestBilibiliAPI(unittest.TestCase):
    """测试Bilibili API接口功能"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建模拟的API响应数据
        self.mock_api_response = {
            "code": 0,
            "message": "0",
            "ttl": 1,
            "data": {
                "items": [
                    {
                        "id": 123456789,
                        "user": {
                            "mid": 10000001,
                            "nickname": "测试用户1",
                            "avatar": "http://example.com/avatar1.jpg"
                        },
                        "item": {
                            "type": "reply",
                            "business_id": 987654321,
                            "title": "测试视频标题",
                            "content": "这是一条测试@评论，内容仅供测试使用。",
                            "uri": "https://www.bilibili.com/video/BV123456"
                        },
                        "at_time": 1620000000
                    },
                    {
                        "id": 123456790,
                        "user": {
                            "mid": 10000002,
                            "nickname": "测试用户2",
                            "avatar": "http://example.com/avatar2.jpg"
                        },
                        "item": {
                            "type": "dynamic",
                            "business_id": 987654322,
                            "title": "",
                            "content": "在动态中@了你，测试动态内容。",
                            "uri": "https://t.bilibili.com/123456789"
                        },
                        "at_time": 1621000000
                    }
                ],
                "last_id": 123456790,
                "has_more": False
            }
        }
    
    @patch('src.api.bilibili.requests.get')
    def test_get_at_messages(self, mock_get):
        """测试获取@信息函数"""
        # 设置mock对象的返回值
        mock_get.return_value = MockResponse(self.mock_api_response)
        
        # 调用测试函数
        result = get_at_messages(page_size=5, page_num=1)
        
        # 验证结果
        self.assertEqual(result["code"], 0)
        self.assertEqual(len(result["data"]["items"]), 2)
        self.assertFalse(result["data"]["has_more"])
        
        # 验证requests.get被正确调用
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertIn("https://api.bilibili.com/x/msgfeed/at", args[0])
        self.assertIn("headers", kwargs)
    
    @patch('src.api.bilibili.requests.get')
    def test_get_at_messages_error(self, mock_get):
        """测试获取@信息失败的情况"""
        # 设置mock对象返回错误响应
        error_response = {"code": -101, "message": "账号未登录"}
        mock_get.return_value = MockResponse(error_response)
        
        # 调用测试函数
        result = get_at_messages()
        
        # 验证结果
        self.assertEqual(result["code"], -101)
        self.assertEqual(result["message"], "账号未登录")
    
    def test_parse_at_messages(self):
        """测试解析@信息函数"""
        # 调用测试函数
        parsed_result = parse_at_messages(self.mock_api_response)
        
        # 验证结果
        self.assertEqual(len(parsed_result), 2)
        
        # 验证第一条消息的解析结果
        first_msg = parsed_result[0]
        self.assertEqual(first_msg["id"], 123456789)
        self.assertEqual(first_msg["user"]["uid"], 10000001)
        self.assertEqual(first_msg["user"]["uname"], "测试用户1")
        self.assertEqual(first_msg["item"]["type"], "reply")
        self.assertEqual(first_msg["item"]["content"], "这是一条测试@评论，内容仅供测试使用。")
        self.assertEqual(first_msg["at_time"], 1620000000)
    
    def test_parse_at_messages_error(self):
        """测试解析错误响应的情况"""
        # 创建错误响应
        error_response = {"code": -101, "message": "账号未登录"}
        
        # 调用测试函数
        parsed_result = parse_at_messages(error_response)
        
        # 验证结果：应该返回空列表
        self.assertEqual(parsed_result, [])
    
    def test_parse_at_messages_empty(self):
        """测试解析空响应的情况"""
        # 创建空响应
        empty_response = {
            "code": 0,
            "message": "0",
            "data": {
                "items": [],
                "has_more": False
            }
        }
        
        # 调用测试函数
        parsed_result = parse_at_messages(empty_response)
        
        # 验证结果：应该返回空列表
        self.assertEqual(parsed_result, [])


if __name__ == '__main__':
    unittest.main() 