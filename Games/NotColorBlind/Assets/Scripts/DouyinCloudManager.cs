using UnityEngine;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Linq.Expressions;
using System.Reflection;
using System.Threading.Tasks;
using TTSDK;
using JsonData = TTSDK.UNBridgeLib.LitJson.JsonData;

/// <summary>
/// 抖音云数据库管理器
/// 负责所有与抖音云数据库的交互
/// </summary>
public class DouyinCloudManager : MonoBehaviour
{
    private static DouyinCloudManager _instance;
    public static DouyinCloudManager Instance
    {
        get
        {
            if (_instance == null)
            {
                GameObject go = new GameObject("DouyinCloudManager");
                DontDestroyOnLoad(go);
                _instance = go.AddComponent<DouyinCloudManager>();
            }
            return _instance;
        }
    }

    [Header("云数据库配置")]
    public string envId = "env-nJ2KymQ8pn"; // 环境ID
    public string collectionName = "game_progress"; // 集合名称
    public string serviceId = "1lyi27pj68f27";//服务id

    // 数据库初始化状态
    private bool isInitialized = false;
    private CloudDBCollection dbCollection;
    private bool isPlatformSupported = false;
    private DouyinCloud _cloud;
    private DouyinCloud Cloud => _cloud ??= TT.CreateCloud();

    // 添加重试机制
    private const int MAX_RETRY_ATTEMPTS = 3;
    private const float RETRY_DELAY = 1.0f;

    #region 初始化

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

    /// <summary>
    /// 初始化抖音云服务
    /// </summary>
    public async Task<bool> InitializeAsync()
    {
        if (isInitialized)
        {
            Debug.Log("[DouyinCloudManager] 云数据库已初始化");
            return true;
        }

        try
        {
            // 检查平台支持
            #if UNITY_WEBGL && !UNITY_EDITOR
            isPlatformSupported = true;
            #elif UNITY_ANDROID || UNITY_IOS
            // 移动平台可能支持
            isPlatformSupported = true;
            #else
            // Unity Editor或其他平台不支持抖音云
            isPlatformSupported = false;
            Debug.LogWarning("[DouyinCloudManager] 当前平台不支持抖音云服务。功能将使用本地存储。");
            return false;
            #endif

            Debug.Log($"[DouyinCloudManager] 初始化抖音云服务，环境ID：{envId}...");

            // 获取数据库集合对象
            dbCollection = Cloud.CloudDb().GenDBCollection(envId, collectionName);

            if (dbCollection != null)
            {
                // 验证集合是否存在
                bool collectionExists = await ValidateCollectionAsync();
                if (!collectionExists)
                {
                    Debug.LogError($"[DouyinCloudManager] 集合 '{collectionName}' 不存在或无权限访问");
                    Debug.LogError($"[DouyinCloudManager] 请在抖音云控制台创建集合，并确保应用有相应权限");
                    isPlatformSupported = false;
                    return false;
                }

                isInitialized = true;
                Debug.Log("[DouyinCloudManager] 初始化成功");
                return true;
            }
            else
            {
                Debug.LogError("[DouyinCloudManager] 获取数据库集合失败");
                isPlatformSupported = false;
                return false;
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"[DouyinCloudManager] 初始化失败：{e.Message}");
            isPlatformSupported = false;
            return false;
        }
    }

    /// <summary>
    /// 验证集合是否存在
    /// </summary>
    private async Task<bool> ValidateCollectionAsync()
    {
        try
        {
            var tcs = new TaskCompletionSource<bool>();

            // 尝试查询集合中的记录来验证集合存在性
            Cloud.CloudDb().GenDBCollection(envId, collectionName).Get(
                response =>
                {
                    Debug.Log($"[DouyinCloudManager] 集合验证成功：{response.StatusCode}");
                    tcs.SetResult(true);
                },
                error =>
                {
                    string errorMsg = GetDetailedErrorMessage(error.StatusCode, error.ErrMsg);
                    Debug.LogError($"[DouyinCloudManager] 集合验证失败：{error.StatusCode}, {error.ErrMsg}");
                    Debug.LogError($"[DouyinCloudManager] 详细错误信息：{errorMsg}");
                    tcs.SetResult(false);
                });

            return await tcs.Task;
        }
        catch (Exception e)
        {
            Debug.LogError($"[DouyinCloudManager] 集合验证异常：{e.Message}");
            return false;
        }
    }

