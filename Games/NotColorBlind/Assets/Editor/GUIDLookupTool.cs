using UnityEngine;
using UnityEditor;
using UnityEditor.Callbacks;
using System;
using System.IO;
using System.Text.RegularExpressions;

public class PostBuildProcessor
{
    static int attemptCount = 0;

    [PostProcessBuildAttribute(1)]
    public static void OnPostprocessBuild(BuildTarget target, string pathToBuiltProject)
    {
        if (target == BuildTarget.WebGL)
        {
            string projectPath = Application.dataPath.Replace("/Assets", "");
            string gameJsPath = Path.Combine(projectPath, "tt-minigame", "tt-minigame", "game.js");
            if (File.Exists(gameJsPath))
            {
                File.Delete(gameJsPath);
                Debug.Log("Deleted old game.js to ensure fresh modification");
            }
            attemptCount = 0;
            EditorApplication.delayCall += () => ModifyGameJsDelayed();
        }
    }

    static void ModifyGameJsDelayed()
    {
        string projectPath = Application.dataPath.Replace("/Assets", "");
        string gameJsPath = Path.Combine(projectPath, "tt-minigame", "tt-minigame", "game.js");
        if (File.Exists(gameJsPath))
        {
            string content = File.ReadAllText(gameJsPath);
            
            // Use regex for more flexible matching
            string pattern = @"(      // 一般不修改，控制icon样式\s+iconConfig:\s*\{\s*visible:\s*true,\s*style:\s*\{\s*width:\s*106,\s*height:\s*40,\s*bottom:\s*141,\s*\},\s*\},)";
            string replacement = @"      // 一般不修改，控制icon样式
      iconConfig: {
        visible: true,
        style: {
          width: 128,
          height: 128,
          bottom: 141,
        },
      },";
            
            System.Text.RegularExpressions.Match match = System.Text.RegularExpressions.Regex.Match(content, pattern, System.Text.RegularExpressions.RegexOptions.Singleline);
            if (match.Success)
            {
                Debug.Log("Found iconConfig with regex, replacing...");
                content = System.Text.RegularExpressions.Regex.Replace(content, pattern, replacement);
                File.WriteAllText(gameJsPath, content);
                Debug.Log("Updated game.js iconConfig to 128x128");
            }
            else
            {
                Debug.LogError("Regex pattern not found. Let's try a simpler approach...");
                
                // Try to find just the iconConfig section and replace the dimensions
                string simplePattern = @"(width:\s*)106(\s*,\s*height:\s*)40";
                string simpleReplacement = @"${1}128${2}128";
                
                if (System.Text.RegularExpressions.Regex.IsMatch(content, simplePattern))
                {
                    Debug.Log("Found dimensions with simple regex, replacing...");
                    content = System.Text.RegularExpressions.Regex.Replace(content, simplePattern, simpleReplacement);
                    File.WriteAllText(gameJsPath, content);
                    Debug.Log("Updated game.js iconConfig dimensions to 128x128");
                }
                else
                {
                    Debug.LogError("Even simple regex failed. Content around iconConfig:");
                    int iconIndex = content.IndexOf("iconConfig:");
                    if (iconIndex >= 0)
                    {
                        int start = Math.Max(0, iconIndex - 50);
                        int end = Math.Min(content.Length, iconIndex + 100);
                        string excerpt = content.Substring(start, end - start);
                        Debug.LogError("Excerpt around iconConfig:\n" + excerpt);
                        
                        // Show hex values of the problematic section
                        byte[] bytes = System.Text.Encoding.UTF8.GetBytes(excerpt);
                        string hex = BitConverter.ToString(bytes).Replace("-", " ");
                        Debug.LogError("Hex dump of excerpt:\n" + hex);
                    }
                }
            }
            attemptCount = 0; // reset
        }
        else if (attemptCount < 20) // try up to 20 times, about 20 seconds
        {
            attemptCount++;
            EditorApplication.delayCall += () => ModifyGameJsDelayed();
        }
        else
        {
            Debug.LogError("Failed to find game.js after 20 attempts");
            attemptCount = 0;
        }
    }
}

public class GUIDLookupTool : EditorWindow
{
    string guidInput = "";
    string pathInput = "";
    string result = "";
    bool useBase64 = false;

    [MenuItem("Tools/GUID互查")]
    static void ShowWindow()
    {
        GetWindow<GUIDLookupTool>("GUID互查");
    }

