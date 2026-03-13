using System;
using UnityEngine;
using UnityEngine.UI;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;
using StarkSDKSpace;
using StarkSDKSpace.UNBridgeLib.LitJson;
using UnityEngine.Networking;

public class PayServiceTest : MonoBehaviour
{
    private Text m_LogText;
    private InputField m_InputPrice;

    class RequestResult
    {
        public int ErrCode;
        public string ErrMsg = "ok";
        public string Data = "";
    }

    private void Start()
    {
        m_LogText = transform.Find("ScrollView/Viewport/LogPanel/Text")?.GetComponent<Text>();
        //m_InputPrice = transform.Find("ScrollView/Viewport/Content/Price/InputField")?.GetComponent<InputField>();
        //transform.Find("ScrollView/Viewport/Content/CheckoutAlipay")?.GetComponent<Button>().onClick
        //    .AddListener(OnCheckoutAlipayButtonTapped);
        //transform.Find("ScrollView/Viewport/Content/CheckoutWechat")?.GetComponent<Button>().onClick
        //    .AddListener(OnCheckoutWechatButtonTapped);
        //transform.Find("ScrollView/Viewport/Content/Wechat")?.GetComponent<Button>().onClick
        //    .AddListener(OnWechatButtonTapped);
        //transform.Find("ScrollView/Viewport/Content/Alipay")?.GetComponent<Button>().onClick
        //    .AddListener(OnAlipayButtonTapped);
        //transform.Find("ScrollView/Viewport/Content/OrderInfoTest")?.GetComponent<Button>().onClick
        //    .AddListener(OnOrderInfoTestButtonTapped);
        transform.Find("ScrollView/Viewport/Content/CleanLog")?.GetComponent<Button>().onClick
            .AddListener(OnCleanLogButtonTapped);
        //transform.Find("ScrollView/Viewport/Content/Init")?.GetComponent<Button>().onClick
        //    .AddListener(PayInit);
        transform.Find("ScrollView/Viewport/Content/MiniGamePay")?.GetComponent<Button>().onClick
            .AddListener(OnMiniGamePayButtonTapped);
    }

    private int GetInputPrice()
    {
        if (m_InputPrice == null || string.IsNullOrEmpty(m_InputPrice.text))
        {
            return 1;
        }

        int price = Int32.Parse(m_InputPrice.text);
        return price;
    }

    //private void OnCheckoutAlipayButtonTapped()
    //{
    //    int price = GetInputPrice();
    //    CallPay(StarkPayService.PayServiceType.Checkout, price);
    //}

    //private void OnCheckoutWechatButtonTapped()
    //{
    //    int price = GetInputPrice();
    //    CallPay(StarkPayService.PayServiceType.Checkout, price, StarkPayService.PayChannel.Wechat);
    //}

    //private void OnWechatButtonTapped()
    //{
    //    int price = GetInputPrice();
    //    CallPay(StarkPayService.PayServiceType.Wechat, price);
    //}

    int payIndex = 0;

    private void OnMiniGamePayButtonTapped()
    {
        if (CanIUse.StarkPayService.RequestGamePayment)
        {
            Dictionary<string, object> orderInfoParams = new Dictionary<string, object>();
            orderInfoParams["mode"] = "game";
            orderInfoParams["env"] = "0";
            orderInfoParams["currencyType"] = "CNY"; // 固定值: CNY。币种
            orderInfoParams["platform"] = "android";
            orderInfoParams["buyQuantity"] = 1;
            orderInfoParams["customId"] = (TimeUtils.GetCurrentTimeMs() / 1000).ToString();

            StarkSDK.API.GetStarkPayService().RequestGamePayment(
                orderInfoParams,
                () =>
                {
                    PrintText("Pay Success " + orderInfoParams["customId"]);
                },
                (errCode, errMsg) =>
                {
                    PrintText("Pay failed - errCode: " + errCode + ", errMsg: " + errMsg, true);
                }
                );
        }
    }

