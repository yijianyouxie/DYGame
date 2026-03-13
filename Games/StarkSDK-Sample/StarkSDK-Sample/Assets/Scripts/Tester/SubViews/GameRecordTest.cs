using System;
using System.Collections.Generic;
using System.Security.Cryptography;
using StarkSDKSpace.UNBridgeLib.LitJson;
using UnityEngine;
using UnityEngine.UI;
using System.IO;
using System.Collections;
using Object = System.Object;

namespace StarkSDKSpace
{

    public class GameRecordTest : MonoBehaviour
    {
        private readonly static string TAG = "GameRecordTest";

        private int m_Counter;
        private float m_Height;
        private bool m_IsOpen = true;
        private float m_Speed = 3000;

        private Text m_RecordDurationText;
        private Text m_CounterText;
        private Vector3 m_InitPos;
        private DateTime m_StartTime;

        private StarkGameRecorder m_StarkGameRecorder;
        private Button m_EnableButton;
        private Button m_AudioEnableButton;
        private Text m_RecordStateText;
        private Text m_ClipStateText;
        private Text m_VideoPathText;
        private Text m_ClipPathText;
        private Text m_ShareStateText;
        private Text m_VideoIdText;
        private List<StarkGameRecorder.TimeRange> m_ClipRanges = new List<StarkGameRecorder.TimeRange>();
        private bool m_IsRecordAudio = true;
        private int m_MaxRecordTime = 0;
        private InputField m_VideoWidthInputField;
        private InputField m_VideoHeightInputField;

        private void Awake()
        {
            //QualitySettings.vSyncCount = 2;
            //Application.targetFrameRate = 30;
        }

