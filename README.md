# B站伪信息检测机器人 (FakeDetectionBot)

## 简介
### 项目背景
- B站上的伪造信息泛滥
- 当前辨别信息真伪的时间成本过高
- DeepResearch技术成熟

### 这个工具是什么？
一个B站Bot，当用户使用B站，查看视频评论，对评论的真实性存疑，就可以在评论下方@FakeDetectionBot。

小机器人会根据用户提到的信息进行深度搜索，校验信息的准确性，并提供可靠的事实依据。

## 功能特点
- 自动监测@机器人的评论
- 智能解析用户查询的内容
- 基于深度搜索验证信息真实性
- 快速回复检测结果到原评论位置
- 提供信息来源和可靠依据

## 安装与配置

### 环境要求
- Python 3.8+
- 有效的B站账号（推荐使用高等级账号）
- Dify API访问权限（需要在系统中配置模型API）

### 安装步骤
1. 克隆本仓库
```bash
git clone https://github.com/yourusername/bilibili-FakeDetection-Bot.git
cd bilibili-FakeDetection-Bot
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置凭证
```bash
cp config.example.py config.py
# 编辑config.py文件，填入您的B站账号信息和Dify API密钥
```

## API配置说明

### B站API配置
1. 获取B站Cookie和CSRF令牌（参考[B站API文档](https://github.com/SocialSisterYi/bilibili-API-collect)）
2. 在config.py中填入您的账号信息
3. 确保账号有足够的等级以避免评论审核问题

### Dify API配置
1. 在[Dify平台](https://dify.ai)注册并创建应用
2. 获取API密钥
3. 在config.py中配置Dify API相关参数

## 使用方法

### 启动机器人
```bash
python bot.py
```

### 用户使用方式
B站用户可以通过以下格式调用机器人：
```
@FakeDetectionBot 请检查内容
```

## 程序运行流程
1. 调用B站API定时刷新Bot的信息列表，查询是否有用户@Bot
2. 解析返回的Json内容，获知用户需要检测的内容
3. 调用Dify API进行DeepResearch并获知结果
4. 将结果内容通过B站API回复到对应的评论中

## 依赖的开源项目&工具链
- [哔哩哔哩 - API 收集整理](https://github.com/SocialSisterYi/bilibili-API-collect)
- [Dify](https://github.com/langgenius/dify)

## 常见问题与解决方案

### 评论审核问题
- B站有严格的审核机制，导致评论容易「被吞」
- 解决方法：尽量使用高等级的账号，避免使用敏感词汇
- 可以设置自动重试机制，检测评论是否成功发送

### API限流问题
- B站API可能存在调用频率限制
- 解决方法：实现请求队列和延迟机制，避免频繁请求

### 信息检测准确性
- 部分复杂或模糊的信息可能难以准确验证
- 解决方法：提供置信度评分，明确标注无法确定的内容

## 项目开发与贡献

### 开发路线图
- [ ] 基础功能实现
- [ ] 提高信息检测准确率
- [ ] 用户界面优化
- [ ] 支持更多类型的信息检测

### 如何贡献
1. Fork本仓库
2. 创建您的功能分支
3. 提交变更
4. 推送到分支
5. 创建Pull Request

## 许可证
本项目采用[MIT许可证](LICENSE)。