    //private void OnOrderInfoTestButtonTapped()
    //{
    //    var orderInfo = GenerateOrderInfo();
    //    StarkSDK.API.GetStarkPayService().Pay(orderInfo,
    //        StarkPayService.PayServiceType.Checkout,
    //        StarkPayService.PayChannel.Alipay,
    //        (orderNo, tradeTime) =>
    //        {
    //            int i = payIndex;
    //            PrintText("GetOrderStatus - orderNo: " + orderNo + ", i = " + i);
    //            if (i % 6 == 0) return StarkPayService.PayStatus.PaySuccess;
    //            if (i % 6 == 1) return StarkPayService.PayStatus.PayCancel;
    //            if (i % 6 == 2) return StarkPayService.PayStatus.PayClosed;
    //            if (i % 6 == 3) return StarkPayService.PayStatus.PayFailed;
    //            if (i % 6 == 4) return StarkPayService.PayStatus.PayTimeout;
    //            return StarkPayService.PayStatus.PayUnknown;
    //        },
    //        payStatus =>
    //        {
    //            ++payIndex;
    //            Debug.Log("Pay callback - status: " + payStatus);
    //            AndroidUIManager.ShowToast("payStatus: " + payStatus);
    //            PrintText("payStatus: " + payStatus);
    //        }, (errCode, errMsg) =>
    //        {
    //            PrintText(
    //                "Pay failed - errCode: " + errCode + ", errMsg: " + errMsg, true);
    //        }
    //    );
    //}

    //private void OnAlipayButtonTapped()
    //{
    //    int price = GetInputPrice();
    //    CallPay(StarkPayService.PayServiceType.Alipay, price);
    //}

    private void OnCleanLogButtonTapped()
    {
        if (m_LogText != null)
        {
            m_LogText.text = "";
        }
    }

    //private void PayInit()
    //{
    //    StarkSDK.API.GetStarkPayService().PayModuleInit();
    //}

    //private void CallPay(StarkPayService.PayServiceType service, int totalAmount,
    //    StarkPayService.PayChannel payChannel = StarkPayService.PayChannel.Alipay)
    //{
    //    string url = "https://tp-pay.snssdk.com/cashdesk/apitest/createmicoapporder";
    //    string appId = "800000040005";
    //    string merchantId = "1300000004";
    //    var reqParams = new Dictionary<string, object>();
    //    reqParams["service"] = 1;
    //    reqParams["totalAmount"] = totalAmount;
    //    reqParams["appId"] = appId;
    //    reqParams["merchantId"] = merchantId;
    //    reqParams["isOffline"] = 0;
    //    PrintText("Request order info... service: " + service + ", amount: " + totalAmount);
    //    RequestOrderInfo(url, reqParams, response =>
    //    {
    //        Debug.Log("RequestOrderInfo success, response: " + response);
    //        PrintText("Request success");
    //        string orderInfo = GetOrderInfoFromResponse(response);
    //        if (string.IsNullOrEmpty(orderInfo))
    //        {
    //            PrintText("Failed to get orderInfo from response", true);
    //            return;
    //        }

