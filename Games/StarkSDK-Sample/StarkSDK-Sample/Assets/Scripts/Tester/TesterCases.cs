using System;
using UnityEngine;
using StarkSDKSpace;
using System.Collections;
using System.Collections.Generic;
using UnityEngine.Events;
using System.Text;
using StarkSDKSpace.UNBridgeLib.LitJson;
using System.IO;

namespace Tester
{
    public partial class TesterMainView : MonoBehaviour
    {
        public static string Code = "";
        public static string AnonymousCode = "";
        private ExampleCube _exampleCube;

        // Use this for initialization
        protected void InitCases()
        {
            if (Application.isEditor)
                MockSetting.OpenAllMockModule();


            RealNameAuthentication();
            AddTestCase("录屏功能", GameRecorderTestCase);
            AddTestCaseInSubview("关注抖音号", new Dictionary<string, UnityAction>
            {
                {"关注抖音账号", FollowAweme},
                {"是否已绑定抖音", HasBoundAweme}
            });
            AddTestCaseInSubview("快捷方式", new Dictionary<string, UnityAction>
            {
                {"创建快捷方式", CreateShortcut},
                {"是否存在快捷方式", IsShortcutExist}
            });
            AddTestCase("Android UI测试", AndroidUITest);
            AddTestCase("测试手机震动", TestVibrate);

            AddTestCaseInSubview("收藏", new Dictionary<string, UnityAction>
            {
                {
                    "收藏", () => { TestGameFavour(true); }
                },
                {
                    "取消收藏", () => { TestGameFavour(false); }
                },
                {"收藏引导TopBar", TestFavoriteGuideTopBar},
                {"收藏引导BottomBar", TestFavoriteGuideBottomBar},
                {"收藏引导Tip", TestFavoriteGuideTip},
                {"是否已收藏", TestIsGameFavorite},
            });

            AddTestCaseInSubview("激励视频", new Dictionary<string, UnityAction>
            {
                {"激励视频播放", ShowExcitingVideo1}
            });
            
            AddTestCase("banner广告", BannerTestCase);

            AddTestCaseInSubview("插屏广告", new Dictionary<string, UnityAction>
            {
                {"创建插屏广告", CreateInterstitialAd},
                {"加载插屏广告", LoadInterstitialAd},
                {"显示插屏广告", ShowInterstitialAd},
                {"销毁插屏广告", DestoryInterstitialAd},
            });

            AddTestCaseInSubview("登录", new Dictionary<string, UnityAction>
            {
                {"登录-force", TestForceLogin},
                {"登录-noforce", TestNoForceLogin},
                {"检查Session", TestCheckSession},
                {"获取登录信息", TestGetUserInfo},
                {"检测是否已经授权", TestGetUserInfoAuth},
                {"打开授权界面", TestOpenSettingPanel}
            });

            AddTestCase("打印当前环境", TestEnv);
            AddTestCase("支付测试", TestPay);

            AddTestCase("埋点上报测试", ReportTest);

            AddTestCaseInSubview("共享文件测试", new Dictionary<string, UnityAction>
            {
                {"删除随机链接", MP_DeleteFile},
                {"删除随机源文件", MP_DeleteSharedFile},
                {"随机修改文件链接", MP_RandomChangeLink}
            });

            AddTestCase("崩溃上报测试", CrashTest);

            AddTestCaseInSubview("游戏保存", new Dictionary<string, UnityAction>
            {
                {"保存", UD_Save},
                {"读取", UD_Load},
                {"删除", UD_Delete},
                {"疯狂写入", UD_MAXIMAL_WRITE},
                {"当前磁盘占用", UD_DISK_SIZE},
                {"Persist目录存储测试", UD_Persistent_Save},
                {"Persist目录读取测试", UD_Persisent_Load},
                {"PlayerPrefs 存储测试", UD_PlayerPrefs_Save},
                {"PlayerPrefs 读取测试", UD_PlayerPrefs_Load},
                {"清除所有存档", UD_CLEAR_ALL},
            });

            AddTestCase("读取启动参数", Read_LaunchOption);
            
            AddTestCase("打开客服页", OpenCustomerPage);
            AddTestCase("跳转到抖音视频", NavigateToVideoViewTestCase);
            AddTestCase("打印SystemInfo", PrintSystemInfo);
            AddTestCaseInSubview("游戏退出测试", new Dictionary<string, UnityAction>
            {
                {"退出游戏(二次确认)", ExitApp},
                {"直接退出游戏", ExitAppDirectly},
                {"系统退出(Application.Quit)", ApplicationQuit},
            });
            AddTestCaseInSubview("陀螺仪(for WebGL)", new Dictionary<string, UnityAction>
            {
                {"开启陀螺仪", StartAccelerometer},
                {"关闭陀螺仪", StopAccelerometer},
            });
            AddTestCaseInSubview("CanIUse(for WebGL)", new Dictionary<string, UnityAction>
            {
                {"StartAccelerometer", () => { PrintText($"StartAccelerometer: {CanIUse.StartAccelerometer}"); }},
                {"StopAccelerometer", () => { PrintText($"StopAccelerometer: {CanIUse.StopAccelerometer}"); }},
                {"FollowDouYinUserProfile", () => { PrintText($"FollowDouYinUserProfile: {CanIUse.FollowDouYinUserProfile}"); }},
                {"HasBoundDouyin", () => { PrintText($"HasBoundDouyin: {CanIUse.HasBoundDouyin}"); }},
                {"ExitApp", () => { PrintText($"ExitApp: {CanIUse.ExitApp}"); }},
                {"OpenSettingsPanel", () => { PrintText($"OpenSettingsPanel: {CanIUse.StarkAccount.OpenSettingsPanel}"); }},
                {"GetUserInfoAuth", () => { PrintText($"GetUserInfoAuth: {CanIUse.StarkAccount.GetUserInfoAuth}"); }},
                {"GetSystemInfo", () => { PrintText($"GetSystemInfo: {CanIUse.GetSystemInfo}"); }},
                {"ShowVideoAdWithId", () => { PrintText($"ShowVideoAdWithId: {CanIUse.StarkAdManager.ShowVideoAdWithId}"); }},
                {"StartRecord", () => { PrintText($"StartRecord: {CanIUse.StarkGameRecorder.StartRecord}"); }},
                {"StopRecord", () => { PrintText($"StopRecord: {CanIUse.StarkGameRecorder.StopRecord}"); }},
                {"ShareVideo", () => { PrintText($"ShareVideo: {CanIUse.StarkGameRecorder.ShareVideo}"); }},
                {"ShareVideoWithTitleTopics", () => { PrintText($"ShareVideoWithTitleTopics: {CanIUse.StarkGameRecorder.ShareVideoWithTitleTopics}"); }},
                {"ShareVideoWithJson", () => { PrintText($"ShareVideoWithJson: {CanIUse.StarkGameRecorder.ShareVideoWithJson}"); }},
                {"ShareAppMessage", () => { PrintText($"ShareAppMessage: {CanIUse.StarkShare.ShareAppMessage}"); }},
                {"Login", () => { PrintText($"Login: {CanIUse.StarkAccount.Login}"); }},
                {"CheckSession", () => { PrintText($"CheckSession: {CanIUse.StarkAccount.CheckSession}"); }},
                {"GetScUserInfo", () => { PrintText($"GetScUserInfo: {CanIUse.StarkAccount.GetScUserInfo}"); }},
                {"GetUserdateDir", () => { PrintText($"GetUserdateDir: {CanIUse.StarkUtils.GetUserdateDir}"); }},
                {"ReportAnalytics", () => { PrintText($"ReportAnalytics: {CanIUse.ReportAnalytics}"); }},
                {"Save", () => { PrintText($"Save: {CanIUse.Save}"); }},
                {"LoadSaving", () => { PrintText($"LoadSaving: {CanIUse.LoadSaving}"); }},
                {"DeleteSaving", () => { PrintText($"DeleteSaving: {CanIUse.DeleteSaving}"); }},
                {"ClearAllSavings", () => { PrintText($"ClearAllSavings: {CanIUse.ClearAllSavings}"); }},
                {"GetSavingDiskSize", () => { PrintText($"GetSavingDiskSize: {CanIUse.GetSavingDiskSize}"); }}
            });
            AddTestCaseInSubview("OnShareAppMessage", new Dictionary<string, UnityAction>
            {
                {"注册OnShareAppMessage", OnShareAppMessage},
                {"注销OffShareAppMessage", OffShareAppMessage}
            });
        }
        