    /// <summary>
    /// 打印配置信息用于调试
    /// </summary>
    public void PrintConfigurationInfo()
    {
        Debug.Log("=== 抖音云数据库配置信息 ===");
        Debug.Log($"环境ID: {envId}");
        Debug.Log($"集合名称: {collectionName}");
        Debug.Log($"平台支持: {isPlatformSupported}");
        Debug.Log($"已初始化: {isInitialized}");
        Debug.Log("=== 配置检查建议 ===");
        Debug.Log("1. 请在抖音云控制台确认环境ID正确");
        Debug.Log("2. 请在抖音云控制台创建集合: " + collectionName);
        Debug.Log("3. 请确保应用有云数据库读写权限");
        Debug.Log("4. 请检查应用ID和密钥配置");
    }

    /// <summary>
    /// 获取详细的错误信息
    /// </summary>
    private string GetDetailedErrorMessage(int statusCode, string errorMsg)
    {
        switch (statusCode)
        {
            case 21101:
                return "集合不存在。请在抖音云控制台创建集合 '" + collectionName + "'，并确保环境ID '" + envId + "' 正确。";
            case 21102:
                return "权限不足或集合不存在。请检查：\n" +
                       "1. 应用是否有云数据库写入权限\n" +
                       "2. 集合 '" + collectionName + "' 是否存在\n" +
                       "3. 环境ID '" + envId + "' 是否正确\n" +
                       "4. 应用ID和密钥是否正确配置";
            case 21103:
                return "数据格式错误。请检查要保存的数据格式是否符合要求。";
            case 21104:
                return "网络连接错误。请检查网络连接。";
            case 21105:
                return "参数错误。请检查API调用参数。";
            case 21106:
                return "服务不可用。请稍后重试。";
            default:
                return $"未知错误 (状态码: {statusCode})。原始错误信息：{errorMsg}";
        }
    }

    /// <summary>
    /// 检查平台是否支持抖音云
    /// </summary>
    public bool IsCloudSupported()
    {
        return isPlatformSupported && isInitialized;
    }

    #endregion

    #region 数据库操作

    /// <summary>
    /// 将 Dictionary<string, object> 转换为 JsonData
    /// </summary>
    private JsonData ToJsonData(Dictionary<string, object> dict)
    {
        if (dict == null)
            return null;

        JsonData jsonData = new JsonData();
        foreach (var kvp in dict)
        {
            var value = ConvertToJsonData(kvp.Value);
            // 根据值的类型添加到JsonData
            if (value is JsonData jd)
            {
                jsonData[kvp.Key] = jd;
            }
            else if (value is string str)
            {
                jsonData[kvp.Key] = str;
            }
            else if (value is int i)
            {
                jsonData[kvp.Key] = i;
            }
            else if (value is long l)
            {
                jsonData[kvp.Key] = l;
            }
            else if (value is double d)
            {
                jsonData[kvp.Key] = d;
            }
            else if (value is bool b)
            {
                jsonData[kvp.Key] = b;
            }
            else
            {
                // 其他类型使用隐式转换
                jsonData[kvp.Key] = new JsonData(value);
            }
        }
        return jsonData;
    }

    private object ConvertToJsonData(object obj)
    {
        if (obj == null)
            return null;

        if (obj is JsonData)
            return obj;

        if (obj is string str)
            return str;

        if (obj is int i)
            return i;

        if (obj is long l)
            return l;

        if (obj is double d)
            return d;

        if (obj is float f)
            return (double)f;

        if (obj is bool b)
            return b;

        if (obj is Dictionary<string, object> dict)
            return ToJsonData(dict);

        if (obj is List<object> list)
        {
            JsonData jsonData = JsonData.NewJsonArray();
            foreach (var item in list)
            {
                jsonData.Add(ConvertToJsonData(item));
            }
            return jsonData;
        }

