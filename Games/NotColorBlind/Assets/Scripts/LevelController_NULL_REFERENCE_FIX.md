# NullReferenceException 修复指南

## 🐛 问题描述

运行游戏后，点击特殊色块时出现 `NullReferenceException` 错误：
```
LevelController.BuildGrid() (at Assets/Scripts/LevelController.cs:126)
```

## ✅ 已修复

已在代码中添加 null 检查，防止 [gridParent](file://g:\DYGame\Games\NotColorBlind\Assets\Scripts\LevelController.cs#L13-L13) 为空时崩溃。

## 🔧 Unity Editor 中需要配置的内容

### LevelController 组件配置

1. **在 Hierarchy 中找到 LevelController GameObject**

2. **在 Inspector 中配置以下字段：**

   **UI References 部分：**
   - ✅ **Level Label** - 显示关卡数的 Text 组件
   - ✅ **Countdown Text** - 显示倒计时的 Text 组件
   - ✅ **Sand Clock Icon** - 沙漏图标 Image 组件
   - ✅ **Grid Parent** - 网格容器的 RectTransform（重要！）
   - ✅ **Block Prefab** - 色块预制体（UI Image + Button 组件）
   - ✅ **Busy Coin Button** - 忙币按钮
   - ✅ **Busy Coin Count Text** - 忙币数量显示 Text

   **Effects 部分：**
   - ✅ **Success Effect Prefab** - 烟花特效预设（可选）
   - ✅ **Combo Text** - 连击次数显示 Text
   - ✅ **Effect Duration** - 特效持续时间（默认 1 秒）

   **Board Background 部分：**
   - ✅ **Board Background** - 棋盘背景 Image（可选）
   - ✅ **Board Color** - 背景颜色
   - ✅ **Board Padding** - 背景边距

### 快速配置步骤

#### 步骤 1：创建 UI 结构

在 Hierarchy 中创建以下结构：

```
Canvas
└── LevelScene
    ├── LevelController (挂载 LevelController 脚本)
    ├── GridParent (RectTransform - 空的 UI 容器)
    ├── UI Elements
    │   ├── LevelLabel (Text)
    │   ├── CountdownText (Text)
    │   ├── SandClockIcon (Image)
    │   ├── BusyCoinButton (Button)
    │   │   └── Text (Button 的子 Text)
    │   ├── BusyCoinCountText (Text)
    │   └── ComboText (Text)
    └── BoardBackground (Image - 可选)
```

#### 步骤 2：创建 Block Prefab

1. 在 Hierarchy 中右键 → UI → Image
2. 添加 Button 组件
3. 调整大小为 75x75
4. 拖到 Project 窗口创建 prefab
5. 赋值给 LevelController 的 **Block Prefab** 字段

#### 步骤 3：赋值所有字段

将对应的 UI 元素拖拽到 LevelController 的各个字段中：
- **Grid Parent** → GridParent RectTransform
- **Block Prefab** → 创建的色块 prefab
- 其他 Text 和 Image 组件对应赋值

### 常见遗漏

❌ **忘记赋值 Grid Parent**（最常见）
- 这是导致 NullReferenceException 的主要原因
- 必须创建一个空的 RectTransform 作为网格容器

❌ **Block Prefab 没有 Button 组件**
- 确保 prefab 同时有 Image 和 Button 组件

❌ **Text 组件引用丢失**
- 确保所有 Text 引用都指向正确的 Text 组件

## 🎯 验证配置

配置完成后：
1. 保存场景
2. 运行游戏
3. 点击色块测试
4. 查看控制台是否有错误

## 📋 检查清单

- [ ] Grid Parent 已赋值（必须！）
- [ ] Block Prefab 已创建并赋值
- [ ] 所有 Text 组件已正确引用
- [ ] Busy Coin Button 已赋值
- [ ] 场景中有 Canvas 组件
- [ ] LevelController 挂载在正确的 GameObject 上

## 💡 提示

如果仍然出现错误，请检查控制台日志：
```
[LevelController] gridParent is null! Please assign it in Inspector.
```
这个错误提示意味着你还没有在 Inspector 中赋值 Grid Parent。