    //        //StarkSDK.API.GetStarkPayService().Pay(orderInfo,
    //        //    service, payChannel,
    //        //    (orderNo, tradeTime) =>
    //        //    {
    //        //        int i = payIndex;
    //        //        PrintText("GetOrderStatus - orderNo: " + orderNo + ", tradeTime: " + tradeTime + ", i = " + i);
    //        //        if (i % 6 == 0) return StarkPayService.PayStatus.PaySuccess;
    //        //        if (i % 6 == 1) return StarkPayService.PayStatus.PayCancel;
    //        //        if (i % 6 == 2) return StarkPayService.PayStatus.PayClosed;
    //        //        if (i % 6 == 3) return StarkPayService.PayStatus.PayFailed;
    //        //        if (i % 6 == 4) return StarkPayService.PayStatus.PayTimeout;
    //        //        return StarkPayService.PayStatus.PayUnknown;
    //        //    },
    //        //    payStatus =>
    //        //    {
    //        //        ++payIndex;
    //        //        Debug.Log("Pay callback - status: " + payStatus);
    //        //        AndroidUIManager.ShowToast("payStatus: " + payStatus);
    //        //        PrintText("payStatus: " + payStatus);
    //        //    }, (errCode, errMsg) =>
    //        //    {
    //        //        ++payIndex;
    //        //        PrintText("Pay failed - errCode: " + errCode + ", errMsg: " + errMsg, true);
    //        //    }
    //        //);
    //    }, errMsg => { PrintText("RequestOrderInfo failed, error: " + errMsg, true); });
    //}

    //private async void RequestOrderInfo(string url,
    //    Dictionary<string, object> requestParams,
    //    Action<string> onSuccess,
    //    Action<string> onError)
    //{
    //    var result = await PostRequestOrderInfo(url, requestParams);
    //    if (result.ErrCode == 0)
    //    {
    //        onSuccess?.Invoke(result.Data);
    //    }
    //    else
    //    {
    //        onError?.Invoke(result.ErrMsg);
    //    }
    //}

    //private async Task<RequestResult> PostRequestOrderInfo(string url,
    //    Dictionary<string, object> otherParams = null)
    //{
    //    WWWForm form = new WWWForm();
    //    AddParams(form, otherParams);
    //    RequestResult result = new RequestResult();
    //    using (UnityWebRequest www = UnityWebRequest.Post(url, form))
    //    {
    //        var ret = www.SendWebRequest();
    //        while (!ret.isDone)
    //        {
    //            await Task.Yield();
    //        }

    //        if (www.isNetworkError || www.isHttpError)
    //        {
    //            result.ErrCode = -1;
    //            result.ErrMsg = www.error;
    //            Debug.Log("Request error: " + www.error);
    //        }
    //        else
    //        {
    //            result.Data = www.downloadHandler.text;
    //            Debug.Log("response: " + result.Data);
    //        }
    //    }

    //    return result;
    //}

    //private void AddParams(WWWForm form, Dictionary<string, object> otherParams)
    //{
    //    if (otherParams == null)
    //    {
    //        return;
    //    }

    //    foreach (var key in otherParams.Keys)
    //    {
    //        var t = otherParams[key].GetType();
    //        if (t == typeof(int))
    //        {
    //            form.AddField(key, (int) otherParams[key]);
    //        }
    //        else if (t == typeof(long))
    //        {
    //            long v = (long) otherParams[key];
    //            form.AddField(key, (int) v);
    //        }
    //        else if (t == typeof(string))
    //        {
    //            form.AddField(key, otherParams[key].ToString());
    //        }
    //    }
    //}

    //private string GetOrderInfoFromResponse(string response)
    //{
    //    JsonData jsonData = GetJsonDataFromString(response);
    //    if (jsonData == null)
    //    {
    //        PrintText("Failed to parse json data", true);
    //        return null;
    //    }

    //    if (!JsonDataUtils.TryToGetValue<int>(jsonData, "code", out var code))
    //    {
    //        PrintText("Invalid json data", true);
    //        return null;
    //    }

    //    if (code != 0)
    //    {
    //        PrintText("RequestOrderInfo failed, error code: " + code, true);
    //        return null;
    //    }

    //    string orderInfo;
    //    if (JsonDataUtils.TryToGetValue<JsonData>(jsonData, "data", out var orderInfoJson))
    //    {
    //        orderInfo = orderInfoJson.ToJson();
    //    }
    //    else if (!JsonDataUtils.TryToGetValue<string>(jsonData, "data", out orderInfo))
    //    {
    //        PrintText("RequestOrderInfo failed from json data", true);
    //        return null;
    //    }

