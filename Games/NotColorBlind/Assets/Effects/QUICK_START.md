# 快速使用指南（已更新材质球）

## 🚀 立即开始使用烟花特效

### 步骤 1：生成特效预设（包含材质球）

在 Unity Editor 中：
```
菜单栏 → Tools → Create Fireworks Effect Prefab
```

控制台会显示：
```
[FireworksEffect] 开始创建烟花特效预设...
[FireworksEffect] 已为粒子系统赋值材质球：FireworksParticleMaterial
[FireworksEffect] ✅ 成功创建烟花特效预设：Assets/Effects/FireworksEffect.prefab
```

### 步骤 2：关联到 LevelController

1. 在 Hierarchy 中找到 **LevelController** GameObject
2. 选中它，在 Inspector 面板中找到 **Effects** 部分
3. 将 `Assets/Effects/FireworksEffect.prefab` 拖拽到 **Success Effect Prefab** 字段

### 步骤 3：测试效果

1. 运行游戏
2. 完成一个关卡（找到不同的色块）
3. 看到带材质的烟花绽放庆祝效果！🎆

---

## 📋 当前配置说明

你的 LevelController 已经有以下配置：

```csharp
[Header("Effects")]
public GameObject successEffectPrefab;  // ← 在这里赋值
public Text comboText;                  // 连击次数显示
public float effectDuration = 1f;       // 特效持续时间
```

## ✨ 特效包含的组件

- ✅ **ParticleSystem** - 主粒子系统
  - ✅ 颜色渐变（金黄→橙红→紫红）
  - ✅ 球形爆炸效果
  - ✅ 子发射器（二次爆炸）
- ✅ **ParticleSystemRenderer** - 粒子渲染器
  - ✅ **FireworksParticleMaterial** - 粒子材质球（新增！）
  - ✅ Billboard 渲染模式
- ✅ **Light** - 点光源
- ✅ **LightAnimator** - 灯光渐隐动画

## 🎯 预期效果

当玩家答对题目时：
1. 在屏幕中央绽放烟花
2. 粒子显示正确的颜色和透明度（材质球已正确赋值）
3. 显示连击次数（如"3 杀"）
4. 点光源提供瞬间照明
5. 1 秒后自动进入下一关

---

## 💡 提示

### 验证材质球是否已赋值：

1. 点击 `FireworksEffect.prefab`
2. 在 Inspector 中展开 ParticleSystem
3. 找到 **Renderer** 模块
4. 确认 **Material** 字段有值（FireworksParticleMaterial）

### 如果材质球仍然丢失：

1. 删除旧的 `FireworksEffect.prefab`
2. 重新运行 `Tools → Create Fireworks Effect Prefab`
3. 检查控制台日志确认材质球创建成功

### 自定义材质效果：

- 修改 `FireworksEffectCreator.cs` 中的材质球创建代码
- 调整 Shader 类型或材质属性
- 添加粒子纹理

---

## 📁 相关文件

- 创建脚本：`Assets/Editor/FireworksEffectCreator.cs`
- 材质球说明：`Assets/Effects/FireworksMaterial_README.md`
- 生成的 Prefab: `Assets/Effects/FireworksEffect.prefab`

文件已创建在正确位置，可以直接使用！