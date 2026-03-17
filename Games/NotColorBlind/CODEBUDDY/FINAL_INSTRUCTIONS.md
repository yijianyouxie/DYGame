# 按钮设置最终说明

## ✅ 已完成的工作

### 1. LevelScene - 返回按钮
- **按钮名称**: `ReturnButton`
- **位置**: 右上角 (anchoredPosition: -100, -50)
- **大小**: 200x75
- **锚点**: 右上角 (anchorMin: 1,1; anchorMax: 1,1)
- **组件**: RectTransform, Image, Button
- **Text子对象**: ✅ 已创建，文字="返回"，fontSize=32
- **状态**: ✅ 已创建并保存

### 2. ResultScene - 排行榜按钮
- **按钮名称**: `ResultLeaderboardButton`
- **位置**: 右上角 (anchoredPosition: -100, -50)
- **大小**: 200x75
- **锚点**: 右上角 (anchorMin: 1,1; anchorMax: 1,1)
- **组件**: RectTransform, Image, Button
- **Text子对象**: ✅ 已创建，文字="排行榜"，fontSize=32
- **状态**: ✅ 已创建并保存

### 3. 脚本修改
- **LevelController.cs**: ✅ 已添加returnButton字段和OnReturnClicked()方法
- **ResultController.cs**: ✅ 已添加returnButton字段和OnReturnClicked()方法

## ⚠️ 需要手动完成的步骤

### 步骤1: 设置按钮的Image sprite

由于无法通过MCP获取Start场景中的LeaderboardButton样式，需要手动设置：

#### LevelScene - ReturnButton
1. 打开 `Assets/Scenes/LevelScene.unity`
2. 选中 `ReturnButton`
3. 在Inspector中找到 Image 组件
4. 查看 Start 场景中的 Button 的 Image 使用的 sprite（如果有的话）
5. 将相同的sprite应用到 ReturnButton 的 Image 组件上
   - 如果Start场景的Button没有特殊sprite，保持默认即可

#### ResultScene - ResultLeaderboardButton
1. 打开 `Assets/Scenes/ResultScene.unity`
2. 选中 `ResultLeaderboardButton`
3. 在Inspector中找到 Image 组件
4. 将与Start场景LeaderboardButton相同的sprite应用到该按钮

### 步骤2: 设置脚本中的按钮引用

#### LevelScene
1. 打开 `Assets/Scenes/LevelScene.unity`
2. 找到包含 `LevelController` 组件的对象（通常是Canvas或某个Panel）
3. 在 Inspector 中找到 `Return Button` 字段
4. 将场景中的 `ReturnButton` 对象拖到该字段

#### ResultScene
1. 打开 `Assets/Scenes/ResultScene.unity`
2. 找到包含 `ResultController` 组件的对象
3. 在 Inspector 中找到 `Leaderboard Button` 字段
4. 将场景中的 `ResultLeaderboardButton` 对象拖到该字段

## 功能验证

完成后测试以下功能：

### LevelScene
- [ ] ReturnButton显示在右上角
- [ ] 文字显示"返回"，字体大小为32
- [ ] 点击后返回主菜单并停止倒计时

### ResultScene
- [ ] ResultLeaderboardButton显示在右上角
- [ ] 文字显示"排行榜"，字体大小为32
- [ ] 点击后弹出排行榜界面

## 按钮规格

两个按钮应该有相同的样式：
- **大小**: 200x75（是原Button大小400x150的一半）
- **位置**: 右上角 (anchoredPosition: -100, -50)
- **锚点**: 右上角 (anchorMin: 1,1; anchorMax: 1,1)
- **字体大小**: 32
- **文字**: 返回按钮显示"返回"，排行榜按钮显示"排行榜"
- **Image sprite**: 与Start场景中的LeaderboardButton相同（如果有特殊设置）

## 注意事项

1. **Start场景中没有LeaderboardButton**: 目前Start场景中没有找到名为"LeaderboardButton"的对象。如果需要参考样式，请查看Start场景中的其他Button对象的Image设置。

2. **Image sprite**: 如果Start场景中的按钮使用的是默认的Unity按钮样式，那么新创建的按钮已经使用了相同的默认样式，不需要额外设置。

3. **脚本引用**: 设置完按钮引用后，确保Unity没有报错。如果有报错，检查：
   - 按钮名称是否正确
   - 脚本字段名称是否匹配
   - 场景中是否保存了修改

## 快速操作清单

- [ ] 打开LevelScene，设置ReturnButton的Image sprite（如需要）
- [ ] 打开LevelScene，将ReturnButton拖到LevelController的Return Button字段
- [ ] 保存LevelScene
- [ ] 打开ResultScene，设置ResultLeaderboardButton的Image sprite（如需要）
- [ ] 打开ResultScene，将ResultLeaderboardButton拖到ResultController的Leaderboard Button字段
- [ ] 保存ResultScene
- [ ] 测试LevelScene的返回按钮功能
- [ ] 测试ResultScene的排行榜按钮功能

## 故障排除

### 问题1: 按钮点击无反应
- 检查按钮引用是否正确设置
- 检查脚本中是否正确绑定了事件
- 查看Unity Console是否有错误信息

### 问题2: 按钮文字不显示
- 检查Text组件是否正确添加
- 检查Text的text属性是否设置了文字
- 检查Text的fontSize是否设置
- 检查Text的颜色是否与背景色相同

### 问题3: 按钮位置不正确
- 检查RectTransform的anchorMin和anchorMax是否都是(1,1)
- 检查anchoredPosition是否是(-100, -50)
- 检查Canvas的Canvas Scaler设置是否影响布局