    //    return orderInfo;
    //}

    private JsonData GetJsonDataFromString(string json)
    {
        try
        {
            JsonData jsonData = JsonMapper.ToObject(json);
            return jsonData;
        }
        catch (Exception e)
        {
            PrintText(e.Message, true);
            return null;
        }
    }

    private void PrintText(string msg, bool isError = false)
    {
        if (isError)
        {
            Debug.LogError(msg);
        }
        else
        {
            Debug.Log(msg);
        }

        if (m_LogText != null)
        {
            if (isError)
            {
                msg = "<color=red>" + msg + "</color>";
            }

            m_LogText.text = m_LogText.text + msg + "\n";
        }
    }

    //private string GenerateOrderInfo()
    //{
    //    string appSecretKey = "a";
    //    var nowTimeSec = TimeUtils.GetCurrentTimeMs() / 1000;
    //    SortedDictionary<string, object> orderInfoParams = new SortedDictionary<string, object>();
    //    orderInfoParams["merchant_id"] = "1300000004"; // 开发者后台支付设置页的商户号
    //    orderInfoParams["app_id"] = "800000040005"; // 开发者后台支付设置页的 app_id
    //    orderInfoParams["sign_type"] = "MD5"; // 固定值：MD5。商户生成签名的算法类型
    //    orderInfoParams["timestamp"] = nowTimeSec; // 发送请求的时间戳，精确到秒
    //    orderInfoParams["version"] = "2.0"; // 固定值：2.0
    //    orderInfoParams["trade_type"] = "H5"; // 固定值：H5
    //    orderInfoParams["product_code"] = "pay"; // 固定值：pay
    //    orderInfoParams["payment_type"] = "direct"; // 固定值：direct
    //    orderInfoParams["out_order_no"] = "MicroApp7075638135"; // 商户订单号
    //    orderInfoParams["uid"] = "2019012211"; // 用户唯一标识
    //    orderInfoParams["total_amount"] = 1; // 金额，整型，单位：分（不能有小数）
    //    orderInfoParams["currency"] = "CNY"; // 固定值: CNY。币种
    //    orderInfoParams["subject"] = "microapp test"; // 商户订单名称
    //    orderInfoParams["body"] = "microapp test"; // 商户订单名称
    //    orderInfoParams["trade_time"] =
    //        nowTimeSec; // 下单时间戳，精确到秒。如果两次支付(调用 tt.pay)传入的订单号(out_order_no)相同，则必须保证 trade_time 也相同
    //    orderInfoParams["valid_time"] = 300; // 订单有效时间（单位 秒）
    //    orderInfoParams["notify_url"] =
    //        "https://tp-pay.snssdk.com/cashdesk/test/paycallback"; // 固定值：https://tp-pay.snssdk.com/paycallback

