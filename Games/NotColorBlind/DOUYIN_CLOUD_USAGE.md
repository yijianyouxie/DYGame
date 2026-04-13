# 抖音云数据库集成使用说明

## 概述

本项目已经集成了抖音云数据库功能，可以用于：
- ✅ 获取用户信息（用户名、头像）
- ✅ 保存和加载玩家关卡进度
- ✅ 保存和加载玩家忙币数量
- ✅ 获取排行榜数据

## 文件说明

### 核心文件

1. **DouyinCloudManager.cs**
   - 抖音云数据库管理器
   - 负责所有云数据库的底层操作
   - 单例模式，自动初始化

2. **LeaderboardManager.cs**
   - 排行榜业务逻辑管理器
   - 负责用户信息获取、数据保存、排行榜查询
   - 单例模式，需要配合 DouyinCloudManager 使用

3. **GameDataSyncManager.cs**
   - 游戏数据同步管理器
   - 负责在游戏过程中自动同步数据
   - 提供便捷的 API 用于更新关卡和忙币

4. **LeaderboardUI.cs**
   - 排行榜 UI 控制器
   - 负责排行榜界面的显示和交互

### 数据结构

1. **PlayerData**
   - 云数据库中存储的玩家数据结构
   - 包含：用户 ID、用户名、头像、关卡、忙币等

2. **LeaderboardRecord**
   - 排行榜显示用的数据结构
   - 包含：排名、用户名、关卡、更新时间等

## 使用步骤

### 1. 场景配置

在游戏的主场景（Start 场景）中添加以下管理器：

```
Hierarchy:
├── DouyinCloudManager (单例，会自动创建)
├── LeaderboardManager (单例，会自动创建)
├── GameDataSyncManager (单例，会自动创建)
└── ...其他游戏对象
```

建议在场景的初始化脚本中调用：

```csharp
void Start()
{
    // 确保管理器已初始化
    var cloudManager = DouyinCloudManager.Instance;
    var leaderboardManager = LeaderboardManager.Instance;
    var syncManager = GameDataSyncManager.Instance;

    // 订阅用户信息就绪事件
    leaderboardManager.OnUserInfoReady += OnUserInfoReady;
}

void OnUserInfoReady(PlayerData playerData)
{
    Debug.Log($"玩家：{playerData.username}");
    Debug.Log($"关卡：{playerData.max_level}");
    Debug.Log($"忙币：{playerData.busy_coins}");
}
```

### 2. 保存游戏数据

#### 自动保存（推荐）

GameDataSyncManager 会每 30 秒自动保存一次数据：

```csharp
// 在游戏启动时初始化
GameDataSyncManager.Instance;

// 自动保存会在后台进行
```

#### 手动保存

在关键节点手动触发保存：

```csharp
// 场景 1：关卡完成
void OnLevelComplete(int level)
{
    // 更新关卡
    GameDataSyncManager.Instance.UpdateLevel(level);

    // 奖励忙币
    GameDataSyncManager.Instance.AddCoins(10);
}

// 场景 2：消耗忙币
void OnBuyItem(int cost)
{
    if (GameDataSyncManager.Instance.SpendCoins(cost))
    {
        Debug.Log("购买成功");
    }
    else
    {
        Debug.Log("忙币不足");
    }
}

// 场景 3：主动保存
void ManualSave()
{
    GameDataSyncManager.Instance.SaveNow();
}
```

#### 使用 LeaderboardManager 直接保存

```csharp
// 保存关卡进度
LeaderboardManager.Instance.SavePlayerProgress(GameData.CurrentLevel);

// 保存忙币数量
LeaderboardManager.Instance.SavePlayerCoins(GameData.BusyCoinCount);
```

### 3. 显示排行榜

在排行榜按钮点击事件中：

```csharp
public void OnLeaderboardButtonClick()
{
    // 显示排行榜界面
    LeaderboardUI leaderboardUI = FindObjectOfType<LeaderboardUI>();
    if (leaderboardUI != null)
    {
        leaderboardUI.ShowLeaderboard();
    }
}
```

LeaderboardUI 会自动调用 `LeaderboardManager.Instance.GetLeaderboardAsync()` 获取数据。

### 4. 获取用户信息

在游戏初始化时获取用户信息：

```csharp
void Start()
{
    // 订阅用户信息就绪事件
    LeaderboardManager.Instance.OnUserInfoReady += (playerData) =>
    {
        // 显示用户名
        UpdateUserNameDisplay(playerData.username);

        // 显示关卡
        UpdateLevelDisplay(playerData.max_level);

        // 显示忙币
        UpdateCoinsDisplay(playerData.busy_coins);
    };
}

void UpdateUserNameDisplay(string username)
{
    // 更新 UI 显示用户名
    Debug.Log($"显示用户名：{username}");
}

void UpdateLevelDisplay(int level)
{
    // 更新 UI 显示关卡
    Debug.Log($"显示关卡：{level}");
}

void UpdateCoinsDisplay(int coins)
{
    // 更新 UI 显示忙币
    Debug.Log($"显示忙币：{coins}");
}
```

## 配置说明

### DouyinCloudManager 配置

```csharp
public class DouyinCloudManager : MonoBehaviour
{
    [Header("云数据库配置")]
    public string databaseName = "leaderboard"; // 数据库名称
    public string collectionName = "player_data"; // 集合名称
}
```

