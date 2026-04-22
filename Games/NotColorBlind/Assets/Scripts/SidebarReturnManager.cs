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
    }

    private void OnClaimClicked()
    {
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
