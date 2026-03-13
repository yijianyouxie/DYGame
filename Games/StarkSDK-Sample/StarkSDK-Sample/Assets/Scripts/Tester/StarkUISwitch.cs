using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class StarkUISwitch : MonoBehaviour
{
    public GameObject m_UIPanel;
    private bool m_IsOpen = true;
    private Button m_SwitchButton;
    private Text m_SwitchText;
    public static StarkUISwitch Instance { get; private set; }

    private void Awake()
    {
        Instance = this;
    }

    void Start()
    {
        m_SwitchButton = GetComponent<Button>();
        m_SwitchText = m_SwitchButton.GetComponentInChildren<Text>();
        m_SwitchButton.onClick.AddListener(OnSwitchButtonClicked);
    }

    private void Update()
    {
        if (m_IsOpen)
        {
            m_UIPanel.transform.localScale = Vector3.one;
        }
        else
        {
            m_UIPanel.transform.localScale = Vector3.zero;
        }
        if (m_IsOpen)
        {
            m_SwitchText.text = "Close";
        }
        else
        {
            m_SwitchText.text = "Open";
        }
    }

    private void OnSwitchButtonClicked()
    {
        m_IsOpen = !m_IsOpen;
    }

    public void Open()
    {
        m_IsOpen = true;
    }

    public void Close()
    {
        m_IsOpen = false;
    }
}
