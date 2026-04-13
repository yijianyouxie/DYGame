# 抖音云数据库集成检查清单

## 前置条件

### 抖音云开发配置

- [ ] 已注册抖音开放平台账号
- [ ] 已创建抖音云开发空间
- [ ] 已开通云数据库服务
- [ ] 已创建数据库（名称：`leaderboard`）
- [ ] 已创建集合（名称：`player_data`）

### 需要提供的配置信息

请在实现前准备以下信息：

- [ ] **云空间 ID (Space ID)**: `cloud-xxxxx`
- [ ] **环境名称 (Env Name)**: `development` 或 `production`
- [ ] **数据库名称**: `leaderboard`
- [ ] **集合名称**: `player_data`
- [ ] **是否使用云函数**: 是 / 否
- [ ] **抖音 SDK 版本**: _______________

## Unity 项目配置

### SDK 安装

- [ ] 已下载抖音小游戏 SDK
- [ ] 已导入抖音 SDK 到 Unity 项目
- [ ] 已安装 JSON 库（推荐 LitJson）
- [ ] 已配置抖音 App ID

### 文件检查

- [ ] `DouyinCloudManager.cs` 已添加到项目
- [ ] `LeaderboardManager.cs` 已添加到项目
- [ ] `GameDataSyncManager.cs` 已添加到项目
- [ ] `LeaderboardUI.cs` 已配置正确
- [ ] `RankItemPrefab.prefab` 已创建
- [ ] `LeaderboardPanel.prefab` 已创建

### 场景配置

- [ ] Start 场景中已包含 LeaderboardPanel 实例
- [ ] ResultScene 场景中已包含 LeaderboardPanel 实例
- [ ] LeaderboardUI 组件已正确绑定引用：
  - [ ] panelRoot
  - [ ] closeButton
  - [ ] contentParent
  - [ ] rankItemPrefab

## 代码实现检查

### DouyinCloudManager.cs

- [ ] 已配置 `databaseName`
- [ ] 已配置 `collectionName`
- [ ] `InitializeAsync()` 方法已正确实现
- [ ] 云函数调用方法已实现（或使用直接数据库操作）

### LeaderboardManager.cs

- [ ] 已配置 `collectionName`
- [ ] `GetDouyinUserInfo()` 已替换为真实 SDK 调用
- [ ] 用户信息获取逻辑已实现
- [ ] 数据保存逻辑已实现
- [ ] 排行榜查询逻辑已实现

### GameDataSyncManager.cs

- [ ] 已配置 `autoSaveInterval`
- [ ] 自动保存功能已测试
- [ ] 手动保存方法已测试
- [ ] 忙币消耗逻辑已测试

## 云数据库配置检查

### 集合结构

`player_data` 集合应包含以下字段：

```json
{
  "_id": "自动生成",
  "user_id": "用户 open_id",
  "username": "用户昵称",
  "avatar_url": "头像 URL",
  "max_level": "最高关卡（整数）",
  "busy_coins": "忙币数量（整数）",
  "total_play_time": "总游戏时长（秒）",
  "play_count": "游戏次数",
  "created_at": "创建时间",
  "updated_at": "更新时间"
}
```

- [ ] `user_id` 字段：string 类型
- [ ] `username` 字段：string 类型
- [ ] `avatar_url` 字段：string 类型
- [ ] `max_level` 字段：int 类型
- [ ] `busy_coins` 字段：int 类型
- [ ] `created_at` 字段：string 类型
- [ ] `updated_at` 字段：string 类型

### 索引配置（建议）

- [ ] `user_id` 唯一索引（加速查询）
- [ ] `max_level` 降序索引 + `updated_at` 升序索引（加速排行榜查询）

```javascript
// 创建索引的云函数或控制台命令
db.player_data.createIndex({ "user_id": 1 }, { unique: true })
db.player_data.createIndex({ "max_level": -1, "updated_at": 1 })
```

### 权限配置

- [ ] 读取权限：已配置
- [ ] 写入权限：已配置
- [ ] 更新权限：已配置
- [ ] 查询权限：已配置

## 测试检查

### 本地测试

- [ ] 游戏可正常启动
- [ ] 无编译错误
- [ ] 无运行时错误
- [ ] Console 输出正常

### 功能测试

#### 用户信息获取

- [ ] 启动时成功获取用户信息
- [ ] Console 输出 "获取到用户信息"
- [ ] 用户名正确显示
- [ ] 头像正确显示（如有）

#### 数据保存

