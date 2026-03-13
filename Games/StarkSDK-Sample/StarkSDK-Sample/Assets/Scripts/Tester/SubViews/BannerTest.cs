using System;
using System.Collections.Generic;
using System.Security.Cryptography;
using System.Text;
using StarkSDKSpace.UNBridgeLib.LitJson;
using UnityEngine;
using UnityEngine.UI;

namespace StarkSDKSpace
{

    public class BannerTest : MonoBehaviour
    {
        private readonly static string TAG = "BannerTest";

        private StarkAdManager.BannerAd m_bannerAdIns = null;
        StarkAdManager.BannerStyle m_style = new StarkAdManager.BannerStyle();
        private InputField m_width;
        private Text m_heiht;
        private InputField m_top;
        private InputField m_left;
  
        private Text m_result;
        private void Awake()
        {

        }

        private void Start()
        {
            m_width = transform.Find("Feilds/Width")?.GetComponent<InputField>();
            m_heiht = transform.Find("Feilds/Height")?.GetComponent<Text>();
            m_top = transform.Find("Feilds/Top")?.GetComponent<InputField>();
            m_left = transform.Find("Feilds/Left")?.GetComponent<InputField>();
            
     
            transform.Find("Viewport1/Content/Create")?.GetComponent<Button>().onClick.AddListener(Create_ShowBannerAd);
            transform.Find("Viewport1/Content/Show")?.GetComponent<Button>().onClick.AddListener(ShowBannerAd);
            transform.Find("Viewport1/Content/Hide")?.GetComponent<Button>().onClick.AddListener(HideBannerAd);
            transform.Find("Viewport1/Content/Destroy")?.GetComponent<Button>().onClick.AddListener(DestroyBannerAd);       
            transform.Find("Viewport1/Content/ButtomCenter")?.GetComponent<Button>().onClick.AddListener(ToButtomCenter);
            transform.Find("Viewport1/Content/Modify")?.GetComponent<Button>().onClick.AddListener(ResizeBannerAd);
            m_result = transform.Find("Viewport2/Content/ResultMsg")?.GetComponent<Text>();


        }
        void ShowPosition()
        {
            m_result.text = $"width: {m_style.width} height: {m_style.height} top: {m_style.top} left: {m_style.left}";
        }
        

        public void Create_ShowBannerAd()
        {
            var bannerAdId = Tester.Common.GetBannerAdId();
            if(bannerAdId == ""){
                m_result.text = "请在TesterCases配置BannerAdId";
                return;
            } 
            m_style.top = 10;
            m_style.left = 10;
            m_style.width = 320;
            if (m_bannerAdIns == null)
            {
               
                m_bannerAdIns = StarkSDK.API.GetStarkAdManager().CreateBannerAd(bannerAdId, m_style, 60,
                    OnAdError, OnBannerLoaded, OnBannerResize);
            }
            else if (m_bannerAdIns.IsInvalid())
            {
                m_bannerAdIns.Destory();
                m_bannerAdIns = StarkSDK.API.GetStarkAdManager().CreateBannerAd(bannerAdId, m_style, 60,
                   OnAdError, OnBannerLoaded, OnBannerResize);
            }
            else
            {
                m_bannerAdIns.Show();
            }
        }
        void OnAdError(int iErrCode, string errMsg)
        {
            Debug.LogError(TAG + "错误 ： " + iErrCode + "  " + errMsg);
        }
        void ShowBannerAd()
        {
            if (m_bannerAdIns != null)
                m_bannerAdIns.Show();
        }

        public void HideBannerAd()
        {
            if (m_bannerAdIns != null)
                m_bannerAdIns.Hide();
        }

        void DestroyBannerAd()
        {
            if (m_bannerAdIns != null)
            {
                m_bannerAdIns.Destory();
                m_bannerAdIns = null;
            }
        }
        private int px2dp(int px) => (int)(px * (160 / Screen.dpi));

        public void ResizeBannerAd()
        {
            m_style.top = int.Parse(m_top.text);
            m_style.left = int.Parse(m_left.text);
            m_style.width = int.Parse(m_width.text);
            if (m_bannerAdIns != null)
            {             
                m_bannerAdIns.ReSize(m_style);
            }

        }
        public void ToButtomCenter()
        {
            int w = m_style.width;
            int h = m_style.height;
            int sw = px2dp(Screen.width);
            int sh = px2dp(Screen.height);

            m_style.top = sh - h;
            m_style.left = sw / 2 - w / 2;

            if (m_bannerAdIns != null)
                m_bannerAdIns.ReSize(m_style);


        }
        void OnBannerLoaded()
        {
                
            if (m_bannerAdIns != null)
                m_bannerAdIns.Show();
        }

        void OnBannerResize(int width, int height)
        {
            Debug.Log($"OnBannerResize - width:{width} height:{height}");
        }

   
        private void Update()
        {           
            ShowPosition();
        }

    }


}