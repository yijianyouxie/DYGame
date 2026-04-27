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

    [Header("忙币按钮")]
    public Button btnMoney;           // Btn_Money按钮（点击无响应）
    public Text textMoney;            // Text_Money 忙币数量文字

    private int _lastDisplayedCoin = -1;  // 上次显示的忙币值，用于检测变化

    private void Start()
    {
        // 面板默认隐藏
        if (sidebarPanel != null)
            sidebarPanel.SetActive(false);

        if (claimButton != null)
            claimButton.onClick.AddListener(OnClaimClicked);

        if (closeButton != null)
            closeButton.onClick.AddListener(OnCloseButtonClicked);

        // Btn_Money 显示正常但不响应点击 - 移除所有点击监听器
        if (btnMoney != null)
            btnMoney.onClick.RemoveAllListeners();

        // 同步初始忙币数量
        SyncBusyCoinUI();

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
            // 从侧边栏进入 → 直接发5个busyCoin并同步到数据库
            GameDataSyncManager.Instance.AddCoins(5);
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

    private void Update()
    {
        // 每帧检测忙币数量变化并同步UI
        SyncBusyCoinUI();
    }

    /// <summary>
    /// 同步忙币数量到Text_Money，变化时触发缩放动画
    /// </summary>
    private void SyncBusyCoinUI()
    {
        if (textMoney == null) return;

        int currentCoin = GameData.BusyCoinCount;
        if (currentCoin != _lastDisplayedCoin)
        {
            textMoney.text = currentCoin.ToString();

            // 忙币增加时播放放大缩小缓动动画
            if (btnMoney != null && _lastDisplayedCoin >= 0 && currentCoin > _lastDisplayedCoin)
            {
                StartCoroutine(PulseAnimation());
            }

            _lastDisplayedCoin = currentCoin;
        }
    }

    /// <summary>
    /// 放大缩小缓动效果
    /// </summary>
    private System.Collections.IEnumerator PulseAnimation()
    {
        float duration = 0.4f;
        float halfTime = duration * 0.5f;
        Vector3 originalScale = Vector3.one;
        float elapsed = 0f;

        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            float t = elapsed / duration;

            // 前半段放大，后半段缩小回原大小（使用smoothStep平滑）
            float scale;
            if (t <= 0.5f)
                scale = 1f + Mathf.SmoothStep(0f, 1f, t / 0.5f) * 0.25f; // 放大到1.25倍
            else
                scale = 1.25f - Mathf.SmoothStep(0f, 1f, (t - 0.5f) / 0.5f) * 0.25f; // 缩小回1倍

            btnMoney.transform.localScale = new Vector3(scale, scale, scale);
            yield return null;
        }

        btnMoney.transform.localScale = originalScale;
    }
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
