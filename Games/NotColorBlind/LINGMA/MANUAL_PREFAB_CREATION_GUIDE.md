# 排行榜预制件手动创建指南

## ⚠️ 重要说明

MCP Unity 工具目前**无法直接保存预制件文件**。你需要在 Unity 编辑器中手动完成以下操作。

---

## 📋 方法一：使用 Unity 编辑器（推荐）

### 步骤 1：检查 Hierarchy 中的 GameObject

打开 Unity 后，在 Hierarchy 窗口中应该能看到之前通过 MCP 创建的 GameObject：

```
Hierarchy
├─ LeaderboardPanel ✓
│  ├─ CloseButton ✓
│  └─ ScrollContainer ✓
└─ RankItemPrefab ✓
```

**如果看不到这些 GameObject**，说明之前的 MCP 调用没有成功创建。请跳过此部分，直接使用**方法二**重新创建。

### 步骤 2：创建 Prefabs 文件夹

1. **在 Project 窗口中**：
   - 右键点击 `Assets/` 目录
   - 选择 `Create → Folder`
   - 命名为 `Prefabs`

2. **最终路径**：
   ```
   Assets/
   └─ Prefabs/  ← 新建的文件夹
   ```

### 步骤 3：保存 LeaderboardPanel 为预制件

#### 方式 A：拖拽法（最简单）

1. **在 Hierarchy 中选中** `LeaderboardPanel`
2. **按住鼠标左键拖拽**到 Project 窗口的 `Assets/Prefabs/` 文件夹
3. **松开鼠标**，Unity 会自动创建预制件
4. **检查结果**：
   ```
   Assets/Prefabs/
   └─ LeaderboardPanel.prefab ✓
   ```

#### 方式 B：右键菜单法

1. **在 Hierarchy 中右键点击** `LeaderboardPanel`
2. **选择** `Create Prefab...`
3. **在弹出的保存对话框中**：
   - 导航到 `Assets/Prefabs/` 目录
   - 文件名输入：`LeaderboardPanel`
   - 点击 `Save` 按钮
4. **检查结果**：
   ```
   Assets/Prefabs/
   └─ LeaderboardPanel.prefab ✓
   ```

### 步骤 4：保存 RankItemPrefab 为预制件

重复步骤 3 的操作：

1. **在 Hierarchy 中选中** `RankItemPrefab`
2. **拖拽到** `Assets/Prefabs/` 文件夹
3. **确认创建成功**：
   ```
   Assets/Prefabs/
   ├─ LeaderboardPanel.prefab
   └─ RankItemPrefab.prefab ✓
   ```

### 步骤 5：清理 Hierarchy

保存为预制件后，Hierarchy 中的原始 GameObject 可以删除（或保留用于配置）：

- **如果要删除**：右键点击 → `Delete`
- **如果要保留**：将其拖到 Canvas 下作为子对象继续使用

---

## 📋 方法二：如果 Hierarchy 中没有 GameObject

如果之前的 MCP 调用失败，Hierarchy 中没有看到这些 GameObject，请按以下步骤手动创建：

### 创建 LeaderboardPanel

1. **在 Hierarchy 中右键** → `UI` → `Panel`
2. **重命名为** `LeaderboardPanel`
3. **添加组件**（在 Inspector中）：
   - 点击 `Add Component`
   - 搜索并添加 `LeaderboardUI`（自动关联脚本）

4. **设置 RectTransform**：
   ```
   Anchor: Center
   Pivot: (0.5, 0.5)
   Pos X: 0, Pos Y: 0
   Width: 800, Height: 600
   ```

5. **设置 Image 颜色**：
   ```
   Color: RGBA(0, 0, 0, 200)  // 半透明黑色
   ```

### 创建子对象

#### CloseButton

1. **右键 LeaderboardPanel** → `UI` → `Button`
2. **重命名为** `CloseButton`
3. **设置 RectTransform**：
   ```
   Anchor: Top Right
   Pos X: -20, Pos Y: -20
   Width: 40, Height: 40
   ```