        // 其他类型转为字符串
        return obj.ToString();
    }

    /// <summary>
    /// 将 List<Dictionary<string, object>> 转换为 List<object>
    /// </summary>
    private List<object> ToObjectList(List<Dictionary<string, object>> list)
    {
        if (list == null)
            return null;

        List<object> result = new List<object>();
        foreach (var item in list)
        {
            result.Add(ToJsonData(item));
        }
        return result;
    }

    /// <summary>
    /// 查询单条记录（根据 ID）
    /// </summary>
    public async Task<string> QueryDocumentAsync(string collection, string docId)
    {
        if (!IsCloudSupported())
        {
            Debug.LogWarning("[DouyinCloudManager] 云数据库不可用，跳过查询");
            return null;
        }

        try
        {
            var tcs = new TaskCompletionSource<string>();

            Debug.Log($"[DouyinCloudManager] 查询文档：{collection}/{docId}");

            Cloud.CloudDb().GenDBCollection(envId, collection).Doc(docId).Get(
                response =>
                {
                    Debug.Log($"[DouyinCloudManager] 查询文档成功：{response.StatusCode}");
                    tcs.SetResult(response.Data.ToJson());
                },
                error =>
                {
                    Debug.LogError($"[DouyinCloudManager] 查询文档失败：{error.StatusCode}, {error.ErrMsg}");
                    tcs.SetResult(null);
                });

            return await tcs.Task;
        }
        catch (Exception e)
        {
            Debug.LogError($"[DouyinCloudManager] 查询文档异常：{e.Message}");
            return null;
        }
    }

    /// <summary>
    /// 条件查询文档
    /// </summary>
    public async Task<string> QueryWhereAsync(string collection, Dictionary<string, object> whereCondition, int limit = 50)
    {
        if (!IsCloudSupported())
        {
            Debug.LogWarning("[DouyinCloudManager] 云数据库不可用，跳过查询");
            return null;
        }

        try
        {
            var tcs = new TaskCompletionSource<string>();

            Debug.Log($"[DouyinCloudManager] 条件查询：{collection}");
            Debug.Log($"[DouyinCloudManager] 查询条件：{(whereCondition != null ? string.Join(", ", whereCondition.Select(kv => $"{kv.Key}={kv.Value}")) : "_openid(自动)")}");

            object collectionObj = Cloud.CloudDb().GenDBCollection(envId, collection);
            if (collectionObj == null)
            {
                Debug.LogError("[DouyinCloudManager] 未能获取集合对象");
                return null;
            }

            var queryType = collectionObj.GetType();
            var getInfo = SelectGetMethod(queryType, whereCondition != null);
            if (getInfo.Method == null)
                throw new InvalidOperationException("无法找到集合的 Get 方法");

            var onSuccessDelegate = CreateDelegate(getInfo.SuccessParameterType, response =>
            {
                var props = response.GetType().GetProperties().Select(p => $"{p.Name}={p.GetValue(response)}");
                var fields = response.GetType().GetFields().Select(f => $"{f.Name}={f.GetValue(response)}");
                Debug.Log($"[DouyinCloudManager] 条件查询响应属性: {string.Join(", ", props.Concat(fields))}");
                var data = GetPropertyValue(response, "Data") ?? GetPropertyValue(response, "data")
                    ?? response.GetType().GetField("Data", BindingFlags.Instance | BindingFlags.Public)?.GetValue(response)
                    ?? response.GetType().GetField("data", BindingFlags.Instance | BindingFlags.Public)?.GetValue(response);
                Debug.Log($"[DouyinCloudManager] data 类型: {data?.GetType().FullName}, ToString: {data?.ToString()?.Substring(0, Mathf.Min(200, data?.ToString()?.Length ?? 0))}");
                tcs.SetResult(data?.ToString());
            });

            var onErrorDelegate = CreateDelegate(getInfo.ErrorParameterType, error =>
            {
                Debug.LogError($"[DouyinCloudManager] 条件查询失败：{GetPropertyValue(error, "StatusCode")}, {GetPropertyValue(error, "ErrMsg")}");
                tcs.SetResult(null);
            });

            object[] args;
            if (getInfo.RequiresQuery)
            {
                var queryArg = ConvertWhereCondition(getInfo.QueryParameterType, whereCondition);
                args = new object[] { queryArg, onSuccessDelegate, onErrorDelegate };
            }
            else
            {
                args = new object[] { onSuccessDelegate, onErrorDelegate };
            }

            getInfo.Method.Invoke(collectionObj, args);
            return await tcs.Task;
        }
        catch (Exception e)
        {
            Debug.LogError($"[DouyinCloudManager] 条件查询异常：{e.Message}");
            Debug.LogError($"[DouyinCloudManager] 异常堆栈：{e.StackTrace}");
            return null;
        }
    }

