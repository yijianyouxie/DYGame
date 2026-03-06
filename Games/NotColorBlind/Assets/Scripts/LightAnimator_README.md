# LightAnimator 组件说明

##  组件用途

`LightAnimator` 是一个简单的灯光动画组件，用于实现烟花特效中点光源的渐隐效果。

## 🎯 使用场景

- 烟花爆炸时的瞬间照明
- 爆炸效果的光照淡出
- 其他需要灯光渐强/渐弱的特效场景

## 🔧 组件属性

### 公共字段

- **Light** (Light) - 要控制的灯光组件引用
- **Fade Duration** (float) - 淡出持续时间（秒），默认 1 秒

## 📖 使用方法

### 方式一：通过代码添加

```csharp
GameObject effect = new GameObject("LightEffect");
Light light = effect.AddComponent<Light>();
light.type = LightType.Point;
light.range = 10f;
light.intensity = 2f;

LightAnimator animator = effect.AddComponent<LightAnimator>();
animator.light = light;
animator.fadeDuration = 1f;
```

### 方式二：Inspector 中赋值

1. 在 Hierarchy 中创建或选择带有 Light 组件的 GameObject
2. 添加组件：`Add Component` → 搜索 `LightAnimator`
3. 在 Inspector 中将 Light 组件拖拽到 `Light` 字段
4. 设置 `Fade Duration` 参数

## ⚙️ 工作原理

- 组件在 `Update` 中每帧更新灯光强度
- 从初始强度 2.0 线性插值到 0
- 达到持续时间后自动禁用组件

## 🎆 在烟花特效中的应用

在 `FireworksEffectCreator.cs` 中自动添加此组件：

```csharp
Light effectLight = fireworksEffect.AddComponent<Light>();
effectLight.type = LightType.Point;
effectLight.range = 10f;
effectLight.intensity = 2f;
effectLight.color = new Color(1, 0.8f, 0.4f);

var lightAnimator = fireworksEffect.AddComponent<LightAnimator>();
lightAnimator.light = effectLight;
lightAnimator.fadeDuration = 1f;
```

## 💡 参数建议

### 快速爆炸效果
- Fade Duration: 0.3 - 0.5 秒
- Light Intensity: 3 - 5

### 标准烟花效果
- Fade Duration: 1.0 秒
- Light Intensity: 2

### 缓慢淡出效果
- Fade Duration: 2.0 - 3.0 秒
- Light Intensity: 1 - 1.5

## ⚠️ 注意事项

1. **必须赋值 Light 引用** - 否则组件不会工作
2. **初始强度固定为 2.0** - 如需修改请调整代码中的 `Mathf.Lerp(2f, 0f, t)`
3. **完成后自动禁用** - 不会自动销毁 GameObject
4. **仅用于运行时** - 不要放在 Editor 文件夹中

##  故障排除

**问题**: 灯光不淡出
- 检查 Light 字段是否赋值
- 确认 GameObject 处于激活状态
- 检查 Light 组件是否启用

**问题**: 淡出速度不对
- 调整 `Fade Duration` 参数
- 检查游戏帧率是否稳定

## 📁 文件位置

- 脚本路径：`Assets/Scripts/LightAnimator.cs`
- 命名空间：全局命名空间（无 namespace）
- 依赖：UnityEngine
