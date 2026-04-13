# 抖音云开发配置指南

## 概述

本游戏使用抖音云数据库存储用户数据（关卡进度、排行榜等），直接使用 C# API 操作数据库，无需云函数。

## 配置信息

- **环境ID**：`env-nJ2KymQ8pn`
- **数据库集合**：`game_progress`

## 部署步骤

### 1. 创建数据库集合

1. 登录 [抖音开放平台控制台](https://developer.open-douyin.com/)
2. 进入你的小游戏管理后台
3. 找到"云开发"或"Serverless"菜单
4. 进入环境 `env-nJ2KymQ8pn`
5. 在"数据库"管理中，创建一个名为 `game_progress` 的集合

### 2. 配置数据库权限（可选）

默认情况下，云数据库的权限规则是"仅创建者可读写"。如果你的游戏需要其他玩家查看排行榜，可能需要调整权限规则。

在云开发控制台的"数据库" -> "权限设置"中，可以配置集合的访问权限。

## Unity 配置

Unity 中已经配置好所有必要的参数：

- 文件：`Assets/Scripts/DouyinCloudManager.cs`
- 环境ID：`env-nJ2KymQ8pn`
- 集合名称：`game_progress`

## 使用的抖音云 API

代码使用以下 C# API 直接操作数据库：

1. **添加文档**：`collection.Add(data)`
2. **更新文档**：`collection.Doc(docId).Update(data)`
3. **查询文档**：`collection.Doc(docId).Get()`
4. **条件查询**：`collection.Where(cmd).Get()`
5. **删除文档**：`collection.Doc(docId).Remove()`

## 数据结构

`game_progress` 集合中的文档结构：

```json
{
  "_id": "文档ID（自动生成）",
  "user_id": "用户openId",
  "username": "用户名",
  "avatar_url": "头像URL",
  "max_level": 1,
  "busy_coins": 100,
  "update_time": "2026-04-03 12:00:00"
}
```

## 测试

配置完成后，发布游戏到抖音小游戏平台进行测试。

**注意**：抖音云 API 只在抖音小游戏环境中工作，Unity 编辑器中无法真正测试。

## 故障排查

### 问题1：数据库操作失败

**可能原因**：
- 集合 `game_progress` 未创建
- 环境ID不匹配

**解决方案**：
- 确认集合已创建
- 确认环境ID正确

### 问题2：权限不足

**可能原因**：
- 数据库权限规则限制了访问

**解决方案**：
- 在云开发控制台调整权限设置
- 检查是否需要修改为"所有用户可读，仅创建者可写"等规则

### 问题3：环境ID错误

**解决方案**：
- 确认环境ID拼写正确
- 确认你有该环境的访问权限

## 下一步

1. 在云开发控制台创建 `game_progress` 集合
2. 发布游戏到抖音小游戏平台
3. 测试数据保存和加载功能
