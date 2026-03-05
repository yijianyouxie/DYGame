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

    private void Start()
    {
        // disable start until data is loaded
        startButton.interactable = false;
        GameData.LoadFromServer(OnDataLoaded);

        startButton.onClick.AddListener(OnStartClicked);
    }

    private void OnDataLoaded()
    {
        playerNameText.text = GameData.PlayerName;
        progressText.text = $"第 {GameData.CurrentLevel} 关";
        startButton.interactable = true;
    }

    private void OnStartClicked()
    {
        // assume we have a scene for levels named "LevelScene"
        SceneManager.LoadScene("LevelScene");
    }
}
