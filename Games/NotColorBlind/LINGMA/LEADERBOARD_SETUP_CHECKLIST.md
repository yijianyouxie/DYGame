# 排行榜系统完整配置清单

## ✅ 代码逻辑状态

### 已实现的脚本逻辑 ✅

1. **MainMenuController.cs** ✅
   - ✅ 排行榜按钮点击事件绑定
   - ✅ 调用 `leaderboardUI.ShowLeaderboard()`
   - ✅ 空安全检查

2. **LeaderboardUI.cs** ✅
   - ✅ 显示/隐藏排行榜面板
   - ✅ 加载排行榜数据
   - ✅ 填充排名项
   - ✅ 前三名特殊样式
   - ✅ 关闭按钮事件

3. **LeaderboardRankItem.cs** ✅
   - ✅ 设置排名数据
   - ✅ 前三名颜色区分
   - ✅ 当前玩家高亮

---

## ⚠️ 需要在 Inspector 中完成的配置

### 配置 1: LeaderboardPanel 预制件

#### 步骤 1：确保已保存为预制件
- [ ] `Assets/Prefabs/LeaderboardPanel.prefab` 存在
- [ ] `Assets/Prefabs/RankItemPrefab.prefab` 存在

#### 步骤 2：配置 LeaderboardUI 组件

**在 Unity 中操作**：

1. **选中 LeaderboardPanel**（Hierarchy 或 Project 中）

2. **在 Inspector 中找到** `LeaderboardUI (Script)` 组件

3. **依次拖拽赋值**：

```
┌─ UI 组件引用 ────────────────────────┐
│ panelRoot:    [LeaderboardPanel]     │ ← 拖入自身
│ closeButton:  [CloseButton]          │ ← 拖入 CloseButton 子对象
│ contentParent: [ScrollContainer]     │ ← 拖入 ScrollContainer 子对象
│ rankItemPrefab: [RankItemPrefab]     │ ← 从 Prefabs 文件夹拖入
└──────────────────────────────────────┘

┌─ 前三名特殊标识 ─────────────────────┐
│ crownImage:   [None] (可选，可留空)   │
└──────────────────────────────────────┘

┌─ 颜色配置 ───────────────────────────┐
│ goldColor:    RGBA(255, 215, 0, 255) │ ← 金色
│ silverColor:  RGBA(192, 192, 192, 255)│ ← 银色
│ bronzeColor:  RGBA(205, 127, 50, 255)│ ← 铜色
│ normalColor:  RGBA(255, 255, 255, 255)│ ← 白色
└──────────────────────────────────────┘
```

**验证**：
- [ ] 所有字段都已赋值（除了 crownImage 可选）
- [ ] 颜色值正确

---

### 配置 2: RankItemPrefab 预制件

#### 步骤 1：选中 RankItemPrefab

**在 Project 窗口中**选中 `Assets/Prefabs/RankItemPrefab.prefab`

#### 步骤 2：配置 LeaderboardRankItem 组件

**在 Inspector 中找到** `LeaderboardRankItem (Script)` 组件

**依次拖拽赋值**：

```
┌─ UI 组件 ────────────────────────────┐
│ rankText:    [RankText]              │ ← 拖入 RankText 子对象
│ nameText:    [NameText]              │ ← 拖入 NameText 子对象
│ levelText:   [LevelText]             │ ← 拖入 LevelText 子对象
│ avatarImage: [None] (可选，可留空)   │
│ background:  [Background]            │ ← 拖入 Background 子对象
└──────────────────────────────────────┘

┌─ 前三名标识 ─────────────────────────┐
│ crownPrefab: [None] (可选，可留空)   │
└──────────────────────────────────────┘
```

**验证**：
- [ ] 所有必填字段都已赋值
- [ ] RankText、NameText、LevelText 的字体正确（FZLTH-GBK）

---

### 配置 3: MainMenuController

#### 步骤 1：找到 MainMenuController

**在 Hierarchy 中**找到挂载 `MainMenuController` 脚本的对象
（通常在 Main Menu Canvas 或某个 Controller 对象上）

#### 步骤 2：配置排行榜引用

**在 Inspector 中找到** `MainMenuController (Script)` 组件

**配置 Leaderboard 部分**：

```
MainMenuController (Script)
├─ UI References
│  ├─ Player Name Text: [已有]
│  ├─ Progress Text: [已有]
│  └─ Start Button: [已有]
└─ Leaderboard
   ├─ Leaderboard Button: [排行榜按钮]  ← 拖入主菜单的排行榜按钮
   └─ Leaderboard UI: [LeaderboardPanel] ← 拖入 LeaderboardPanel 预制件
```

**验证**：
- [ ] leaderboardButton 已赋值
- [ ] leaderboardUI 已赋值

---

## 🎯 完整验证流程

### 验证 1：检查预制件结构

