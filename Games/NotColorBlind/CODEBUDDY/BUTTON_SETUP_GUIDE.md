# 按钮设置完成指南

## ✅ 已完成的工作

### 1. LevelScene - 返回按钮
- **按钮名称**: `ReturnButton`
- **位置**: 右上角 (anchoredPosition: -100, -50)
- **大小**: 200x75
- **锚点**: 右上角 (anchorMin: 1,1; anchorMax: 1,1)
- **组件**: RectTransform, Image, Button
- **状态**: ✅ 已创建，RectTransform属性已正确设置

### 2. ResultScene - 排行榜按钮
- **按钮名称**: `ResultLeaderboardButton`
- **位置**: 右上角 (anchoredPosition: -100, -50)
- **大小**: 200x75
- **锚点**: 右上角 (anchorMin: 1,1; anchorMax: 1,1)
- **组件**: RectTransform, Image, Button, Text (子对象)
- **文字**: "排行榜"
- **字体大小**: 32
- **状态**: ✅ 已创建，所有属性已正确设置

### 3. 脚本修改

#### LevelController.cs
- 添加了 `returnButton` 字段
- 添加了 `OnReturnClicked()` 方法，用于返回主菜单并停止倒计时
- 在 Start() 中绑定了返回按钮事件

#### ResultController.cs
- 添加了 `returnButton` 字段
- 添加了 `OnReturnClicked()` 方法，用于返回主菜单
- 排行榜按钮点击事件已存在
- 在 Start() 中绑定了返回按钮和排行榜按钮事件

## ⚠️ 需要手动完成的步骤

由于Unity MCP无法自动设置按钮引用，需要在Unity编辑器中手动完成：

### LevelScene 设置
1. 打开 `LevelScene.unity`
2. 选择包含 `LevelController` 组件的对象
3. 在 Inspector 中找到 `Return Button` 字段
4. 将场景中的 `ReturnButton` 拖动到该字段

### ResultScene 设置
1. 打开 `ResultScene.unity`
2. 选择包含 `ResultController` 组件的对象
3. 在 Inspector 中找到 `Leaderboard Button` 字段
4. 将场景中的 `ResultLeaderboardButton` 拖动到该字段
5. 如果有 `Return Button` 字段，可以暂时留空（Result场景没有返回按钮）

## 功能说明

设置完成后，按钮将实现以下功能：

### LevelScene - 返回按钮
- 点击后停止倒计时
- 返回到主菜单 (Start场景)

### ResultScene - 排行榜按钮
- 点击后弹出排行榜界面
- 使用已有的 `leaderboardUI.ShowLeaderboard()` 方法

## 按钮样式

两个按钮都采用相同的样式：
- 尺寸：200x75（是原Button大小400x150的一半）
- 位置：右上角
- 文字：返回按钮显示"返回"，排行榜按钮显示"排行榜"
- 字体大小：32

## 注意事项

1. **LevelScene的Text子对象**：当前LevelScene中的ReturnButton下有Text子对象，但Text组件可能没有正确添加。如果文字没有显示，需要：
   - 在Unity中选中ReturnButton下的Text
   - 检查是否有UnityEngine.UI.Text组件
   - 如果没有，添加该组件并设置text为"返回"，fontSize为32

2. **ResultScene的Text子对象**：ResultLeaderboardButton下的Text已正确设置，显示"排行榜"。

3. **图片背景**：当前按钮只有默认的Image组件，如果需要自定义背景图片，需要在Unity中设置Image的Source Image。
