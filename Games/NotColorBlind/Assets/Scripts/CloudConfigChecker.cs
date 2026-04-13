using UnityEngine;
using TTSDK;

/// <summary>
/// 抖音云数据库配置检查工具
/// </summary>
public class CloudConfigChecker : MonoBehaviour
{
    [Header("配置检查")]
    public string envId = "env-nJ2KymQ8pn";
    public string collectionName = "game_progress";

    void Start()
    {
        CheckConfiguration();
    }

    /// <summary>
    /// 检查配置
    /// </summary>
    public void CheckConfiguration()
    {
        Debug.Log("=== 抖音云数据库配置检查 ===");
        Debug.Log($"环境ID: {envId}");
        Debug.Log($"集合名称: {collectionName}");

        // 检查平台支持
        #if UNITY_WEBGL && !UNITY_EDITOR
        Debug.Log("平台: WebGL (支持抖音云)");
        #elif UNITY_EDITOR
        Debug.Log("平台: Unity Editor (不支持抖音云，使用模拟数据)");
        #else
        Debug.Log("平台: 其他平台 (可能不支持抖音云)");
        #endif

        Debug.Log("=== 常见问题检查 ===");
        Debug.Log("1. 请确认环境ID在抖音云控制台存在");
        Debug.Log("2. 请确认集合已创建且有读写权限");
        Debug.Log("3. 请确认应用ID和密钥正确配置");
        Debug.Log("4. 请确认网络连接正常");

        Debug.Log("=== 错误码说明 ===");
        Debug.Log("21101: 集合不存在");
        Debug.Log("21102: 权限不足或集合不存在");
        Debug.Log("21103: 数据格式错误");
        Debug.Log("21104: 网络连接错误");
    }
}