        private void Start()
        {
            Log.Debug(TAG, "Start");
            StarkSDK.EnableStarkSDKDebugToast = false;
            InitPosition();

            m_StartTime = DateTime.Now;
            m_StarkGameRecorder = StarkSDK.API.GetStarkGameRecorder();
            m_RecordDurationText = transform.Find("RecordDuration")?.GetComponent<Text>();
            m_CounterText = transform.Find("CountText")?.GetComponent<Text>();
            m_EnableButton = transform.Find("ScrollView/Viewport/Content/SetEnable")?.GetComponent<Button>();
            m_AudioEnableButton = transform.Find("ScrollView/Viewport/Content/SetAudioEnable")?.GetComponent<Button>();
            m_RecordStateText = transform.Find("ScrollView/Viewport/RecordState/Text")?.GetComponent<Text>();
            m_ClipStateText = transform.Find("ScrollView/Viewport/ClipState/Text")?.GetComponent<Text>();
            m_ShareStateText = transform.Find("ScrollView/Viewport/ShareState/Text")?.GetComponent<Text>();
            m_VideoIdText = transform.Find("ScrollView/Viewport/VideoId/Text")?.GetComponent<Text>();
            m_VideoPathText = transform.Find("ScrollView/Viewport/VideoPath/Text")?.GetComponent<Text>();
            m_ClipPathText = transform.Find("ScrollView/Viewport/ClipPath/Text")?.GetComponent<Text>();
            // m_EnableButton?.onClick.AddListener(OnSetEnableTapped);
            m_AudioEnableButton?.onClick.AddListener(OnSetAudioEnableTapped);
            transform.Find("ScrollView/Viewport/Content/Start")?.GetComponent<Button>().onClick.AddListener(OnStartButtonTapped);
            transform.Find("ScrollView/Viewport/Content/Stop")?.GetComponent<Button>().onClick.AddListener(OnStopButtonTapped);
            transform.Find("ScrollView/Viewport/Content/AutoRecord")?.GetComponent<Button>().onClick.AddListener(OnAutoRecordButtonTapped);
            transform.Find("ScrollView/Viewport/Content/AutoRecord2")?.GetComponent<Button>().onClick.AddListener(OnAutoRecord2ButtonTapped);
            transform.Find("ScrollView/Viewport/Content/RecordClip1")?.GetComponent<Button>().onClick.AddListener(OnRecordClip1Tapped);
            transform.Find("ScrollView/Viewport/Content/RecordClip2")?.GetComponent<Button>().onClick.AddListener(OnRecordClip2Tapped);
            transform.Find("ScrollView/Viewport/Content/ClipVideo")?.GetComponent<Button>().onClick.AddListener(OnClipVideoTapped);
            transform.Find("ScrollView/Viewport/Content/ClipLast10s")?.GetComponent<Button>().onClick.AddListener(OnClipLast10sTapped);
            transform.Find("ScrollView/Viewport/Content/RandomClip")?.GetComponent<Button>().onClick.AddListener(OnRandomClipTapped);
            transform.Find("ScrollView/Viewport/Content/ShareVideo")?.GetComponent<Button>().onClick.AddListener(OnShareVideoTapped);
            transform.Find("ScrollView/Viewport/Content/ShareVideoWithJson")?.GetComponent<Button>().onClick.AddListener(OnShareVideoWithJsonTapped);
            transform.Find("ScrollView/Viewport/Content/ShareVideoWithVideoId")?.GetComponent<Button>().onClick.AddListener(OnShareVideoWithVideoIdTapped);
            transform.Find("ScrollView/Viewport/Content/ShareVideoWithTitleTopics")?.GetComponent<Button>().onClick.AddListener(OnShareVideoWithTitleTopicsTapped);
            transform.Find("ScrollView/Viewport/Content/ShareClipVideo")?.GetComponent<Button>().onClick.AddListener(OnShareClippedVideoTapped);
            transform.Find("ScrollView/Viewport/Content/ShareVideoWithDeaultBgm")?.GetComponent<Button>().onClick.AddListener(OnShareVideoWithDeaultBgmTapped);
            transform.Find("ScrollView/Viewport/Content/ShareVideoWithCutTemplate")?.GetComponent<Button>().onClick.AddListener(OnShareVideoWithCutTemplateTapped);
            transform.Find("ScrollView/Viewport/Content/ShareLocalVideo")?.GetComponent<Button>().onClick.AddListener(OnShareLocalVideo);
            transform.Find("ScrollView/Viewport/Content/SetCustomKeyFrameInterval")?.GetComponent<Button>().onClick
                .AddListener(OnSetIntervalButtonTapped);
            // SetEnableButtonText(m_EnableButton, m_StarkGameRecorder.GetEnabled(), "Enabled");
            SetEnableButtonText(m_AudioEnableButton, m_IsRecordAudio, "AudioEnabled");

            m_CounterText.text = string.Format("Counter: 0 Time: 0 s");
            m_RecordDurationText.text = "";
        }

        private bool isFinished = false;

        private void Update()
        {
            if (m_IsOpen)
            {
                if (transform.localPosition.y < m_InitPos.y)
                {
                    transform.localPosition = new Vector3(transform.localPosition.x, transform.localPosition.y + Time.deltaTime * m_Speed, transform.localPosition.z);
                }
            }
            else
            {
                if (transform.localPosition.y > (m_InitPos.y - m_Height))
                {
                    transform.localPosition = new Vector3(transform.localPosition.x, transform.localPosition.y - Time.deltaTime * m_Speed, transform.localPosition.z);
                }
            }

            if (m_StarkGameRecorder.GetVideoRecordState() == StarkGameRecorder.VideoRecordState.RECORD_COMPLETED)
            {
                if (!isFinished)
                {
                    isFinished = true;
                    m_RecordDurationText.text = string.Format("Duration: {0} s", m_StarkGameRecorder.GetRecordDuration() / 1000.0f);
                }
            }
            else
            {
                isFinished = false;
                m_RecordDurationText.text = "";
            }
            if (m_StarkGameRecorder.GetVideoRecordState() == StarkGameRecorder.VideoRecordState.RECORD_STARTED)
            {
                m_Counter += 1;
                TimeSpan ts = DateTime.Now - m_StartTime;
                m_CounterText.text = string.Format("Counter: {0} Time: {1:0.000} s", m_Counter, ts.TotalMilliseconds / 1000.0f);
            }
            SetStateText();
        }