        IEnumerator UnCompressVideo()
        {
            string filename = "/record_video_local.mp4";
            string originalPath = Application.streamingAssetsPath + filename;
            string targetPath = Application.temporaryCachePath + filename;
            WWW www = new WWW(originalPath);
            yield return www;
            if (www.isDone)
            {
                //拷贝数据库到指定路径
                File.WriteAllBytes(targetPath, www.bytes);

                Debug.Log("demo video exist? " + File.Exists(targetPath));
                if (File.Exists(targetPath))
                {
                   PrintText("视频解压成功");
                }
                else
                {
                    PrintText("视频解压失败");
                }
            }
            else
            {
                PrintText("视频解压失败");
            }
        }

        private void OffShareAppMessage()
        {
            PrintText("注销OnShareAppMessage回调 ");
            StarkSDK.API.GetStarkShare().OffShareAppMessage((res) => null);
        }
        
        private void OnShareAppMessage()
        {
            StartCoroutine(UnCompressVideo());
            PrintText("注册OnShareAppMessage回调 ");
            StarkSDK.API.GetStarkShare().OnShareAppMessage((res) =>
                {
                    var channel = res.channel;
                    if (channel == "video")
                    {
                        JsonData json = new JsonData();
                        json["title"] = "分享标题";
                        json["channel"] = "video";
                        json["query"] = "t1=hello&t2+2=world";
                        JsonData topic = new JsonData();
                        topic.Add("test1 videoTopics");
                        topic.Add("test2 videoTopics");
                        JsonData extra = new JsonData();
                        extra["videoTopics"] = topic;
                        string filename = "/record_video_local.mp4";
                        string targetPath = Application.temporaryCachePath + filename;
                        if (File.Exists(targetPath))
                        {
                            extra["videoPath"] = targetPath;
                        }
                        else
                        {
                            PrintText("视频文件不存在");
                        }

                        json["extra"] = extra;
                        return new StarkShare.ShareParam(
                            json,
                            (data) => { PrintText("分享成功"); },
                            (msg) => { PrintText("分享失败" + msg); },
                            () => { PrintText("取消分享"); }
                        );
                }
                else 
                {
                    JsonData json = new JsonData();
                    json["title"] = "SC文章分享";
                    json["imageUrl"] = "https://example.com/test.png";
                    json["query"] = "t1=hello&t2+2=world";
                    return new StarkShare.ShareParam(
                        json,
                        (data) => { PrintText("分享成功"); },
                        (msg) => { PrintText("分享失败" + msg); },
                        () => { PrintText("取消分享"); }
                    );
                }
            }
         );
        }

