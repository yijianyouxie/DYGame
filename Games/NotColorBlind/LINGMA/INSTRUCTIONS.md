# 按钮设置说明

## 当前状态

### LevelScene
- ✅ ReturnButton已创建（只保留了一个）
- ✅ RectTransform属性已正确设置
- ⚠️ Text子对象需要手动处理（添加Text组件并设置文字）

### ResultScene
- ❌ 还没有添加排行榜按钮

## 需要完成的步骤

### 1. 在ResultScene中添加排行榜按钮

**方法A：使用脚本（推荐）**
1. 在Unity编辑器中打开 `ResultScene.unity`
2. 确保MCP服务器正在运行（应该已经在运行）
3. 运行以下命令：
   ```bash
   cd g:/DYGame/Games/NotColorBlind
   python add_result_leaderboard_button_correct.py
   ```
4. 脚本会自动创建ResultLeaderboardButton及其所有组件

**方法B：手动创建**
如果脚本失败，可以手动创建：
1. 在Canvas右键 → UI → Button，命名为"ResultLeaderboardButton"
2. 设置RectTransform属性：
   - Anchor: 右上角 (Anchor Min: 1,1, Anchor Max: 1,1)
   - Position: (-100, -50)
   - Size: (200, 75)
3. 修改Button下的Text子对象：
   - Text内容改为"排行榜"
   - Font Size改为32

### 2. 设置脚本中的按钮引用

在Unity编辑器中：

#### LevelScene
1. 打开 `LevelScene.unity`
2. 找到包含 `LevelController` 组件的对象
3. 在Inspector中找到 `Return Button` 字段
4. 将场景中的 `ReturnButton` 拖到该字段

#### ResultScene
1. 打开 `ResultScene.unity`
2. 找到包含 `ResultController` 组件的对象
3. 在Inspector中找到 `Leaderboard Button` 字段
4. 将场景中的 `ResultLeaderboardButton` 拖到该字段

### 3. 修复LevelScene的ReturnButton文字（如果需要）

如果LevelScene的ReturnButton没有显示"返回"文字：
1. 选中 `ReturnButton`
2. 展开它找到 `Text` 子对象
3. 检查是否有 `UnityEngine.UI.Text` 组件
4. 如果没有：
   - Add Component → 搜索 "Text" → 添加 Text 组件
5. 设置Text属性：
   - Text: "返回"
   - Font Size: 32

## 验证功能

完成后测试以下功能：

### LevelScene
- [ ] ReturnButton显示在右上角
- [ ] 文字显示"返回"
- [ ] 点击后返回主菜单并停止倒计时

### ResultScene
- [ ] ResultLeaderboardButton显示在右上角
- [ ] 文字显示"排行榜"
- [ ] 点击后弹出排行榜界面

## 按钮规格

两个按钮应该有相同的样式：
- **大小**: 200x75（原Button大小的一半）
- **位置**: 右上角 (anchoredPosition: -100, -50)
- **锚点**: 右上角 (anchorMin: 1,1; anchorMax: 1,1)
- **字体大小**: 32
- **文字**: 返回按钮显示"返回"，排行榜按钮显示"排行榜"