#### LeaderboardPanel 预制件
```
LeaderboardPanel.prefab
├─ RectTransform ✓
├─ CanvasRenderer ✓
├─ Image ✓
├─ LeaderboardUI (脚本) ✓
│  └─ Inspector 中已配置所有字段 ✓
├─ CloseButton ✓
│  ├─ RectTransform ✓
│  ├─ Button ✓
│  └─ Text ✓ (×, 28 号字体，FZLTH-GBK)
└─ ScrollContainer ✓
   └─ RectTransform ✓
      └─ Vertical Layout Group ✓
```

#### RankItemPrefab 预制件
```
RankItemPrefab.prefab
├─ RectTransform ✓
├─ CanvasRenderer ✓
├─ Image ✓
├─ LeaderboardRankItem (脚本) ✓
│  └─ Inspector 中已配置所有字段 ✓
├─ Background ✓
│  ├─ RectTransform ✓
│  └─ Image ✓
├─ RankText ✓
│  ├─ RectTransform ✓
│  └─ Text ✓ (24 号字体，FZLTH-GBK, MiddleCenter)
├─ NameText ✓
│  ├─ RectTransform ✓
│  └─ Text ✓ (20 号字体，FZLTH-GBK, MiddleLeft)
└─ LevelText ✓
   ├─ RectTransform ✓
   └─ Text ✓ (18 号字体，FZLTH-GBK, MiddleRight)
```

---

### 验证 2：场景配置

#### Start 场景
- [ ] LeaderboardPanel 已添加到场景中（作为 Canvas 的子对象）
- [ ] MainMenuController 存在且配置正确
- [ ] 主菜单有排行榜按钮

---

## 🧪 测试步骤

### 步骤 1：运行游戏

1. **点击 Unity 的 Play 按钮**
2. **进入主菜单场景**

### 步骤 2：检查主菜单

- [ ] 能看到排行榜按钮
- [ ] 按钮上有文字"排行榜"

### 步骤 3：点击排行榜按钮

- [ ] 排行榜界面弹出
- [ ] 能看到排名列表
- [ ] 前三名有特殊颜色（金/银/铜）
- [ ] 有"×"关闭按钮

### 步骤 4：点击关闭按钮

- [ ] 排行榜界面消失

### 步骤 5：查看 Console

**应该看到的日志**：
```
[LeaderboardUI] 正在加载排行榜数据...
[LeaderboardManager] 获取排行榜数据...
[LeaderboardUI] 已加载 X 条排行榜数据
```

**不应该看到的错误**：
```
❌ [LeaderboardUI] panelRoot 未赋值！
❌ [MainMenuController] leaderboardUI 未赋值！
❌ MissingReferenceException
```

---

## 🔧 故障排查

### 问题 1：点击排行榜按钮没反应

**可能原因**：
1. MainMenuController 中的 leaderboardButton 未赋值
2. MainMenuController 中的 leaderboardUI 未赋值
3. LeaderboardPanel 未添加到场景中

**解决方法**：
1. 选中 MainMenuController 所在对象
2. 在 Inspector 中检查 Leaderboard 部分
3. 重新拖拽赋值 leaderboardButton 和 leaderboardUI

---

### 问题 2：提示"panelRoot 未赋值"

**可能原因**：
LeaderboardUI 组件的 panelRoot 字段为空

**解决方法**：
1. 选中 LeaderboardPanel
2. 在 Inspector 中找到 LeaderboardUI 组件
3. 将 LeaderboardPanel 自身拖到 panelRoot 字段

---

### 问题 3：排行榜显示空白

**可能原因**：
1. rankItemPrefab 未赋值
2. contentParent 未赋值
3. Vertical Layout Group 缺失或配置错误

**解决方法**：
1. 检查 LeaderboardUI 组件的所有字段
2. 确保 ScrollContainer 有 Vertical Layout Group
3. 重新赋值所有引用

---

### 问题 4：Text 字体不对

**可能原因**：
Text 组件的 Font 字段未使用 FZLTH-GBK

**解决方法**：
1. 在 Project 窗口找到 `Assets/Font/FZLTH-GBK.TTF`
2. 依次选中 RankText、NameText、LevelText
3. 在 Inspector 中将字体拖到 Font 字段

---

## 📋 最终检查清单

完成所有配置后，请确认：

- [ ] LeaderboardPanel 已保存为预制件
- [ ] RankItemPrefab 已保存为预制件
- [ ] LeaderboardUI 组件的所有字段已赋值
- [ ] LeaderboardRankItem 组件的所有字段已赋值
- [ ] MainMenuController 的排行榜引用已配置
- [ ] 场景中有 LeaderboardPanel 实例
- [ ] 所有 Text 使用 FZLTH-GBK 字体
- [ ] 运行游戏测试通过

---

## 🎯 下一步

配置完成后，排行榜系统应该可以正常工作：

1. ✅ 在主菜单点击"排行榜"按钮
2. ✅ 显示排行榜界面
3. ✅ 显示抖音云数据库的排行榜数据
4. ✅ 前三名有金/银/铜色标识
5. ✅ 点击"×"关闭排行榜

**恭喜！排行榜系统配置完成！** 🎉

---

*文档创建时间：2026-03-16*
*基于之前的修复工作整合*
