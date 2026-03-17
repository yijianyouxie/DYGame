using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// 排行榜单项 UI 组件
/// </summary>
public class LeaderboardRankItem : MonoBehaviour
{
    [Header("UI 组件")]
    public Text rankText;      // 排名文本
    public Text nameText;      // 用户名
    public Text levelText;     // 关卡数
    public Image avatarImage;  // 头像
    public Image background;   // 背景
    
    [Header("前三名标识")]
    public GameObject crownPrefab;  // 皇冠预制件（可选）
    
    /// <summary>
    /// 设置排名项数据
    /// </summary>
    public void SetData(LeaderboardRecord record, int rank, bool isCurrentPlayer)
    {
        if (rankText != null)
        {
            rankText.text = rank.ToString();
            
            // 前三名特殊样式
            if (rank <= 3)
            {
                SetRankStyle(rank);
            }
        }
        
        if (nameText != null)
        {
            nameText.text = record.username;
        }
        
        if (levelText != null)
        {
            levelText.text = $"第{record.max_level}关";
        }
        
        // 当前玩家高亮背景
        if (background != null && isCurrentPlayer)
        {
            background.color = new Color(0.8f, 1f, 0.8f, 0.3f);
        }
    }
    
    /// <summary>
    /// 设置前三名特殊样式
    /// </summary>
    private void SetRankStyle(int rank)
    {
        Color rankColor = rank == 1 ? new Color(1f, 0.843f, 0f) :    // 金色
                         rank == 2 ? new Color(0.753f, 0.753f, 0.753f) : // 银色
                                    new Color(0.804f, 0.498f, 0.196f);    // 铜色
        
        if (rankText != null)
        {
            rankText.color = rankColor;
            rankText.fontSize = 24;
            rankText.fontStyle = FontStyle.Bold;
        }
        
        // 添加皇冠图标（如果有）
        if (crownPrefab != null && rank == 1)
        {
            GameObject crown = Instantiate(crownPrefab, transform);
            // 设置皇冠位置...
        }
    }
}