    private (MethodInfo Method, bool RequiresQuery, Type QueryParameterType, Type SuccessParameterType, Type ErrorParameterType) SelectGetMethod(Type queryType, bool needQuery)
    {
        var getMethods = queryType.GetMethods(BindingFlags.Instance | BindingFlags.Public)
            .Where(m => string.Equals(m.Name, "Get", StringComparison.OrdinalIgnoreCase))
            .ToArray();

        MethodInfo fallback = null;
        foreach (var method in getMethods)
        {
            var parameters = method.GetParameters();
            if (parameters.Length == 3 && IsCallbackParameter(parameters[1]) && IsCallbackParameter(parameters[2]))
            {
                if (!needQuery)
                {
                    return (method, false, null, parameters[1].ParameterType, parameters[2].ParameterType);
                }

                if (parameters[0].ParameterType == typeof(JsonData)
                    || parameters[0].ParameterType == typeof(string)
                    || parameters[0].ParameterType == typeof(object))
                {
                    return (method, true, parameters[0].ParameterType, parameters[1].ParameterType, parameters[2].ParameterType);
                }
            }
            else if (parameters.Length == 2 && IsCallbackParameter(parameters[0]) && IsCallbackParameter(parameters[1]))
            {
                fallback = method;
            }
        }

        if (fallback != null)
        {
            var parameters = fallback.GetParameters();
            return (fallback, false, null, parameters[0].ParameterType, parameters[1].ParameterType);
        }

        return (null, false, null, null, null);
    }

    private bool IsCallbackParameter(ParameterInfo parameter)
    {
        return typeof(Delegate).IsAssignableFrom(parameter.ParameterType);
    }

    private object ConvertWhereCondition(Type paramType, object condition)
    {
        if (condition == null)
            return null;

        if (paramType == typeof(JsonData))
        {
            if (condition is JsonData jd)
                return jd;
            if (condition is Dictionary<string, object> dict)
                return ToJsonData(dict);
            return new JsonData(condition.ToString());
        }

        if (paramType == typeof(string) && condition is JsonData jsonData)
        {
            return jsonData.ToJson();
        }

        if (paramType == typeof(string) && condition is Dictionary<string, object> dictAsString)
        {
            return ToJsonData(dictAsString).ToJson();
        }

        if (paramType == typeof(object) && condition is Dictionary<string, object> dictAsObject)
        {
            return ToJsonData(dictAsObject);
        }

        if (paramType.IsAssignableFrom(condition.GetType()))
        {
            return condition;
        }

        try
        {
            return Convert.ChangeType(condition, paramType);
        }
        catch
        {
            return condition;
        }
    }

    private Delegate CreateDelegate(Type delegateType, Action<object> callback)
    {
        var invokeMethod = delegateType.GetMethod("Invoke");
        var parameters = invokeMethod.GetParameters();
        if (parameters.Length != 1)
            throw new InvalidOperationException("仅支持单参数回调代理");

        var paramType = parameters[0].ParameterType;
        var param = Expression.Parameter(paramType, "arg");
        var callbackConst = Expression.Constant(callback);
        var convert = Expression.Convert(param, typeof(object));
        var call = Expression.Call(callbackConst, callback.GetType().GetMethod("Invoke"), convert);
        var lambda = Expression.Lambda(delegateType, call, param);
        return lambda.Compile();
    }

