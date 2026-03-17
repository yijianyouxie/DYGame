using UnityEngine;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

/// <summary>
/// 抖音云数据库排行榜管理器
/// 负责玩家数据的存储、读取和排行榜查询
/// </summary>
public class LeaderboardManager : MonoBehaviour
{
    private static LeaderboardManager _instance;
    public static LeaderboardManager Instance
    {
        get
        {
            if (_instance == null)
            {
                GameObject go = new GameObject("LeaderboardManager");
                DontDestroyOnLoad(go);
                _instance = go.AddComponent<LeaderboardManager>();
            }
            return _instance;
        }
    }

    [Header("云数据库配置")]
    public string databaseName = "leaderboard"; // 数据库名称
    
    // 当前用户信息
    private string currentUserId;
    private string currentUsername;
    private string currentAvatarUrl;
    
    // 公共属性：提供对当前用户 ID 的只读访问
    public string CurrentUserId => currentUserId;
    
    // 事件：当获取到用户信息时触发
    public event Action<UserInfo> OnUserInfoReady;
    
    void Awake()
    {
        if (_instance != null && _instance != this)
        {
            Destroy(gameObject);
            return;
        }
        
        _instance = this;
        DontDestroyOnLoad(gameObject);
        
        // 初始化抖音 SDK 并获取用户信息
        InitDouyinSDK();
    }
    
    /// <summary>
    /// 初始化抖音 SDK 并获取用户信息
    /// </summary>
    private async void InitDouyinSDK()
    {
        Debug.Log("[LeaderboardManager] 开始初始化抖音 SDK...");
        
        try
        {
            // 等待抖音 SDK 初始化完成
            await Task.Delay(1000);
            
            // 获取用户信息（需要先请求授权）
            await RequestUserInfo();
        }
        catch (Exception e)
        {
            Debug.LogError($"[LeaderboardManager] 初始化失败：{e.Message}");
        }
    }
    
    /// <summary>
    /// 请求用户信息授权并获取用户数据
    /// </summary>
    private async Task RequestUserInfo()
    {
        try
        {
            // 使用抖音 SDK 获取用户信息
            // 注意：这里需要根据实际 SDK API 调整
            var userInfo = await GetDouyinUserInfo();
            
            if (userInfo != null)
            {
                currentUserId = userInfo.openId;
                currentUsername = userInfo.nickName;
                currentAvatarUrl = userInfo.avatarUrl;
                
                Debug.Log($"[LeaderboardManager] 获取到用户信息：{currentUsername}");
                
                // 触发自定义事件
                OnUserInfoReady?.Invoke(new UserInfo
                {
                    user_id = currentUserId,
                    username = currentUsername,
                    avatar_url = currentAvatarUrl
                });
            }
            else
            {
                // 如果无法获取用户信息，使用默认值
                UseDefaultUserInfo();
            }
        }
        catch (Exception e)
        {
            Debug.LogWarning($"[LeaderboardManager] 获取用户信息失败，使用默认信息：{e.Message}");
            UseDefaultUserInfo();
        }
    }
    
    /// <summary>
    /// 使用默认用户信息（用于测试或无法获取真实信息时）
    /// </summary>
    private void UseDefaultUserInfo()
    {
        currentUserId = $"user_{UnityEngine.Random.Range(10000, 99999)}";
        currentUsername = "游客_" + GameData.PlayerName;
        currentAvatarUrl = "";
        
        Debug.Log($"[LeaderboardManager] 使用默认用户信息：{currentUsername}");
        
        OnUserInfoReady?.Invoke(new UserInfo
        {
            user_id = currentUserId,
            username = currentUsername,
            avatar_url = currentAvatarUrl
        });
    }
    
    /// <summary>
    /// 从抖音 SDK 获取用户信息
    /// </summary>
    private Task<DouyinUserInfo> GetDouyinUserInfo()
    {
        var tcs = new TaskCompletionSource<DouyinUserInfo>();
        
        try
        {
            // 调用抖音 SDK API
            // 注意：这是伪代码，需要根据实际 SDK API 调整
            // StarkSDK.GetUserProfile((userInfo) => {
            //     tcs.SetResult(new DouyinUserInfo {
            //         openId = userInfo.openId,
            //         nickName = userInfo.nickName,
            //         avatarUrl = userInfo.avatarUrl
            //     });
            // }, (error) => {
            //     tcs.SetException(new Exception(error));
            // });
            
            // 临时模拟数据
            UnityEngine.Debug.Log("[LeaderboardManager] 模拟获取抖音用户信息...");
            tcs.SetResult(new DouyinUserInfo
            {
                openId = System.Guid.NewGuid().ToString(),
                nickName = "抖音用户",
                avatarUrl = ""
            });
        }
        catch (Exception e)
        {
            tcs.SetException(e);
        }
        
        return tcs.Task;
    }
    
