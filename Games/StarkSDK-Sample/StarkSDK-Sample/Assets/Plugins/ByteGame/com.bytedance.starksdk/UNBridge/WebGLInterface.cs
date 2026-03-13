using System.Runtime.InteropServices;
using UnityEngine.Scripting;

[assembly: Preserve]

namespace StarkSDKSpace.UNBridgeLib
{
    public class WebGLInterface
    {
#if UNITY_WEBPLAYER || UNITY_WEBGL
        //以下接口为Web使用，用于调用JS代码。
        [method: Preserve]
        [DllImport("__Internal")]
        public static extern void unityCallJs(string msg);

        [method: Preserve]
        [DllImport("__Internal")]
        public static extern string unityCallJsSync(string msg);

        [method: Preserve]
        [DllImport("__Internal")]
        public static extern bool h5HasAPI(string apiName);

        [method: Preserve]
        [DllImport("__Internal")]
        public static extern string unityMixCallJs(string msg);
#endif
    }
}