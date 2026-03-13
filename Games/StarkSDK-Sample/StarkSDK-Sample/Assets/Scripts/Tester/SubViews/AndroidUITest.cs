using System;
using StarkSDKSpace;
using UnityEngine;
using UnityEngine.UI;

public class AndroidUITest : MonoBehaviour
{
    private readonly static string TAG = "AndroidUITest: ";
    private long m_ProcessStartShowTime = 0;
    private bool m_isLoading;

    void Start()
    {
        transform.Find("ScrollView/Viewport/Content/ShowToast")?.GetComponent<Button>().onClick.AddListener(OnShowToastTapped);
        transform.Find("ScrollView/Viewport/Content/ShowDialog")?.GetComponent<Button>().onClick.AddListener(OnShowDialogTapped);
        transform.Find("ScrollView/Viewport/Content/ShowProgress")?.GetComponent<Button>().onClick.AddListener(OnShowProgressTapped);
    }

    void Update() {
        if (m_ProcessStartShowTime > 0 ) {
            long diff = (DateTime.Now.Ticks - m_ProcessStartShowTime) / 10000;
            if (diff > 3000) {
                m_ProcessStartShowTime = 0;
                AndroidUIManager.HideProgressPopup();
            }
        }
    }

    private void OnShowToastTapped()
    {
        AndroidUIManager.ShowToast("显示吐司");
    }

    private void OnShowDialogTapped()
    {
        AndroidUIManager.ShowDialogPopup("标题", "内容", "Ok", "Cancel", true, 
        () => {
            Debug.Log(TAG + "Ok clicked");
            AndroidUIManager.ShowToast("Ok clicked");
        },
        () => {
            Debug.Log(TAG + "dialog dissmissed");
            AndroidUIManager.ShowToast("dialog dissmissed");
        });
    }

    private void OnShowProgressTapped()
    {
        m_ProcessStartShowTime = DateTime.Now.Ticks;
        string title = "Processing...";
        if (m_isLoading) {
            title = "Loading...";
        }
        m_isLoading = !m_isLoading;
        AndroidUIManager.ShowProgressPopup(title, true, () => {
            Debug.Log(TAG + " dismiss");
            m_ProcessStartShowTime = 0;
            AndroidUIManager.ShowToast("progress dismissed");
        });
    }
}