    void OnGUI()
    {
        useBase64 = EditorGUILayout.Toggle("使用团结引擎GUID格式", useBase64);

        GUILayout.Label("输入GUID获取路径：");
        guidInput = EditorGUILayout.TextField("GUID", guidInput);
        if (GUILayout.Button("查询路径"))
        {
            string guid = guidInput;
            if (useBase64 && IsBase64Guid(guidInput))
            {
                guid = Base64ToGuid(guidInput);
            }
            string path = AssetDatabase.GUIDToAssetPath(guid);
            result = path != "" ? path : "未找到";
            Debug.Log("路径: " + result);
        }

        GUILayout.Label("输入路径获取GUID：");
        pathInput = EditorGUILayout.TextField("路径", pathInput);
        if (GUILayout.Button("查询GUID"))
        {
            string guid = AssetDatabase.AssetPathToGUID(pathInput);
            if (useBase64)
            {
                guid = GuidToBase64(guid);
            }
            result = guid != "" ? guid : "未找到";
            Debug.Log("GUID: " + result);
        }

        GUILayout.Label("结果：" + result);

        if (GUILayout.Button("扫描所有GUID"))
        {
            ScanAllGUIDs();
        }

        if (GUILayout.Button("修复非标准GUID"))
        {
            FixNonStandardGUIDs();
        }
    }

    string GuidToBase64(string guid)
    {
        if (guid.Length != 32) return guid;
        byte[] bytes = new byte[16];
        for (int i = 0; i < 16; i++)
        {
            bytes[i] = Convert.ToByte(guid.Substring(i * 2, 2), 16);
        }
        return Convert.ToBase64String(bytes);
    }

    string Base64ToGuid(string base64)
    {
        try
        {
            byte[] bytes = Convert.FromBase64String(base64);
            if (bytes.Length != 16) return base64;
            return BitConverter.ToString(bytes).Replace("-", "").ToLower();
        }
        catch
        {
            return base64;
        }
    }

    void ScanAllGUIDs()
    {
        Debug.Log("开始扫描所有资产GUID...");
        string[] allAssetPaths = AssetDatabase.GetAllAssetPaths();
        foreach (string path in allAssetPaths)
        {
            if (!path.StartsWith("Assets/")) continue;
            string metaPath = path + ".meta";
            if (File.Exists(metaPath))
            {
                string metaContent = File.ReadAllText(metaPath);
                string metaGuid = ExtractGuidFromMeta(metaContent);
                if (!IsStandardGuid(metaGuid))
                {
                    string standardGuid = AssetDatabase.AssetPathToGUID(path);
                    Debug.Log($"文件: {path}, 32位标准GUID: {standardGuid}");
                }
            }
        }
        Debug.Log("扫描完成。");
    }

    string ExtractGuidFromMeta(string metaContent)
    {
        Match match = Regex.Match(metaContent, @"guid:\s*([a-zA-Z0-9+/=]+)");
        return match.Success ? match.Groups[1].Value : "";
    }

    bool IsStandardGuid(string guid)
    {
        return guid.Length == 32 && Regex.IsMatch(guid, @"^[a-fA-F0-9]{32}$");
    }

    bool IsBase64Guid(string str)
    {
        try
        {
            Convert.FromBase64String(str);
            return str.Length == 24; // base64 for 16 bytes is 24 chars
        }
        catch
        {
            return false;
        }
    }

    void FixNonStandardGUIDs()
    {
        Debug.Log("开始修复非标准GUID...");
        string[] allAssetPaths = AssetDatabase.GetAllAssetPaths();
        int fixedCount = 0;
        foreach (string path in allAssetPaths)
        {
            if (!path.StartsWith("Assets/")) continue;
            string metaPath = path + ".meta";
            if (File.Exists(metaPath))
            {
                string metaContent = File.ReadAllText(metaPath);
                string metaGuid = ExtractGuidFromMeta(metaContent);
                if (!IsStandardGuid(metaGuid))
                {
                    string standardGuid = AssetDatabase.AssetPathToGUID(path);
                    string newMetaContent = Regex.Replace(metaContent, @"guid:\s*[a-zA-Z0-9+/=]+", "guid: " + standardGuid);
                    File.WriteAllText(metaPath, newMetaContent);
                    Debug.Log($"修复文件: {path}, 新GUID: {standardGuid}");
                    fixedCount++;
                }
            }
        }
        if (fixedCount > 0)
        {
            AssetDatabase.Refresh();
            Debug.Log($"修复完成，共修复 {fixedCount} 个文件。");
        }
        else
        {
            Debug.Log("没有需要修复的文件。");
        }
    }
}

public class GUIDContextMenu
{
    [MenuItem("Assets/输出GUID")]
    static void OutputGUID()
    {
        foreach (var obj in Selection.objects)
        {
            string path = AssetDatabase.GetAssetPath(obj);
            string guid = AssetDatabase.AssetPathToGUID(path);
            string base64Guid = GuidToBase64(guid);
            Debug.Log($"文件: {path}, 标准GUID: {guid}, 团结GUID: {base64Guid}");
        }
    }

    static string GuidToBase64(string guid)
    {
        if (guid.Length != 32) return guid;
        byte[] bytes = new byte[16];
        for (int i = 0; i < 16; i++)
        {
            bytes[i] = Convert.ToByte(guid.Substring(i * 2, 2), 16);
        }
        return Convert.ToBase64String(bytes);
    }
}