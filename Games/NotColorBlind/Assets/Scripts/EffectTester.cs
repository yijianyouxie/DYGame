using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Simple test script to manually trigger success effects for testing
/// </summary>
public class EffectTester : MonoBehaviour
{
    public GameObject successEffectPrefab;
    public Text comboText; // 作为 Prefab 引用
    public float effectDuration = 1f;

    private Text runtimeComboText;

    void Update()
    {
        // Press 'T' to test success effect
        if (Input.GetKeyDown(KeyCode.T))
        {
            Debug.Log("[EffectTester] Testing success effect...");
            StartCoroutine(ShowSuccessEffectCoroutine());
        }

        // Press 'C' to test combo text
        if (Input.GetKeyDown(KeyCode.C))
        {
            Debug.Log("[EffectTester] Testing combo text...");
            ShowComboText(5);
        }
    }

    private System.Collections.IEnumerator ShowSuccessEffectCoroutine()
    {
        // 显示烟花特效
        if (successEffectPrefab != null)
        {
            // 查找Canvas
            Canvas canvas = FindObjectOfType<Canvas>();
            if (canvas != null)
            {
                // 创建特效
                GameObject effect = Instantiate(successEffectPrefab, canvas.transform);

                // 检查是否为UI元素（有RectTransform）还是3D对象（有Transform）
                RectTransform effectRect = effect.GetComponent<RectTransform>();
                if (effectRect != null)
                {
                    // UI元素处理
                    // 设置为屏幕中心位置
                    effectRect.anchorMin = new Vector2(0.5f, 0.5f);
                    effectRect.anchorMax = new Vector2(0.5f, 0.5f);
                    effectRect.anchoredPosition = Vector2.zero;
                    effectRect.sizeDelta = new Vector2(400, 400); // 设置合适的大小

                    // 确保在UI层级的最上层
                    effectRect.SetAsLastSibling();

                    Debug.Log("[EffectTester] 🎆 成功特效已创建为UI元素!");
                    Debug.Log($"   UI位置：{effectRect.anchoredPosition}");
                }
                else
                {
                    // 3D对象处理 - 转换为UI元素
                    Debug.Log("[EffectTester] 🔄 检测到3D特效，转换为UI元素...");

                    // 移除Transform，添加RectTransform
                    Transform oldTransform = effect.GetComponent<Transform>();
                    Vector3 localPosition = oldTransform.localPosition;
                    Quaternion localRotation = oldTransform.localRotation;
                    Vector3 localScale = oldTransform.localScale;

                    // 销毁旧的Transform
                    DestroyImmediate(oldTransform);

                    // 添加RectTransform
                    RectTransform newRectTransform = effect.AddComponent<RectTransform>();
                    newRectTransform.localPosition = localPosition;
                    newRectTransform.localRotation = localRotation;
                    newRectTransform.localScale = localScale;

                    // 设置为屏幕中心位置
                    newRectTransform.anchorMin = new Vector2(0.5f, 0.5f);
                    newRectTransform.anchorMax = new Vector2(0.5f, 0.5f);
                    newRectTransform.anchoredPosition = Vector2.zero;
                    newRectTransform.sizeDelta = new Vector2(400, 400);

                    // 确保在UI层级的最上层
                    newRectTransform.SetAsLastSibling();

                    Debug.Log("[EffectTester] ✅ 3D特效已转换为UI元素!");
                    Debug.Log($"   UI位置：{newRectTransform.anchoredPosition}");

                    effectRect = newRectTransform;
                }

                // 获取 ParticleSystem 组件
                ParticleSystem ps = effect.GetComponent<ParticleSystem>();
                if (ps != null)
                {
                    // 设置为UI渲染模式
                    ParticleSystemRenderer renderer = ps.GetComponent<ParticleSystemRenderer>();
                    if (renderer != null)
                    {
                        renderer.renderMode = ParticleSystemRenderMode.Billboard;
                        Debug.Log("   🎨 设置为Billboard渲染模式");
                    }

                    // 自动播放
                    if (!ps.isPlaying)
                    {
                        ps.Play();
                        Debug.Log("   ▶️ 已启动粒子系统");
                    }
                }
                else
                {
                    Debug.LogError("   ❌ 未找到 ParticleSystem 组件!");
                }

                // 销毁特效
                Destroy(effect, effectDuration);
                Debug.Log($"   ⏱️ 特效将在 {effectDuration} 秒后自动销毁");
            }
            else
            {
                Debug.LogError("[EffectTester] ❌ 未找到Canvas，无法显示UI特效!");
            }
        }
        else
        {
            Debug.LogError("[EffectTester] ❌ successEffectPrefab 为空！请在 Inspector 中赋值");
        }

        yield return null;
    }

    private void ShowComboText(int comboCount)
    {
        if (comboCount > 1)
        {
            if (runtimeComboText == null && comboText != null)
            {
                Canvas canvas = FindObjectOfType<Canvas>();
                if (canvas != null)
                {
                    runtimeComboText = Instantiate(comboText, canvas.transform);
                    runtimeComboText.gameObject.name = "ComboText(Runtime-Tester)";
                }
            }

            if (runtimeComboText == null)
            {
                Debug.LogError("[EffectTester] comboText Prefab 未正确实例化，无法显示连击文本");
                return;
            }

            runtimeComboText.gameObject.SetActive(true);
            runtimeComboText.text = $"{comboCount} 杀";
            runtimeComboText.transform.SetAsLastSibling(); // 确保在最上层显示

            // 动画效果
            runtimeComboText.transform.localScale = Vector3.zero;
            StartCoroutine(AnimateComboText());
        }
    }

    private System.Collections.IEnumerator AnimateComboText()
    {
        float elapsed = 0f;
        float animationDuration = effectDuration * 0.5f;

        while (elapsed < animationDuration)
        {
            elapsed += Time.deltaTime;
            float t = elapsed / animationDuration;
            if (runtimeComboText != null)
            {
                runtimeComboText.transform.localScale = Vector3.Lerp(Vector3.zero, Vector3.one * 1.5f, t);
            }
            yield return null;
        }

        // 等待一段时间
        yield return new WaitForSeconds(effectDuration * 0.5f);

        if (runtimeComboText != null)
        {
            runtimeComboText.gameObject.SetActive(false);
        }
    }
}