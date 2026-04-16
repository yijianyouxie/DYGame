using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;

/// <summary>
/// Attached to the main menu canvas. Displays player name/level and
/// responds to the start button.
/// </summary>
public class MainMenuController : MonoBehaviour
{
    [Header("UI References")]
    public Text playerNameText;
    public Text progressText;
    public Button startButton;
    
    [Header("Leaderboard")]
    public Button leaderboardButton;       // 排行榜按钮
    public LeaderboardUI leaderboardUI;   // 排行榜 UI 引用

    private LeaderboardManager leaderboardManager;

    private void Start()
    {
        // disable start until actual player data is ready
        startButton.interactable = false;

        // ensure sync manager exists and subscribes to user info ready events
        var syncManager = GameDataSyncManager.Instance;

        // subscribe to LeaderboardManager user info ready event
        leaderboardManager = LeaderboardManager.Instance;
        leaderboardManager.OnUserInfoReady += OnUserInfoReady;

        // refresh UI with any previously loaded game data
        playerNameText.text = GameData.PlayerName;
        progressText.text = $"第 {GameData.CurrentLevel} 关";

        if (!string.IsNullOrEmpty(GameData.PlayerName) && GameData.PlayerName != "Player")
        {
            startButton.interactable = true;
        }

        startButton.onClick.AddListener(OnStartClicked);

        // 绑定排行榜按钮事件
        if (leaderboardButton != null)
        {
            leaderboardButton.onClick.AddListener(OnLeaderboardClicked);
        }
    }

    private void OnUserInfoReady(PlayerData playerData)
    {
        if (playerData != null)
        {
            GameData.PlayerName = playerData.username;
            GameData.CurrentLevel = playerData.max_level;
        }

        playerNameText.text = GameData.PlayerName;
        progressText.text = $"第 {GameData.CurrentLevel} 关";
        startButton.interactable = true;
    }

    private void OnStartClicked()
    {
        // assume we have a scene for levels named "LevelScene"
        SceneManager.LoadScene("LevelScene");
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
            Debug.LogWarning("[MainMenuController] leaderboardUI 未赋值！");
        }
    }

    private void OnDestroy()
    {
        if (leaderboardManager != null)
        {
            leaderboardManager.OnUserInfoReady -= OnUserInfoReady;
        }
    }
}
