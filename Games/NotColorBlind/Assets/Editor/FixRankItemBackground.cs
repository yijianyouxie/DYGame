using UnityEngine;
using UnityEngine.UI;

namespace NotColorBlind.Editor
{
    public class FixRankItemBackground : MonoBehaviour
    {
        [ContextMenu("Add Image to Background")]
        private void AddImageToBackground()
        {
            // 查找 Background 子对象
            Transform backgroundTransform = transform.Find("Background");
            
            if (backgroundTransform == null)
            {
                Debug.LogError("未找到 Background 子对象！");
                return;
            }
            
            // 检查是否已有 Image 组件
            Image image = backgroundTransform.GetComponent<Image>();
            
            if (image != null)
            {
                Debug.Log("Background 已经有 Image 组件了");
                return;
            }
            
            // 添加 Image 组件
            image = backgroundTransform.gameObject.AddComponent<Image>();
            image.color = new Color(1, 1, 1, 1); // 默认白色
            
            Debug.Log("成功为 Background 添加 Image 组件");
        }
    }
}
