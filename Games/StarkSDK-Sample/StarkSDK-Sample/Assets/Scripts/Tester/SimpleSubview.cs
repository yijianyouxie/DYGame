using UnityEngine;
using UnityEngine.Events;
using UnityEngine.UI;

public class SimpleSubview : MonoBehaviour
{
    public GameObject TestItemButtonPrefab;
    public Transform m_Content;
    public Button m_BackBtn;

    public Text m_Title;

    private void Start()
    {
        m_BackBtn.onClick.AddListener(OnBackClick);

    }

    protected void OnBackClick()
    {
        gameObject.SetActive(false);
    }

    public void ClearAllCases()
    {
        foreach (Transform child in m_Content.transform)
        {
            GameObject.Destroy(child.gameObject);
        }
    }

    public void SetTitle(string name)
    {
        m_Title.text = name;
    }

    /// <summary>
    /// Add a test case button to the main view, pass in the click callback to handle the case
    /// </summary>
    /// <param name="btnName"></param>
    /// <param name="onClick"></param>
    public void AddTestCase(string btnName, UnityAction onClick)
    {
        GameObject btn = Instantiate(TestItemButtonPrefab);
        btn.transform.SetParent(m_Content, false);
        btn.transform.position = Vector3.zero;
        Text btnTxt = btn.GetComponentInChildren<Text>();
        if (null != btnTxt)
        {
            btnTxt.text = btnName;
        }

        Button bItem = btn.GetComponent<Button>();
        if (null != bItem && null != onClick)
        {
            bItem.onClick.AddListener(onClick);
        }
    }
}
