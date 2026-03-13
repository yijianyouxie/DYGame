using UnityEngine;
using UnityEngine.UI;
using StarkSDKSpace;

public class NavigateToVideoViewTest : MonoBehaviour
{
    private readonly static string TAG = "NaigateToVideoTest";
    private Text m_result;

    private void Start()
    {
        transform.Find("Feilds/Navigate")?.GetComponent<Button>().onClick.AddListener(delegate {
            string videoId = transform.Find("Feilds/Navigate_Content")?.GetComponent<InputField>().text;
            NavigateToVideoView(videoId);
        });

        transform.Find("Viewport1/Content/case1")?.GetComponent<Button>().onClick.AddListener(delegate {
            NavigateToVideoView("13104110592c463656561746007f436d56542b42017246605e5d444c0f7e446c5e5d4145087f");
        });
        transform.Find("Viewport1/Content/case2")?.GetComponent<Button>().onClick.AddListener(delegate {
            NavigateToVideoView("");
        });
        transform.Find("Viewport1/Content/case3")?.GetComponent<Button>().onClick.AddListener(delegate {
            NavigateToVideoView(null);
        });
        transform.Find("Viewport1/Content/case4")?.GetComponent<Button>().onClick.AddListener(delegate {
            NavigateToVideoView("0");
        });
        m_result = transform.Find("Viewport2/Content/ResultMsg")?.GetComponent<Text>();

    }

    private void NavigateToVideoView(string videoId)
    {
        Debug.Log("NavigateToVideoView: videoId -- " + videoId);
        StarkSDK.API.NavigateToVideoView(videoId,
           success =>
           {
               m_result.text = "NavigateToVideoView: issuccess  " + success;
           });
    }
}