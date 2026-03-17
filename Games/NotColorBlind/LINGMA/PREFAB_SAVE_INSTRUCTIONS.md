# 排行榜预制件手动保存指南

## ⚠️ 问题说明

通过 MCP Unity 工具在 Hierarchy 中添加的组件**不会自动保存到预制件文件中**。这是因为：

1. **MCP 的工作方式**：`manage_gameobject` 和 `manage_components` 工具只修改场景中的 GameObject
2. **Unity 预制件机制**：预制件是独立的资产文件，需要显式保存操作
3. **API 限制**：当前的 MCP API 没有提供"从 Hierarchy 更新预制件"的功能

## ✅ 解决方案：在 Unity 中手动保存

### 方法一：拖拽法（推荐）

#### 步骤 1：打开 Unity 并查看 Hierarchy

在 Unity 编辑器的 Hierarchy 窗口中，你应该能看到以下结构：

```
Hierarchy
├─ LeaderboardPanel
│  ├─ RectTransform ✓
│  ├─ CanvasRenderer ✓
│  ├─ Image ✓
│  ├─ LeaderboardUI (脚本) ✓
│  ├─ CloseButton
│  │  ├─ RectTransform ✓
│  │  ├─ Button ✓
│  │  └─ Text ✓
│  └─ ScrollContainer
│     └─ RectTransform ✓
└─ RankItemPrefab
   ├─ RectTransform ✓
   ├─ CanvasRenderer ✓
   ├─ Image ✓
   ├─ LeaderboardRankItem (脚本) ✓
   ├─ Background
   │  ├─ RectTransform ✓
   │  └─ Image ✓
   ├─ RankText
   │  ├─ RectTransform ✓
   │  └─ Text ✓
   ├─ NameText
   │  ├─ RectTransform ✓
   │  └─ Text ✓
   └─ LevelText
      ├─ RectTransform ✓
      └─ Text ✓
```

#### 步骤 2：保存 LeaderboardPanel.prefab

1. **在 Hierarchy 中选中** `LeaderboardPanel`
2. **按住鼠标左键拖拽**到 Project 窗口
3. **移动到** `Assets/Prefabs/` 文件夹上方
4. **松开鼠标**，Unity 会提示 "Replace Prefab?"
5. **点击** `Replace` 按钮覆盖现有预制件

#### 步骤 3：保存 RankItemPrefab.prefab

重复步骤 2：

1. **在 Hierarchy 中选中** `RankItemPrefab`
2. **拖拽到** `Assets/Prefabs/` 文件夹
3. **点击** `Replace` 覆盖现有预制件

---

### 方法二：右键菜单法

#### 保存 LeaderboardPanel

1. **在 Hierarchy 中右键点击** `LeaderboardPanel`
2. **选择** `Create Prefab...`
3. **在保存对话框中**:
   - 导航到 `Assets/Prefabs/` 目录
   - 文件名输入：`LeaderboardPanel`
   - **重要**: 如果提示是否替换，选择 `Replace`
4. **点击** `Save`

#### 保存 RankItemPrefab

重复上述步骤，使用文件名 `RankItemPrefab`

---

### 方法三：使用 Unity 的 Apply 功能（如果预制件已关联）

如果 Hierarchy 中的 GameObject 已经链接到预制件（显示为蓝色名称）：

1. **在 Hierarchy 中选中** GameObject
2. **在 Inspector 顶部**找到预制件状态栏
3. **点击** `Apply All` 按钮

这会将对 GameObject 的所有修改应用到关联的预制件文件。

---

## 🔍 验证保存结果

### 检查预制件内容

1. **在 Project 窗口中展开** `Assets/Prefabs/`
2. **单击选中** `LeaderboardPanel.prefab`
3. **查看 Inspector 窗口**，应该看到：

```
LeaderboardPanel Prefab
├─ Transform / RectTransform
├─ Canvas Renderer
├─ Image
├─ LeaderboardUI (Script)
├─ CloseButton (子对象)
│  ├─ RectTransform
│  ├─ Button
│  └─ Text
└─ ScrollContainer (子对象)
   └─ RectTransform
```

### 检查 RankItemPrefab

同样选中 `RankItemPrefab.prefab`，应该看到：

```
RankItemPrefab Prefab
├─ Transform / RectTransform
├─ Canvas Renderer
├─ Image
├─ LeaderboardRankItem (Script)
├─ Background
│  ├─ RectTransform
│  └─ Image
├─ RankText
│  ├─ RectTransform
│  └─ Text
├─ NameText
│  ├─ RectTransform
│  └─ Text
└─ LevelText
   ├─ RectTransform
   └─ Text
```

---

## ❌ 常见问题排查

### Q1: 拖拽后创建了新预制件而不是覆盖

**原因**: Unity 没有识别出这是要替换现有预制件

**解决方法**:
1. 删除新创建的预制件（如 `LeaderboardPanel 1.prefab`）
2. 确保拖拽时鼠标悬停在原预制件文件上
3. 或者使用方法二的右键菜单法

