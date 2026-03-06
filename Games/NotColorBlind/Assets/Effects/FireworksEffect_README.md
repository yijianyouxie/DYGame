# 烟花特效使用说明

## 🎆 FireworksEffect Prefab

这是一个用于庆祝玩家成功完成关卡的烟花粒子特效预设。

### 使用方法

#### 方法一：通过菜单创建（推荐）

1. 打开 Unity Editor
2. 点击菜单栏 `Tools` > `Create Fireworks Effect Prefab`
3. 特效预设将自动创建在 `Assets/Effects/FireworksEffect.prefab`
4. 查看控制台日志确认创建成功

#### 方法二：手动配置

如果自动创建失败，可以手动创建 ParticleSystem：

1. 在 Hierarchy 中右键 > Effects > Particle System
2. 重命名为 "FireworksEffect"
3. 按照以下参数配置各个模块

### 特效特性

- **持续时间**: 1 秒
- **最大粒子数**: 200
- **颜色渐变**: 金黄色 → 橙红色 → 紫红色
- **爆炸效果**: 球形扩散，带二次爆炸子发射器
- **光照效果**: 动态点光源，逐渐变暗
- **物理效果**: 受重力影响，模拟真实烟花

### 在 LevelController 中使用

1. 选择 LevelController GameObject
2. 在 Inspector 中找到 "Effects" 部分
3. 将 `FireworksEffect.prefab` 拖拽到 `Success Effect Prefab` 字段
4. 运行游戏，当玩家答对时会自动播放特效

### 参数说明

```csharp
// 在 LevelController 中可调整的参数
public float effectDuration = 1f; // 特效持续时间
```

### 自定义建议

如果需要调整特效效果，可以修改以下参数：

- **颜色**: 修改 `colorOverLifetime.color` 渐变
- **规模**: 调整 `main.startSize` 和 `shape.radius`
- **持续时间**: 修改 `main.duration`
- **粒子密度**: 调整 `emission.rateOverTime` 和 `main.maxParticles`

### 文件位置

- 编辑器脚本：`Assets/Editor/FireworksEffectCreator.cs`
- 生成的预设：`Assets/Effects/FireworksEffect.prefab`

### 故障排除

**问题**: 菜单项不可用
- 确保脚本位于 `Assets/Editor` 文件夹
- 等待 Unity 编译完成
- 检查控制台是否有编译错误

**问题**: 特效不显示
- 检查 Camera 是否能看见特效位置
- 确认 ParticleSystem 的 Play On Awake 已启用
- 检查 Layer 和 Sorting Layer 设置

**问题**: 性能问题
- 减少 `maxParticles` 数量
- 降低 `emission.bursts` 的粒子数量
- 禁用 `noise` 模块