        private void PrintSystemInfo()
        {
            var systemInfo = StarkSDK.API.GetSystemInfo();
            Debug.Log(JsonUtility.ToJson(systemInfo));
            PrintText(JsonUtility.ToJson(systemInfo));
        }

        private static void ExitApp()
        {
            StarkSDK.API.ExitApp(true);
        }

        private static void ExitAppDirectly()
        {
            StarkSDK.API.ExitApp(false);
        }

        private void StartAccelerometer()
        {
            Vector3 acceleration = Vector3.zero;
            StarkSDK.API.StartAccelerometer((x, y, z) =>
            {
                var text = $"x: {x}\ny: {y}\nz: {z}";
                PrintText(text);
                if (acceleration != Vector3.zero)
                {
                    float dx = (float) (x - acceleration.x) * 100;
                    float dy = (float) (y - acceleration.y) * 100;
                    float dz = (float) (z - acceleration.z) * 100;
                    _exampleCube?.Rotate(dx, dy, dz);
                }

                acceleration.x = (float) x;
                acceleration.y = (float) y;
                acceleration.z = (float) z;
            }, (success, errMsg) =>
            {
                if (success)
                {
                    acceleration = Vector3.zero;
                    if (_exampleCube == null)
                    {
                        var gameObject = new GameObject();
                        _exampleCube = gameObject.AddComponent<ExampleCube>();
                    }
                    else
                    {
                        _exampleCube.Reset();
                        _exampleCube.Show();
                    }

                    StarkUISwitch.Instance?.Close();
                }

                PrintText(errMsg);
            });
        }

        private void StopAccelerometer()
        {
            _exampleCube?.Hide();
            StarkSDK.API.StopAccelerometer((success, errMsg) => { PrintText(errMsg); });
        }

        private static void ApplicationQuit()
        {
            Debug.Log("Application.Quit called.");
            Application.Quit();
        }

        void OpenCustomerPage()
        {
            if (CanIUse.OpenCustomerServicePage)
            {
                PrintText("打开客服页");
                StarkSDK.API.OpenCustomerServicePage(
                    (flag) =>
                    {
                        if (flag)
                        {
                            PrintTextAppended("成功");
                        }
                        else
                        {
                            PrintTextAppended("失败");
                        }
                    });
            }
            else
            {
                StarkUIManager.ShowToast("AndroidSDK版本不足以打开客服页");
                PrintTextAppended("AndroidSDK版本不足以打开客服页");
            }
        }

