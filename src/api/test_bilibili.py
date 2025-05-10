#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试Bilibili API接口模块功能
可以直接运行此脚本进行测试
"""

import logging
import json
import sys
import os
from datetime import datetime

# 添加项目根目录到系统路径，确保可以正确导入模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# 导入需要测试的模块
from src.api.bilibili import get_at_messages, parse_at_messages

def test_at_messages():
    """测试获取和解析@消息的功能"""
    print("\n=============== 测试获取@消息 ===============")
    
    try:
        # 1. 测试获取@信息列表
        page_size = 5
        print(f"获取最近{page_size}条@信息...")
        response = get_at_messages(page_size=page_size, page_num=1)
        
        # 保存原始响应到文件，便于调试
        with open(f"test_at_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w", encoding="utf-8") as f:
            json.dump(response, f, ensure_ascii=False, indent=2)
        
        # 打印API响应基本信息
        print(f"API响应状态码: {response.get('code')}")
        print(f"API响应消息: {response.get('message')}")
        
        # 成功获取数据时，打印更多信息
        if response.get('code') == 0 and 'data' in response:
            items = response['data'].get('items', [])
            print(f"成功获取数据, 共有 {len(items)} 条@信息")
            print(f"是否有更多数据: {response['data'].get('has_more', False)}")
            
            # 打印响应中的部分原始数据结构
            if items:
                print("\n原始数据结构示例(第一条消息):")
                print(json.dumps(items[0], ensure_ascii=False, indent=2))
        else:
            print("获取数据失败")
            return
        
        # 2. 测试解析@信息列表
        print("\n=============== 测试解析@消息 ===============")
        parsed_messages = parse_at_messages(response)
        print(f"成功解析 {len(parsed_messages)} 条@信息")
        
        # 打印解析后的结果
        if parsed_messages:
            print("\n解析后的数据结构示例(前3条消息):")
            for i, msg in enumerate(parsed_messages[:3], 1):
                print(f"\n----- 消息 {i} -----")
                print(f"消息ID: {msg['id']}")
                print(f"用户: UID={msg['user']['uid']}, 名称={msg['user']['uname']}")
                print(f"标题: {msg['item']['title']}")
                content = msg['item']['content']
                print(f"内容: {content[:100]}..." if len(content) > 100 else f"内容: {content}")
                print(f"链接: {msg['item']['uri']}")
                print(f"时间戳: {msg['at_time']} (约 {datetime.fromtimestamp(msg['at_time'])})")
    
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")
    
    print("\n=============== 测试完成 ===============")

def main():
    """主函数，运行所有测试"""
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 运行测试
    print("开始测试Bilibili API功能...")
    test_at_messages()
    print("所有测试已完成")

if __name__ == "__main__":
    main() 