        /// <summary>
        /// 记录精彩的视频片段，调用时必须是正在录屏。
        /// 以调用时的录屏时刻为基准，指定前 x 毫秒，后 y 毫秒为将要裁剪的片段，可以多次调用，记录不同时刻。
        /// 在结束录屏时，可以调用 ClipVideo 接口剪辑并合成记录的片段。
        /// </summary>
        /// <param name="beforeNowMs">记录那一刻前的毫秒数</param>
        /// <param name="afterNowInMillis">记录那一刻后的毫秒数</param>
        /// <returns>函数调用状态，调用成功返回true，否则返回false</returns>
        public bool RecordClip(int beforeNowMs, int afterNowInMillis)
        {
            if (m_StarkGameRecorder.GetVideoRecordState() != StarkGameRecorder.VideoRecordState.RECORD_STARTED)
            {
                Log.Error(TAG, "Recorder is not started");
                return false;
            }
            if (beforeNowMs < 0) beforeNowMs = 0;
            if (afterNowInMillis < 0) afterNowInMillis = 0;
            int duration = m_StarkGameRecorder.GetRecordDuration();
            StarkGameRecorder.TimeRange timeRange = new StarkGameRecorder.TimeRange(duration - beforeNowMs, duration + afterNowInMillis);
            timeRange.start = Math.Max(timeRange.start, 0);
            timeRange.end = Math.Max(timeRange.end, 0);
            if (timeRange.start == timeRange.end)
            {
                Log.Error(TAG, "Clip time start can not equal to end");
                return false;
            }
            if (timeRange.start > timeRange.end)
            {
                Log.Warning(TAG, "start > end, swap start and end");
                var t = timeRange.start;
                timeRange.start = timeRange.end;
                timeRange.end = t;
            }
            m_ClipRanges.Add(timeRange);
            Log.Debug(TAG, "RecordClip success, start: {0}ms, end: {1}ms, total count: {2}", timeRange.start, timeRange.end, m_ClipRanges.Count);
            return true;
        }

        private void SetStateText()
        {
            if (m_RecordStateText != null)
            {
                m_RecordStateText.text = m_StarkGameRecorder.GetVideoRecordState().ToString();
            }
            if (m_ShareStateText != null)
            {
                m_ShareStateText.text = m_StarkGameRecorder.GetVideoShareState().ToString();
            }
            
        }

        public void TogglePanel()
        {
            m_IsOpen = !m_IsOpen;
        }

        private void InitPosition()
        {
            m_Height = transform.GetComponent<RectTransform>().sizeDelta.y;
            m_InitPos = transform.localPosition;
            if (!m_IsOpen)
            {
                transform.localPosition = new Vector3(transform.localPosition.x, m_InitPos.y - m_Height, transform.localPosition.z);
            }
        }

        private void SetEnableButtonText(Button button, bool enabled, string text)
        {
            if (button != null)
            {
                if (enabled)
                {
                    button.GetComponentInChildren<Text>().text = string.Format("{0}: <color=#00ff00ff>True</color>", text);
                }
                else
                {
                    button.GetComponentInChildren<Text>().text = string.Format("{0}: <color=#ff0000ff>False</color>", text);
                }
            }
        }
        
        private void OnSetAudioEnableTapped()
        {
            m_IsRecordAudio = !m_IsRecordAudio;
            SetEnableButtonText(m_AudioEnableButton, m_IsRecordAudio, "AudioEnabled");
        }