### Q2: 预制件中仍然没有组件

**可能原因**:
- Hierarchy 中的 GameObject 本身就没有这些组件
- 保存时选择了错误的 GameObject

**解决方法**:
1. 回到 Hierarchy，选中 `LeaderboardPanel`
2. 在 Inspector 中确认所有组件都存在
3. 如果缺少组件，重新运行 MCP 脚本添加组件
4. 再次尝试保存预制件

### Q3: 提示"无法保存，有未解决的冲突"

**原因**: 预制件可能有实例冲突

**解决方法**:
1. 在 Hierarchy 中选中 GameObject
2. 在 Inspector 顶部的预制件工具栏点击 `Resolve Conflicts`
3. 选择 `Apply All` 应用所有更改
4. 再次尝试保存

---

## 📋 完整工作流程总结

### 已完成的工作（通过 MCP）

✅ 在 Hierarchy 中创建了所有 GameObject  
✅ 添加了所有必要的组件  
✅ 建立了正确的父子层级关系  

### 待完成的工作（必须在 Unity 中手动完成）

⏳ **保存预制件文件**（本指南的核心内容）  
⏳ 配置 LeaderboardUI 组件的引用字段  
⏳ 调整 UI 元素的属性（RectTransform、Text 等）  
⏳ 测试运行游戏  

### 后续配置步骤

保存预制件后，继续以下步骤：

1. **配置 LeaderboardUI 组件**：
   - 选中 `LeaderboardPanel` 预制件
   - 在 Inspector 中找到 `LeaderboardUI (Script)` 组件
   - 拖拽赋值：
     - Panel Root: 拖入自身
     - Close Button: 拖入 CloseButton 子对象
     - Content Parent: 拖入 ScrollContainer 子对象
     - Rank Item Prefab: 从 Assets/Prefabs/拖入 RankItemPrefab.prefab

2. **调整 UI 布局**：
   - 设置各元素的 RectTransform 位置和大小
   - 修改 Text 组件的内容（如 CloseButton 的 Text 改为 "×"）
   - 配置颜色、字体大小等

3. **添加到场景**：
   - 将 `LeaderboardPanel.prefab` 拖入场景中的 Canvas 下
   - 在 MainMenuController 和 ResultController 中绑定排行榜按钮事件

---

## 💡 为什么不能自动化？

### Unity 预制件的工作机制

1. **预制件是独立资产**：`.prefab` 文件是序列化的 Unity 资产，存储在磁盘上
2. **Hierarchy 是运行时实例**：场景中的 GameObject 是预制件的实例或独立对象
3. **需要显式保存操作**：Unity 要求用户明确确认何时将实例更改写回预制件文件

### MCP API 的限制

当前的 MCP Unity API 设计用于：
- ✅ 创建和修改场景中的 GameObject
- ✅ 添加、移除、配置组件
- ❌ **不直接支持**预制件文件的读写操作

这是合理的，因为：
- 预制件管理涉及复杂的版本控制和冲突解决
- Unity 提供了可视化的预制件工作流工具
- 手动保存可以防止意外覆盖重要的预制件数据

---

## 🎯 最佳实践建议

### 1. 使用 MCP 快速搭建原型
- 利用 MCP 快速创建 GameObject 和组件
- 在 Hierarchy 中验证结构和功能

### 2. 在 Unity 中完善配置
- 手动保存预制件以获得更好的可视化控制
- 使用 Unity 的 Prefab Mode 进行深度编辑
- 利用 Unity 的实时预览功能调整 UI 布局

### 3. 建立工作流程
```
MCP 创建 → 手动保存 → Unity 配置 → 测试验证 → 迭代优化
```

### 4. 备份重要预制件
在进行重大修改前：
- 复制预制件文件到备份目录
- 或使用 Unity 的 Prefab Variant 功能创建变体

---

## 📁 相关文件清单

### 预制件文件（需要手动保存）
- `Assets/Prefabs/LeaderboardPanel.prefab`
- `Assets/Prefabs/RankItemPrefab.prefab`

### Python 脚本（已执行）
- [`add_components_to_leaderboard.py`](file://g:\DYGame\Games\NotColorBlind\add_components_to_leaderboard.py) - 添加组件到 Hierarchy 中的 GameObject
- [`update_prefabs_from_hierarchy.py`](file://g:\DYGame\Games\NotColorBlind\update_prefabs_from_hierarchy.py) - 尝试更新预制件（未成功，需手动操作）

### 文档
- [`MANUAL_PREFAB_CREATION_GUIDE.md`](file://g:\DYGame\Games\NotColorBlind\MANUAL_PREFAB_CREATION_GUIDE.md) - 手动创建预制件指南
- [`PREFAB_SAVE_INSTRUCTIONS.md`](file://g:\DYGame\Games\NotColorBlind\PREFAB_SAVE_INSTRUCTIONS.md) - 本文档

---

*最后更新：2026-03-16*
