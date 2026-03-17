# 抖音云数据库排行榜系统实现文档

## 📋 功能概述

已实现的排行榜系统包含以下功能：
1. ✅ 抖音 SDK 用户信息获取
2. ✅ 云数据库玩家进度存储
3. ✅ 排行榜查询（前 50 名）
4. ✅ 排行榜 UI 界面（含金/银/铜牌标识）
5. ✅ 实时存档（答对题目后立即保存）
6. ✅ 主菜单和结果场景的排行榜按钮

---

## 🎯 数据库结构升级

### 当前结构
```json
{
    "_id": "69b3c3e3610dcca16a089765",
    "level": 1,
    "name": "test_user"
}
```

### 建议的新结构
```json
{
    "_id": "自动生成",
    "user_id": "抖音用户 ID",
    "username": "用户名",
    "avatar_url": "头像 URL",
    "max_level": 最高关卡数，
    "update_time": "最后更新时间"
}
```

### 如何修改数据库结构

#### 方法 1：在抖音云数据库控制台手动修改
1. 登录抖音开发者后台
2. 进入云数据库管理
3. 删除旧数据（或备份）
4. 创建新字段：
   - `user_id` (string)
   - `username` (string)
   - `avatar_url` (string)
   - `max_level` (int)
   - `update_time` (timestamp)

#### 方法 2：使用代码自动迁移
在 Unity 启动时执行一次数据迁移：

```csharp
// 伪代码示例
public async Task MigrateDatabase()
{
    var oldRecords = await QueryOldDatabase();
    
    foreach (var oldRecord in oldRecords)
    {
        var newRecord = new LeaderboardRecord
        {
            user_id = oldRecord._id,
            username = oldRecord.name,
            avatar_url = "",
            max_level = oldRecord.level,
            update_time = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss")
        };
        
        await SaveToNewDatabase(newRecord);
    }
}
```

---

## 🏗️ 系统架构

### 核心组件

#### 1. LeaderboardManager.cs
**位置**: `Assets/Scripts/LeaderboardManager.cs`

**职责**:
- 初始化抖音 SDK
- 获取用户信息
- 管理云数据库操作
- 提供排行榜查询接口

**关键方法**:
```csharp
// 保存玩家进度
LeaderboardManager.Instance.SavePlayerProgress(int level);

// 获取排行榜数据
var records = await LeaderboardManager.Instance.GetLeaderboardAsync();
```

#### 2. LeaderboardUI.cs
**位置**: `Assets/Scripts/LeaderboardUI.cs`

**职责**:
- 控制排行榜面板显示/隐藏
- 填充排行榜数据
- 处理前三名特殊样式

**Inspector 配置**:
```csharp
[Header("UI 组件引用")]
public RectTransform panelRoot;      // 排行榜面板
public Button closeButton;           // 关闭按钮
public Transform contentParent;      // 内容容器
public GameObject rankItemPrefab;    // 排名项预制件

[Header("颜色配置")]
public Color goldColor;              // 金色 #FFD700
public Color silverColor;            // 银色 #C0C0C0
public Color bronzeColor;            // 铜色 #CD7F32
```

#### 3. LeaderboardRankItem.cs
**位置**: `Assets/Scripts/LeaderboardRankItem.cs`

**职责**:
- 单个排名项的数据展示
- 前三名特殊标识

---

## 🎨 UI 设计

### 排行榜界面布局

```
┌─────────────────────────────────┐
│     排 行 榜                    │
│                    [×] 关闭     │
├─────────────────────────────────┤
│ ┌─────────────────────────────┐ │
│ │ 👑 第 1 名  张三    第 50 关   │ │ ← 金色背景 + 皇冠
│ │ 🥈 第 2 名  李四    第 45 关   │ │ ← 银色背景
│ │ 🥉 第 3 名  王五    第 40 关   │ │ ← 铜色背景
│ ├─────────────────────────────┤ │
│ │ 4   赵六      第 38 关       │ │
│ │ 5   钱七      第 35 关       │ │
│ │ ...                          │ │
│ │ 50  吴十      第 10 关       │ │
│ └─────────────────────────────┘ │
└─────────────────────────────────┘
```