        private void OnStartButtonTapped()
        {
            // if (m_StarkGameRecorder.GetEnabled())
            // {
                if (m_StarkGameRecorder.GetVideoRecordState() != StarkGameRecorder.VideoRecordState.RECORD_STARTED)
                {
                    m_StarkGameRecorder.StartRecord(m_IsRecordAudio, m_MaxRecordTime, OnRecordStart, OnRecordError, OnRecordTimeout);
                }
                else
                {
                    Log.Warning(TAG, "Recorder is started");
                }
            // }
            // else
            // {
            //     Log.Error(TAG, "Recorder is disabled");
            // }
        }

        private void OnStopButtonTapped()
        {
            m_StarkGameRecorder.StopRecord(OnRecordComplete, OnRecordError);
        }

        private void OnAutoRecordButtonTapped()
        {
            m_MaxRecordTime = 5;
            OnStartButtonTapped();
            m_MaxRecordTime = 0;
        }

        private void OnAutoRecord2ButtonTapped()
        {
            m_MaxRecordTime = 2;
            OnStartButtonTapped();
            m_MaxRecordTime = 0;
        }

        private void OnRecordClip1Tapped()
        {
            if (m_StarkGameRecorder.GetVideoRecordState() != StarkGameRecorder.VideoRecordState.RECORD_STARTED)
            {
                Log.Error(TAG, "Recorder not started");
                return;
            }
            StarkGameRecorder.TimeRange timeRange = VideoClipUtils.CreateClipTimeRange(3000, 4000);
            m_ClipRanges.Add(timeRange);
            Log.Info(TAG, "OnRecordClip1Tapped - counter: {0}", m_Counter);
        }

        private void OnRecordClip2Tapped()
        {
            if (m_StarkGameRecorder.GetVideoRecordState() != StarkGameRecorder.VideoRecordState.RECORD_STARTED)
            {
                Log.Error(TAG, "Recorder not started");
                return;
            }
            Log.Info(TAG, "OnRecordClip2Tapped - counter: {0}", m_Counter);
            StarkGameRecorder.TimeRange timeRange = VideoClipUtils.CreateClipTimeRange(0, 5000);
            m_ClipRanges.Add(timeRange);
        }

        private void OnClipVideoTapped()
        {
            if (m_StarkGameRecorder.GetVideoRecordState() == StarkGameRecorder.VideoRecordState.RECORD_STARTED)
            {
                m_StarkGameRecorder.StopRecord(OnRecordComplete, OnRecordError, m_ClipRanges, true);
            }
            else
            {
                Log.Error(TAG, "Recorder not started");
            }
        }

        private void OnClipLast10sTapped()
        {
            Log.Info(TAG, "OnClipLast10sTapped");
            if (m_StarkGameRecorder.GetVideoRecordState() == StarkGameRecorder.VideoRecordState.RECORD_STARTED)
            {
                int videoDurationMs = m_StarkGameRecorder.GetRecordDuration();
                List<StarkGameRecorder.TimeRange> clipRanges = new List<StarkGameRecorder.TimeRange>();
                // 裁剪视频最后10s
                clipRanges.Add(new StarkGameRecorder.TimeRange(videoDurationMs - 10 * 1000, videoDurationMs));
                m_StarkGameRecorder.StopRecord(OnRecordComplete, OnRecordError, clipRanges, true);
            }
            else
            {
                Log.Error(TAG, "Recorder not started");
            }
        }

        private void OnRandomClipTapped()
        {
            if (m_StarkGameRecorder.GetVideoRecordState() == StarkGameRecorder.VideoRecordState.RECORD_STARTED)
            {
                List<StarkGameRecorder.TimeRange> clipRanges = new List<StarkGameRecorder.TimeRange>(m_ClipRanges);
                Log.Info(TAG, "OnRandomClipTapped - total clips: {0}", clipRanges.Count);

                //Shuffle(clipRanges);
                // 倒序拼接
                clipRanges.Reverse();
                m_StarkGameRecorder.StopRecord(OnRecordComplete, OnRecordError, clipRanges, false);
            }
            else
            {
                Log.Error(TAG, "Recorder not started");
            }
        }

