# 配置文件使用指南

## 概述

本项目使用两个配置文件来管理设置：
- `config.example.py`：配置模板，包含所有可配置项及其默认值
- `config.py`：实际配置文件，包含您的个人设置和API密钥

## 安全注意事项

**重要**：`config.py` 文件包含敏感信息（如API密钥和账号凭据），永远不要将其提交到版本控制系统。我们已将此文件添加到 `.gitignore` 中以防止意外提交。

## 初始配置步骤

1. 复制配置模板创建实际配置文件：
   ```bash
   cp config.example.py config.py
   ```

2. 编辑 `config.py` 文件，更新以下关键配置项：
   - B站账号信息（SESSDATA, BILI_JCT等）
   - Dify API密钥
   - 其他需要自定义的配置

## 获取B站账号配置信息

要获取B站账号的必要信息，请按照以下步骤操作：

1. 登录B站网站 (https://www.bilibili.com/)
2. 打开浏览器开发者工具 (F12 或右键 -> 检查)
3. 切换到 "应用程序" 或 "Application" 标签
4. 在左侧导航栏中，展开 "Cookies"，选择 "https://www.bilibili.com"
5. 在右侧查找并记录以下Cookie值：
   - SESSDATA
   - bili_jct
   - BUVID3
   - DedeUserID

## 获取Dify API密钥

1. 在Dify平台 (https://dify.ai) 注册并登录您的账号
2. 创建一个新应用或选择现有应用
3. 进入"API访问"或"API密钥"设置
4. 生成API密钥并复制到配置文件中

## 配置项说明

### B站配置 (BILIBILI_CONFIG)

| 配置项 | 描述 | 默认值 |
|--------|------|--------|
| SESSDATA | 登录Cookie中的SESSDATA值 | - |
| BILI_JCT | 登录Cookie中的bili_jct值 | - |
| BUVID3 | 登录Cookie中的BUVID3值 | - |
| DEDEUSERID | 登录Cookie中的DedeUserID值 | - |
| USER_AGENT | 请求使用的用户代理 | Mozilla/5.0 (Windows NT 10.0...) |
| REFERER | 请求头中的Referer值 | https://www.bilibili.com/ |
| BOT_NAME | 机器人名称，用于检测@ | FakeDetectionBot |
| BOT_UID | 机器人账号的UID | - |
| CHECK_INTERVAL | 检查新@的时间间隔(秒) | 300 |
| RETRY_TIMES | 评论发送失败重试次数 | 3 |
| RETRY_INTERVAL | 重试间隔(秒) | 60 |

### Dify配置 (DIFY_CONFIG)

| 配置项 | 描述 | 默认值 |
|--------|------|--------|
| API_KEY | Dify API密钥 | - |
| API_URL | Dify API地址 | https://api.dify.ai/v1 |
| MODEL_NAME | 使用的模型名称 | deepresearch |
| MAX_TOKENS | 最大生成token数 | 1000 |
| TEMPERATURE | 生成温度，越低越精确，越高越有创意 | 0.7 |
| TIMEOUT | API请求超时时间(秒) | 120 |

### 系统配置 (SYSTEM_CONFIG)

| 配置项 | 描述 | 默认值 |
|--------|------|--------|
| DEBUG_MODE | 是否启用调试模式 | False |

### 日志配置 (LOG_CONFIG)

| 配置项 | 描述 | 默认值 |
|--------|------|--------|
| LOG_LEVEL | 日志记录级别 | INFO |

## 敏感词配置

敏感词列表在 `data/sensitive_words.txt` 文件中定义，您可以从 `data/sensitive_words.txt.example` 创建此文件：

```bash
cp data/sensitive_words.txt.example data/sensitive_words.txt
```

然后编辑文件，每行添加一个敏感词。

## 故障排除

如果配置出现问题，请检查：

1. 确认 `config.py` 文件存在且包含必要配置
2. 确认B站账号信息正确且未过期
3. 确认Dify API密钥有效
4. 检查日志文件获取详细错误信息 