        void RealNameAuthentication()
        {
            if (CanIUse.StarkAccount.SetRealNameAuthenticationCallback)
            {
                Debug.Log("realNameAu");
                StarkSDK.API.GetAccountManager().SetRealNameAuthenticationCallback(
                    () => { AndroidUIManager.ShowToast($"用户完成了实名认证"); });
            }
            else
            {
                Debug.Log("AndroidSDKVersion is Lower than 560");
            }
        }

        void CrashTest()
        {
            UnityEngine.Diagnostics.Utils.ForceCrash(UnityEngine.Diagnostics.ForcedCrashCategory.FatalError);
        }

        protected void ReportTest()
        {
            Dictionary<string, string> tmpDic = new Dictionary<string, string>();
            tmpDic.Add("start", "start1");
            StarkSDK.API.ReportAnalytics("startgame", tmpDic);
            PrintText("上报自定义埋点：start");
        }

        protected void GameRecorderTestCase()
        {
            PrintText("录屏功能");
            ShowTipsWhenDontUse(CanIUse.StarkGameRecorder.StartRecord);
            OpenCaseView("GameRecordPanel");
        }

        protected void BannerTestCase()
        {
            PrintText("Banner广告");
            OpenCaseView("BannerAd");
        }

        public void ShowExcitingVideo1()
        {
            if(Common.GetVideoAdId() == ""){
                PrintText("请在TesterCases配置BannerAdId");
                return;
            } 
            PrintText("激励视频播放");
            ShowTipsWhenDontUse(CanIUse.StarkAdManager.ShowVideoAdWithId);
            StarkSDK.API.GetStarkAdManager().ShowVideoAdWithId(Common.GetVideoAdId(),
                (bComplete) => { PrintText("激励视频关闭 " + bComplete); }, OnAdError);
        }

        StarkAdManager.BannerAd m_bannerAdIns = null;
        StarkAdManager.InterstitialAd m_InterAdIns = null;

        #region 测试插屏AD

        void CreateInterstitialAd()
        {
            if(Common.GetInterstitialAdId() == ""){
                PrintText("请在TesterCases配置InterstitialAdId");
                return;
            } 
            ShowTipsWhenDontUse(CanIUse.StarkAdManager.CreateInterstitialAd);
            PrintText("创建插屏AD");
            m_InterAdIns = StarkSDK.API.GetStarkAdManager().CreateInterstitialAd(Common.GetInterstitialAdId(), OnAdError,
                () => { PrintText("插屏广告关闭"); }, () => { PrintText("插屏广告加载"); });
        }

        void LoadInterstitialAd()
        {
            if (m_InterAdIns != null)
                m_InterAdIns.Load();
            else
            {
                PrintText("插屏AD未创建");
            }
        }


        void ShowInterstitialAd()
        {
            PrintText("显示插屏AD");
            if (m_InterAdIns != null)
                m_InterAdIns.Show();
            else
            {
                PrintText("插屏AD未创建");
            }
        }

        void DestoryInterstitialAd()
        {
            PrintText("销毁插屏AD");
            if (m_InterAdIns != null)
                m_InterAdIns.Destory();
            m_InterAdIns = null;
        }

        void OnAdError(int iErrCode, string errMsg)
        {
            PrintText("错误 ： " + iErrCode + "  " + errMsg);
        }

        #endregion


        #region 创建快捷方式

        void CreateShortcut()
        {
            PrintText("创建快捷方式");
            ShowTipsWhenDontUse(CanIUse.CreateShortcut);
            StarkSDK.API.CreateShortcut(OnCreateShortcut);
        }

        void IsShortcutExist()
        {
            ShowTipsWhenDontUse(CanIUse.IsShortcutExist);
            StarkSDK.API.IsShortcutExist(exist => { PrintText("Shortcut exist: " + exist); });
        }

        void OnCreateShortcut(bool bSuccess)
        {
            PrintText("OnCreateShortcut : {0}", bSuccess);
        }

        #endregion

        #region 关注抖音账号

        void FollowAweme()
        {
            PrintText("关注抖音账号");
            ShowTipsWhenDontUse(CanIUse.FollowDouYinUserProfile);
            StarkSDK.API.FollowDouYinUserProfile(OnFollowAwemeCallback, OnFollowAwemeError);
        }

        void OnFollowAwemeCallback()
        {
            PrintTextAppended("OnFollowAwemeCallback");
        }