        private void OnShareVideoTapped()
        {
            m_StarkGameRecorder.ShareVideo(OnShareVideoSuccess, OnShareVideoFailed, OnShareVideoCancelled);
        }

        private void OnShareVideoWithTitleTopicsTapped()
        {
            string title = "SC小游戏，高品质游戏！";
            List<string> topics = new List<string>();
            topics.Add("SC小游戏");
            topics.Add("抖音小游戏");
            topics.Add("字节游戏");
            m_StarkGameRecorder.ShareVideoWithTitleTopics(OnShareVideoSuccess, OnShareVideoFailed, OnShareVideoCancelled, title, topics);
        }

        private void OnShareVideoWithJsonTapped()
        {
            JsonData shareJson = new JsonData();
            shareJson["title"] = "SC小游戏，高品质游戏！";
            shareJson["desc"] = "快来一起玩吧！";
            shareJson["imageUrl"] = "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1599735672379&di=679a39096fde83e3a1941381de7de9aa&imgtype=0&src=http%3A%2F%2Fimg.ivsky.com%2Fimg%2Fbizhi%2Fpre%2F201212%2F18%2Fkobe_bryant-007.jpg";

            JsonData extraJson = new JsonData();
            JsonData videoTopics = new JsonData();
            videoTopics.SetJsonType(JsonType.Array);
            videoTopics.Add("SC小游戏");
            videoTopics.Add("字节游戏");
            extraJson["videoTopics"] = videoTopics;
            extraJson["hashtag_list"] = videoTopics;
            extraJson["video_title"] = "StarkSDK Demo";
            shareJson["extra"] = extraJson;
            m_StarkGameRecorder.ShareVideoWithJson(OnShareVideoSuccess, OnShareVideoFailed, OnShareVideoCancelled, shareJson);
        }
        
        private void OnShareVideoWithVideoIdTapped()
        {
            JsonData shareJson = new JsonData();
            shareJson["title"] = "SC小游戏，高品质游戏！";
            shareJson["desc"] = "快来一起玩吧！";
            shareJson["imageUrl"] = "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1599735672379&di=679a39096fde83e3a1941381de7de9aa&imgtype=0&src=http%3A%2F%2Fimg.ivsky.com%2Fimg%2Fbizhi%2Fpre%2F201212%2F18%2Fkobe_bryant-007.jpg";

            JsonData extraJson = new JsonData();
            JsonData videoTopics = new JsonData();
            videoTopics.SetJsonType(JsonType.Array);
            videoTopics.Add("SC小游戏");
            videoTopics.Add("字节游戏");
            extraJson["videoTopics"] = videoTopics;
            extraJson["hashtag_list"] = videoTopics;
            extraJson["video_title"] = "StarkSDK Demo";
            extraJson["withVideoId"] = true;
            shareJson["extra"] = extraJson;
            m_StarkGameRecorder.ShareVideoWithJson(OnShareVideoSuccess, OnShareVideoFailed, OnShareVideoCancelled, shareJson);
        }

        private void OnShareClippedVideoTapped()
        {
            m_StarkGameRecorder.ShareVideo(OnShareVideoSuccess, OnShareVideoFailed, OnShareVideoCancelled);
        }

