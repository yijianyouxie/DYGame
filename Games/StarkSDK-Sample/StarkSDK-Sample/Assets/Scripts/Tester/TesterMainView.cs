using System;
using System.Collections;
using System.Collections.Generic;
using StarkSDKSpace;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.UI;

namespace Tester
{
    public partial class TesterMainView : MonoBehaviour
    {
        public GameObject TestItemButtonPrefab;
        public Transform m_Content;
        public TesterSubView m_SubView;
        public Text m_LogMessage;
        public Text m_EnvMessage;
        public PerfomanceStats m_PerformanceWidget;
        public SimpleSubview m_SimpleSubview;

        protected string m_Message;

        private static int s_BtnCount = 0;

        // Start is called before the first frame update
        void Start()
        {
            StarkSDK.API.SetContainerInitCallback(OnStarkContainerInitCallback);
            //StarkSDK.Init();

            m_SubView.gameObject.SetActive(false);
            m_SimpleSubview.gameObject.SetActive(false);

            InitCases();

            StarkSDK.API.RegisterCommandEvent(OnCommand);

            if(CanIUse.GamePublishVersion)
                PrintText("Versions: SDK {0}, Game {1}  Publish {2} ", StarkSDK.API.SDKVersion, StarkSDK.API.GameVersion, StarkSDK.API.GamePublishVersion);
            else
                PrintText("Versions: SDK {0}, Game {1}", StarkSDK.API.SDKVersion, StarkSDK.API.GameVersion);
        }

        private void Update()
        {
            if (m_SubView.gameObject.activeSelf)
            {
                gameObject.transform.localScale = Vector3.zero;
            }
            else
            {
                gameObject.transform.localScale = Vector3.one;
            }
            if (Input.GetKeyDown(KeyCode.Escape))
            {
                PrintText("Press again to exit");
            }
        }

        void OnStarkContainerInitCallback(ContainerEnv env)
        {
            m_EnvMessage.text = env.m_HostEnum.ToString() + "    " + env.m_LaunchFromEnum.ToString();
        }

        /// <summary>
        /// Add a test case button to the main view, pass in the click callback to handle the case
        /// </summary>
        /// <param name="btnName"></param>
        /// <param name="onClick"></param>
        void AddTestCase(string btnName, UnityAction onClick)
        {
            GameObject btn = Instantiate(TestItemButtonPrefab);
            btn.transform.SetParent(m_Content, false);
            btn.transform.position = Vector3.zero;
            Text btnTxt = btn.GetComponentInChildren<Text>();
            if (null != btnTxt)
            {
                btnTxt.text = string.Format("{0}.{1}", ++s_BtnCount, btnName);
            }

            Button bItem = btn.GetComponent<Button>();
            if (null != bItem && null != onClick)
            {
                bItem.onClick.AddListener(onClick);
            }
        }

        protected void AddTestCaseInSubview(string btnName, Dictionary<string, UnityAction> cases)
        {
            GameObject btn = Instantiate(TestItemButtonPrefab);
            btn.transform.SetParent(m_Content, false);
            btn.transform.position = Vector3.zero;
            Text btnTxt = btn.GetComponentInChildren<Text>();
            if (null != btnTxt)
            {
                btnTxt.text = string.Format("{0}.{1}", ++s_BtnCount, btnName);
            }

            Button bItem = btn.GetComponent<Button>();
            if (null != bItem)
            {
                bItem.onClick.AddListener(()=> {
                    OpenSimpleSubview(btnName, cases);
                });
            }
        }

        protected void OpenSimpleSubview(string name, Dictionary<string, UnityAction> cases)
        {
            m_SimpleSubview.ClearAllCases();
            m_SimpleSubview.gameObject.SetActive(true);
            m_SimpleSubview.SetTitle(name);

            foreach(var oneCase in cases)
            {
                m_SimpleSubview.AddTestCase(oneCase.Key, oneCase.Value);
            }
        }

        /// <summary>
        /// Open a detailed case view on top of the MainView.
        /// The opened view should be stored under "Assets/Resources/Prefab/Tester/SubViews/" folder
        /// </summary>
        /// <param name="prefabName"></param>
        protected void OpenCaseView(string prefabName)
        {

            GameObject prefab = Resources.Load<GameObject>("Prefab/Tester/SubViews/" + prefabName);
            if (null != prefab)
            {
                m_SubView.ShowSubView(prefab);
                m_SubView.gameObject.SetActive(true);
            }
        }

        

        /// <summary>
        /// Print text on the mainview
        /// </summary>
        /// <param name="msg"></param>
        protected void PrintText(string msg, params object[] args)
        {
            try
            {
                string formated = string.Format(msg, args);
                m_Message = formated;
            }
            catch (Exception e)
            {
                m_Message = msg;
            }
            Debug.Log(m_Message);
            m_LogMessage.text = m_Message;
        }

        /// <summary>
        /// Append a message to the end of text on the main view
        /// </summary>
        /// <param name="msg"></param>
        protected void PrintTextAppended(string msg, params object[] args)
        {
            try
            {
                string formated = string.Format(msg, args);
                m_Message = string.Format("{0}\n{1}", m_Message, formated);
            }
            catch (Exception e)
            {
                m_Message = string.Format("{0}\n{1}", m_Message, msg);
            }
            m_LogMessage.text = m_Message;
            Debug.Log(m_Message);
        }

        private void OnCommand(string cmd, IList<string> paramLst)
        {
            Debug.Log("Custom command: " + cmd + ", params: " + paramLst.Count);
        }
    }
}