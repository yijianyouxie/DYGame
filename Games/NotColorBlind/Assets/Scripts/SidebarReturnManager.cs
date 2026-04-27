using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TTSDK;
using JsonData = TTSDK.UNBridgeLib.LitJson.JsonData;

public class SidebarReturnManager : MonoBehaviour
{
    public Button claimButton;
    public GameObject sidebarPanel;   // 侧边栏引导面板
    public Button closeButton;         // 面板上的关闭/跳转按钮X

    private void Start()
    {
        // 面板默认隐藏
        if (sidebarPanel != null)
            sidebarPanel.SetActive(false);

        if (claimButton != null)
            claimButton.onClick.AddListener(OnClaimClicked);

        if (closeButton != null)
            closeButton.onClick.AddListener(OnCloseButtonClicked);

        TT.GetAppLifeCycle().OnShow += OnAppShow;
    }

    private void OnDestroy()
    {
        TT.GetAppLifeCycle().OnShow -= OnAppShow;
    }

    private bool _fromSidebar;

    private void OnAppShow(Dictionary<string, object> param)
    {
        object scene = null;
        param?.TryGetValue("scene", out scene);
        var sceneStr = scene?.ToString();
        Debug.Log($"[Sidebar] OnShow scene={sceneStr}");
        _fromSidebar = sceneStr == "021036";
        if (_fromSidebar)
            Debug.Log("[Sidebar] 从侧边栏返回游戏，可以领奖");
    }

    private void OnClaimClicked()
    {
        if (_fromSidebar)
        {
            // 从侧边栏进入 → 直接发10个busyCoin
            GameData.BusyCoinCount += 10;
            Debug.Log($"[Sidebar] 已从侧边栏进入，领奖成功！当前BusyCoin: {GameData.BusyCoinCount}");
            return;
        }

        // 不是从侧边栏进入 → 检查侧边栏是否可用
        TT.CheckScene(TTSideBar.SceneEnum.SideBar,
            supported =>
            {
                if (supported)
                {
                    // 侧边栏可用但不是从侧边栏进入 → 弹出引导面板
                    Debug.Log("[Sidebar] 侧边栏可用，弹出引导面板");
                    ShowSidebarPanel();
                }
                else
                {
                    Debug.Log("[Sidebar] 当前版本不支持侧边栏");
                }
            },
            null,
            (code, msg) => Debug.LogWarning($"[Sidebar] CheckScene error {code}: {msg}"));
    }

    /// <summary>
    /// 显示侧边栏引导面板
    /// </summary>
    private void ShowSidebarPanel()
    {
        if (sidebarPanel != null)
            sidebarPanel.SetActive(true);
    }

    /// <summary>
    /// 关闭按钮X点击 → 跳转到侧边栏 + 关闭面板
    /// </summary>
    private void OnCloseButtonClicked()
    {
        // 关闭面板
        if (sidebarPanel != null)
            sidebarPanel.SetActive(false);

        // 跳转到侧边栏
        NavigateToSidebar();
    }

    private void NavigateToSidebar()
    {
        var data = new JsonData();
        data["scene"] = "sidebar";
        TT.NavigateToScene(data,
            () => Debug.Log("[Sidebar] 跳转成功"),
            null,
            (code, msg) => Debug.LogWarning($"[Sidebar] NavigateToScene error {code}: {msg}"));
    }
}