        private void OnShareVideoWithDeaultBgmTapped()
        {
            JsonData shareJson = new JsonData();
            shareJson["title"] = "SC小游戏，高品质游戏！";
            shareJson["desc"] = "快来一起玩吧！";
            shareJson["imageUrl"] = "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1599735672379&di=679a39096fde83e3a1941381de7de9aa&imgtype=0&src=http%3A%2F%2Fimg.ivsky.com%2Fimg%2Fbizhi%2Fpre%2F201212%2F18%2Fkobe_bryant-007.jpg";

            JsonData extraJson = new JsonData();
            JsonData videoTopics = new JsonData();
            videoTopics.SetJsonType(JsonType.Array);
            videoTopics.Add("SC小游戏");
            videoTopics.Add("字节游戏");
            extraJson["videoTopics"] = videoTopics;
            extraJson["hashtag_list"] = videoTopics;
            extraJson["video_title"] = "StarkSDK Demo";
            extraJson["defaultBgm"] = "https://v.douyin.com/RCkLY1N/";
            shareJson["extra"] = extraJson;
            m_StarkGameRecorder.ShareVideoWithJson(OnShareVideoSuccess, OnShareVideoFailed, OnShareVideoCancelled, shareJson);
        }

        private void OnShareVideoWithCutTemplateTapped()
        {
            JsonData shareJson = new JsonData();
            shareJson["title"] = "SC小游戏，高品质游戏！";
            shareJson["desc"] = "快来一起玩吧！";
            shareJson["imageUrl"] = "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1599735672379&di=679a39096fde83e3a1941381de7de9aa&imgtype=0&src=http%3A%2F%2Fimg.ivsky.com%2Fimg%2Fbizhi%2Fpre%2F201212%2F18%2Fkobe_bryant-007.jpg";

            JsonData extraJson = new JsonData();
            JsonData videoTopics = new JsonData();
            videoTopics.SetJsonType(JsonType.Array);
            videoTopics.Add("SC小游戏");
            videoTopics.Add("字节游戏");
            extraJson["cutTemplateId"] = "7054065762675313931";
            extraJson["abortWhenCutTemplateUnavailable"] = true;
            extraJson["videoTopics"] = videoTopics;
            extraJson["hashtag_list"] = videoTopics;
            extraJson["video_title"] = "StarkSDK Demo";
            shareJson["extra"] = extraJson;
            m_StarkGameRecorder.ShareVideoWithJson(OnShareVideoSuccess, OnShareVideoFailed, OnShareVideoCancelled, shareJson);
        }

        private void OnShareLocalVideo()
        {
            StartCoroutine(CopyVideoAndShareIt());
        }

