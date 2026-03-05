using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;

/// <summary>
/// Displays the outcome of the completed level and lets player proceed.
/// </summary>
public class ResultController : MonoBehaviour
{
    public Text messageText;
    public Button nextButton;

    public static bool LastLevelSuccess;

    private void Start()
    {
        messageText.text = LastLevelSuccess ? "闯关成功！" : "闯关失败！";
        nextButton.onClick.AddListener(OnNextClicked);

        if (!LastLevelSuccess)
            nextButton.GetComponentInChildren<Text>().text = "重试";
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
