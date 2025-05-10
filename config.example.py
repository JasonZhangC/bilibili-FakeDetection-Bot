#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置文件示例
请复制此文件为 config.py 并填入您的实际配置
注意：config.py 不应提交到版本控制系统中
"""

# B站账号配置
BILIBILI_CONFIG = {
    "SESSDATA": "你的SESSDATA",  # 登录B站后的Cookie中的SESSDATA值
    "BILI_JCT": "你的bili_jct",  # 登录B站后的Cookie中的bili_jct值
    
    # 机器人配置
    "BOT_NAME": "FakeDetectionBot",  # 机器人名称，用于检测@
    "BOT_UID": "你的机器人账号UID",   # 机器人账号的UID
    
    # 运行配置
    "CHECK_INTERVAL": 10,  # 检查新@的时间间隔(秒)
    "RETRY_TIMES": 3,       # 评论发送失败重试次数
    "RETRY_INTERVAL": 60,   # 重试间隔(秒)
}

# Dify API配置
DIFY_CONFIG = {
    "API_KEY": "你的Dify API密钥",
    "API_URL": "https://api.dify.ai/v1",  # Dify API地址
}

# 系统配置
SYSTEM_CONFIG = {
    "DEBUG_MODE": True,  # 在开发阶段启用调试模式
}

# 日志配置
LOG_CONFIG = {
    "LOG_LEVEL": "DEBUG",  # 在开发阶段使用更详细的日志级别
}