        //用于将视频文件从streamingAssets中拷到cache/StarkContainer下
        IEnumerator CopyVideoAndShareIt()
        {
            Debug.Log("streamingAssetsPath " + Application.streamingAssetsPath);
            Debug.Log("temporaryCachePath " + Application.temporaryCachePath);

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
                    JsonData json = new JsonData();
                    json["channel"] = "video";
                    json["title"] = "ASoul AR摄影棚";

                    JsonData topic = new JsonData();
                    topic.Add("Asoul");
                    topic.Add("AR");

                    JsonData extra = new JsonData();
                    extra["defaultBgm"] = null;
                    extra["videoPath"] = targetPath;
                    extra["videoTopics"] = topic;
                    extra["hashtag_list"] = topic;

                    json["extra"] = extra;

                    Debug.Log(json.ToJson());

                    StarkSDK.API.GetStarkShare().ShareAppMessage(
                        OnShareVideoSuccess,
                        OnShareVideoFailed,
                        OnShareVideoCancelled,
                        json);
                }
                else
                    Debug.LogError(targetPath + " is not exist");
            }
        }

        private void OnShareVideoSuccess(Dictionary<String, Object> result)
        {
            Log.Debug(TAG, "OnShareVideoSuccess " + result);
            if (result.ContainsKey("videoId"))
                m_VideoIdText.text = result["videoId"].ToString();
            else
                m_VideoIdText.text = "Undefined";
        }

        private void OnShareVideoFailed(string errMsg)
        {
            Log.Error(TAG, "OnShareVideoFailed - errMsg: " + errMsg);
        }

        private void OnShareVideoCancelled()
        {
            Log.Debug(TAG, "OnShareVideoCancelled");
        }

        private void Reset()
        {
            m_StartTime = DateTime.Now;
            m_Counter = 0;
            m_ClipRanges.Clear();
            m_VideoPathText.text = "";
            m_ClipPathText.text = "";
        }

        private void OnRecordStart()
        {
            Reset();
            Log.Info(TAG, "OnRecordStart");
        }

        private void OnRecordPause()
        {
            Log.Info(TAG, "OnRecordPause");
        }

        private void OnRecordResume()
        {
            Log.Info(TAG, "OnRecordResume");
        }

        private void OnRecordComplete(string videoPath)
        {
            Log.Info(TAG, "OnRecordComplete - videoPath: {0}, video duration: {1} s", videoPath, m_StarkGameRecorder.GetRecordDuration() / 1000.0f);
            StarkUIManager.ShowToast($"OnRecordComplete - videoPath: {videoPath}, video duration: {m_StarkGameRecorder.GetRecordDuration() / 1000.0f} s");
            m_VideoPathText.text = videoPath;
            m_MaxRecordTime = 0;
        }

        private void OnRecordError(int errCode, string errMsg)
        {
            Log.Info(TAG, "OnRecordError - errCode: {0}, errMsg: {1}", errCode, errMsg);
            StarkUIManager.ShowToast($"OnRecordError - errCode: {errCode}, errMsg: {errMsg}");
        }

        private void OnRecordTimeout(string videoPath)
        {
            Log.Info(TAG, "OnRecordTimeout - videoPath: {0}, video duration: {1} s", videoPath, m_StarkGameRecorder.GetRecordDuration() / 1000.0f);
            StarkUIManager.ShowToast($"OnRecordTimeout - videoPath: {videoPath}, video duration: {m_StarkGameRecorder.GetRecordDuration() / 1000.0f} s");
            m_VideoPathText.text = videoPath;
            m_MaxRecordTime = 0;
        }

        public static void Shuffle<T>(IList<T> list)
        {
            RNGCryptoServiceProvider provider = new RNGCryptoServiceProvider();
            int n = list.Count;
            while (n > 1)
            {
                byte[] box = new byte[1];
                do provider.GetBytes(box);
                while (!(box[0] < n * (Byte.MaxValue / n)));
                int k = (box[0] % n);
                n--;
                T value = list[k];
                list[k] = list[n];
                list[n] = value;
            }
        }
        
        private void OnSetIntervalButtonTapped()
        {
            m_StarkGameRecorder.SetCustomKeyFrameInterval(300, b =>
            {
                print("设置间隔成功 " + b);
                m_VideoPathText.text = "设置间隔成功 " + b;
            });
        }
    }

    #region Log
    class Log
    {
        private enum LogType
        {
            DEBUG,
            INFO,
            WARNING,
            ERROR,
        }

        public static void Debug(string tag, string message, params object[] args)
        {
            UnityEngine.Debug.Log(GetFormatMessageWithTAG(tag, LogType.DEBUG, message, args));
        }

        public static void Info(string tag, string message, params object[] args)
        {
            string msg = GetFormatMessageWithTAG(tag, LogType.INFO, message, args);

            UnityEngine.Debug.Log(msg);
        }

        public static void Warning(string tag, string message, params object[] args)
        {
            string msg = GetFormatMessageWithTAG(tag, LogType.WARNING, message, args);

            UnityEngine.Debug.LogWarning(msg);
        }

        public static void Error(string tag, string message, params object[] args)
        {
            string msg = GetFormatMessageWithTAG(tag, LogType.ERROR, message, args);

            UnityEngine.Debug.LogError(msg);
        }

        private static string GetFormatMessageWithTAG(string tag, LogType logType, string message, params object[] args)
        {
            System.Text.StringBuilder sb = new System.Text.StringBuilder();
            if (message == null)
            {
                message = "";
            }
            sb.Append(logType.ToString()).Append("/").Append(tag).Append(": ");
            sb.Append(string.Format(message, args));
            return sb.ToString();
        }
    }
    #endregion
}