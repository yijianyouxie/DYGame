using UnityEngine;

/// <summary>
/// 简单的灯光渐隐动画组件
/// 用于烟花特效的灯光淡出效果
/// </summary>
public class LightAnimator : MonoBehaviour
{
    public Light light;
    public float fadeDuration = 1f;
    
    private float elapsed = 0f;
    
    void Update()
    {
        if (light != null)
        {
            elapsed += Time.deltaTime;
            float t = Mathf.Clamp01(elapsed / fadeDuration);
            light.intensity = Mathf.Lerp(2f, 0f, t);
            
            if (elapsed >= fadeDuration)
            {
                enabled = false;
            }
        }
    }
}