    /// <summary>
    /// 保存玩家进度到云数据库
    /// </summary>
    /// <param name="level">当前关卡</param>
    public async void SavePlayerProgress(int level)
    {
        if (string.IsNullOrEmpty(currentUserId))
        {
            Debug.LogError("[LeaderboardManager] 用户 ID 为空，无法保存进度");
            return;
        }
        
        try
        {
            // 先查询是否已有记录
            var existingRecord = await QueryPlayerRecord(currentUserId);
            
            if (existingRecord != null)
            {
                // 如果新关卡更高，则更新
                if (level > existingRecord.max_level)
                {
                    await UpdatePlayerRecord(existingRecord._id, level);
                    Debug.Log($"[LeaderboardManager] 更新玩家进度：关卡 {existingRecord.max_level} -> {level}");
                }
                else
                {
                    Debug.Log($"[LeaderboardManager] 当前关卡未超过最高记录，不更新");
                }
            }
            else
            {
                // 创建新记录
                await CreatePlayerRecord(level);
                Debug.Log($"[LeaderboardManager] 创建新玩家记录：关卡 {level}");
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"[LeaderboardManager] 保存进度失败：{e.Message}");
        }
    }
    
    /// <summary>
    /// 查询玩家现有记录
    /// </summary>
    private async Task<LeaderboardRecord> QueryPlayerRecord(string userId)
    {
        // TODO: 实现云数据库查询
        // 示例：SELECT * FROM leaderboard WHERE user_id = userId
        Debug.Log($"[LeaderboardManager] 查询玩家记录：{userId}");
        
        // 临时返回 null，后续实现云数据库查询
        return await Task.FromResult<LeaderboardRecord>(null);
    }
    
    /// <summary>
    /// 创建新的玩家记录
    /// </summary>
    private async Task CreatePlayerRecord(int level)
    {
        // TODO: 实现云数据库插入
        var newRecord = new LeaderboardRecord
        {
            user_id = currentUserId,
            username = currentUsername,
            avatar_url = currentAvatarUrl,
            max_level = level,
            update_time = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss")
        };
        
        Debug.Log($"[LeaderboardManager] 创建记录：{JsonUtility.ToJson(newRecord)}");
        await Task.CompletedTask;
    }
    
    /// <summary>
    /// 更新玩家记录
    /// </summary>
    private async Task UpdatePlayerRecord(string recordId, int newLevel)
    {
        // TODO: 实现云数据库更新
        Debug.Log($"[LeaderboardManager] 更新记录 {recordId} 到关卡 {newLevel}");
        await Task.CompletedTask;
    }
    
    /// <summary>
    /// 获取排行榜数据（前 50 名）
    /// </summary>
    public async Task<List<LeaderboardRecord>> GetLeaderboardAsync()
    {
        try
        {
            Debug.Log("[LeaderboardManager] 获取排行榜数据...");
            
            // TODO: 实现云数据库查询
            // SELECT * FROM leaderboard ORDER BY max_level DESC, update_time ASC LIMIT 50
            
            // 临时模拟数据
            return await Task.FromResult(GetMockLeaderboardData());
        }
        catch (Exception e)
        {
            Debug.LogError($"[LeaderboardManager] 获取排行榜失败：{e.Message}");
            return new List<LeaderboardRecord>();
        }
    }
    
    /// <summary>
    /// 获取模拟的排行榜数据（用于测试）
    /// </summary>
    private List<LeaderboardRecord> GetMockLeaderboardData()
    {
        var list = new List<LeaderboardRecord>();
        
        // 添加当前玩家
        list.Add(new LeaderboardRecord
        {
            _id = "current_player",
            user_id = currentUserId,
            username = currentUsername,
            avatar_url = currentAvatarUrl,
            max_level = GameData.CurrentLevel,
            update_time = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss")
        });
        
        // 添加其他虚拟玩家
        string[] names = { "张三", "李四", "王五", "赵六", "钱七", "孙八", "周九", "吴十" };
        for (int i = 0; i < 20; i++)
        {
            list.Add(new LeaderboardRecord
            {
                _id = $"user_{i}",
                user_id = $"user_{i}",
                username = names[i % names.Length] + "_" + i,
                avatar_url = "",
                max_level = UnityEngine.Random.Range(1, 50),
                update_time = DateTime.Now.AddHours(-i).ToString("yyyy-MM-dd HH:mm:ss")
            });
        }
        
        // 排序：先按关卡降序，再按时间升序
        list.Sort((a, b) =>
        {
            int levelCompare = b.max_level.CompareTo(a.max_level);
            return levelCompare != 0 ? levelCompare : a.update_time.CompareTo(b.update_time);
        });
        
        return list;
    }
}

/// <summary>
/// 抖音用户信息（简化版）
/// </summary>
[System.Serializable]
public class DouyinUserInfo
{
    public string openId;
    public string nickName;
    public string avatarUrl;
}

/// <summary>
/// 用户信息
/// </summary>
[System.Serializable]
public class UserInfo
{
    public string user_id;
    public string username;
    public string avatar_url;
}

/// <summary>
/// 排行榜记录
/// </summary>
[System.Serializable]
public class LeaderboardRecord
{
    public string _id;
    public string user_id;
    public string username;
    public string avatar_url;
    public int max_level;
    public string update_time;
}
