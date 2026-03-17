# 排行榜系统 - 快速开始指南

## 🚀 5 分钟快速配置

### 第 1 步：创建 UI 预制件（3 分钟）

#### 1.1 创建 LeaderboardPanel

1. **Hierarchy 中右键** → UI → Panel
2. 重命名为 `LeaderboardPanel`
3. **设置属性**:
   ```
   Pos X: 0, Pos Y: 0
   Width: 800, Height: 600
   Anchor: Center
   ```

4. **添加子元素**:
   - **Header** (Image)
     - Height: 60
     - 添加 Text 组件，输入 "排行榜"
   
   - **CloseButton** (Button)
     - Pos X: 370, Pos Y: 20
     - Width: 40, Height: 40
     - Text: "×"
   
   - **Scroll View** (UI → Scroll View)
     - Pos X: 20, Pos Y: -20
     - Width: 760, Height: 500
     - 在 Content 下添加 Vertical Layout Group:
       ```
       Spacing: 10
       Child Force Expand Width: ✓
       ```

#### 1.2 创建 RankItemPrefab

1. **Hierarchy 中右键** → UI → Panel
2. 重命名为 `RankItemPrefab`
3. **设置属性**:
   ```
   Height: 60
   Anchor: Stretch Left/Right
   Pos X: 0, Width: -40
   ```

4. **添加子元素**:
   - **Background** (Image) - 填充整个面板
   - **RankText** (Text)
     - Width: 50
     - Font Size: 24
     - Text: "1"
   - **NameText** (Text)
     - Pos X: 60
     - Text: "用户名"
   - **LevelText** (Text)
     - Pos X: 400
     - Text: "第 X 关"

5. **保存为 Prefab**:
   - 拖到 `Assets/Prefabs/RankItemPrefab.prefab`

6. **同样保存 LeaderboardPanel**:
   - 拖到 `Assets/Prefabs/LeaderboardPanel.prefab`

---

### 第 2 步：配置组件引用（2 分钟）

#### 2.1 配置 LeaderboardUI

1. 选中 `LeaderboardPanel`
2. 添加 `LeaderboardUI` 组件
3. **拖拽赋值**:
   ```
   Panel Root: LeaderboardPanel (自身)
   Close Button: CloseButton
   Content Parent: Scroll View/Viewport/Content
   Rank Item Prefab: RankItemPrefab
   ```

#### 2.2 配置 MainMenuController

1. 找到主菜单的 Controller 对象
2. 在 `MainMenuController` 中:
   ```
   Leaderboard Button: 你的排行榜按钮
   Leaderboard UI: 刚才创建的 LeaderboardPanel
   ```

#### 2.3 配置 ResultController

1. 找到结果场景的 Controller 对象
2. 在 `ResultController` 中:
   ```
   Leaderboard Button: 你的排行榜按钮
   Leaderboard UI: 同样的 LeaderboardPanel (或新建一个)
   ```

---

### 第 3 步：测试运行（1 分钟）

1. **打开 Unity**
2. **运行游戏**
3. **点击排行榜按钮**
4. **查看效果**:
   - ✅ 应该显示排行榜界面
   - ✅ 显示 50 条模拟数据
   - ✅ 前三名有金/银/铜色标识
   - ✅ 点击关闭按钮隐藏界面

---

## ⚙️ 云数据库配置

### 抖音开发者后台操作

1. **登录后台**: https://developer.open-douyin.com
2. **进入云数据库**
3. **创建集合**: `leaderboard`
4. **添加索引**:
   - `user_id`: 唯一索引
   - `max_level`: 普通索引（用于排序）
   - `update_time`: 普通索引

### 修改代码连接真实数据库