        void OnFollowAwemeError(int errCode, string errMsg)
        {
            PrintTextAppended("OnFollowAwemeError errCode {0} errMsg {1}", errCode, errMsg);
        }

        #endregion

        #region Android UI测试

        void AndroidUITest()
        {
            PrintText("Android UI测试");
            OpenCaseView("AndroidUIPanel");
        }

        #endregion

        protected void TestVibrate()
        {
            long[] pattern = {0, 100, 1000, 300};
            ShowTipsWhenDontUse(CanIUse.Vibrate);
            StarkSDK.API.Vibrate(pattern);
        }

        private void TestIsGameFavorite()
        {
            ShowTipsWhenDontUse(CanIUse.StarkFavorite.IsCollected);
            bool isCollected = StarkSDK.API.GetStarkFavorite().IsCollected();
            PrintText("IsGameFavorite: " + isCollected);
        }

        private void TestGameFavour(bool isCollect)
        {
            if (isCollect)
            {
                ShowTipsWhenDontUse(CanIUse.StarkFavorite.Collect);
                StarkSDK.API.GetStarkFavorite().Collect(success => { PrintText("Collect - success: " + success); });
            }
            else
            {
                ShowTipsWhenDontUse(CanIUse.StarkFavorite.CancelCollection);
                StarkSDK.API.GetStarkFavorite().CancelCollection(success =>
                {
                    PrintText("CancelCollection - success: " + success);
                });
            }
        }

        private void TestFavoriteGuideTopBar()
        {
            PrintText("TestFavoriteGuideTopBar");
            ShowTipsWhenDontUse(CanIUse.StarkFavorite.ShowFavoriteGuide);
            StarkSDK.API.GetStarkFavorite().ShowFavoriteGuide(StarkFavorite.Style.TopBar);
        }

        private void TestFavoriteGuideBottomBar()
        {
            PrintText("TestFavoriteGuideBottomBar");
            ShowTipsWhenDontUse(CanIUse.StarkFavorite.ShowFavoriteGuide);
            StarkSDK.API.GetStarkFavorite().ShowFavoriteGuide(StarkFavorite.Style.BottomBar);
        }

        private void TestFavoriteGuideTip()
        {
            PrintText("TestFavoriteGuideTip");
            ShowTipsWhenDontUse(CanIUse.StarkFavorite.ShowFavoriteGuide);
            StarkSDK.API.GetStarkFavorite().ShowFavoriteGuide(StarkFavorite.Style.Tip, "测试文案测试文案测试文案测试文案测试文案测试文案");
        }
        
        private void HasBoundAweme()
        {
            //ShowTipsWhenDontUse(CanIUse.IsFollowDouyin);
            StarkSDK.API.HasBoundDouyin((isBinded) => { PrintText("IsBindDouyin: \nisBinded: " + isBinded); });
        }

        #region 账号

        private void TestForceLogin()
        {
            RealLogin(true);
        }

        private void TestNoForceLogin()
        {
            RealLogin(false);
        }

        private void RealLogin(bool force)
        {
            Code = "";
            AnonymousCode = "";

            ShowTipsWhenDontUse(CanIUse.StarkAccount.Login);
            StarkSDK.API.GetAccountManager().Login((c1, c2, isLogin) =>
                {
                    PrintText($"TestLogin: force:{force},code:{c1},anonymousCode:{c2},isLogin:{isLogin}");
                    Code = c1;
                    AnonymousCode = c2;
                },
                (msg) => { PrintText($"TestLogin: force:{force},{msg}"); }, force);
        }

        private void TestCheckSession()
        {
            ShowTipsWhenDontUse(CanIUse.StarkAccount.CheckSession);
            StarkSDK.API.GetAccountManager().CheckSession(() => { PrintText($"TestCheckSession success session"); },
                (errMsg) => { PrintText($"TestCheckSession fail: {errMsg}"); });
        }

        private void TestGetUserInfo()
        {
            ShowTipsWhenDontUse(CanIUse.StarkAccount.GetScUserInfo);
            StarkSDK.API.GetAccountManager().GetScUserInfo(
                (ref ScUserInfo scUserInfo) => { PrintText($"TestGetUserInfo info: {scUserInfo.ToString()}"); },
                (errMsg) => { PrintText($"TestGetUserInfo fail: {errMsg}"); });
        }

        private void TestGetUserInfoAuth()
        {
            ShowTipsWhenDontUse(CanIUse.StarkAccount.GetUserInfoAuth);
            StarkSDK.API.GetAccountManager().GetUserInfoAuth(
                (auth) => { PrintText($"TestGetUserInfoAuth info auth: {auth}"); },
                (errMsg) => { PrintText($"TestGetUserInfoAuth fail: {errMsg}"); });
        }

