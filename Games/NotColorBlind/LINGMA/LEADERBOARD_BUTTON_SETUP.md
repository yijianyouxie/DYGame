# 排行榜按钮配置指南

## ✅ 已完成的工作

### MCP 自动创建的部分 ✅

1. **GameObject 创建** ✅
   - 名称：`LeaderboardButton`
   - 父对象：`Canvas`
   - 路径：`Canvas/LeaderboardButton`

2. **Button 组件** ✅
   - 已添加到 `LeaderboardButton`

---

## ⚠️ 需要手动完成的配置

### 步骤 1：添加 Text 子对象

1. **在 Hierarchy 中**:
   - 展开 `Canvas`
   - 找到 `LeaderboardButton`

2. **右键 LeaderboardButton** → `UI` → `Text - Legacy` → `Text`

3. **重命名**生成的 Text 对象为 `Text`（如果名称不是这个）

---

### 步骤 2：设置按钮的 RectTransform

**选中 LeaderboardButton**，在 Inspector 中设置：

#### RectTransform 属性
```
Anchor Preset: Top Right  ↗️
├─ Anchor Min: (1, 1)
├─ Anchor Max: (1, 1)
├─ Pivot: (0.5, 0.5)

Pos X: -50
Pos Y: -30
Pos Z: 0

Width: 80   ← 普通按钮（160）的一半
Height: 40  ← 普通按钮（80）的一半

Rotation: X:0, Y:0, Z:0
Scale: X:1, Y:1, Z:1
```

**设置方法**：
1. 点击 Anchor Preset 图标，选择右上角的锚点
2. 手动输入 Pos X、Pos Y、Width、Height

---

### 步骤 3：设置 Text 组件

**选中 Text 子对象**，在 Inspector 中设置：

#### Text 属性
```
Text: 排行榜
Font Size: 18
Font: FZLTH-GBK (Assets/Font/FZLTH-GBK.TTF)
Alignment: Center (图标选择中间)
```

**设置字体的方法**：
1. 在 Project 窗口中展开 `Assets/Font/`
2. 找到 `FZLTH-GBK.TTF`
3. 拖拽到 Text 组件的 **Font** 字段上

或者：
1. 点击 Font 字段旁边的圆圈 🔍
2. 搜索 `FZLTH`
3. 选择 `FZLTH-GBK`

#### Text 的 RectTransform
```
Anchor Preset: Stretch ↔️
├─ Anchor Min: (0, 0)
├─ Anchor Max: (1, 1)
├─ Pivot: (0.5, 0.5)

Pos X: 0
Pos Y: 0
Width: 0
Height: 0
```

---

### 步骤 4：在 MainMenuController 中绑定按钮

1. **在 Hierarchy 中选中 Canvas**（挂载 MainMenuController 的对象）

2. **在 Inspector 中找到** `MainMenuController (Script)` 组件

3. **展开 Leaderboard 部分**：
   ```
   Leaderboard
   ├─ Leaderboard Button: [拖入 LeaderboardButton]
   └─ Leaderboard UI: [已有或留空]
   ```

4. **拖拽操作**：
   - 从 Hierarchy 中拖入 `Canvas/LeaderboardButton` 到 `Leaderboard Button` 字段

---

## 🎯 验证配置

### 检查清单

- [ ] `LeaderboardButton` 是 `Canvas` 的子对象
- [ ] `LeaderboardButton` 有 Button 组件
- [ ] `LeaderboardButton` 有 Text 子对象
- [ ] RectTransform 锚点在右上角
- [ ] 按钮大小是 80x40
- [ ] Text 显示"排行榜"
- [ ] Text 字体是 FZLTH-GBK
- [ ] Text 字号是 18
- [ ] MainMenuController 的 leaderboardButton 字段已赋值

---

## 🧪 测试运行

### 步骤 1：运行游戏

点击 Unity 顶部的 `Play` 按钮

### 步骤 2：检查主菜单

- [ ] 能看到"排行榜"按钮
- [ ] 按钮位于 Canvas 右上角
- [ ] 按钮大小适中
- [ ] 按钮文字清晰

### 步骤 3：点击排行榜按钮

- [ ] 排行榜界面弹出
- [ ] 能看到排名数据
- [ ] 有"×"关闭按钮

### 步骤 4：点击关闭按钮

- [ ] 排行榜界面消失

---

##  按钮规格对比

| 属性 | 普通按钮 | 排行榜按钮 | 说明 |
|------|---------|-----------|------|
| **Width** | 160 | 80 | 一半大小 ✓ |
| **Height** | 80 | 40 | 一半大小 ✓ |
| **Text** | 按钮文字 | 排行榜 | ✓ |
| **Font** | FZLTH-GBK | FZLTH-GBK | 统一字体 ✓ |
| **Font Size** | 20-24 | 18 | 适配小按钮 |
| **Anchor** | Center | Top Right | 右上角定位 ✓ |

---

## 🔧 故障排查

### 问题 1：按钮不在右上角

**原因**：锚点设置错误

**解决方法**：
1. 选中 `LeaderboardButton`
2. 在 Inspector 的 RectTransform 中
3. 点击 Anchor Preset
4. 选择右上角的锚点图标

---

### 问题 2：按钮文字显示为方框

**原因**：字体未正确设置

**解决方法**：
1. 选中 Text 子对象
2. 在 Inspector 的 Text 组件中
3. 重新拖拽 `FZLTH-GBK.TTF` 到 Font 字段
4. 确认字体名称显示为 `FZLTH-GBK`

---

### 问题 3：点击按钮没反应

**原因**：MainMenuController 中未绑定按钮

**解决方法**：
1. 选中 Canvas（挂载 MainMenuController 的对象）
2. 在 Inspector 的 MainMenuController 组件中
3. 将 `LeaderboardButton` 拖入 `leaderboardButton` 字段
4. 确保字段显示为蓝色（已赋值）

---

### 问题 4：按钮太大或太小

**调整方法**：
1. 选中 `LeaderboardButton`
2. 在 RectTransform 中调整 Width 和 Height
3. 建议保持 80x40（普通按钮 160x80 的一半）

---

## 📁 相关文件位置

### 脚本
- [`MainMenuController.cs`](file://g:\DYGame\Games\NotColorBlind\Assets\Scripts\MainMenuController.cs) - 主菜单控制器
- [`LeaderboardUI.cs`](file://g:\DYGame\Games\NotColorBlind\Assets\Scripts\LeaderboardUI.cs) - 排行榜 UI 控制器

### 字体
- [`FZLTH-GBK.TTF`](file://g:\DYGame\Games\NotColorBlind\Assets\Font\FZLTH-GBK.TTF) - 方正兰亭黑简体

### 预制件
- `Assets/Prefabs/LeaderboardPanel.prefab` - 排行榜面板
- `Assets/Prefabs/RankItemPrefab.prefab` - 排名项预制件

---

## 💡 提示

1. **按钮位置微调**：
   - 如果按钮位置不理想，可以调整 Pos X 和 Pos Y
   - 负值会让按钮向左/向下移动

2. **按钮样式**：
   - 可以在 Button 组件的 Colors 中修改正常/按下/悬停的颜色
   - 建议保持与主菜单按钮一致

3. **保存配置**：
   - 完成配置后，如果 Canvas 是预制件实例，记得保存回预制件
   - 或者在场景中直接使用

---

*创建时间：2026-03-16*
*按钮已创建：Canvas/LeaderboardButton*
*下一步：添加 Text 子对象并配置所有属性*