    //    // 调用支付宝 App 支付所需的支付请求参数，详见支付宝 App 支付请求参数说明。service=1 时，如不传则不展示支付宝支付；service=4 时必传。
    //    orderInfoParams["alipay_url"] =
    //        "alipay_sdk=alipay-sdk-java-3.4.27.ALL&app_id=2018061460417275&biz_content=%7B%22body%22%3A%22%E6%B5%8B%E8%AF%95%E8%AE%A2%E5%8D%95%22%2C%22extend_params%22%3A%7B%7D%2C%22out_trade_no%22%3A%2211908250000028453790%22%2C%22product_code%22%3A%22QUICK_MSECURITY_PAY%22%2C%22seller_id%22%3A%222088721387102560%22%2C%22subject%22%3A%22%E6%B5%8B%E8%AF%95%E8%AE%A2%E5%8D%95%22%2C%22timeout_express%22%3A%22599m%22%2C%22total_amount%22%3A%220.01%22%7D&charset=utf-8&format=json&method=alipay.trade.app.pay&notify_url=http%3A%2F%2Fapi-test-pcs.snssdk.com%2Fgateway%2Fpayment%2Fcallback%2Falipay%2Fnotify%2Fpay&sign=D2A6ua51os2aIzIH907ppK7Bd9Q2Kk5h7AtKPdudP%2Be%2BNTtAkp0Lfojtgl4BMOIQ3Z7cWyYMx6nk4qbntSx7aZnBhWAcImLbVVr1cmaYAedmrmJG%2B3f8G5TfAZu53ESzUgk02%2FhU1XV0iXRyE8TdEJ97ufmxwsUEc7K0EvwEFDIBCJg73meQtyCRFgCqYRWvmxetQgL7pwfKXpFXjAYsvFrRBas2YGYt689XpBS321g%2BZ8SZ0JOtLPWqhROzEs3dnAtWBW15y3NzRiSNi5rPzah4cWd4SgT0LZHmNf3eDQEHEcPmofoWfnA4ao75JmP95aLUxerMumzo9OwqhiYOUw%3D%3D&sign_type=RSA2&timestamp=2019-08-25+16%3A11%3A22&version=1.0";

    //    // 调用微信 H5 支付统一下单接口 返回的 mweb_url 字段值（请注意不要进行 urlencode）service=1 时，如不传则不展示微信支付；service=3 时必传。
    //    orderInfoParams["wx_url"] =
    //        "https://wx.tenpay.com/cgi-bin/mmpayweb-bin/checkmweb?prepay_id=wx25161122572189727ea14cfd1832451500&package=2746219290";

    //    orderInfoParams["wx_type"] = "MWEB"; // wx_url 非空时传 'MWEB'。wx_url 为空时，该字段不传
    //    orderInfoParams["risk_info"] = "{\"ip\":\"127.0.0.1\"}"; // 支付风控参数。序列化后的 JSON 结构字符串，JSON 结构如下：{ip: "用户外网IP"}

    //    string unsignedStr = GetUnsignedString(orderInfoParams);
    //    string sign = CalculateMD5(unsignedStr + appSecretKey);
    //    orderInfoParams["sign"] = sign;
    //    var json = JsonMapper.ToJson(orderInfoParams);
    //    string orderInfo = json;
    //    Debug.Log(unsignedStr);
    //    Debug.Log(sign);
    //    Debug.Log(orderInfo);
    //    return orderInfo;
    //}

    //private string GetUnsignedString(SortedDictionary<string, object> orderInfoParams)
    //{
    //    List<string> items = new List<string>();
    //    StringBuilder builder = new StringBuilder();
    //    foreach (var item in orderInfoParams)
    //    {
    //        if (item.Key.Equals("risk_info") || item.Key.Equals("sign")) // risk_info和sign不参与签名
    //        {
    //            continue;
    //        }

    //        if (item.Value is string)
    //        {
    //            builder.Append("\"" + item.Key + "\": \"" + item.Value + "\",\n");
    //        }
    //        else
    //        {
    //            builder.Append("\"" + item.Key + "\": " + item.Value + ",\n");
    //        }

    //        items.Add(item.Key + "=" + item.Value);
    //    }

    //    return string.Join("&", items);
    //}

    //public static string CalculateMD5(string input)
    //{
    //    // Use input string to calculate MD5 hash
    //    using (System.Security.Cryptography.MD5 md5 = System.Security.Cryptography.MD5.Create())
    //    {
    //        byte[] inputBytes = Encoding.ASCII.GetBytes(input);
    //        byte[] hashBytes = md5.ComputeHash(inputBytes);

    //        // Convert the byte array to hexadecimal string
    //        StringBuilder sb = new StringBuilder();
    //        for (int i = 0; i < hashBytes.Length; i++)
    //        {
    //            sb.Append(hashBytes[i].ToString("x2"));
    //        }

    //        return sb.ToString();
    //    }
    //}
}