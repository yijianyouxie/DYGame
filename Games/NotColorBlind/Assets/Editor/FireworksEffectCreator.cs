using UnityEngine;
using UnityEditor;
using System.IO;

/// <summary>
/// 创建烟花特效预设的编辑器工具
/// </summary>
public class FireworksEffectCreator
{
    [MenuItem("Tools/Create Fireworks Effect Prefab")]
    static void CreateFireworksPrefab()
    {
        Debug.Log("[FireworksEffect] 开始创建烟花特效预设...");
        
        // 1. 创建基础 GameObject
        GameObject fireworksEffect = new GameObject("FireworksEffect");
        
        // 2. 添加 ParticleSystem 组件
        ParticleSystem ps = fireworksEffect.AddComponent<ParticleSystem>();
        
        // 2.1 创建粒子材质球
        Material particleMaterial = new Material(Shader.Find("Particles/Standard Unlit"));
        particleMaterial.name = "FireworksParticleMaterial";
        particleMaterial.color = Color.white;
        
        // 3. 配置主模块
        var main = ps.main;
        main.duration = 1.0f;
        main.loop = false;
        main.prewarm = false;
        main.startLifetime = new ParticleSystem.MinMaxCurve(0.5f, 1.5f);
        main.startSpeed = new ParticleSystem.MinMaxCurve(5f, 15f);
        main.startSize = new ParticleSystem.MinMaxCurve(0.2f, 0.5f);
        main.startColor = Color.white;
        main.gravityModifier = 0.5f;
        main.maxParticles = 200;
        
        // 4. 配置发射模块
        var emission = ps.emission;
        emission.rateOverTime = new ParticleSystem.MinMaxCurve(0f, 100f);
        ParticleSystem.Burst[] bursts = new ParticleSystem.Burst[]
        {
            new ParticleSystem.Burst(0f, 50f),
            new ParticleSystem.Burst(0.1f, 30f),
            new ParticleSystem.Burst(0.2f, 20f)
        };
        emission.SetBursts(bursts);
        
        // 5. 配置形状模块（球形爆炸）
        var shape = ps.shape;
        shape.shapeType = ParticleSystemShapeType.Sphere;
        shape.radius = 0.5f;
        
        // 6. 配置速度模块（增加随机性）
        var velocity = ps.velocityOverLifetime;
        velocity.enabled = true;
        velocity.x = new ParticleSystem.MinMaxCurve(-2f, 2f);
        velocity.y = new ParticleSystem.MinMaxCurve(-2f, 2f);
        velocity.z = new ParticleSystem.MinMaxCurve(-2f, 2f);
        
        // 7. 配置颜色渐变
        var colorOverLifetime = ps.colorOverLifetime;
        colorOverLifetime.enabled = true;
        Gradient colorGradient = new Gradient();
        GradientColorKey[] colorKeys = new GradientColorKey[]
        {
            new GradientColorKey(new Color(1, 0.8f, 0.2f), 0f), // 金黄色
            new GradientColorKey(new Color(1, 0.4f, 0.2f), 0.5f), // 橙红色
            new GradientColorKey(new Color(0.8f, 0.2f, 0.5f), 1f) // 紫红色
        };
        GradientAlphaKey[] alphaKeys = new GradientAlphaKey[]
        {
            new GradientAlphaKey(1f, 0f),
            new GradientAlphaKey(0.8f, 0.5f),
            new GradientAlphaKey(0f, 1f)
        };
        colorGradient.SetKeys(colorKeys, alphaKeys);
        colorOverLifetime.color = colorGradient;
        
        // 8. 配置大小变化
        var sizeOverLifetime = ps.sizeOverLifetime;
        sizeOverLifetime.enabled = true;
        sizeOverLifetime.size = new ParticleSystem.MinMaxCurve(1f, 0.2f);
        
        // 9. 配置旋转
        var rotation = ps.rotationOverLifetime;
        rotation.enabled = true;
        rotation.z = new ParticleSystem.MinMaxCurve(-180f, 180f);
        
        // 10. 配置噪声效果（增加自然感）
        var noise = ps.noise;
        noise.enabled = true;
        noise.strength = new ParticleSystem.MinMaxCurve(0.5f, 1f);
        noise.frequency = 0.5f;
        
        // 11. 添加子发射器（模拟二次爆炸）
        var subEmitters = ps.subEmitters;
        GameObject subEmitterObject = new GameObject("SubEmitter");
        subEmitterObject.transform.SetParent(fireworksEffect.transform);
        ParticleSystem subPs = subEmitterObject.AddComponent<ParticleSystem>();
        
        var subMain = subPs.main;
        subMain.duration = 0.5f;
        subMain.startLifetime = new ParticleSystem.MinMaxCurve(0.3f, 0.8f);
        subMain.startSpeed = new ParticleSystem.MinMaxCurve(2f, 8f);
        subMain.startSize = new ParticleSystem.MinMaxCurve(0.1f, 0.3f);
        subMain.startColor = new Color(1, 1, 0.8f);
        
        var subEmission = subPs.emission;
        emission.rateOverTime = 50f;
        
        var subShape = subPs.shape;
        subShape.shapeType = ParticleSystemShapeType.Sphere;
        subShape.radius = 0.3f;
        
        // 关联子发射器
        subEmitters.AddSubEmitter(subPs, ParticleSystemSubEmitterType.Death, ParticleSystemSubEmitterProperties.InheritColor);
        
        // 11.5 配置粒子渲染器并赋值材质球
        var renderer = ps.GetComponent<ParticleSystemRenderer>();
        if (renderer != null)
        {
            renderer.material = particleMaterial;
            renderer.renderMode = ParticleSystemRenderMode.Billboard;
            Debug.Log("[FireworksEffect] 已为粒子系统赋值材质球：" + particleMaterial.name);
        }
        else
        {
            Debug.LogError("[FireworksEffect] 未找到 ParticleSystemRenderer 组件");
        }
        
        // 12. 添加 Light 组件（照亮周围）
        Light effectLight = fireworksEffect.AddComponent<Light>();
        effectLight.type = LightType.Point;
        effectLight.range = 10f;
        effectLight.intensity = 2f;
        effectLight.color = new Color(1, 0.8f, 0.4f);
        
        // 添加光的动画（使用内嵌的 MonoBehaviour）
        var lightAnimator = fireworksEffect.AddComponent<LightAnimator>();
        lightAnimator.light = effectLight;
        lightAnimator.fadeDuration = 1f;
        
        // 13. 添加音频组件（可选，如果需要爆炸声）
        // AudioSource audioSource = fireworksEffect.AddComponent<AudioSource>();
        // audioSource.playOnAwake = true;
        // audioSource.loop = false;
        
        // 14. 创建预设文件夹
        string effectsPath = "Assets/Effects";
        if (!Directory.Exists(effectsPath))
        {
            Directory.CreateDirectory(effectsPath);
            AssetDatabase.Refresh();
        }
        
        // 15. 保存为预设
        string prefabPath = Path.Combine(effectsPath, "FireworksEffect.prefab");
        PrefabUtility.SaveAsPrefabAsset(fireworksEffect, prefabPath);
        
        // 16. 清理场景中的临时对象
        Object.DestroyImmediate(fireworksEffect);
        
        Debug.Log($"[FireworksEffect] ✅ 成功创建烟花特效预设：{prefabPath}");
        Debug.Log("===========================================");
        Debug.Log("🎆 烟花特效特性：");
        Debug.Log("- 持续时长：1 秒");
        Debug.Log("- 粒子数量：最多 200 个");
        Debug.Log("- 颜色渐变：金黄→橙红→紫红");
        Debug.Log("- 包含子发射器效果");
        Debug.Log("- 带有点光源照明");
        Debug.Log("===========================================");
    }
}