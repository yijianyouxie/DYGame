using UnityEngine;

/// <summary>
/// 游戏数据同步管理器
/// 负责在游戏过程中自动同步数据到云数据库
/// </summary>
public class GameDataSyncManager : MonoBehaviour
{
    private static GameDataSyncManager _instance;
    public static GameDataSyncManager Instance
    {
        get
        {
            if (_instance == null)
            {
                GameObject go = new GameObject("GameDataSyncManager");
                DontDestroyOnLoad(go);
                _instance = go.AddComponent<GameDataSyncManager>();
            }
            return _instance;
        }
    }

    // 自动保存间隔（秒）
    [Header("自动保存配置")]
    public float autoSaveInterval = 30f; // 每 30 秒自动保存一次
    private float lastSaveTime;

    // 是否已初始化
    private bool isInitialized = false;

    void Awake()
    {
        if (_instance != null && _instance != this)
        {
            Destroy(gameObject);
            return;
        }
        _instance = this;
        DontDestroyOnLoad(gameObject);
    }

    void Start()
    {
        // 订阅用户信息就绪事件
        LeaderboardManager.Instance.OnUserInfoReady += OnUserInfoReady;
    }

    void Update()
    {
        // 自动保存检查
        if (isInitialized && Time.time - lastSaveTime >= autoSaveInterval)
        {
            AutoSave();
            lastSaveTime = Time.time;
        }
    }

    /// <summary>
    /// 当用户信息就绪时调用
    /// </summary>
    private void OnUserInfoReady(PlayerData playerData)
    {
        Debug.Log("[GameDataSyncManager] 用户信息就绪，开始数据同步");
        isInitialized = true;
        lastSaveTime = Time.time;

        // 更新本地显示的玩家名称
        if (!string.IsNullOrEmpty(playerData.username))
        {
            GameData.PlayerName = playerData.username;
        }

        // 立即保存当前数据，确保云端有记录
        SaveNow();
    }

    /// <summary>
    /// 自动保存数据
    /// </summary>
    private void AutoSave()
    {
        Debug.Log("[GameDataSyncManager] 自动保存数据");
        LeaderboardManager.Instance.SavePlayerData(GameData.CurrentLevel, GameData.BusyCoinCount);
    }

    /// <summary>
    /// 主动触发数据保存（例如：关卡完成、应用退出时）
    /// </summary>
    public void SaveNow()
    {
        if (isInitialized)
        {
            Debug.Log("[GameDataSyncManager] 手动保存数据");
            LeaderboardManager.Instance.SavePlayerData(GameData.CurrentLevel, GameData.BusyCoinCount);
            lastSaveTime = Time.time;
        }
        else
        {
            Debug.LogWarning("[GameDataSyncManager] 尚未初始化，无法保存");
        }
    }

    /// <summary>
    /// 更新关卡进度
    /// </summary>
    /// <param name="newLevel">新关卡</param>
    public void UpdateLevel(int newLevel)
    {
        if (newLevel > GameData.CurrentLevel)
        {
            GameData.CurrentLevel = newLevel;
            Debug.Log($"[GameDataSyncManager] 更新关卡：{newLevel}");

            // 立即保存
            SaveNow();
        }
    }

    /// <summary>
    /// 更新忙币数量
    /// </summary>
    /// <param name="newCoins">新忙币数量</param>
    public void UpdateCoins(int newCoins)
    {
        if (newCoins != GameData.BusyCoinCount)
        {
            GameData.BusyCoinCount = newCoins;
            Debug.Log($"[GameDataSyncManager] 更新忙币：{newCoins}");

            // 立即保存
            SaveNow();
        }
    }

    /// <summary>
    /// 增加忙币
    /// </summary>
    /// <param name="amount">增加数量</param>
    public void AddCoins(int amount)
    {
        UpdateCoins(GameData.BusyCoinCount + amount);
    }

    /// <summary>
    /// 消耗忙币
    /// </summary>
    /// <param name="amount">消耗数量</param>
    /// <returns>是否足够消耗</returns>
    public bool SpendCoins(int amount)
    {
        if (GameData.BusyCoinCount >= amount)
        {
            UpdateCoins(GameData.BusyCoinCount - amount);
            return true;
        }
        Debug.LogWarning($"[GameDataSyncManager] 忙币不足：{GameData.BusyCoinCount} < {amount}");
        return false;
    }

    /// <summary>
    /// 应用暂停时保存
    /// </summary>
    private void OnApplicationPause(bool pauseStatus)
    {
        if (pauseStatus)
        {
            SaveNow();
        }
    }

    /// <summary>
    /// 应用退出时保存
    /// </summary>
    private void OnApplicationQuit()
    {
        SaveNow();
    }
}
