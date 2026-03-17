# FireworksEffect 材质球配置总结

## ✅ 已完成的任务

### 1. 创建材质球
- **路径**: `Assets/Effects/FireworksParticleMaterial.mat`
- **GUID**: `c49ec41ea225333469a36faa9ad0a209`
- **状态**: ✅ 已成功创建

### 2. 创建 FireworksEffect GameObject
- **位置**: Unity Hierarchy 中的 "FireworksEffect"
- **组件**: ParticleSystem
- **状态**: ✅ 已成功创建并配置以下模块:
  - ✅ 主模块 (duration: 1s, maxParticles: 200, etc.)
  - ✅ 发射模块 (rateOverTime: 0-100)
  - ✅ 形状模块 (Sphere, radius: 0.5)
  - ✅ 颜色渐变模块 (金黄→橙红→紫红)

## ⚠️ 需要手动完成的步骤

### 问题说明
MCP 的 `manage_vfx` 工具在调用 `particle_set_renderer` 时，参数校验未通过。这可能是因为：
1. 参数名称不匹配（可能需要使用其他参数名）
2. MCP Unity 插件的版本差异
3. 需要不同的工具调用方式

### 解决方案

#### 方案一：手动赋值材质球（推荐）
1. 打开 Unity Editor
2. 在 Hierarchy 中找到 **FireworksEffect** GameObject
3. 选中它，在 Inspector 面板中找到 **Particle System Renderer** 组件
4. 将 `Assets/Effects/FireworksParticleMaterial.mat` 拖拽到 **Material** 字段
5. 确认 **Render Mode** 设置为 **Billboard**

#### 方案二：使用 Unity 菜单重新生成
1. 在 Unity Editor 中点击菜单：`Tools > Create Fireworks Effect Prefab`
2. 这会自动运行 `FireworksEffectCreator.cs` 脚本
3. 脚本会自动创建并赋值材质球
4. 生成的 Prefab 位于：`Assets/Effects/FireworksEffect.prefab`

#### 方案三：在 Unity Console 中运行命令
打开 Unity Console 窗口，运行以下 C# 代码：

```csharp
using UnityEngine;
using UnityEditor;

// 查找 FireworksEffect
GameObject fireworks = GameObject.Find("FireworksEffect");
if (fireworks != null)
{
    // 获取 ParticleSystemRenderer
    var renderer = fireworks.GetComponent<ParticleSystemRenderer>();
    if (renderer != null)
    {
        // 加载材质球
        Material mat = AssetDatabase.LoadAssetAtPath<Material>(
            "Assets/Effects/FireworksParticleMaterial.mat"
        );
        if (mat != null)
        {
            renderer.material = mat;
            Debug.Log("✅ 材质球已成功赋值！");
        }
        else
        {
            Debug.LogError("❌ 无法加载材质球");
        }
    }
}
```

## 📋 材质球配置详情

### FireworksParticleMaterial 属性
- **Shader**: Particles/Standard Unlit（自动应用）
- **颜色**: White (1, 1, 1, 1)
- **渲染模式**: Billboard（粒子系统控制）

### 为什么材质球是白色的？
根据烟花特效的设计逻辑：
1. 粒子的颜色由 ParticleSystem 的 `colorOverLifetime` 模块控制
2. 材质球本身保持白色，作为"画布"
3. 粒子系统在渲染时会将颜色渐变应用到材质上
4. 这样可以动态改变颜色而不需要多个材质球

## 🎯 预期效果

完成材质球赋值后，烟花特效将显示：
- ✨ 金黄色起爆的粒子
- 🔥 渐变为橙红色
- 💜 最后变为紫红色并逐渐透明消失
- 💫 球形爆炸扩散效果
- 🌟 带有子发射器的二次爆炸

## 📁 相关文件

- 材质球：`Assets/Effects/FireworksParticleMaterial.mat`
- 创建脚本：`Assets/Editor/FireworksEffectCreator.cs`
- 配置脚本：`setup_fireworks_material.py`
- 说明文档：`Assets/Effects/FireworksMaterial_README.md`

## 🔍 验证步骤

1. **检查材质球**:
   - 在 Project 窗口展开 `Assets/Effects/`
   - 确认 `FireworksParticleMaterial.mat` 存在
   - 双击查看 Inspector，确认 Shader 为 "Particles/Standard Unlit"

2. **检查 GameObject**:
   - 在 Hierarchy 中找到 `FireworksEffect`
   - 展开查看子对象
   - 选中后在 Inspector 中查看 ParticleSystem 组件

3. **检查材质引用**:
   - 找到 ParticleSystem Renderer 模块
   - 确认 Material 字段有值
   - 如果是 "Default-Particle" 或为空，需要手动赋值为 FireworksParticleMaterial

4. **测试效果**:
   - 点击 Unity 的 Play 按钮
   - 观察烟花是否正确显示颜色和透明度渐变
   - 检查 Console 是否有错误信息

## 💡 提示

- 如果材质球仍然无法赋值，可以直接使用 `FireworksEffectCreator.cs` 菜单命令
- 该脚本会自动处理所有配置，包括材质球的创建和赋值
- 手动赋值材质球是最简单直接的解决方案