在抖音云控制台创建对应的数据库和集合。

### LeaderboardManager 配置

```csharp
public class LeaderboardManager : MonoBehaviour
{
    [Header("数据库配置")]
    public string collectionName = "player_data"; // 数据集合名称
}
```

### GameDataSyncManager 配置

```csharp
public class GameDataSyncManager : MonoBehaviour
{
    [Header("自动保存配置")]
    public float autoSaveInterval = 30f; // 自动保存间隔（秒）
}
```

## 数据流程

### 启动流程

```
1. 游戏启动
   ↓
2. DouyinCloudManager 初始化
   ↓
3. LeaderboardManager 初始化
   ↓
4. 调用抖音 SDK 获取用户信息
   ↓
5. 从云数据库加载玩家数据
   ↓
6. 更新 GameData（关卡、忙币）
   ↓
7. 触发 OnUserInfoReady 事件
   ↓
8. 游戏正常运行
```

### 保存流程

```
1. 游戏事件触发（关卡完成、消耗忙币等）
   ↓
2. 更新本地 GameData
   ↓
3. 调用 GameDataSyncManager 或 LeaderboardManager 保存
   ↓
4. 查询云数据库中是否有该玩家记录
   ↓
5a. 有记录 → 更新现有记录
5b. 无记录 → 创建新记录
   ↓
6. 保存完成
```

### 排行榜流程

```
1. 用户点击排行榜按钮
   ↓
2. LeaderboardUI.ShowLeaderboard() 被调用
   ↓
3. 调用 LeaderboardManager.Instance.GetLeaderboardAsync()
   ↓
4. 构建聚合查询（按关卡降序）
   ↓
5. 调用云数据库查询
   ↓
6. 返回排行榜数据
   ↓
7. LeaderboardUI 填充并显示排行榜
```

## 测试步骤

### 1. 本地测试（模拟数据）

在未配置真实抖音云的情况下，代码会使用模拟数据：

```csharp
// 自动生成的模拟数据
- 用户 ID：随机生成
- 用户名："游客_" + GameData.PlayerName
- 头像：空
```

### 2. 真实云数据库测试

配置完成后，按照以下步骤测试：

1. **初始化测试**
   ```
   - 运行游戏
   - 检查 Console 是否输出 "获取到用户信息"
   - 检查是否成功从云数据库加载数据
   ```

2. **保存测试**
   ```
   - 完成一关
   - 检查 Console 是否输出 "保存玩家数据"
   - 在云控制台查看数据是否更新
   ```

3. **排行榜测试**
   ```
   - 点击排行榜按钮
   - 检查排行榜是否正确显示
   - 验证排序是否正确（关卡降序）
   ```

4. **多设备测试**
   ```
   - 在不同设备上登录同一账号
   - 验证数据是否同步
   - 验证排行榜是否实时更新
   ```

## 注意事项

1. **网络连接**
   - 云数据库操作需要网络连接
   - 建议在操作前检查网络状态
   - 提供离线缓存机制（可选）

2. **错误处理**
   - 所有的云数据库操作都包含 try-catch
   - 失败时会回退到模拟数据
   - 检查 Console 输出获取错误信息

3. **性能优化**
   - 避免频繁保存（使用自动保存）
   - 排行榜查询限制数量（50 条）
   - 考虑使用分页加载（如果数据量大）

4. **数据安全**
   - 生产环境配置合适的读写权限
   - 敏感数据加密（可选）
   - 避免存储用户隐私信息

## 常见问题

### Q1: 用户信息获取失败？

**A**: 检查以下项：
- 抖音 SDK 是否正确初始化
- 用户是否授权
- 网络是否正常
- 查看 Console 错误信息

### Q2: 数据保存失败？

**A**: 检查以下项：
- 云数据库配置是否正确
- 权限配置是否允许写入
- 数据格式是否正确
- 查看 Console 错误信息

### Q3: 排行榜不显示数据？

**A**: 检查以下项：
- 云数据库中是否有数据
- 查询语句是否正确
- LeaderboardUI 是否正确配置
- 查看 Console 输出

### Q4: 如何清除本地缓存？

**A**: 删除游戏数据存储文件（如果实现了本地缓存），或在云控制台手动删除记录。

## 下一步

1. **配置云数据库**
   - 参考 `DOUYIN_CLOUD_SETUP.md` 配置云数据库

2. **替换 SDK 调用**
   - 在 `DouyinCloudManager.cs` 中替换模拟代码为真实 SDK 调用
   - 在 `LeaderboardManager.cs` 中替换 `GetDouyinUserInfo()` 方法

3. **测试验证**
   - 完成上述配置后进行测试
   - 验证所有功能正常工作

4. **发布上线**
   - 确保生产环境配置正确
   - 进行压力测试
   - 监控数据库性能

## 技术支持

如有问题，请查看：
- 抖音云开发文档：https://developer.open-douyin.com/docs/resource/zh-CN/developer/tools/cloud/develop-guide/local-develop/douyincloud-basedon-app/sc-game-how-to-use-cloud
- 抖音小游戏 API 文档：https://developer.open-douyin.com/docs/resource/zh-CN/mini-game/develop/api/c-api/api-overview
- 项目控制台输出（查看详细错误信息）