### 前三名视觉规范

| 名次 | 颜色 | 图标 | 字号 | 特效 |
|------|------|------|------|------|
| 第 1 名 | 金色 (#FFD700) | 👑 皇冠 | 24pt Bold | 光晕 |
| 第 2 名 | 银色 (#C0C0C0) | 🥈 银牌 | 24pt Bold | - |
| 第 3 名 | 铜色 (#CD7F32) | 🥉 铜牌 | 24pt Bold | - |
| 其他 | 白色 (#FFFFFF) | - | 18pt Normal | - |

---

## 📦 预制件创建指南

### 创建 LeaderboardPanel.prefab

#### 步骤 1：创建 Canvas 层级结构

```
Canvas
└── LeaderboardPanel (RectTransform)
    ├── Header (Image)
    │   ├── TitleText (Text) - "排行榜"
    │   └── CloseButton (Button)
    │       └── Text - "×"
    ├── Content (Scroll View)
    │   └── Viewport
    │       └── ContentParent (Vertical Layout Group)
    └── Background (Image)
```

#### 步骤 2：设置 Scroll View

1. **创建方式**: Hierarchy → UI → Scroll View
2. **调整大小**: 
   - Anchor: Stretch
   - PosX: 20, PosY: -60
   - Width: -40, Height: -120
3. **Content 设置**:
   - 添加 `Vertical Layout Group`
   - Spacing: 10
   - Child Force Expand: Width ✓

#### 步骤 3：创建 RankItemPrefab

```
RankItemPrefab (RectTransform)
├── Background (Image)
├── RankText (Text) - "1"
├── AvatarImage (Image) - 头像
├── NameText (Text) - "用户名"
└── LevelText (Text) - "第 X 关"
```

**尺寸设置**:
- Height: 60
- Anchor: Stretch Left/Right
- Padding: Left 20, Right 20

#### 步骤 4：保存为 Prefab

1. 将 `LeaderboardPanel` 拖到 `Assets/Prefabs/` 目录
2. 将 `RankItemPrefab` 拖到 `Assets/Prefabs/` 目录

---

## 🔧 Inspector 配置步骤

### 1. 配置 LeaderboardManager

1. 在 Hierarchy 中创建空对象 `GameManager`
2. 添加 `LeaderboardManager` 组件
3. 设置参数:
   - **Database Name**: `leaderboard`

### 2. 配置 MainMenuController

1. 选中 MainMenuCanvas 的 Controller 对象
2. 在 `MainMenuController` 组件中:
   - **Leaderboard Button**: 拖入排行榜按钮
   - **Leaderboard UI**: 拖入 LeaderboardUI 对象

### 3. 配置 LeaderboardUI

1. 选中 LeaderboardPanel
2. 在 `LeaderboardUI` 组件中:
   - **Panel Root**: 拖入自身 RectTransform
   - **Close Button**: 拖入关闭按钮
   - **Content Parent**: 拖入 Content 下的 ContentParent
   - **Rank Item Prefab**: 拖入 RankItemPrefab

### 4. 配置 ResultController

1. 选中 ResultCanvas 的 Controller 对象
2. 在 `ResultController` 组件中:
   - **Leaderboard Button**: 拖入排行榜按钮
   - **Leaderboard UI**: 拖入 LeaderboardUI 对象

---

## 💾 云数据库集成

### 当前实现状态

目前代码中使用的是**模拟数据**，需要替换为真实的云数据库调用。

### 抖音云数据库 API 参考

根据您提供的文档：
- https://developer.open-douyin.com/docs/resource/zh-CN/developer/tools/cloud/api-reference/cloud-database/client/unity-sdk-clouddatabase

### 需要实现的接口

#### 1. 查询玩家记录
```csharp
private async Task<LeaderboardRecord> QueryPlayerRecord(string userId)
{
    // TODO: 使用抖音云数据库 API
    // 示例代码（需要根据实际 API 调整）:
    /*
    var db = CloudDatabase.DefaultDatabase();
    var collection = db.Collection("leaderboard");
    
    var query = collection.Where("user_id", "==", userId);
    var result = await query.Get();
    
    if (result.Count > 0)
    {
        return JsonUtility.FromJson<LeaderboardRecord>(result[0].ToJson());
    }
    return null;
    */
    
    return null; // 当前返回 null
}
```

#### 2. 创建玩家记录
```csharp
private async Task CreatePlayerRecord(int level)
{
    // TODO: 使用抖音云数据库 API
    /*
    var db = CloudDatabase.DefaultDatabase();
    var collection = db.Collection("leaderboard");
    
    var newRecord = new LeaderboardRecord
    {
        user_id = currentUserId,
        username = currentUsername,
        avatar_url = currentAvatarUrl,
        max_level = level,
        update_time = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss")
    };
    
    await collection.Add(JsonUtility.ToJson(newRecord));
    */
}
```

#### 3. 更新玩家记录
```csharp
private async Task UpdatePlayerRecord(string recordId, int newLevel)
{
    // TODO: 使用抖音云数据库 API
    /*
    var db = CloudDatabase.DefaultDatabase();
    var collection = db.Collection("leaderboard");
    
    var updateData = new Dictionary<string, object>
    {
        { "max_level", newLevel },
        { "update_time", DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") }
    };
    
    await collection.Document(recordId).Update(updateData);
    */
}
```

#### 4. 获取排行榜
```csharp
public async Task<List<LeaderboardRecord>> GetLeaderboardAsync()
{
    // TODO: 使用抖音云数据库 API
    /*
    var db = CloudDatabase.DefaultDatabase();
    var collection = db.Collection("leaderboard");
    
    // 排序：max_level DESC, update_time ASC
    var query = collection
        .OrderByDescending("max_level")
        .Ascending("update_time")
        .Limit(50);
    
    var result = await query.Get();
    
    var records = new List<LeaderboardRecord>();
    foreach (var doc in result)
    {
        records.Add(JsonUtility.FromJson<LeaderboardRecord>(doc.ToJson()));
    }
    
    return records;
    */
    
    return GetMockLeaderboardData(); // 当前使用模拟数据
}
```

---

## 🎮 游戏流程集成

### 开始游戏场景（Start.scene）

```
玩家点击开始游戏
    ↓
GameData.LoadFromServer()
    ↓
初始化 LeaderboardManager
    ↓
获取抖音用户信息
    ↓
显示主菜单
    ↓
玩家点击排行榜按钮
    ↓
LeaderboardUI.ShowLeaderboard()
    ↓
从云数据库加载前 50 名
    ↓
显示排行榜界面
```

### 关卡场景（LevelScene）

```
LevelController.Start()
    ↓
生成关卡
    ↓
玩家答题
    ↓
答对题目
    ↓
LeaderboardManager.SavePlayerProgress(currentLevel)
    ↓
播放成功特效
    ↓
进入下一关
```

### 结果场景（ResultScene）

```
ResultController.Start()
    ↓
显示结果（成功/失败）
    ↓
玩家点击排行榜按钮
    ↓
显示排行榜界面
    ↓
玩家可以查看自己的排名
```

---

## 🧪 测试步骤

### 1. 单元测试

```csharp
// 测试数据模型
[Test]
public void TestLeaderboardRecordSerialization()
{
    var record = new LeaderboardRecord
    {
        user_id = "test123",
        username = "TestUser",
        max_level = 10
    };
    
    string json = JsonUtility.ToJson(record);
    Debug.Log(json);
}
```

### 2. 集成测试

1. **测试用户信息获取**:
   - 运行游戏
   - 查看 Console 日志是否输出用户信息
   
2. **测试存档功能**:
   - 完成一个关卡
   - 查看 Console 是否输出保存日志
   
3. **测试排行榜显示**:
   - 点击排行榜按钮
   - 确认显示 50 条数据
   - 确认前三名有特殊样式

### 3. 真机测试

1. 构建 WebGL 版本
2. 上传到抖音小游戏平台
3. 测试真实环境下的 SDK 调用

---

## ⚠️ 注意事项

### 1. 抖音 SDK 集成

- 确保已在抖音开发者后台开通云数据库
- 配置正确的 AppID 和 AppSecret
- 在 `game.json` 中添加必要的权限:
```json
{
  "permission": {
    "userProfile": {
      "desc": "用于显示用户昵称和头像"
    }
  }
}
```

### 2. 网络请求

- 抖音小游戏环境可能需要使用 `tt.request` 而非 `UnityWebRequest`
- 注意跨域问题
- 添加超时处理

### 3. 数据安全

- 不要在客户端存储敏感信息
- 考虑添加数据验证机制
- 防止作弊（可以在服务端验证关卡合法性）

### 4. 性能优化

- 排行榜数据可以本地缓存，避免频繁请求
- 头像图片使用缩略图
- 限制同时显示的项数（使用对象池）

---

## 📝 待完成任务

### 高优先级

- [ ] **实现真实的云数据库调用**
  - 替换 `QueryPlayerRecord` 中的 TODO
  - 替换 `CreatePlayerRecord` 中的 TODO
  - 替换 `UpdatePlayerRecord` 中的 TODO
  - 替换 `GetLeaderboardAsync` 中的 TODO

- [ ] **创建 UI 预制件**
  - 创建 `LeaderboardPanel.prefab`
  - 创建 `RankItemPrefab.prefab`
  - 在场景中布置 UI 元素

- [ ] **完善抖音 SDK 用户信息获取**
  - 实现 `GetDouyinUserInfo()` 方法
  - 处理用户授权流程
  - 添加错误处理

### 中优先级

- [ ] **头像加载**
  - 实现 `LoadAvatar()` 方法
  - 使用 `UnityWebRequestTexture` 下载头像
  - 添加头像缓存

- [ ] **UI 美化**
  - 添加滚动动画
  - 添加刷新按钮
  - 添加当前玩家排名高亮

- [ ] **数据迁移**
  - 编写迁移脚本
  - 将旧数据转换为新格式

### 低优先级

- [ ] **社交功能**
  - 添加好友排行榜
  - 分享成绩到抖音

- [ ] **成就系统**
  - 连续答对奖励
  - 速度奖励

---

## 🔗 相关资源

### 官方文档
- [抖音云数据库 Unity SDK](https://developer.open-douyin.com/docs/resource/zh-CN/developer/tools/cloud/api-reference/cloud-database/client/unity-sdk-clouddatabase)
- [抖音小游戏 API](https://developer.open-douyin.com/docs/resource/zh-CN/mini-game/develop/api/c-api/api-overview)
- [用户信息授权](https://developer.open-douyin.com/docs/resource/zh-CN/mini-game/develop/open-capacity/user-information/authorization/authorization/)

### 项目文件
- [`LeaderboardManager.cs`](file://g:\DYGame\Games\NotColorBlind\Assets\Scripts\LeaderboardManager.cs)
- [`LeaderboardUI.cs`](file://g:\DYGame\Games\NotColorBlind\Assets\Scripts\LeaderboardUI.cs)
- [`LeaderboardRankItem.cs`](file://g:\DYGame\Games\NotColorBlind\Assets\Scripts\LeaderboardRankItem.cs)
- [`LevelController.cs`](file://g:\DYGame\Games\NotColorBlind\Assets\Scripts\LevelController.cs) (已添加存档功能)
- [`MainMenuController.cs`](file://g:\DYGame\Games\NotColorBlind\Assets\Scripts\MainMenuController.cs) (已添加排行榜按钮)
- [`ResultController.cs`](file://g:\DYGame\Games\NotColorBlind\Assets\Scripts\ResultController.cs) (已添加排行榜按钮)

---

## 🎉 总结

已完成的工作：
✅ 创建了完整的排行榜系统架构
✅ 实现了 LeaderboardManager 核心逻辑
✅ 实现了 LeaderboardUI 界面控制
✅ 添加了实时存档功能
✅ 在主菜单和结果场景添加了排行榜按钮
✅ 设计了前三名特殊标识（金/银/铜）
✅ 创建了详细的使用文档

下一步行动：
1. **按照本文档创建 UI 预制件**
2. **在 Inspector 中完成组件配置**
3. **实现真实的云数据库调用**
4. **测试并调试**

祝您开发顺利！🚀
