using UnityEngine;

/// <summary>
/// Holds global game state such as player's name and current level.
/// This data could be filled from a remote server or local storage.
/// </summary>
public static class GameData
{
    public static string PlayerName { get; set; } = "Player";
    public static int CurrentLevel { get; set; } = 1;
    public static int BusyCoinCount { get; set; } = 10; // 忙币数量，默认10个
    public static int ConsecutiveCorrect { get; set; } = 0; // 连续答对次数

    /// <summary>
    /// Total number of levels in the game.
    /// </summary>
    public const int MaxLevels = 100;

    /// <summary>
    /// Simulate loading data from a server. In a real project you would
    /// perform a UnityWebRequest and parse the JSON.
    /// </summary>
    public static void LoadFromServer(System.Action onComplete)
    {
        // placeholder implementation - replace with actual networking code
        Debug.Log("[GameData] Loading data from server...");
        // simulate delay
        GameObject runner = new GameObject("ServerRunner");
        var loader = runner.AddComponent<CoroutineRunner>();
        loader.RunCoroutine(LoadCoroutine(onComplete));
    }

    private static System.Collections.IEnumerator LoadCoroutine(System.Action onComplete)
    {
        yield return new WaitForSeconds(0.5f);
        // set dummy values
        PlayerName = "TestUser";
        CurrentLevel = 1;
        BusyCoinCount = 10; // 从服务器加载忙币数量
        onComplete?.Invoke();
        Object.Destroy(GameObject.Find("ServerRunner"));
    }
}

// helper class to run coroutines from a static context
public class CoroutineRunner : MonoBehaviour { public void RunCoroutine(System.Collections.IEnumerator c) { StartCoroutine(c); } }
