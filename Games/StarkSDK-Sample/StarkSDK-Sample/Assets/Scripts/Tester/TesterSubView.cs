using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class TesterSubView : MonoBehaviour
{
    public Button m_BackBtn;

    public Transform m_Content;

    private void Start()
    {
        m_BackBtn.onClick.AddListener(OnBackClick);

    }

    // Start is called before the first frame update
    public void ShowSubView(GameObject prefab)
    {
        bool alreadyCreated = false;
        for(int i=0;i<m_Content.childCount;i++)
        {
            var child = m_Content.GetChild(i);
            if (child.name.Equals(prefab.name))
            {
                alreadyCreated = true;
                child.gameObject.SetActive(true);
            }
            else
            {
                child.gameObject.SetActive(false);
            }
        }

        if (!alreadyCreated)
        {
            GameObject go = Instantiate(prefab);
            if (null != go)
            {
                go.transform.SetParent(m_Content.transform, false);
                go.transform.localPosition = Vector3.zero;
                go.name = prefab.name;
            }
        }
    }

    protected void OnBackClick()
    {
        gameObject.SetActive(false);
    }

}
