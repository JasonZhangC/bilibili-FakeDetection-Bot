# 简介
## 项目背景
- B站上的伪造信息泛滥
- 当前辨别信息真伪的时间成本过高
- DeepResearch技术成熟
## 这个工具是什么？
一个B站Bot，当用户使用B站，查看视频评论，对评论的真实性存疑，就可以在评论下方@FakeDetectionBot。

小机器人会根据用户提到的信息进行深度搜索，校验信息的准确性。

## 依赖的开源项目&工具链
- [哔哩哔哩 - API 收集整理](https://github.com/SocialSisterYi/bilibili-API-collect)
- [Dify](https://github.com/langgenius/dify)

## 程序运行流程
1. 调用B站API定时刷新Bot的信息列表，查询是否有用户@Bot
2. 解析返回的Json内容，获知用户需要检测的内容
3. 调用Dify API进行DeepResearch并获知结果
4. 将结果内容通过B站API回复到对应的评论中

# 一些坑
- B站有严格的审核机制，导致评论容易「被吞」，解决方法尽量使用高等级的账号