    private object GetPropertyValue(object obj, string property)
    {
        if (obj == null)
            return null;
        var prop = obj.GetType().GetProperty(property, BindingFlags.Instance | BindingFlags.Public);
        return prop?.GetValue(obj);
    }

    /// <summary>
    /// 聚合查询（支持排序、分组等复杂查询）
    /// </summary>
    public async Task<string> AggregateAsync(string collection, List<Dictionary<string, object>> pipeline, int limit = 50)
    {
        if (!IsCloudSupported())
        {
            Debug.LogWarning("[DouyinCloudManager] 云数据库不可用，跳过聚合查询");
            return null;
        }

        try
        {
            var tcs = new TaskCompletionSource<string>();

            Debug.Log($"[DouyinCloudManager] 聚合查询：{collection}");

            // 使用 Where 进行简单查询，不支持复杂的聚合管道
            // 如果需要排序，可以在查询后处理
            Cloud.CloudDb().GenDBCollection(envId, collection).Get(
                response =>
                {
                    Debug.Log($"[DouyinCloudManager] 聚合查询成功：{response.StatusCode}");
                    tcs.SetResult(response.Data.ToJson());
                },
                error =>
                {
                    Debug.LogError($"[DouyinCloudManager] 聚合查询失败：{error.StatusCode}, {error.ErrMsg}");
                    tcs.SetResult(null);
                });

            return await tcs.Task;
        }
        catch (Exception e)
        {
            Debug.LogError($"[DouyinCloudManager] 聚合查询异常：{e.Message}");
            return null;
        }
    }

    /// <summary>
    /// 添加文档
    /// </summary>
    public async Task<string> AddDocumentAsync(string collection, Dictionary<string, object> data)
    {
        if (!IsCloudSupported())
        {
            Debug.LogWarning("[DouyinCloudManager] 云数据库不可用，跳过添加");
            return null;
        }

        for (int attempt = 1; attempt <= MAX_RETRY_ATTEMPTS; attempt++)
        {
            try
            {
                var tcs = new TaskCompletionSource<string>();

                Debug.Log($"[DouyinCloudManager] 添加文档：{collection} (尝试 {attempt}/{MAX_RETRY_ATTEMPTS})");

                // 转换为 JsonData
                var jsonData = ToJsonData(data);

                Cloud.CloudDb().GenDBCollection(envId, collection).Add(
                    jsonData,
                    response =>
                    {
                        Debug.Log($"[DouyinCloudManager] 添加文档成功：{response.StatusCode}");
                        tcs.SetResult(response.Data.ToJson());
                    },
                    error =>
                    {
                        string errorMsg = GetDetailedErrorMessage(error.StatusCode, error.ErrMsg);
                        Debug.LogError($"[DouyinCloudManager] 添加文档失败：{error.StatusCode}, {error.ErrMsg}");
                        Debug.LogError($"[DouyinCloudManager] 详细错误信息：{errorMsg}");
                        tcs.SetResult(null);
                    });

                var result = await tcs.Task;
                if (result != null)
                {
                    return result; // 成功则返回
                }

                // 如果是最后一次尝试，抛出异常
                if (attempt == MAX_RETRY_ATTEMPTS)
                {
                    throw new Exception($"添加文档失败，已重试{MAX_RETRY_ATTEMPTS}次");
                }

                // 等待后重试
                await Task.Delay((int)(RETRY_DELAY * 1000 * attempt));
            }
            catch (Exception e)
            {
                Debug.LogError($"[DouyinCloudManager] 添加文档异常 (尝试 {attempt})：{e.Message}");
                if (attempt == MAX_RETRY_ATTEMPTS)
                {
                    return null;
                }
                await Task.Delay((int)(RETRY_DELAY * 1000 * attempt));
            }
        }

        return null;
    }

