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
    "BUVID3": "你的BUVID3",      # 登录B站后的Cookie中的BUVID3值
    "DEDEUSERID": "你的DedeUserID",  # 登录B站后的Cookie中的DedeUserID值
    
    # API访问配置
    "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "REFERER": "https://www.bilibili.com/",
    
    # 机器人配置
    "BOT_NAME": "FakeDetectionBot",  # 机器人名称，用于检测@
    "BOT_UID": "你的机器人账号UID",   # 机器人账号的UID
    
    # 运行配置
    "CHECK_INTERVAL": 300,  # 检查新@的时间间隔(秒)
    "RETRY_TIMES": 3,       # 评论发送失败重试次数
    "RETRY_INTERVAL": 60,   # 重试间隔(秒)
}

# Dify API配置
DIFY_CONFIG = {
    "API_KEY": "你的Dify API密钥",
    "API_URL": "https://api.dify.ai/v1",  # Dify API地址
    "MODEL_NAME": "deepresearch",          # 使用的模型名称
    "MAX_TOKENS": 1000,                    # 最大生成token数
    "TEMPERATURE": 0.7,                    # 生成温度，越低越精确，越高越有创意
    "TIMEOUT": 120,                        # API请求超时时间(秒)
}
