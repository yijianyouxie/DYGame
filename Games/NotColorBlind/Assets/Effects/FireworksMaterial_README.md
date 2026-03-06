# 烟花特效材质球说明

## 🎆 FireworksParticleMaterial

烟花特效使用的粒子材质球，已集成到 FireworksEffect Prefab 中。

## ✨ 材质球属性

### 基础配置

- **Shader**: Particles/Standard Unlit
- **颜色**: 白色（通过粒子系统的 colorOverLifetime 模块控制渐变）
- **渲染模式**: Billboard（始终面向相机）
- **透明度**: 支持（使用粒子系统的 Alpha 通道）

### 材质球特点

1. **无光照渲染** - 使用 Unlit Shader，不受场景灯光影响
2. **透明混合** - 支持透明度混合，实现粒子淡入淡出效果
3. **Billboard 渲染** - 粒子始终面向相机，获得最佳视觉效果
4. **颜色渐变** - 通过粒子系统的颜色渐变模块控制，材质本身保持白色

## 🔧 如何生成

### 方式一：自动创建（推荐）

运行 Unity 菜单：
```
Tools → Create Fireworks Effect Prefab
```

材质球会自动创建并赋值给粒子系统。

### 方式二：手动创建

1. 在 Project 窗口右键 → Create → Material
2. 重命名为 "FireworksParticleMaterial"
3. 选择 Shader: `Particles/Standard Unlit`
4. 将材质球拖拽到粒子系统的 Renderer 模块的 Material 字段

## 📋 在粒子系统中的配置

在 FireworksEffect Prefab 中：

```
FireworksEffect
└── ParticleSystem
    └── Renderer 模块
        ├── Material → FireworksParticleMaterial
        └── Render Mode → Billboard
```

## 🎨 自定义材质效果

### 如果要修改粒子外观：

**1. 改变粒子颜色**
- 修改 `colorOverLifetime.color` 渐变
- 不要修改材质球颜色（保持白色）

**2. 改变粒子形状**
- 在 Renderer 模块中修改 Mesh 属性
- 或使用不同的 Render Mode（Stretched Billboard 等）

**3. 添加纹理**
- 在材质球的 Albedo 通道添加粒子纹理
- 常用纹理：圆形渐变、火花形状等

**4. 调整透明度**
- 修改粒子系统的 startAlpha 和 colorOverLifetime 的 Alpha 曲线
- 调整材质球的渲染队列

## ⚙️ Shader 属性说明

### Particles/Standard Unlit 主要属性：

- **Color** - 基础颜色（通常保持白色）
- **Albedo** - 基础纹理（可选）
- **Mode** - 渲染模式（Alpha Blended Premultiply）
- **Flipbook** - 序列帧动画（可选）
- **Soft Particles** - 软粒子效果（可选）

## 💡 性能优化建议

1. **使用简单的 Shader** - Unlit 比 Lit 性能更好
2. **避免过度绘制** - 控制粒子数量和透明度
3. **使用纹理图集** - 减少材质切换
4. **批量渲染** - 相同材质的粒子可以批量处理

## 🐛 常见问题

**问题**: 粒子显示为白色方块
- 检查是否赋值了正确的材质球
- 确认 Shader 类型正确
- 检查粒子纹理是否缺失

**问题**: 粒子不透明
- 检查材质球的渲染模式
- 确认粒子系统的 startColor 包含 Alpha 值
- 检查 colorOverLifetime 的 Alpha 曲线

**问题**: 材质球不显示颜色渐变
- 颜色渐变由粒子系统控制，不是材质球
- 检查 colorOverLifetime 模块是否启用
- 确认渐变曲线设置正确

## 📁 相关文件

- 创建脚本：`Assets/Editor/FireworksEffectCreator.cs`
- 生成位置：`Assets/Effects/FireworksEffect.prefab`
- 材质球：运行时动态创建（无需手动保存）

## 🎯 使用示例

在代码中访问材质球：

```csharp
ParticleSystem ps = GetComponent<ParticleSystem>();
ParticleSystemRenderer renderer = ps.GetComponent<ParticleSystemRenderer>();
Material mat = renderer.material;

// 修改材质颜色
mat.color = new Color(1, 1, 1, 0.5f);
```

## ⚠️ 注意事项

1. **运行时修改** - 使用 `renderer.material` 会创建材质实例，不影响原材质
2. **共享材质** - 使用 `renderer.sharedMaterial` 会修改原材质资产
3. **内存管理** - 动态创建的材质需要及时清理避免内存泄漏
4. **预制体引用** - 确保 Prefab 正确引用材质球