        private void TestOpenSettingPanel()
        {
            ShowTipsWhenDontUse(CanIUse.StarkAccount.OpenSettingsPanel);
            StarkSDK.API.GetAccountManager().OpenSettingsPanel(
                (auth) => { PrintText($"TestOpenSettingPanel info new auth: {auth}"); },
                (errMsg) => { PrintText($"TestOpenSettingPanel fail: {errMsg}"); });
        }

        #endregion

        private void TestEnv()
        {
            PrintText($"HostEnum: {StarkSDK.s_ContainerEnv.m_HostEnum} " +
                      $"LaunchFromEnum:{StarkSDK.s_ContainerEnv.m_LaunchFromEnum}");
        }
        private void TestPay()
        {
            ShowTipsWhenDontUse(CanIUse.GetStarkPayService);
            PrintText("支付测试");
            OpenCaseView("PayTestPanel");
        }

        /// <summary>
        /// 判断当前这个接口在Container下是否可以使用，若不可以使用则提醒用户
        /// </summary>
        /// <param name="caniuse">是否可用</param>
        /// <returns></returns>
        private bool ShowTipsWhenDontUse(bool caniuse)
        {
            if (Application.platform == RuntimePlatform.Android && !caniuse)
            {
                UnityEngine.Debug.LogError("当前宿主的Container版本过低，不可使用该接口");
                AndroidUIManager.ShowToast("当前宿主的Container版本过低，不可使用该接口");
            }

            return caniuse;
        }

        #region Multi-package download tester

        private void MP_RandomChangeLink()
        {
            Debug.Log("MultipackageTester");
#if UNITY_ANDROID
            string version = StarkSDK.API.GetStarkContainerVersion();
            if (CheckVersionValide("3.8.0"))
            {
                using (AndroidJavaClass mp_tester =
                    new AndroidJavaClass("com.bytedance.stark.common.tester.MultipackageTester"))
                {
                    string randomFile = mp_tester.CallStatic<string>("testonly_randomFile");
                    string randomSharedFile = mp_tester.CallStatic<string>("testonly_randomSharedFile");

                    bool succ1 = mp_tester.CallStatic<bool>("testonly_changeLink", randomSharedFile, randomFile);
                    PrintTextAppended("3. Random link [" + randomSharedFile + "]\n->\n[" + randomFile + "] with " +
                                      succ1);
                }
            }
            else
            {
                PrintText("Test case failed, version below " + StarkSDK.API.SDKVersion);
            }
#endif
        }

        private void MP_DeleteFile()
        {
#if UNITY_ANDROID
            string version = StarkSDK.API.GetStarkContainerVersion();
            if (CheckVersionValide("3.8.0"))
            {
                using (AndroidJavaClass mp_tester =
                    new AndroidJavaClass("com.bytedance.stark.common.tester.MultipackageTester"))
                {
                    string randomFile = mp_tester.CallStatic<string>("testonly_randomFile");

                    bool succ = mp_tester.CallStatic<bool>("testonly_deleteFile", randomFile);
                    PrintTextAppended("1. Delete " + randomFile + " " + succ);
                }
            }
            else
            {
                PrintText("Test case failed, version below " + StarkSDK.API.SDKVersion);
            }
#endif
        }

        private void MP_DeleteSharedFile()
        {
#if UNITY_ANDROID
            string version = StarkSDK.API.GetStarkContainerVersion();
            if (CheckVersionValide("3.8.0"))
            {
                using (AndroidJavaClass mp_tester =
                    new AndroidJavaClass("com.bytedance.stark.common.tester.MultipackageTester"))
                {
                    string randomSharedFile = mp_tester.CallStatic<string>("testonly_randomSharedFile");

                    bool succ = mp_tester.CallStatic<bool>("testonly_deleteFile", randomSharedFile);
                    PrintTextAppended("2. Delete source " + randomSharedFile + " " + succ);
                }
            }
            else
            {
                PrintText("Test case failed, version below " + StarkSDK.API.SDKVersion);
            }
#endif
        }

        #endregion