打开 [`LeaderboardManager.cs`](file://g:\DYGame\Games\NotColorBlind\Assets\Scripts\LeaderboardManager.cs)

找到以下方法并替换 TODO 部分：

```csharp
// 第 147 行：QueryPlayerRecord
private async Task<LeaderboardRecord> QueryPlayerRecord(string userId)
{
    // 使用抖音云数据库 API
    var db = CloudDatabase.DefaultDatabase();
    var collection = db.Collection("leaderboard");
    
    var query = collection.Where("user_id", "==", userId);
    var result = await query.Get();
    
    if (result.Count > 0)
    {
        return JsonUtility.FromJson<LeaderboardRecord>(result[0].ToJson());
    }
    return null;
}
```

```csharp
// 第 166 行：CreatePlayerRecord
private async Task CreatePlayerRecord(int level)
{
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
}
```

```csharp
// 第 178 行：UpdatePlayerRecord
private async Task UpdatePlayerRecord(string recordId, int newLevel)
{
    var db = CloudDatabase.DefaultDatabase();
    var collection = db.Collection("leaderboard");
    
    var updateData = new Dictionary<string, object>
    {
        { "max_level", newLevel },
        { "update_time", DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") }
    };
    
    await collection.Document(recordId).Update(updateData);
}
```

```csharp
// 第 189 行：GetLeaderboardAsync
public async Task<List<LeaderboardRecord>> GetLeaderboardAsync()
{
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
}
```

---

## 🎨 UI 美化建议

### 颜色方案

```
背景色：半透明黑色 RGBA(0, 0, 0, 0.8)
边框色：金色 RGBA(255, 215, 0, 0.5)
文字色：白色
第一名：金色 RGBA(255, 215, 0, 1)
第二名：银色 RGBA(192, 192, 192, 1)
第三名：铜色 RGBA(205, 127, 50, 1)
```

### 字体选择

- **标题**: 微软雅黑 Bold, 36pt
- **排名**: Arial Bold, 24pt
- **用户名**: 微软雅黑，20pt
- **关卡**: Arial, 18pt

### 动画效果

可以添加 DOTween 插件实现:
```csharp
// 显示时从上方滑入
panelRoot.DOMoveY(Screen.height / 2, 0.3f);

// 关闭时淡出
panelRoot.DOFade(0, 0.2f);
```

---

## 🐛 常见问题排查

### Q1: 点击排行榜按钮没反应

**检查**:
1. Button 是否绑定了 OnClick 事件
2. LeaderboardUI 是否赋值
3. Console 是否有错误日志

### Q2: 排行榜显示空白

**检查**:
1. RankItemPrefab 是否正确赋值
2. ContentParent 是否为空
3. 查看 Console 是否有 "未赋值" 的错误

### Q3: 前三名颜色不对

**检查**:
1. LeaderboardUI 中的 goldColor/silverColor/bronzeColor 是否设置正确
2. SetRankStyle 方法是否被调用

### Q4: 无法连接云数据库

**检查**:
1. 抖音 SDK 是否初始化
2. AppID 是否正确
3. 网络权限是否开启
4. 查看 Console 的网络错误信息

---

## 📱 真机调试技巧

### 1. 启用远程调试

在 `game.json` 中添加:
```json
{
  "debug": true
}
```

### 2. 查看真机日志

使用抖音开发者工具的远程调试功能

### 3. 性能监控

添加 FPS 显示:
```csharp
QualitySettings.vSyncCount = 0; // 禁用垂直同步
Application.targetFrameRate = 60; // 目标 60 帧
```

---

## ✅ 检查清单

在发布前确认:

- [ ] UI 预制件已创建并正确配置
- [ ] 所有 Inspector 引用已赋值
- [ ] 云数据库集合已创建
- [ ] 索引已建立
- [ ] 测试过存档功能
- [ ] 测试过排行榜显示
- [ ] 前三名样式正确
- [ ] 真机测试通过
- [ ] 性能测试通过（无明显卡顿）

---

## 🎯 下一步优化

完成基础功能后可以考虑:

1. **好友排行榜**: 只显示微信/抖音好友
2. **全国排行榜**: 按地区分组
3. **赛季制度**: 每月重置排行榜
4. **成就系统**: 连续答对奖励
5. **分享功能**: 分享成绩到抖音

---

祝您开发顺利！有任何问题欢迎随时询问。🎉