- [ ] 完成关卡后保存成功
- [ ] Console 输出 "保存玩家数据"
- [ ] 忙币消耗后保存成功
- [ ] 云数据库中数据已更新

#### 数据加载

- [ ] 重新启动游戏后数据已加载
- [ ] 关卡进度正确恢复
- [ ] 忙币数量正确恢复

#### 排行榜

- [ ] 排行榜按钮可点击
- [ ] 排行榜界面正常显示
- [ ] 数据正确填充
- [ ] 排序正确（关卡降序）
- [ ] 滚动功能正常
- [ ] 当前玩家高亮显示

#### 自动保存

- [ ] 每 30 秒自动保存一次
- [ ] 应用暂停时保存
- [ ] 应用退出时保存

### 真实云数据库测试

- [ ] 云数据库连接成功
- [ ] 数据成功写入云数据库
- [ ] 数据成功从云数据库读取
- [ ] 排行榜数据正确获取
- [ ] 多设备数据同步正常

## UI 配置检查

### LeaderboardPanel

- [ ] 位置：底部到 3/4 屏幕高度
- [ ] 宽度：充满屏幕
- [ ] 背景：background2 精灵

### Viewport

- [ ] RectTransform 配置正确
- [ ] Mask 组件已添加
- [ ] Mask 组件正常工作（内容裁剪）

### ScrollContainer

- [ ] VerticalLayoutGroup 组件已添加
- [ ] ContentSizeFitter 组件已添加
- [ ] 从顶部开始排列

### RankItemPrefab

- [ ] 高度：75
- [ ] 背景：bg_info2 精灵
- [ ] RankText 字体大小：27
- [ ] NameText 字体大小：24
- [ ] LevelText 字体大小：21
- [ ] LayoutElement 组件已添加

### CloseButton

- [ ] 位置：右上角
- [ ] 点击事件正常触发
- [ ] 使用 Image 组件（非 Text）

## 性能检查

- [ ] 启动时间可接受（< 5 秒）
- [ ] 排行榜加载速度可接受（< 2 秒）
- [ ] 数据保存不影响游戏流畅度
- [ ] 内存使用正常

## 错误处理检查

- [ ] 网络断开时有提示
- [ ] 云数据库访问失败时有回退
- [ ] 用户未授权时有提示
- [ ] 所有异常都有日志输出

## 文档检查

- [ ] 已阅读 `DOUYIN_CLOUD_SETUP.md`
- [ ] 已阅读 `DOUYIN_CLOUD_USAGE.md`
- [ ] 已查看抖音云开发官方文档
- [ ] 已查看抖音小游戏 API 文档

## 发布前检查

- [ ] 生产环境配置正确
- [ ] 云数据库权限配置正确
- [ ] 所有调试代码已移除
- [ ] 日志级别已调整
- [ ] 性能测试已通过
- [ ] 真机测试已通过

## 完成标记

当你完成所有检查项后，标记：

- [ ] 集成完成
- [ ] 测试通过
- [ ] 准备发布

---

## 快速参考

### 代码示例

```csharp
// 保存关卡
GameDataSyncManager.Instance.UpdateLevel(newLevel);

// 保存忙币
GameDataSyncManager.Instance.UpdateCoins(newCoins);

// 消耗忙币
if (GameDataSyncManager.Instance.SpendCoins(cost))
{
    // 消耗成功
}

// 显示排行榜
FindObjectOfType<LeaderboardUI>()?.ShowLeaderboard();

// 获取用户信息
LeaderboardManager.Instance.OnUserInfoReady += (playerData) => {
    Debug.Log($"玩家：{playerData.username}");
};
```

### 常见 Console 输出

- ✅ `[DouyinCloudManager] 抖音云服务初始化成功`
- ✅ `[LeaderboardManager] 获取到用户信息：xxx`
- ✅ `[LeaderboardManager] 加载关卡：5`
- ✅ `[LeaderboardManager] 加载忙币：100`
- ✅ `[LeaderboardManager] 保存玩家数据：关卡 5, 忙币 100`
- ✅ `[LeaderboardManager] 获取到 50 条排行榜数据`

### 常见错误信息

- ❌ `[DouyinCloudManager] 初始化失败：xxx`
- ❌ `[LeaderboardManager] 用户 ID 为空，无法保存数据`
- ❌ `[LeaderboardManager] 保存数据失败：xxx`
- ❌ `[LeaderboardManager] 获取排行榜失败：xxx`

---

**完成所有检查项后，抖音云数据库集成即可正常使用！**
