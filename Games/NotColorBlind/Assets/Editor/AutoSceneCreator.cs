using UnityEngine;
using UnityEditor;
using System.IO;

/// <summary>
/// 命令行工具 - 用于从命令行创建测试场景
/// 使用方法：Unity -batchmode -quit -projectPath [项目路径] -executeMethod AutoSceneCreator.CreateTestSceneFromCommand
/// </summary>
public static class AutoSceneCreator
{
    /// <summary>
    /// 从命令行调用此方法创建测试场景
    /// </summary>
    public static void CreateTestSceneFromCommand()
    {
        Debug.Log("===========================================");
        Debug.Log("🚀 从命令行启动场景创建...");
        Debug.Log("===========================================");
        
        // 调用实际的创建逻辑
        SceneCreator.ExecuteCreateScene();
        
        Debug.Log("===========================================");
        Debug.Log("✅ 命令行任务完成");
        Debug.Log("===========================================");
    }
}
