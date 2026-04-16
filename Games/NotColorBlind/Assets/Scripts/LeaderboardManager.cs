using UnityEngine;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using TTSDK;
using TTSDK.UNBridgeLib.LitJson;
using JsonData = TTSDK.UNBridgeLib.LitJson.JsonData;

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

    [Header("数据库配置")]
    public string collectionName = "game_progress"; // 数据集合名称

    // 当前用户信息
    private string currentUserId;
    private string currentOpenId;
    private string currentUsername;
    private string currentAvatarUrl;
    private string loginAnonymousCode;
    private string deviceId; // 设备级别的稳定标识

    // 云数据库管理器
    private DouyinCloudManager cloudManager;

    // 初始化状态
    private bool isInitialized = false;

    // 是否使用真实用户（用于云数据库）
    private bool isRealUser = false;

    // 公共属性：提供对当前用户 ID 的只读访问
    public string CurrentUserId => currentUserId;
    public string CurrentOpenId => currentOpenId;
    public bool IsInitialized => isInitialized;
    public bool IsRealUser => isRealUser;

    // 事件：当获取到用户信息时触发
    public event Action<PlayerData> OnUserInfoReady;
    
    void Awake()
    {
        if (_instance != null && _instance != this)
        {
            Destroy(gameObject);
            return;
        }

        _instance = this;
        DontDestroyOnLoad(gameObject);

        // 初始化设备ID
        InitializeDeviceId();

        // 获取云数据库管理器
        cloudManager = DouyinCloudManager.Instance;

        // 初始化抖音 SDK 并获取用户信息
        InitDouyinSDK();
    }

    /// <summary>
    /// 初始化设备ID（用于跨会话数据持久化）
    /// </summary>
    private void InitializeDeviceId()
    {
        try
        {
            // 从本地存储获取设备ID
            deviceId = TTSDK.TTStorage.GetStringSync("DeviceId", "");
            if (string.IsNullOrEmpty(deviceId))
            {
                deviceId = System.Guid.NewGuid().ToString();
                TTSDK.TTStorage.SetStringSync("DeviceId", deviceId);
                Debug.Log($"[LeaderboardManager] 生成新设备ID：{deviceId}");
            }
            else
            {
                Debug.Log($"[LeaderboardManager] 加载设备ID：{deviceId}");
            }
        }
        catch (Exception e)
        {
            Debug.LogWarning($"[LeaderboardManager] 初始化设备ID失败：{e.Message}");
            // 失败时使用随机ID
            deviceId = System.Guid.NewGuid().ToString();
        }
    }

    /// <summary>
    /// 初始化抖音 SDK 并获取用户信息
    /// </summary>
    private async void InitDouyinSDK()
    {
        Debug.Log("[LeaderboardManager] 开始初始化抖音 SDK...");

        try
        {
            // 初始化云数据库
            await cloudManager.InitializeAsync();

            // 打印配置信息用于调试
            cloudManager.PrintConfigurationInfo();

            // 先进行用户登录
            await LoginUserAsync();

            // 获取用户信息（需要先登录）
            await RequestUserInfo();
        }
        catch (Exception e)
        {
            Debug.LogError($"[LeaderboardManager] 初始化失败：{e.Message}");
            UseDefaultUserInfo();
        }
    }

    /// <summary>
    /// 用户登录
    /// </summary>
    private Task LoginUserAsync()
    {
        var tcs = new TaskCompletionSource<bool>();

        try
        {
            Debug.Log("[LeaderboardManager] 开始用户登录...");

            TTSDK.TT.Login(
                (code, anonymousCode, isLogin) =>
                {
                    loginAnonymousCode = anonymousCode;
                    Debug.Log($"[LeaderboardManager] 登录成功，isLogin: {isLogin}, code: {code}, anonymousCode: {anonymousCode}");
                    tcs.SetResult(true);
                },
                (errorMsg) =>
                {
                    Debug.LogError($"[LeaderboardManager] 登录失败：{errorMsg}");
                    tcs.SetResult(false);
                },
                false // 不强制弹出登录框
            );
        }
        catch (Exception e)
        {
            Debug.LogError($"[LeaderboardManager] 登录异常：{e.Message}");
            tcs.SetException(e);
        }

        return tcs.Task;
    }

    /// <summary>
    /// 请求用户信息授权并获取用户数据
    /// </summary>
    private async Task RequestUserInfo()
    {
        try
        {
            // 调用抖音 SDK 获取用户信息
            var userInfo = await GetDouyinUserInfo();

            if (userInfo != null)
            {
                currentUserId = deviceId;
                currentUsername = userInfo.nickName;
                currentAvatarUrl = userInfo.avatarUrl;
                isInitialized = true;
                isRealUser = true;
                GameData.PlayerName = currentUsername;

                // 通过云函数获取 openId
                var openId = await cloudManager.GetOpenIdAsync();
                if (!string.IsNullOrEmpty(openId))
                {
                    currentOpenId = openId;
                    Debug.Log($"[LeaderboardManager] 云函数获取 openId: {currentOpenId}");
                }

                Debug.Log($"[LeaderboardManager] 用户信息：{currentUsername}, openId={currentOpenId}");

                // 从云数据库加载玩家数据
                await LoadPlayerDataFromCloud();

                // 触发事件
                var playerData = new PlayerData
                {
                    user_id = currentUserId,
                    username = currentUsername,
                    avatar_url = currentAvatarUrl,
                    max_level = GameData.CurrentLevel,
                    busy_coins = GameData.BusyCoinCount
                };
                OnUserInfoReady?.Invoke(playerData);
            }
            else
            {
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
    /// 从云数据库加载玩家数据（仅真实用户）
    /// </summary>
    private async Task LoadPlayerDataFromCloud()
    {
        if (!isRealUser)
        {
            Debug.Log("[LeaderboardManager] 非真实用户，跳过云端数据加载");
            return;
        }

        try
        {
            var userRecord = await GetUserRecordAsync();
            
            if (userRecord != null)
            {
                // 从云端记录加载数据
                if (userRecord.ContainsKey("max_level") && userRecord["max_level"] != null)
                {
                    GameData.CurrentLevel = Convert.ToInt32(userRecord["max_level"]);
                    Debug.Log($"[LeaderboardManager] 从云端加载关卡：{GameData.CurrentLevel}");
                }
                
                if (userRecord.ContainsKey("busy_coins") && userRecord["busy_coins"] != null)
                {
                    GameData.BusyCoinCount = Convert.ToInt32(userRecord["busy_coins"]);
                    Debug.Log($"[LeaderboardManager] 从云端加载忙币：{GameData.BusyCoinCount}");
                }
                
                Debug.Log("[LeaderboardManager] 云端数据加载完成");
            }
            else
            {
                Debug.Log("[LeaderboardManager] 云端没有用户记录，尝试从本地存储加载");
                // 尝试从本地存储加载作为后备
                LoadFromLocalStorage();
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"[LeaderboardManager] 从云端加载数据失败：{e.Message}");
            // 失败时使用本地存储作为后备
            LoadFromLocalStorage();
        }
    }
    
    /// <summary>
    /// 使用默认用户信息（用于测试或无法获取真实信息时）
    /// 注意：非真实用户只能使用本地存储，不能写入云数据库
    /// </summary>
    private void UseDefaultUserInfo()
    {
        currentUserId = $"guest_{UnityEngine.Random.Range(10000, 99999)}";
        currentOpenId = "";  // 非真实用户，不设置 openid
        currentUsername = "游客_" + GameData.PlayerName;
        currentAvatarUrl = "";
        isInitialized = true;
        isRealUser = false;

        GameData.PlayerName = currentUsername;

        Debug.Log($"[LeaderboardManager] 使用默认用户信息（本地模式）：{currentUsername}");

        // 只从本地存储加载数据
        LoadFromLocalStorage();

        OnUserInfoReady?.Invoke(new PlayerData
        {
            user_id = currentUserId,
            username = currentUsername,
            avatar_url = currentAvatarUrl,
            max_level = GameData.CurrentLevel,
            busy_coins = GameData.BusyCoinCount
        });
    }

    /// <summary>
    /// 从本地存储加载数据（降级方案）
    /// </summary>
    private void LoadFromLocalStorage()
    {
        try
        {
            // 使用抖音SDK的存储API，兼容WebGL
            if (TTSDK.TTStorage.HasKeySync("PlayerLevel"))
            {
                GameData.CurrentLevel = TTSDK.TTStorage.GetIntSync("PlayerLevel", 1);
                Debug.Log($"[LeaderboardManager] 从本地存储加载关卡：{GameData.CurrentLevel}");
            }

            if (TTSDK.TTStorage.HasKeySync("PlayerCoins"))
            {
                GameData.BusyCoinCount = TTSDK.TTStorage.GetIntSync("PlayerCoins", 10);
                Debug.Log($"[LeaderboardManager] 从本地存储加载忙币：{GameData.BusyCoinCount}");
            }

            string lastSaveTime = TTSDK.TTStorage.GetStringSync("LastSaveTime", "");
            if (!string.IsNullOrEmpty(lastSaveTime))
            {
                Debug.Log($"[LeaderboardManager] 最后保存时间：{lastSaveTime}");
            }
        }
        catch (Exception e)
        {
            Debug.LogWarning($"[LeaderboardManager] 从本地存储加载数据失败：{e.Message}");
        }
    }

    /// <summary>
    /// 从抖音 SDK 获取用户信息
    /// 使用 TT.GetUserInfo API，withCredentials=true 获取 cloudId
    /// </summary>
    private Task<DouyinUserInfo> GetDouyinUserInfo()
    {
        var tcs = new TaskCompletionSource<DouyinUserInfo>();

        try
        {
            Debug.Log("[LeaderboardManager] 开始调用抖音 SDK 获取用户信息...");

            // 使用 TT.GetUserInfo API，withCredentials=true 获取 cloudId
            TTSDK.TT.GetUserInfo(
                true, // withCredentials = true，获取 cloudId
                (ref TTSDK.TTUserInfo userInfo) =>
                {
                    if (userInfo == null || string.IsNullOrEmpty(userInfo.nickName))
                    {
                        Debug.LogWarning("[LeaderboardManager] GetUserInfo 返回的数据为空或 nickName 为空。");
                        tcs.SetResult(null);
                        return;
                    }

                    Debug.Log($"[LeaderboardManager] GetUserInfo 成功，昵称={userInfo.nickName}");
                    Debug.Log($"[LeaderboardManager] CloudId: {(string.IsNullOrEmpty(GetUserInfoCloudId(userInfo)) ? "未获取" : GetUserInfoCloudId(userInfo))}");

                    tcs.SetResult(new DouyinUserInfo
                    {
                        openId = string.Empty,
                        nickName = userInfo.nickName,
                        avatarUrl = userInfo.avatarUrl
                    });
                },
                (errMsg) =>
                {
                    Debug.LogError($"[LeaderboardManager] GetUserInfo 失败：{errMsg}");
                    tcs.SetResult(null);
                });
        }
        catch (Exception e)
        {
            Debug.LogError($"[LeaderboardManager] GetDouyinUserInfo 异常：{e.Message}");
            tcs.SetException(e);
        }

        return tcs.Task;
    }

    private string GetUserInfoCloudId(TTSDK.TTUserInfo userInfo)
    {
        return GetUserInfoFieldOrProperty(userInfo, "cloudId");
    }

    private string GetUserInfoFieldOrProperty(TTSDK.TTUserInfo userInfo, string name)
    {
        try
        {
            var type = userInfo.GetType();
            var property = type.GetProperty(name, System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic);
            if (property != null)
            {
                return property.GetValue(userInfo)?.ToString();
            }

            var field = type.GetField(name, System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic);
            if (field != null)
            {
                return field.GetValue(userInfo)?.ToString();
            }
        }
        catch
        {
        }
        return null;
    }

    /// <summary>
    /// 保存玩家进度到云数据库
    /// </summary>
    /// <param name="level">当前关卡</param>
    public async void SavePlayerProgress(int level)
    {
        // 等待初始化完成
        if (!isInitialized)
        {
            Debug.LogWarning("[LeaderboardManager] 初始化未完成，等待中...");
            await WaitForInitialization();
        }

        await SavePlayerData(level, GameData.BusyCoinCount);
    }

    /// <summary>
    /// 等待初始化完成
    /// </summary>
    private async Task WaitForInitialization()
    {
        int maxWait = 10; // 最多等待10秒
        int waited = 0;
        while (!isInitialized && waited < maxWait)
        {
            await Task.Delay(1000);
            waited++;
        }

        if (!isInitialized)
        {
            Debug.LogWarning("[LeaderboardManager] 初始化超时，强制使用默认信息");
            UseDefaultUserInfo();
        }
    }

    /// <summary>
    /// 获取当前用户的云端记录
    /// </summary>
    private async Task<Dictionary<string, object>> GetUserRecordAsync()
    {
        try
        {
            Dictionary<string, object> whereCondition = null;
            if (!string.IsNullOrEmpty(currentOpenId))
                whereCondition = new Dictionary<string, object> { { "_openid", currentOpenId } };

            Debug.Log($"[LeaderboardManager] 查询用户记录，_openid={currentOpenId ?? "未知，返回全部"}");
            var result = await cloudManager.QueryWhereAsync(collectionName, whereCondition, 1);
            var record = ParseQueryResult(result);

            // 首次查询时从记录中保存 _openid
            if (record != null && string.IsNullOrEmpty(currentOpenId) && record.ContainsKey("_openid"))
            {
                currentOpenId = record["_openid"]?.ToString();
                TTSDK.TTStorage.SetStringSync("CachedOpenId", currentOpenId);
                Debug.Log($"[LeaderboardManager] 获取并缓存 _openid: {currentOpenId}");
            }

            return record;
        }
        catch (Exception e)
        {
            Debug.LogError($"[LeaderboardManager] 查询用户记录失败：{e.Message}");
            return null;
        }
    }

    private Dictionary<string, object> ParseQueryResult(string result)
    {
        if (string.IsNullOrEmpty(result))
        {
            Debug.LogWarning("[LeaderboardManager] ParseQueryResult: result 为空");
            return null;
        }

        var jsonData = JsonMapper.ToObject(result);
        if (jsonData == null)
            return null;

        // 结构: {request_id, list:[...], offset, limit}
        var list = jsonData["list"] as JsonData;
        if (list == null || list.Count == 0)
        {
            Debug.Log("[LeaderboardManager] ParseQueryResult: list 为空，无记录");
            return null;
        }

        Debug.Log($"[LeaderboardManager] ParseQueryResult: 找到 {list.Count} 条记录");

        var firstItem = list[0];
        var recordDict = new Dictionary<string, object>();
        foreach (var key in firstItem.Keys)
        {
            var val = firstItem[key];
            recordDict[key] = val?.IsString == true ? (object)val.ToString()
                : val?.IsInt == true ? (object)(int)val
                : val?.IsLong == true ? (object)(long)val
                : val?.IsDouble == true ? (object)(double)val
                : val?.IsBoolean == true ? (object)(bool)val
                : val?.ToString();
        }

        return recordDict;
    }

    /// <summary>
    /// 保存玩家忙币数量
    /// </summary>
    /// <param name="coins">忙币数量</param>
    public async void SavePlayerCoins(int coins)
    {
        await SavePlayerData(GameData.CurrentLevel, coins);
    }

    /// <summary>
    /// 保存玩家所有数据
    /// 真实用户保存到云数据库，非真实用户只保存到本地存储
    /// 注意：抖音云数据库自动管理 _openid，不需要手动设置
    /// </summary>
    /// <param name="level">当前关卡</param>
    /// <param name="coins">忙币数量</param>
    public async Task SavePlayerData(int level, int coins)
    {
        // 1. 先保存到本地存储（所有用户都需要）
        try
        {
            TTSDK.TTStorage.SetIntSync("PlayerLevel", level);
            TTSDK.TTStorage.SetIntSync("PlayerCoins", coins);
            TTSDK.TTStorage.SetStringSync("LastSaveTime", DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"));
            Debug.Log($"[LeaderboardManager] 本地存储已保存：关卡 {level}, 忙币 {coins}");
        }
        catch (Exception localEx)
        {
            Debug.LogError($"[LeaderboardManager] 本地存储失败：{localEx.Message}");
        }

        // 2. 只有真实用户才保存到云数据库
        if (!isRealUser)
        {
            Debug.Log("[LeaderboardManager] 非真实用户，数据仅保存在本地存储");
            return;
        }

        try
        {
            Debug.Log($"[LeaderboardManager] 保存玩家数据到云端：关卡 {level}, 忙币 {coins}");

            // 先查询用户是否已有记录
            var existingRecord = await GetUserRecordAsync();
            
            if (existingRecord != null)
            {
                // 更新现有记录
                var updateData = new Dictionary<string, object>
                {
                    {"user_id", currentUserId},
                    {"username", currentUsername},
                    {"avatar_url", currentAvatarUrl},
                    {"max_level", level},
                    {"busy_coins", coins},
                    {"update_time", DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss")}
                };

                var result = await cloudManager.UpdateDocumentAsync(collectionName, existingRecord["_id"].ToString(), updateData);
                if (!string.IsNullOrEmpty(result))
                {
                    Debug.Log("[LeaderboardManager] 云端记录更新成功");
                }
                else
                {
                    Debug.LogWarning("[LeaderboardManager] 云端记录更新失败");
                }
            }
            else
            {
                // 创建新记录
                var newData = new Dictionary<string, object>
                {
                    {"user_id", currentUserId},
                    {"username", currentUsername},
                    {"avatar_url", currentAvatarUrl},
                    {"max_level", level},
                    {"busy_coins", coins},
                    {"update_time", DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss")}
                };

                var result = await cloudManager.AddDocumentAsync(collectionName, newData);
                if (!string.IsNullOrEmpty(result))
                {
                    Debug.Log("[LeaderboardManager] 云端记录创建成功");
                }
                else
                {
                    Debug.LogWarning("[LeaderboardManager] 云端记录创建失败（权限问题或集合不存在）");
                }
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"[LeaderboardManager] 保存到云端失败：{e.Message}\n{e.StackTrace}");
            Debug.Log("[LeaderboardManager] 数据已保存到本地存储");
        }
    }

    /// <summary>
    /// 获取排行榜数据（前 50 名）
    /// </summary>
    public async Task<List<LeaderboardRecord>> GetLeaderboardAsync()
    {
        try
        {
            Debug.Log("[LeaderboardManager] 获取排行榜数据...");

            // 构建聚合查询：按关卡降序，按更新时间升序
            var pipeline = new List<Dictionary<string, object>>
            {
                new Dictionary<string, object>
                {
                    {"$sort", new Dictionary<string, object>
                        {
                            {"max_level", -1},  // 关卡降序
                            {"update_time", 1}   // 时间升序
                        }
                    }
                },
                new Dictionary<string, object>
                {
                    {"$limit", 50}
                },
                new Dictionary<string, object>
                {
                    {"$project", new Dictionary<string, object>
                        {
                            {"user_id", 1},
                            {"username", 1},
                            {"avatar_url", 1},
                            {"max_level", 1},
                            {"update_time", 1}
                        }
                    }
                }
            };

            var jsonResult = await cloudManager.AggregateAsync(collectionName, pipeline, 50);

            List<LeaderboardRecord> records = new List<LeaderboardRecord>();

            if (!string.IsNullOrEmpty(jsonResult))
            {
                var result = JsonMapper.ToObject(jsonResult);
                // 结构: {request_id, list:[...], offset, limit}
                var dataList = result?["list"] as JsonData;
                if (dataList != null)
                {
                    for (int i = 0; i < dataList.Count; i++)
                    {
                        var recordJson = dataList[i].ToString();
                        var playerData = JsonMapper.ToObject<PlayerData>(recordJson);
                        if (playerData != null)
                        {
                            records.Add(new LeaderboardRecord
                            {
                                user_id = playerData.user_id,
                                username = playerData.username,
                                avatar_url = playerData.avatar_url,
                                max_level = playerData.max_level,
                                update_time = playerData.update_time ?? DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss")
                            });
                        }
                    }
                }
            }

            Debug.Log($"[LeaderboardManager] 获取到 {records.Count} 条排行榜数据");
            return records;
        }
        catch (Exception e)
        {
            Debug.LogError($"[LeaderboardManager] 获取排行榜失败：{e.Message}");

            // 失败时返回模拟数据
            return GetMockLeaderboardData();
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
/// 排行榜记录（UI 显示用）
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
