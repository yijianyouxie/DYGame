# 排行榜预设属性配置详解

## 📋 目录
- [LeaderboardUI 脚本属性](#leaderboardui-脚本属性)
- [LeaderboardRankItem 脚本属性](#leaderboardrankitem-脚本属性)
- [已完成的自动配置](#已完成的自动配置)
- [需要手动配置的字段](#需要手动配置的字段)
- [字体设置说明](#字体设置说明)

---

## LeaderboardUI 脚本属性

### UI 组件引用

| 属性名 | 类型 | 作用 | 是否必须 | 当前状态 |
|-------|------|------|---------|---------|
| **panelRoot** | RectTransform | 排行榜面板根节点，控制整体显示/隐藏 | ✅ 必须 | ⚠️ 待配置 |
| **closeButton** | Button | 关闭按钮，绑定点击事件 | ✅ 必须 | ⚠️ 待配置 |
| **contentParent** | Transform | 内容容器，放置所有排名项的父对象 | ✅ 必须 | ⚠️ 待配置 |
| **rankItemPrefab** | GameObject | 排名项预制件，用于实例化排名条目 | ✅ 必须 | ⚠️ 待配置 |

### 前三名特殊标识

| 属性名 | 类型 | 作用 | 是否必须 | 当前状态 |
|-------|------|------|---------|---------|
| **crownImage** | Image | 皇冠图标，显示在第一名上方 | ❌ 可选 | 留空 |

### 颜色配置

| 属性名 | 类型 | 默认值 | 作用 | 当前状态 |
|-------|------|--------|------|---------|
| **goldColor** | Color | RGBA(1, 0.843, 0, 1) | 第一名的金色 | ✅ 脚本默认值 |
| **silverColor** | Color | RGBA(0.753, 0.753, 0.753, 1) | 第二名的银色 | ✅ 脚本默认值 |
| **bronzeColor** | Color | RGBA(0.804, 0.498, 0.196, 1) | 第三名的铜色 | ✅ 脚本默认值 |
| **normalColor** | Color | RGBA(1, 1, 1, 1) | 普通排名的白色 | ✅ 脚本默认值 |

---

## LeaderboardRankItem 脚本属性

### UI 组件

| 属性名 | 类型 | 作用 | 是否必须 | 当前状态 |
|-------|------|------|---------|---------|
| **rankText** | Text | 显示排名数字（1、2、3...） | ✅ 必须 | ⚠️ 待配置 |
| **nameText** | Text | 显示玩家用户名 | ✅ 必须 | ⚠️ 待配置 |
| **levelText** | Text | 显示玩家通过的关卡数 | ✅ 必须 | ⚠️ 待配置 |
| **avatarImage** | Image | 玩家头像（可选） | ❌ 可选 | 留空 |
| **background** | Image | 排名项背景，当前玩家高亮显示 | ✅ 必须 | ⚠️ 待配置 |

### 前三名标识

| 属性名 | 类型 | 作用 | 是否必须 | 当前状态 |
|-------|------|------|---------|---------|
| **crownPrefab** | GameObject | 皇冠预制件，显示在前三名头顶 | ❌ 可选 | 留空 |

---

## 已完成的自动配置 ✅

### 通过 MCP 脚本设置的属性

#### 1. CloseButton.Text 属性
```csharp
text: "×"           // 关闭按钮的 X 符号
fontSize: 28        // 字体大小 28
alignment: MiddleCenter  // 居中对齐
font: FZLTH-GBK     // 方正兰亭黑简体
```

#### 2. RankText 属性
```csharp
fontSize: 24        // 排名文本字体大小 24
alignment: MiddleCenter  // 居中对齐
font: FZLTH-GBK     // 方正兰亭黑简体
```

#### 3. NameText 属性
```csharp
fontSize: 20        // 用户名文本字体大小 20
alignment: MiddleLeft  // 左对齐
font: FZLTH-GBK     // 方正兰亭黑简体
```

#### 4. LevelText 属性
```csharp
fontSize: 18        // 关卡数文本字体大小 18
alignment: MiddleRight  // 右对齐
font: FZLTH-GBK     // 方正兰亭黑简体
```

#### 5. 组件完整性检查
- ✅ LeaderboardPanel: RectTransform, CanvasRenderer, Image, LeaderboardUI 脚本
- ✅ CloseButton: RectTransform, Button, Text
- ✅ ScrollContainer: RectTransform
- ✅ RankItemPrefab: RectTransform, CanvasRenderer, Image, LeaderboardRankItem 脚本
- ✅ Background: RectTransform, Image
- ✅ RankText: RectTransform, Text
- ✅ NameText: RectTransform, Text
- ✅ LevelText: RectTransform, Text

---

## 需要手动配置的字段 ⚠️

### 在 Unity Inspector中配置 LeaderboardPanel

#### 步骤 1：选中 LeaderboardPanel
在 Hierarchy 或 Project 窗口中选中 `LeaderboardPanel` 预制件

#### 步骤 2：配置 LeaderboardUI 组件

在 Inspector 中找到 `LeaderboardUI (Script)` 组件，依次拖拽赋值：

```
┌─ UI 组件引用 ────────────────┐
│ panelRoot:    LeaderboardPanel │ ← 拖入自身（从 Hierarchy 或 Project）
│ closeButton:  CloseButton      │ ← 拖入 CloseButton 子对象
│ contentParent: ScrollContainer │ ← 拖入 ScrollContainer 子对象
│ rankItemPrefab: [RankItemPrefab] │ ← 从 Assets/Prefabs/拖入预制件
└───────────────────────────────┘
┌─ 前三名特殊标识 ─────────────┐
│ crownImage: [None] (可选)     │ ← 可留空
└───────────────────────────────┘
┌─ 颜色配置 ───────────────────┐
│ goldColor:    RGBA(1, 0.84, 0, 1)   ✓
│ silverColor:  RGBA(0.75, 0.75, 0.75, 1) ✓
│ bronzeColor:  RGBA(0.80, 0.50, 0.20, 1) ✓
│ normalColor:  RGBA(1, 1, 1, 1)       ✓
└───────────────────────────────┘
```

**详细操作步骤**：

1. **panelRoot 字段**:
   - 方法 A: 从 Hierarchy 中选中 `LeaderboardPanel`，拖到字段上
   - 方法 B: 从 Project 窗口选中 `LeaderboardPanel.prefab`，拖到字段上

2. **closeButton 字段**:
   - 在 Hierarchy 中展开 `LeaderboardPanel` → 找到 `CloseButton`
   - 拖拽 `CloseButton` 到字段上

3. **contentParent 字段**:
   - 在 Hierarchy 中找到 `ScrollContainer` 子对象
   - 拖拽到字段上

4. **rankItemPrefab 字段**:
   - 打开 Project 窗口 → 展开 `Assets/Prefabs/`
   - 找到 `RankItemPrefab.prefab`
   - 拖拽到字段上

### 在 Unity Inspector中配置 RankItemPrefab

#### 步骤 1：选中 RankItemPrefab
在 Project 窗口中选中 `Assets/Prefabs/RankItemPrefab.prefab`

#### 步骤 2：配置 LeaderboardRankItem 组件

在 Inspector 中找到 `LeaderboardRankItem (Script)` 组件，依次拖拽赋值：

```
┌─ UI 组件 ────────────────────┐
│ rankText:    RankText         │ ← 拖入 RankText 子对象
│ nameText:    NameText         │ ← 拖入 NameText 子对象
│ levelText:   LevelText        │ ← 拖入 LevelText 子对象
│ avatarImage: [None] (可选)    │ ← 可留空
│ background:  Background       │ ← 拖入 Background 子对象
└───────────────────────────────┘
┌─ 前三名标识 ─────────────────┐
│ crownPrefab: [None] (可选)   │ ← 可留空
└───────────────────────────────┘
```

**详细操作步骤**：

1. **rankText 字段**:
   - 在 Hierarchy 或 Prefab 编辑模式中展开 `RankItemPrefab` → 找到 `RankText`
   - 拖拽 `RankText` 到字段上

2. **nameText 字段**:
   - 找到 `NameText` 子对象
   - 拖拽到字段上

3. **levelText 字段**:
   - 找到 `LevelText` 子对象
   - 拖拽到字段上

4. **background 字段**:
   - 找到 `Background` 子对象
   - 拖拽到字段上

---

## 字体设置说明 📝

### 使用的字体
**Font/FZLTH-GBK** - 方正兰亭黑简体

### 字体路径
```
Assets/Resources/Fonts/FZLTH-GBK.ttf
```

### 各 Text 组件的字体配置

| 组件 | 字体大小 | 对齐方式 | 用途 |
|-----|---------|---------|------|
| **CloseButton.Text** | 28 | MiddleCenter | 关闭按钮的"×"符号 |
| **RankText** | 24 | MiddleCenter | 排名数字（1、2、3...） |
| **NameText** | 20 | MiddleLeft | 玩家用户名（左对齐） |
| **LevelText** | 18 | MiddleRight | 关卡数（右对齐） |

### 如果 MCP 设置的字体未生效

MCP 可能无法直接设置 Unity 的 Font 引用，需要在 Inspector 中手动指定：

#### 手动设置字体的步骤

1. **在 Hierarchy 中选中** 包含 Text 的对象（如 `CloseButton`）
2. **在 Inspector 中找到** Text 组件
3. **点击 Font 字段旁边的圆圈** 🔍
4. **在弹出的选择窗口中**:
   - 搜索框输入：`FZLTH`
   - 找到 `FZLTH-GBK` 字体
   - 点击选择

5. **重复上述步骤**为以下对象设置字体：
   - CloseButton → Text
   - RankText → Text
   - NameText → Text
   - LevelText → Text

或者直接在每个 Text 组件的 Font 字段拖入：
```
Assets/Resources/Fonts/FZLTH-GBK.ttf
```

---

## 验证配置是否正确

### 检查清单

完成上述配置后，请确认：

- [ ] LeaderboardPanel 的 `panelRoot` 字段已赋值（拖入自身）
- [ ] LeaderboardPanel 的 `closeButton` 字段已赋值（拖入 CloseButton）
- [ ] LeaderboardPanel 的 `contentParent` 字段已赋值（拖入 ScrollContainer）
- [ ] LeaderboardPanel 的 `rankItemPrefab` 字段已赋值（拖入 RankItemPrefab.prefab）
- [ ] RankItemPrefab 的 `rankText` 字段已赋值（拖入 RankText）
- [ ] RankItemPrefab 的 `nameText` 字段已赋值（拖入 NameText）
- [ ] RankItemPrefab 的 `levelText` 字段已赋值（拖入 LevelText）
- [ ] RankItemPrefab 的 `background` 字段已赋值（拖入 Background）
- [ ] 所有 Text 组件都使用了 FZLTH-GBK 字体
- [ ] 保存了预制件更新（拖拽到 Assets/Prefabs/并替换）

### 测试运行

1. **点击 Unity 顶部的 Play 按钮**
2. **触发排行榜显示**（例如点击排行榜按钮）
3. **观察 Console 日志**:
   ```
   [LeaderboardUI] 正在加载排行榜数据...
   [LeaderboardManager] 获取排行榜数据...
   [LeaderboardUI] 已加载 XX 条排行榜数据
   ```
4. **检查显示效果**:
   - 排行榜界面正确显示
   - 关闭按钮可以点击
   - 显示排名数据
   - 字体正确（方正兰亭黑）
   - 前三名有特殊颜色（金、银、铜）
   - 当前玩家的条目有浅绿色背景

---

## 保存预制件更新 ⚠️

配置完成后，**必须保存预制件**，否则配置会丢失：

### 方法一：拖拽保存（推荐）
1. 在 Hierarchy 中选中配置好的 GameObject
2. 拖拽到 Project 窗口的对应 `.prefab` 文件上
3. 点击弹出的 `Replace` 按钮

### 方法二：Apply 保存
1. 在 Hierarchy 中选中 GameObject
2. 在 Inspector 顶部的 Prefab 工具栏点击 `Apply All`
3. 确认应用到预制件文件

---

## 📁 相关文件

### 脚本文件
- [`LeaderboardUI.cs`](file://g:\DYGame\Games\NotColorBlind\Assets\Scripts\LeaderboardUI.cs) - 排行榜 UI 控制器
- [`LeaderboardRankItem.cs`](file://g:\DYGame\Games\NotColorBlind\Assets\Scripts\LeaderboardRankItem.cs) - 排名项组件
- [`LeaderboardManager.cs`](file://g:\DYGame\Games\NotColorBlind\Assets\Scripts\LeaderboardManager.cs) - 排行榜数据管理器

### 预制件文件
- `Assets/Prefabs/LeaderboardPanel.prefab` - 主面板预制件
- `Assets/Prefabs/RankItemPrefab.prefab` - 排名项预制件

### 字体文件
- `Assets/Resources/Fonts/FZLTH-GBK.ttf` - 方正兰亭黑简体

### Python 脚本（已执行）
- [`setup_leaderboard_properties.py`](file://g:\DYGame\Games\NotColorBlind\setup_leaderboard_properties.py) - 配置属性的脚本
- [`recreate_leaderboard_panel.py`](file://g:\DYGame\Games\NotColorBlind\recreate_leaderboard_panel.py) - 重新创建带 RectTransform 的面板

### 文档
- [`LEADERBOARD_SYSTEM_DOCUMENTATION.md`](file://g:\DYGame\Games\NotColorBlind\LEADERBOARD_SYSTEM_DOCUMENTATION.md) - 完整系统文档
- [`PREFAB_PROPERTIES_GUIDE.md`](file://g:\DYGame\Games\NotColorBlind\PREFAB_PROPERTIES_GUIDE.md) - 本文档

---

*最后更新：2026-03-16*