4. **修改 Text**：
   - Text 内容改为：`×`
   - Font Size: 28

#### ScrollContainer

1. **右键 LeaderboardPanel** → `Create Empty`
2. **重命名为** `ScrollContainer`
3. **添加组件**：`Rect Mask 2D`（可选，用于裁剪）
4. **设置 RectTransform**：
   ```
   Anchor: Stretch
   Pos X: 20, Pos Y: -60
   Width: -40, Height: -120
   ```
5. **添加 Vertical Layout Group**：
   ```
   Spacing: 10
   Child Force Expand Width: ✓
   Child Control Width: ✓
   Child Force Expand Height: ✗
   ```

### 创建 RankItemPrefab

1. **在 Hierarchy 中右键** → `UI` → `Panel`
2. **重命名为** `RankItemPrefab`
3. **添加组件**：
   - `LeaderboardRankItem` 脚本

4. **设置 RectTransform**：
   ```
   Anchor: Stretch Left/Right
   Width: -20, Height: 60
   ```

5. **添加子元素**：
   - **Background** (Image)
   - **RankText** (Text) - 显示排名
   - **NameText** (Text) - 显示用户名
   - **LevelText** (Text) - 显示关卡数

### 保存为预制件

按照**方法一**的步骤，将创建的 GameObject 拖到 `Assets/Prefabs/` 文件夹。

---

## 🎨 配置 LeaderboardUI 组件

保存预制件后，需要配置组件引用：

### 1. 选中 LeaderboardPanel

在 Hierarchy 或 Project 窗口中选中 `LeaderboardPanel`

### 2. 在 Inspector 中找到 LeaderboardUI 组件

展开 `LeaderboardUI (Script)` 组件

### 3. 拖拽赋值所有字段

```
LeaderboardUI (Script)
├─ UI 组件引用
│  ├─ Panel Root: LeaderboardPanel (拖入自身)
│  ├─ Close Button: CloseButton (拖入 CloseButton 子对象)
│  ├─ Content Parent: ScrollContainer (拖入 ScrollContainer 子对象)
│  └─ Rank Item Prefab: RankItemPrefab (从 Assets/Prefabs/拖入预制件)
├─ 前三名特殊标识
│  └─ Crown Image: (可选，留空)
└─ 颜色配置
   ├─ Gold Color: RGBA(255, 215, 0, 255)
   ├─ Silver Color: RGBA(192, 192, 192, 255)
   ├─ Bronze Color: RGBA(205, 127, 50, 255)
   └─ Normal Color: RGBA(255, 255, 255, 255)
```

**详细操作步骤**：

1. **Panel Root**:
   - 在 Hierarchy 中选中 `LeaderboardPanel`
   - 拖到 `Panel Root` 字段

2. **Close Button**:
   - 展开 `LeaderboardPanel`
   - 找到 `CloseButton` 子对象
   - 拖到 `Close Button` 字段

3. **Content Parent**:
   - 找到 `ScrollContainer` 子对象
   - 拖到 `Content Parent` 字段

4. **Rank Item Prefab**:
   - 打开 Project 窗口
   - 展开 `Assets/Prefabs/`
   - 找到 `RankItemPrefab.prefab`
   - 拖到 `Rank Item Prefab` 字段

---

## ✅ 验证清单

完成后请检查以下项目：

- [ ] `Assets/Prefabs/` 文件夹存在
- [ ] `LeaderboardPanel.prefab` 已创建
- [ ] `RankItemPrefab.prefab` 已创建
- [ ] `LeaderboardUI` 组件的所有字段都已赋值
- [ ] `CloseButton` 是 `LeaderboardPanel` 的子对象
- [ ] `ScrollContainer` 是 `LeaderboardPanel` 的子对象
- [ ] `RankItemPrefab` 包含 `LeaderboardRankItem` 脚本

---

## 🎯 测试运行

### 1. 添加到场景

