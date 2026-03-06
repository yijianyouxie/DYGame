# 忙币功能实现说明

## 功能概述
在LevelScene场景中添加了忙币系统，包括：
- 忙币按钮：显示在倒计时下方
- 忙币数量显示：显示当前拥有的忙币数量
- 高亮提示功能：点击忙币按钮后高亮显示不同的色块并闪动3次
- 扣费机制：只有在提示后选择正确答案才扣除1个忙币
- 广告奖励：观看广告可以增加忙币数量

## UI设置步骤

### 1. 在LevelScene中添加UI元素

1. 打开 `LevelScene` 场景
2. 在Canvas下创建两个UI元素：
   - **忙币按钮**: 使用 `Assets/Prefabs/BusyCoinButton.prefab` 预制件
   - **忙币数量文本**: 使用 `Assets/Prefabs/BusyCoinCountText.prefab` 预制件

### 2. 调整UI位置

- 忙币按钮：放置在倒计时文本下方，建议位置 Y = -50
- 忙币数量文本：放置在忙币按钮下方，建议位置 Y = -100

### 3. 配置LevelController组件

在LevelController组件中设置以下引用：
- **Busy Coin Button**: 拖拽忙币按钮到此字段
- **Busy Coin Count Text**: 拖拽忙币数量文本到此字段

## 代码说明

### GameData.cs
- 添加了 `BusyCoinCount` 静态属性用于全局管理忙币数量
- 在 `LoadFromServer` 方法中可以从服务器加载忙币数量

### LevelController.cs
- 添加了忙币相关的UI引用和状态变量
- `OnBusyCoinClicked()`: 处理忙币按钮点击事件
- `HighlightOddBlock()`: 高亮显示不同的色块
- `DeductBusyCoin()`: 在选择正确答案后扣除忙币
- `AddBusyCoinFromAd()`: 观看广告后增加忙币（接口预留）

## 使用说明

1. **查看忙币数量**: 游戏开始时会显示当前拥有的忙币数量
2. **使用提示**: 在关卡进行过程中点击忙币按钮，可以高亮提示不同的色块
3. **扣费时机**: 只有使用了提示且选择正确答案后才会扣除1个忙币
4. **获取忙币**: 可以通过观看广告等方式增加忙币数量

## 后续开发

- 接入真实的广告SDK替换 `AddBusyCoinFromAd()` 方法
- 实现服务器通信来同步忙币数量
- 添加忙币购买功能
- 实现忙币数量的本地持久化存储