        private bool CheckVersionValide(string version)
        {
            string[] pluginVersion = StarkSDK.API.GetStarkContainerVersion().Split('.');
            string[] unitySDKVersion = version.Split('.');

            if (null == pluginVersion || pluginVersion.Length != 3 || null == unitySDKVersion ||
                unitySDKVersion.Length != 3)
                return false;

            int[] pluginVersions = new int[3];
            int[] unitySDKVersions = new int[3];

            try
            {
                for (int i = 0; i < 3; i++)
                {
                    pluginVersions[i] = int.Parse(pluginVersion[i]);
                    unitySDKVersions[i] = int.Parse(unitySDKVersion[i]);
                }
            }
            catch (Exception e)
            {
                PrintText(e.ToString());
                return false;
            }


            if (pluginVersions[0] > unitySDKVersions[0]
                || (pluginVersions[0] == unitySDKVersions[0] && pluginVersions[1] >= unitySDKVersions[1]))
            {
                return true;
            }
            else
            {
                return false;
            }
        }
        
        [Serializable]
        class SaveData
        {
            public int IntValue = 99;
            private float FloatValue = 1.0f;
            public string StrValue = "Stark gogo";
            public Dictionary<String, bool> map;
            public List<String> listStr;

            public override string ToString()
            {
                StringBuilder sb = new StringBuilder();
                sb.Append("IntValue:").Append(IntValue).Append("\n")
                    .Append("FloatValue:").Append(FloatValue).Append("\n")
                    .Append("StrValue:").Append(StrValue).Append("\n")
                    .Append("Map:\n");

                foreach (KeyValuePair<string, bool> entry in map)
                {
                    sb.Append("Key:").Append(entry.Key).Append("->Value:").Append(entry.Value).Append("\n");
                }

                sb.Append("List:");

                foreach (string str in listStr)
                {
                    sb.Append(" ").Append(str);
                }

                return sb.ToString();
            }
        }

        private void UD_Save()
        {
            SaveData sd = new SaveData();
            sd.IntValue = 77;
            sd.StrValue = "Save test";
            sd.map = new Dictionary<string, bool>();
            sd.map.Add("Sekiro", true);
            sd.map.Add("Monkey", false);
            sd.listStr = new List<string>();
            sd.listStr.Add("list1");
            sd.listStr.Add("list2");
            //for(int i=0;i<1000;i++)
            //{
            //    sd.listStr.Add("Autolist" + i);
            //}

            bool ret = StarkSDK.API.Save<SaveData>(sd);

            //ret &= StarkSDK.API.SaveGame<SaveData>(sd, "2");
            if (ret)
            {
                PrintText("UD_Save success:\n{0}", sd.ToString());
            }
            else
            {
                PrintText("UD_Save failed");
            }
        }

        private void UD_Load()
        {
            SaveData loaded = StarkSDK.API.LoadSaving<SaveData>();

            if (null == loaded)
            {
                PrintText("Load failed, save-file not existed");
            }
            else
            {
                PrintText("UD_Load\n{0}", loaded.ToString());
            }
        }

        private void UD_Delete()
        {
            StarkSDK.API.DeleteSaving<SaveData>();

            PrintText("Delete SaveData");
        }

        private void UD_MAXIMAL_WRITE()
        {
            SaveData sd = new SaveData();
            sd.IntValue = 77;
            sd.StrValue = "Save test";
            sd.map = new Dictionary<string, bool>();
            sd.map.Add("Sekiro", true);
            sd.map.Add("Monkey", false);
            sd.listStr = new List<string>();
            for (int i = 0; i < 100000; i++)
            {
                sd.listStr.Add("shijie-test-test-test" + i);
            }

            bool ret = true;
            int count = 0;
            do
            {
                count++;
                ret &= StarkSDK.API.Save(sd, count.ToString());

                Debug.Log("Write to " + count);
            } while (ret);

            PrintText("Write {0} files and stopped", count);
        }

        private void UD_DISK_SIZE()
        {
            PrintText("Disk size {0}M", StarkSDK.API.GetSavingDiskSize() / 1024f / 1024f);
        }

        private void UD_CLEAR_ALL()
        {
            StarkSDK.API.ClearAllSavings();

            PrintText("Clear all savings");
        }

        private void UD_Persistent_Save()
        {
            string saveName = "save_test_file.txt";
            string saveContent = "Save Test!!!";
            string dir = Application.persistentDataPath;
            if (!Directory.Exists(dir))
            {
                Directory.CreateDirectory(dir);
            }

            String savePath = string.Format("{0}/{1}", dir, saveName);
            if (File.Exists(savePath))
            {
                File.Delete(savePath);
            }

            FileStream fs = new FileStream(savePath, FileMode.Create);
            byte[] bytes = new UTF8Encoding().GetBytes(saveContent);
            fs.Write(bytes, 0, bytes.Length);
            fs.Close();
            PrintText(string.Format("UD_Persistent_Save 写入成功\n写入路径为:{0}\n写入数据为:{1}", savePath, saveContent));
        }

