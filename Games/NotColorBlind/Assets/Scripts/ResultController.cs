using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;
using Debug = UnityEngine.Debug;

/// <summary>
/// Displays the outcome of the completed level and lets player proceed.
/// </summary>
public class ResultController : MonoBehaviour
{
    public Text messageText;
    public Button nextButton;
    public Button returnButton;  // 返回按钮
    [Header("Leaderboard")]
    public Button leaderboardButton;       // 排行榜按钮
    public LeaderboardUI leaderboardUI;    // 排行榜 UI 引用

    public static bool LastLevelSuccess;

    private void Start()
    {
        messageText.text = LastLevelSuccess ? "闯关成功！" : "闯关失败！";
        nextButton.onClick.AddListener(OnNextClicked);

        if (!LastLevelSuccess)
            nextButton.GetComponentInChildren<Text>().text = "重试";
        
        // 绑定排行榜按钮事件
        if (leaderboardButton != null)
        {
            leaderboardButton.onClick.AddListener(OnLeaderboardClicked);
        }
        
        // 绑定返回按钮事件
        if (returnButton != null)
        {
            returnButton.onClick.AddListener(OnReturnClicked);
        }
    }
    
    /// <summary>
    /// 排行榜按钮点击事件
    /// </summary>
    private void OnLeaderboardClicked()
    {
        if (leaderboardUI != null)
        {
            leaderboardUI.ShowLeaderboard();
        }
        else
        {
            Debug.LogWarning("[ResultController] leaderboardUI 未赋值！");
        }
    }
    
    /// <summary>
    /// 返回按钮点击事件
    /// </summary>
    private void OnReturnClicked()
    {
        SceneManager.LoadScene("Start");
    }

    private void OnNextClicked()
    {
        if (LastLevelSuccess)
        {
            GameData.CurrentLevel = Mathf.Min(GameData.CurrentLevel + 1, GameData.MaxLevels);
        }

        SceneManager.LoadScene("LevelScene");
    }
}
