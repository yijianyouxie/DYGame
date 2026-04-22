using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using TTSDK;
using JsonData = TTSDK.UNBridgeLib.LitJson.JsonData;

public class SidebarReturnManager : MonoBehaviour
{
    public Button claimButton;

    private void Start()
    {
        if (claimButton != null)
            claimButton.onClick.AddListener(OnClaimClicked);

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
            Debug.Log("[Sidebar] 已从侧边栏进入，领奖成功");
            return;
        }
        TT.CheckScene(TTSideBar.SceneEnum.SideBar,
            supported =>
            {
                if (supported)
                    NavigateToSidebar();
                else
                    Debug.Log("[Sidebar] 当前版本不支持侧边栏");
            },
            null,
            (code, msg) => Debug.LogWarning($"[Sidebar] CheckScene error {code}: {msg}"));
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