        private void UD_Persisent_Load()
        {
            string loadName = "save_test_file.txt";
            string dir = Application.persistentDataPath;
            if (!Directory.Exists(dir))
            {
                PrintText(string.Format("UD_Persisent_Load 读取失败\n原因：无该路径:{0}", dir));
                return;
            }

            string loadPath = string.Format("{0}/{1}", dir, loadName);
            if (!File.Exists(loadPath))
            {
                PrintText(string.Format("UD_Persisent_Load 读取失败\n原因：无该路径:{0}", loadPath));
                return;
            }

            FileStream fs = new FileStream(loadPath, FileMode.Open);
            byte[] bytes = new byte[512];
            fs.Read(bytes, 0, bytes.Length);
            string loadContent = new UTF8Encoding().GetString(bytes);
            PrintText(string.Format("UD_Persisent_Load 读取成功\n读取路径为:{0}\n读取到的数据为:{1}", loadPath, loadContent));
        }

        private void UD_PlayerPrefs_Save()
        {
            string saveKey = "SaveKey";
            string saveContent = "SaveText!!!!";
            PlayerPrefs.SetString(saveKey, saveContent);
            PrintText(string.Format("UD_PlayerPrefs_Save 数据写入成功\n写入数据key为:{0}\nvalue为:{1}", saveKey, saveContent));
        }

        private void UD_PlayerPrefs_Load()
        {
            string loadKey = "SaveKey";
            string loadContent = PlayerPrefs.GetString(loadKey);
            PrintText(string.Format("UD_PlayerPrefs_Save 数据读取成功\n读取数据key为:{0}\nvalue为:{1}", loadKey, loadContent));
        }
        
        private void Read_LaunchOption()
        {
            PrintText("LaunchOption: ");
            if (StarkSDK.s_ContainerEnv != null)
            {
                StarkSDKSpace.LaunchOption launchOption = StarkSDK.s_ContainerEnv.GetLaunchOptionsSync();
                PrintTextAppended("path :" + launchOption.Path);
                PrintTextAppended("scene :" + launchOption.Scene);
                PrintTextAppended("subScene :" + launchOption.SubScene);
                PrintTextAppended("group_id :" + launchOption.GroupId);
                PrintTextAppended("shareTicket :" + launchOption.ShareTicket);
                PrintTextAppended("is_sticky :" + launchOption.IsSticky);
                PrintTextAppended("query :");
                if (launchOption.Query != null)
                {
                    foreach (KeyValuePair<string, string> kv in launchOption.Query)
                        if (kv.Value != null)
                            PrintTextAppended(kv.Key + ": " + kv.Value);
                        else
                            PrintTextAppended(kv.Key + ": " + "null ");
                }
                
                PrintTextAppended("refererInfo :");
                if (launchOption.RefererInfo != null)
                {
                    foreach (KeyValuePair<string, string> kv in launchOption.RefererInfo)
                        if (kv.Value != null)
                            PrintTextAppended(kv.Key + ": " + kv.Value);
                        else
                            PrintTextAppended(kv.Key + ": " + "null ");
                }
                
                PrintTextAppended("extra :");
                if (launchOption.Extra != null)
                {
                    foreach (KeyValuePair<string, string> kv in launchOption.Extra)
                        if (kv.Value != null)
                            PrintTextAppended(kv.Key + ": " + kv.Value);
                        else
                            PrintTextAppended(kv.Key + ": " + "null ");
                }
            }
        }

        IEnumerator RunAsync(float secondsCloseCountdown)
        {
            PrintText("TitleBarCapsuleClose:  seconds download" + secondsCloseCountdown);
            yield return new WaitForSeconds(secondsCloseCountdown / 2);
            PrintTextAppended("TitleBarCapsuleClose half over");
        }

        protected void NavigateToVideoViewTestCase()
        {
            PrintText("跳转抖音视频功能");
            ShowTipsWhenDontUse(CanIUse.NavigateToVideoView);
            OpenCaseView("NavigatetoVideoViewPanel");
        }
    }
    
    //需要业务方根据自己小游戏开发者后台拿到的id进行配置
    class Common
    {
        public static string GetBannerAdId()
        {
            return "";
        }
        public static string GetVideoAdId()
        {
            return "";
        }
        public static string GetInterstitialAdId()
        {
            return "";
        }
    }
}