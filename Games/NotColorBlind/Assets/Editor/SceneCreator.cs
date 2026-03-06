using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEditor;
using UnityEditor.SceneManagement;
using System.IO;

/// <summary>
/// 自动创建测试场景的编辑器脚本
/// 可通过菜单或命令行调用
/// </summary>
public class SceneCreator : EditorWindow
{
    // 菜单项：Tools > Create Test Scene
    [MenuItem("Tools/Create Test Scene")]
    static void CreateTestScene()
    {
        ExecuteCreateScene();
    }
    
    // 可由 MCP 或其他外部工具调用的静态方法
    public static void ExecuteCreateScene()
    {
        Debug.Log("[SceneCreator] 开始创建测试场景...");
        
        try
        {
            // 1. 创建新场景
            Scene newScene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            Debug.Log($"[SceneCreator] 创建新场景：{newScene.name}");
            
            // 2. 创建胶囊体
            GameObject capsule = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            capsule.name = "RedCapsule";
            Debug.Log("[SceneCreator] 创建胶囊体：RedCapsule");
            
            // 3. 设置位置
            capsule.transform.position = new Vector3(0, 0.5f, 0);
            Debug.Log($"[SceneCreator] 设置位置：{capsule.transform.position}");
            
            // 4. 创建红色材质
            Shader standardShader = Shader.Find("Standard");
            if (standardShader == null)
            {
                // 如果找不到 Standard shader，使用 Built-in Render Pipeline 的默认 shader
                standardShader = Shader.Find("Sprites/Default");
            }
            
            Material redMaterial = new Material(standardShader);
            redMaterial.color = new Color(1, 0, 0, 1); // 红色
            Debug.Log("[SceneCreator] 创建红色材质");
            
            // 5. 应用材质到胶囊体
            Renderer capsuleRenderer = capsule.GetComponent<Renderer>();
            if (capsuleRenderer != null)
            {
                capsuleRenderer.material = redMaterial;
                Debug.Log("[SceneCreator] 应用红色材质到胶囊体");
            }
            
            // 6. 添加灯光（场景需要灯光才能看到物体）
            GameObject lightObj = new GameObject("Directional Light");
            Light light = lightObj.AddComponent<Light>();
            light.type = LightType.Directional;
            light.intensity = 1.0f;
            lightObj.transform.rotation = Quaternion.Euler(50, -30, 0);
            Debug.Log("[SceneCreator] 添加方向光");
            
            // 7. 保存场景
            string scenesPath = "Assets/Scenes";
            if (!Directory.Exists(scenesPath))
            {
                Directory.CreateDirectory(scenesPath);
                Debug.Log($"[SceneCreator] 创建目录：{scenesPath}");
            }
            
            string scenePath = Path.Combine(scenesPath, "test3.unity");
            EditorSceneManager.SaveScene(newScene, scenePath);
            Debug.Log($"[SceneCreator] ✅ 成功创建场景：{scenePath}");
            
            // 8. 输出摘要信息
            Debug.Log("===========================================");
            Debug.Log("✅ 场景创建完成！");
            Debug.Log($"📁 场景路径：{scenePath}");
            Debug.Log($"🔴 胶囊体：RedCapsule @ {capsule.transform.position}");
            Debug.Log($"🎨 材质：红色标准材质");
            Debug.Log($"💡 灯光：Directional Light");
            Debug.Log("===========================================");
            
            // 9. 刷新 Asset 数据库
            AssetDatabase.Refresh();
            
        }
        catch (System.Exception ex)
        {
            Debug.LogError($"[SceneCreator] ❌ 创建场景失败：{ex.Message}");
            Debug.LogError(ex.StackTrace);
        }
    }
    
    // 验证菜单项是否应该显示
    [MenuItem("Tools/Create Test Scene", validate = true)]
    static bool ValidateCreateTestScene()
    {
        // 总是允许执行
        return true;
    }
}
