using UnityEngine;
using UnityEngine.UI;
using System.Collections.Generic;
using System.Threading.Tasks;

/// <summary>
/// 排行榜 UI 控制器
/// </summary>
public class LeaderboardUI : MonoBehaviour
{
    [Header("UI 组件引用")]
    public RectTransform panelRoot;          // 排行榜面板根节点
    public Button closeButton;               // 关闭按钮
    public Transform contentParent;          // 内容容器（放置排名项）
    public GameObject rankItemPrefab;        // 排名项预制件
    
    [Header("前三名特殊标识")]
    public Image crownImage;                 // 皇冠图标（可选）
    
    [Header("颜色配置")]
    public Color goldColor = new Color(1f, 0.843f, 0f);      // 金色
    public Color silverColor = new Color(0.753f, 0.753f, 0.753f); // 银色
    public Color bronzeColor = new Color(0.804f, 0.498f, 0.196f); // 铜色
    public Color normalColor = Color.white;                   // 普通颜色
    
    private List<GameObject> rankItems = new List<GameObject>();
    
    void Start()
    {
        // 初始隐藏面板
        if (panelRoot != null)
        {
            panelRoot.gameObject.SetActive(false);
        }
        
        // 绑定关闭按钮事件
        if (closeButton != null)
        {
            closeButton.onClick.AddListener(OnCloseClicked);
        }
    }
    
    /// <summary>
    /// 显示排行榜界面
    /// </summary>
    public async void ShowLeaderboard()
    {
        if (panelRoot == null)
        {
            Debug.LogError("[LeaderboardUI] panelRoot 未赋值！");
            return;
        }

        panelRoot.gameObject.SetActive(true);

        // 确保关闭按钮事件已绑定
        if (closeButton != null)
        {
            closeButton.onClick.RemoveAllListeners();
            closeButton.onClick.AddListener(OnCloseClicked);
        }

        // 清空现有项
        ClearRankItems();

        // 显示加载提示
        Debug.Log("[LeaderboardUI] 正在加载排行榜数据...");

        // 获取排行榜数据
        var records = await LeaderboardManager.Instance.GetLeaderboardAsync();

        // 填充排行榜
        FillLeaderboard(records);
    }
    
    /// <summary>
    /// 清空所有排名项
    /// </summary>
    private void ClearRankItems()
    {
        foreach (var item in rankItems)
        {
            Destroy(item);
        }
        rankItems.Clear();
    }
    
    /// <summary>
    /// 填充排行榜数据
    /// </summary>
    private void FillLeaderboard(List<LeaderboardRecord> records)
    {
        if (contentParent == null)
        {
            Debug.LogError("[LeaderboardUI] contentParent 未赋值！");
            return;
        }

        if (rankItemPrefab == null)
        {
            Debug.LogError("[LeaderboardUI] rankItemPrefab 未赋值！请创建预制件");
            return;
        }

        // 只显示前 50 名
        int displayCount = Mathf.Min(records.Count, 50);

        for (int i = 0; i < displayCount; i++)
        {
            CreateRankItem(records[i], i + 1);
        }

        // 强制刷新布局
        if (contentParent is RectTransform rectTransform)
        {
            LayoutRebuilder.ForceRebuildLayoutImmediate(rectTransform);
        }

        Debug.Log($"[LeaderboardUI] 已加载 {displayCount} 条排行榜数据");
    }
    
    /// <summary>
    /// 创建单个排名项
    /// </summary>
    private void CreateRankItem(LeaderboardRecord record, int rank)
    {
        if (rankItemPrefab == null || contentParent == null) return;

        // 先实例化不带父对象，避免 persistent 父对象问题
        GameObject newItem = Instantiate(rankItemPrefab);
        
        // 然后再设置父对象
        newItem.transform.SetParent(contentParent, false);
        
        rankItems.Add(newItem);
        
        // 获取子组件
        Text rankText = newItem.GetComponentInChildren<Text>(true);
        Text nameText = null;
        Text levelText = null;
        Image avatarImage = null;
        Image background = null;
        
        // 查找子组件（根据实际 UI 结构调整）
        Transform[] children = newItem.GetComponentsInChildren<Transform>();
        foreach (Transform child in children)
        {
            if (child.name == "RankText" && rankText == null)
                rankText = child.GetComponent<Text>();
            else if (child.name == "NameText")
                nameText = child.GetComponent<Text>();
            else if (child.name == "LevelText")
                levelText = child.GetComponent<Text>();
            else if (child.name == "AvatarImage")
                avatarImage = child.GetComponent<Image>();
            else if (child.name == "Background")
                background = child.GetComponent<Image>();
        }
        
        // 填充数据
        if (rankText != null)
        {
            rankText.text = rank.ToString();
            
            // 前三名特殊样式
            if (rank <= 3)
            {
                SetRankStyle(rankText, rank);
            }
        }
        
        if (nameText != null)
        {
            nameText.text = record.username;
            
            // 前三名名字也特殊颜色
            if (rank <= 3)
            {
                Color rankColor = rank == 1 ? goldColor : 
                                 rank == 2 ? silverColor : bronzeColor;
                nameText.color = rankColor;
            }
        }
        
        if (levelText != null)
        {
            levelText.text = $"第{record.max_level}关";
        }
        
        // 设置头像（如果有）
        if (avatarImage != null && !string.IsNullOrEmpty(record.avatar_url))
        {
            // TODO: 加载网络图片
            // LoadAvatar(avatarImage, record.avatar_url);
        }
        
        // 设置背景颜色（当前玩家高亮）
        if (background != null && record.user_id == LeaderboardManager.Instance.CurrentUserId)
        {
            background.color = new Color(0.8f, 1f, 0.8f, 0.3f); // 浅绿色背景
        }
    }
    
    /// <summary>
    /// 设置前三名的特殊样式
    /// </summary>
    private void SetRankStyle(Text rankText, int rank)
    {
        Color rankColor = rank == 1 ? goldColor : 
                         rank == 2 ? silverColor : bronzeColor;
        
        rankText.color = rankColor;
        rankText.fontSize = 24; // 增大字号
        rankText.fontStyle = FontStyle.Bold; // 加粗
        
        // 可以在这里添加更多特效，比如图标、光晕等
    }
    
    /// <summary>
    /// 关闭按钮点击事件
    /// </summary>
    private void OnCloseClicked()
    {
        if (panelRoot != null)
        {
            panelRoot.gameObject.SetActive(false);
        }
    }
    
    /// <summary>
    /// 加载网络头像（预留实现）
    /// </summary>
    private void LoadAvatar(Image image, string url)
    {
        // TODO: 使用 UnityWebRequest 下载并设置头像
        Debug.Log($"[LeaderboardUI] 加载头像：{url}");
    }
}
