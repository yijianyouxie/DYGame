# 抖音云数据库配置指南

## 需要提供的配置信息

在实现抖音云数据库功能之前，请准备以下信息：

### 1. 抖音云开发配置

#### 云空间 ID (Space ID)
- 在抖音云开发控制台获取
- 格式：`cloud-xxxxx`
- 用于指定连接的云空间

#### 环境名称 (Env Name)
- 通常为：`development` 或 `production`
- 用于区分开发环境和生产环境

#### 数据库配置
- **数据库名称**：建议使用 `leaderboard` 或 `game_data`
- **集合名称**：建议使用 `player_data`

### 2. 抖音云开发权限配置

需要在抖音云控制台配置以下权限：

#### 用户权限
- `query`: 查询玩家数据
- `insert`: 创建新玩家记录
- `update`: 更新玩家数据
- `get`: 获取单个记录

#### 集合索引（建议创建）
为了提高查询性能，建议创建以下索引：

```javascript
// player_data 集合索引
db.player_data.createIndex({ "user_id": 1 }, { unique: true })
db.player_data.createIndex({ "max_level": -1, "updated_at": 1 })
```

## 数据库结构设计

### player_data 集合字段说明

| 字段名 | 类型 | 说明 | 必填 |
|--------|------|------|------|
| _id | string | 文档 ID（自动生成） | 是 |
| user_id | string | 用户唯一 ID（open_id） | 是 |
| username | string | 用户昵称 | 是 |
| avatar_url | string | 头像 URL | 否 |
| max_level | int | 最高通关关卡 | 是 |
| busy_coins | int | 忙币数量 | 是 |
| total_play_time | int | 总游戏时长（秒） | 否 |
| play_count | int | 游戏次数 | 否 |
| created_at | string | 创建时间 | 自动 |
| updated_at | string | 更新时间 | 自动 |

## 云函数配置（可选）

如果需要使用云函数来处理业务逻辑，需要创建以下云函数：

### 1. queryDocument
```javascript
exports.main = async (event) => {
  const { collection, docId } = event
  const db = cloud.database()
  const result = await db.collection(collection).doc(docId).get()
  return { data: result.data }
}
```

### 2. queryWhere
```javascript
exports.main = async (event) => {
  const { collection, where, limit = 50 } = event
  const db = cloud.database()
  const result = await db.collection(collection)
    .where(where)
    .limit(limit)
    .get()
  return { data: result.data }
}
```

### 3. addDocument
```javascript
exports.main = async (event) => {
  const { collection, data } = event
  const db = cloud.database()
  const result = await db.collection(collection).add({ data })
  return { data: result, id: result.id }
}
```

### 4. updateDocument
```javascript
exports.main = async (event) => {
  const { collection, docId, data } = event
  const db = cloud.database()
  const result = await db.collection(collection).doc(docId).update({ data })
  return { data: result }
}
```

### 5. aggregate
```javascript
exports.main = async (event) => {
  const { collection, pipeline, limit = 50 } = event
  const db = cloud.database()
  const result = await db.collection(collection)
    .aggregate()
    .pipeline(pipeline)
    .limit(limit)
    .end()
  return { data: result.list }
}
```

## Unity 项目配置

### 1. 安装 SDK

需要安装以下 SDK：

1. **抖音小游戏 SDK**
   - 从抖音开放平台下载
   - 导入到 Unity 项目

2. **LitJson（或其他 JSON 库）**
   - 用于 JSON 解析
   - 可通过 Package Manager 安装

### 2. 配置 DouyinCloudManager

在场景中添加 `DouyinCloudManager` 单例，配置以下参数：

```csharp
// DouyinCloudManager 配置
databaseName = "leaderboard"
collectionName = "player_data"
```

### 3. 配置 LeaderboardManager

在场景中添加 `LeaderboardManager` 单例，配置以下参数：

```csharp
// LeaderboardManager 配置
collectionName = "player_data"
```

## 使用示例

### 保存玩家数据

```csharp
// 保存关卡进度
LeaderboardManager.Instance.SavePlayerProgress(GameData.CurrentLevel);

// 保存忙币数量
LeaderboardManager.Instance.SavePlayerCoins(GameData.BusyCoinCount);

// 监听用户信息就绪事件
LeaderboardManager.Instance.OnUserInfoReady += (playerData) => {
    Debug.Log($"用户：{playerData.username}");
    Debug.Log($"最高关卡：{playerData.max_level}");
    Debug.Log($"忙币：{playerData.busy_coins}");
};
```

### 获取排行榜

```csharp
// LeaderboardUI 中已实现
await LeaderboardManager.Instance.GetLeaderboardAsync();
```

## 测试步骤

1. 在抖音云控制台创建云空间和数据库
2. 创建 player_data 集合
3. 配置必要的索引和权限
4. 在 Unity 中配置 DouyinCloudManager
5. 运行游戏测试数据保存和读取

## 注意事项

1. **网络延迟**：云数据库操作需要网络，注意处理超时和错误
2. **并发问题**：如果多个设备同时更新同一用户数据，需要考虑并发控制
3. **数据安全**：生产环境应配置合适的读写权限，避免数据泄露
4. **成本控制**：注意云数据库的读写次数和存储限制
5. **本地缓存**：建议实现本地缓存，提高启动速度

## 下一步

提供以下信息后，我可以继续完善实现：

1. 云空间 ID (Space ID)
2. 环境名称 (Env Name)
3. 是否使用云函数
4. 具体的抖音云 SDK 文档链接

收到这些信息后，我将更新代码以适配您的实际配置。