    /// <summary>
    /// 更新文档
    /// </summary>
    public async Task<string> UpdateDocumentAsync(string collection, string docId, Dictionary<string, object> data)
    {
        if (!IsCloudSupported())
        {
            Debug.LogWarning("[DouyinCloudManager] 云数据库不可用，跳过更新");
            return null;
        }

        try
        {
            var tcs = new TaskCompletionSource<string>();

            Debug.Log($"[DouyinCloudManager] 更新文档：{collection}/{docId}");

            // 转换为 JsonData (使用TTSDK的JsonData)
            var jsonData = ToJsonData(data);

            Cloud.CloudDb().GenDBCollection(envId, collection).Doc(docId).Update(
                jsonData,
                response =>
                {
                    Debug.Log($"[DouyinCloudManager] 更新文档成功：{response.StatusCode}");
                    tcs.SetResult(response.Data.ToJson());
                },
                error =>
                {
                    Debug.LogError($"[DouyinCloudManager] 更新文档失败：{error.StatusCode}, {error.ErrMsg}");
                    tcs.SetResult(null);
                });

            return await tcs.Task;
        }
        catch (Exception e)
        {
            Debug.LogError($"[DouyinCloudManager] 更新文档异常：{e.Message}");
            return null;
        }
    }

    /// <summary>
    /// 删除文档
    /// </summary>
    public async Task<string> DeleteDocumentAsync(string collection, string docId)
    {
        if (!IsCloudSupported())
        {
            Debug.LogWarning("[DouyinCloudManager] 云数据库不可用，跳过删除");
            return null;
        }

        try
        {
            var tcs = new TaskCompletionSource<string>();

            Debug.Log($"[DouyinCloudManager] 删除文档：{collection}/{docId}");

            Cloud.CloudDb().GenDBCollection(envId, collection).Doc(docId).Remove(
                response =>
                {
                    Debug.Log($"[DouyinCloudManager] 删除文档成功：{response.StatusCode}");
                    tcs.SetResult(response.Data.ToJson());
                },
                error =>
                {
                    Debug.LogError($"[DouyinCloudManager] 删除文档失败：{error.StatusCode}, {error.ErrMsg}");
                    tcs.SetResult(null);
                });

            return await tcs.Task;
        }
        catch (Exception e)
        {
            Debug.LogError($"[DouyinCloudManager] 删除文档异常：{e.Message}");
            return null;
        }
    }

    /// <summary>
    /// 通过云函数获取当前用户的 openId
    /// </summary>
    public async Task<string> GetOpenIdAsync()
    {
        if (!IsCloudSupported())
            return null;

        try
        {
            var tcs = new TaskCompletionSource<string>();
            var options = new DouyinCloud.Options
            {
                Method = "POST",
                Data = TTSDK.UNBridgeLib.LitJson.JsonMapper.ToObject("{}")
            };
            Cloud.CallContainer(
                envId, serviceId, "/get_open_id", options,
                (Action<DouyinCloud.Response>)(response =>
                {
                    Debug.Log($"[DouyinCloudManager] CallContainer 返回: {response.Data}");
                    try
                    {
                        var json = TTSDK.UNBridgeLib.LitJson.JsonMapper.ToObject(response.Data);
                        tcs.SetResult(json["data"]?.ToString());
                    }
                    catch { tcs.SetResult(null); }
                }),
                (Action<DouyinCloud.ErrorResponse>)(error =>
                {
                    Debug.LogError($"[DouyinCloudManager] CallContainer 失败: {error.ErrMsg}");
                    tcs.SetResult(null);
                })
            );

            return await tcs.Task;
        }
        catch (Exception e)
        {
            Debug.LogError($"[DouyinCloudManager] GetOpenIdAsync 异常: {e.Message}\n{e.StackTrace}");
            return null;
        }
    }

    #endregion
}

/// <summary>
/// 玩家数据结构（云数据库 game_progress 集合）
/// </summary>
[Serializable]
public class PlayerData
{
    public string _id; // 文档 ID
    public string _openid; // 抖音 openid
    public string user_id; // 用户唯一 ID（open_id）
    public string username; // 用户名
    public string avatar_url; // 头像 URL
    public int max_level; // 最大关卡
    public int busy_coins; // 忙币数量
    public string update_time; // 更新时间
}

/// <summary>
/// 抖音用户信息
/// </summary>
[Serializable]
public class DouyinUserInfo
{
    public string openId;
    public string nickName;
    public string avatarUrl;
}