1. **打开 Start.scene**（或任意场景）
2. **从 Project 窗口拖入** `LeaderboardPanel.prefab` 到 Hierarchy
3. **确保它是 Canvas 的子对象**

### 2. 运行游戏

1. 点击 Unity 顶部的 `Play` 按钮
2. 触发显示排行榜的代码（如点击排行榜按钮）
3. **观察 Console 日志**：
   ```
   [LeaderboardUI] 正在加载排行榜数据...
   [LeaderboardManager] 获取排行榜数据...
   [LeaderboardUI] 已加载 XX 条排行榜数据
   ```

### 3. 检查显示效果

- [ ] 排行榜界面正确显示
- [ ] 关闭按钮可以点击
- [ ] 显示模拟数据（前 50 名）
- [ ] 前三名有金/银/铜色标识
- [ ] 当前玩家条目有高亮背景（浅绿色）

---

## 🔧 常见问题排查

### Q1: 找不到 LeaderboardUI 脚本

**原因**：脚本不存在或编译错误

**解决方法**：
1. 检查 `Assets/Scripts/LeaderboardUI.cs` 是否存在
2. 查看 Console 是否有编译错误
3. 如果有错误，先修复错误

### Q2: 拖拽后字段显示 "None (GameObject)"

**原因**：引用未正确赋值

**解决方法**：
1. 确保从 Hierarchy 或 Project 窗口正确拖拽
2. 检查拖拽的对象类型是否正确
3. 重新拖拽一次

### Q3: 运行时提示 "panelRoot 未赋值"

**原因**：Inspector 中的引用丢失

**解决方法**：
1. 停止游戏运行
2. 重新在 Inspector 中赋值所有字段
3. 再次运行测试

### Q4: 预制件图标显示为问号

**原因**：预制件关联丢失

**解决方法**：
1. 右键预制件 → `Reveal in Explorer`
2. 检查 `.prefab` 文件是否存在
3. 如果文件损坏，重新保存预制件

---

## 📁 相关文件位置

### 脚本文件
- [`LeaderboardManager.cs`](file://g:\DYGame\Games\NotColorBlind\Assets\Scripts\LeaderboardManager.cs)
- [`LeaderboardUI.cs`](file://g:\DYGame\Games\NotColorBlind\Assets\Scripts\LeaderboardUI.cs)
- [`LeaderboardRankItem.cs`](file://g:\DYGame\Games\NotColorBlind\Assets\Scripts\LeaderboardRankItem.cs)

### 预制件文件（需要手动创建）
- `Assets/Prefabs/LeaderboardPanel.prefab`
- `Assets/Prefabs/RankItemPrefab.prefab`

### Python 脚本（已失效）
- ~~[`create_leaderboard_prefabs.py`](file://g:\DYGame\Games\NotColorBlind\create_leaderboard_prefabs.py)~~ - 创建了 Hierarchy 中的 GameObject
- ~~[`save_leaderboard_prefabs.py`](file://g:\DYGame\Games\NotColorBlind\save_leaderboard_prefabs.py)~~ - 尝试保存预制件但失败

### 文档
- [`LEADERBOARD_PREFABS_CREATED.md`](file://g:\DYGame\Games\NotColorBlind\LEADERBOARD_PREFABS_CREATED.md) - MCP 创建报告
- [`MANUAL_PREFAB_CREATION_GUIDE.md`](file://g:\DYGame\Games\NotColorBlind\MANUAL_PREFAB_CREATION_GUIDE.md) - 本文档

---

## 💡 总结

**MCP Unity 工具的局限性**：
- ✅ 可以创建 Hierarchy 中的 GameObject
- ✅ 可以添加组件
- ❌ 无法直接保存为 `.prefab` 文件到磁盘

**推荐工作流程**：
1. 使用 MCP 快速创建 GameObject 和组件（节省时间）
2. 在 Unity 编辑器中手动保存为预制件（必须步骤）
3. 在 Inspector 中配置所有引用（可视化操作）
4. 测试运行并调整

虽然多了一步手动操作，但这比完全手动创建还是要快很多！🚀
