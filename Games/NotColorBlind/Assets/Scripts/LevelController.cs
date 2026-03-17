using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;
using System.Collections;

/// <summary>
/// Responsible for generating the grid of colored squares and
/// handling the player's selection.
/// </summary>
public class LevelController : MonoBehaviour
{
    [Header("UI References")]
    public Text levelLabel;            // "第 x 关"
    public Text countdownText;         // countdown display
    public Image sandClockIcon;        // sand clock icon
    public RectTransform gridParent;   // container for blocks
    public GameObject blockPrefab;     // simple UI Image prefab
    public Button busyCoinButton;      // 忙币按钮
    public Text busyCoinCountText;     // 忙币数量显示
    public Button returnButton;         // 返回按钮
    [Header("Effects")]
    public GameObject successEffectPrefab; // 成功特效预制件
    public Text comboText;             // 连击次数显示文本（作为 Prefab 引用）
    public float effectDuration = 0.5f; // 特效持续时间
    [Header("Effect Settings")]
    public float effectScale = 10f;    // 特效缩放倍数（UI Canvas 适配）
    public int effectRenderTextureSize = 1024; // 特效渲染到UI的RT尺寸
    public Vector2 effectOverlaySize = new Vector2(700f, 700f); // UI上显示的特效尺寸
    [Header("Board Background")]
    public Image boardBackground;      // optional Image to use as board background
    public Color boardColor = Color.white;
    public Vector2 boardPadding = new Vector2(10, 10);

    // parameters that change with difficulty
    private int rows;
    private int cols;
    private Color commonColor;
    private Color oddColor;
    private Vector2Int oddPosition;
    private float countdownDuration = 10f; // temporary fixed 10s
    private bool hasSelected = false;
    
    // 忙币相关
    private bool hasUsedBusyCoin = false; // 是否已经使用过忙币
    private GameObject highlightedBlock; // 当前高亮的块
    
    // 倒计时协程引用，用于提前停止倒计时
    private Coroutine countdownCoroutine;
    // 运行时实例化出来的连击文本
    private Text runtimeComboText;

    private void Start()
    {
        SetupLevel(GameData.CurrentLevel);
        
        // 检查特效预制件是否赋值
        if (successEffectPrefab == null)
        {
            Debug.LogError("[LevelController] successEffectPrefab 未赋值！请在 Inspector 中拖拽 Assets/Effects/FireworksEffect.prefab");
        }
        else
        {
            Debug.Log($"[LevelController] 成功特效预制件已加载：{successEffectPrefab.name}");
        }
    }

    private void SetupLevel(int level)
    {
        levelLabel.text = $"第 {level} 关";
        ComputeGridSize(level);
        GenerateColors(level);
        BuildGrid();
        hasSelected = false;
        hasUsedBusyCoin = false;
        highlightedBlock = null;
        UpdateBusyCoinUI();
        
        // 准备/隐藏连击文本（从 Prefab 实例化到 Canvas 下）
        Canvas canvas = FindObjectOfType<Canvas>();
        if (comboText != null && canvas != null)
        {
            if (runtimeComboText == null)
            {
                runtimeComboText = Instantiate(comboText, canvas.transform);
                runtimeComboText.gameObject.name = "ComboText(Runtime)";
            }
            runtimeComboText.gameObject.SetActive(false);
        }
        
        // 添加忙币按钮事件监听
        if (busyCoinButton != null)
        {
            busyCoinButton.onClick.RemoveAllListeners();
            busyCoinButton.onClick.AddListener(OnBusyCoinClicked);
        }
        
        // 添加返回按钮事件监听
        if (returnButton != null)
        {
            returnButton.onClick.RemoveAllListeners();
            returnButton.onClick.AddListener(OnReturnClicked);
        }
        
        // 启动倒计时并保存协程引用
        countdownCoroutine = StartCoroutine(StartCountdown());
    }

    private void ComputeGridSize(int level)
    {
        // example progression: start 2x2, grow until 12x10
        rows = Mathf.Min(2 + (level / 3), 12);
        cols = Mathf.Min(2 + (level / 4), 10);
        // ensure at least 2x2 and rows>cols
        rows = Mathf.Max(2, rows);
        cols = Mathf.Max(2, cols);
        if (cols >= rows)
            cols = Mathf.Max(2, rows - 1);
    }

    private void GenerateColors(int level)
    {
        // seed the random generator with the level so colors/position are repeatable
        var prevState = Random.state;
        Random.InitState(level * 7919 + 137); // arbitrary primes to decorrelate from other usage

        // choose a base hue and saturation/value deterministically
        float baseHue = Random.Range(0f, 1f);
        float sat = Random.Range(0.6f, 1f);
        float val = Random.Range(0.6f, 1f);
        commonColor = Color.HSVToRGB(baseHue, sat, val);
        
        // compute how different the odd block should be by adjusting saturation/value
        // difference shrinks as level grows (closer colors at higher levels)
        float satDiff = Mathf.Lerp(0.3f, 0.01f, (float)level / GameData.MaxLevels);
        float valDiff = Mathf.Lerp(0.3f, 0.01f, (float)level / GameData.MaxLevels);
        float oddSat = Mathf.Clamp01(sat + Random.Range(-satDiff, satDiff));
        float oddVal = Mathf.Clamp01(val + Random.Range(-valDiff, valDiff));
        oddColor = Color.HSVToRGB(baseHue, oddSat, oddVal);
        
        // ensure not identical due to rounding
        if (oddColor == commonColor)
        {
            oddVal = Mathf.Clamp01(val + 0.02f);
            oddColor = Color.HSVToRGB(baseHue, oddSat, oddVal);
        }
        
        // pick odd position deterministically
        oddPosition = new Vector2Int(Random.Range(0, rows), Random.Range(0, cols));

        // restore previous random state so other code is unaffected
        Random.state = prevState;
    }

    private void BuildGrid()
    {
        // 检查 gridParent 是否赋值
        if (gridParent == null)
        {
            Debug.LogError("[LevelController] gridParent is null! Please assign it in Inspector.");
            return;
        }
        
        // clear previous
        foreach (Transform t in gridParent)
            Destroy(t.gameObject);

        // 检查是否已经存在 GridLayoutGroup，如果存在则复用，否则添加新的
        var grid = gridParent.GetComponent<GridLayoutGroup>();
        if (grid == null)
        {
            grid = gridParent.gameObject.AddComponent<GridLayoutGroup>();
        }
        grid.constraint = GridLayoutGroup.Constraint.FixedColumnCount;
        grid.constraintCount = cols;
        // small spacing between blocks
        grid.spacing = new Vector2(2,2);
        // base size for each cell
        float cell = 75f;
        // compute full grid dimensions based on current cell size and spacing
        float totalW = cols * cell + (cols - 1) * grid.spacing.x;
        float totalH = rows * cell + (rows - 1) * grid.spacing.y;
        
        // if width exceeds threshold, shrink cells so that width == 700
        if (totalW > 700f)
        {
            cell = (700f - (cols - 1) * grid.spacing.x) / cols;
            totalW = cols * cell + (cols - 1) * grid.spacing.x;
            totalH = rows * cell + (rows - 1) * grid.spacing.y;
        }
        
        // adjust container size to match grid
        gridParent.sizeDelta = new Vector2(totalW, totalH);
        
        grid.cellSize = new Vector2(cell, cell);

        // ensure board background exists and matches size (plus padding)
        Vector2 boardSize = new Vector2(totalW + boardPadding.x * 2f, totalH + boardPadding.y * 2f);
        if (boardBackground == null)
        {
            // create a background Image under the same parent as gridParent
            var parent = gridParent.parent as RectTransform;
            if (parent != null)
            {
                var bgGO = new GameObject("BoardBackground", typeof(RectTransform), typeof(CanvasRenderer), typeof(Image));
                bgGO.transform.SetParent(parent, false);
                var bgRect = bgGO.GetComponent<RectTransform>();
                // match anchors/pivot/position to gridParent for easy alignment
                bgRect.anchorMin = gridParent.anchorMin;
                bgRect.anchorMax = gridParent.anchorMax;
                bgRect.pivot = gridParent.pivot;
                bgRect.anchoredPosition = gridParent.anchoredPosition;
                bgRect.sizeDelta = boardSize;
                var img = bgGO.GetComponent<Image>();
                img.color = boardColor;
                // place background behind gridParent
                int gridIndex = gridParent.GetSiblingIndex();
                bgGO.transform.SetSiblingIndex(gridIndex);
                gridParent.SetSiblingIndex(gridIndex + 1);
                boardBackground = img;
            }
        }
        else
        {
            var bgRect = boardBackground.GetComponent<RectTransform>();
            if (bgRect != null)
            {
                bgRect.sizeDelta = boardSize;
                bgRect.anchoredPosition = gridParent.anchoredPosition;
            }
            boardBackground.color = boardColor;
        }
        // note: prefab can include an Outline component or border image if needed

        for (int r = 0; r < rows; r++)
        {
            for (int c = 0; c < cols; c++)
            {
                var blockGo = Instantiate(blockPrefab, gridParent);
                var img = blockGo.GetComponent<Image>();
                img.color = (r == oddPosition.x && c == oddPosition.y) ? oddColor : commonColor;
                var button = blockGo.GetComponent<Button>();
                int rr = r, cc = c;
                button.onClick.AddListener(() => OnBlockClicked(rr, cc));
            }
        }
    }

    private IEnumerator StartCountdown()
    {
        float timeLeft = countdownDuration;
        while (timeLeft > 0)
        {
            countdownText.text = $"倒计时:{Mathf.Ceil(timeLeft)}";
            if (sandClockIcon != null)
            {
                sandClockIcon.transform.Rotate(0, 0, 180);
            }
            yield return new WaitForSeconds(1f);
            timeLeft -= 1f;
        }
        countdownText.text = "倒计时:0";
        if (!hasSelected)
        {
            ShowResult(false);
        }
    }

    private void OnBlockClicked(int r, int c)
    {
        if (hasSelected) return; // prevent multiple clicks
        hasSelected = true;
        bool correct = (r == oddPosition.x && c == oddPosition.y);
        
        // 停止倒计时
        if (countdownCoroutine != null)
        {
            StopCoroutine(countdownCoroutine);
            countdownCoroutine = null;
        }
        
        // 如果使用了忙币且选择正确，扣除忙币
        if (correct && hasUsedBusyCoin)
        {
            DeductBusyCoin();
        }
        
        if (correct)
        {
            // 答对，增加连续答对次数
            GameData.ConsecutiveCorrect++;
            
            // 保存玩家进度到云数据库
            LeaderboardManager.Instance.SavePlayerProgress(GameData.CurrentLevel);
            
            ShowSuccessEffect();
        }
        else
        {
            // 答错，重置连续答对次数
            GameData.ConsecutiveCorrect = 0;
            ShowResult(false);
        }
    }

    private void ShowResult(bool success)
    {
        if (success)
        {
            // 成功时直接进入下一关
            GameData.CurrentLevel++;
            if (GameData.CurrentLevel > GameData.MaxLevels)
            {
                GameData.CurrentLevel = 1; // 循环到第一关
            }
            SetupLevel(GameData.CurrentLevel);
        }
        else
        {
            // 失败时切换到结果场景
            SceneManager.LoadScene("ResultScene");
            ResultController.LastLevelSuccess = success;
        }
    }
    
    // 显示成功特效
    private void ShowSuccessEffect()
    {
        StartCoroutine(ShowSuccessEffectCoroutine());
    }
    
    private IEnumerator ShowSuccessEffectCoroutine()
    {
        // 注意：LevelScene 的 Canvas 是 Screen Space - Overlay，普通 3D 粒子会被 UI 覆盖导致 Game 视图“看不到”
        // 这里使用“特效相机 + RenderTexture + RawImage”的方式，把粒子渲染到 UI 顶层显示。
        const int effectLayer = 31; // 使用一个空闲层（无需命名）

        RenderTexture rt = null;
        GameObject camGo = null;
        GameObject overlayGo = null;
        GameObject effect = null;

        Canvas canvas = FindObjectOfType<Canvas>();
        if (successEffectPrefab == null)
        {
            Debug.LogError("[LevelController] ❌ successEffectPrefab 为空！请在 Inspector 中赋值");
        }
        else if (canvas == null)
        {
            Debug.LogError("[LevelController] ❌ 未找到Canvas，无法显示UI特效!");
        }
        else
        {
            // 1) 创建 RenderTexture
            int rtSize = Mathf.Clamp(effectRenderTextureSize, 256, 2048);
            rt = new RenderTexture(rtSize, rtSize, 16, RenderTextureFormat.ARGB32)
            {
                name = "SuccessEffectRT"
            };
            rt.Create();

            // 2) 创建相机，只渲染 effectLayer，并输出到 RT（透明背景）
            camGo = new GameObject("SuccessEffectCamera");
            Camera cam = camGo.AddComponent<Camera>();
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(0f, 0f, 0f, 0f);
            cam.cullingMask = 1 << effectLayer;
            cam.orthographic = true;
            cam.orthographicSize = 12f;
            cam.nearClipPlane = 0.01f;
            cam.farClipPlane = 100f;
            cam.targetTexture = rt;
            camGo.transform.position = new Vector3(0f, 0f, -10f);
            camGo.transform.rotation = Quaternion.identity;

            // 3) 创建 UI 叠加层，把 RT 贴到最上层
            overlayGo = new GameObject("SuccessEffectOverlay", typeof(RectTransform), typeof(CanvasRenderer), typeof(RawImage));
            overlayGo.transform.SetParent(canvas.transform, false);
            RawImage overlay = overlayGo.GetComponent<RawImage>();
            overlay.raycastTarget = false;
            overlay.texture = rt;
            RectTransform overlayRect = overlayGo.GetComponent<RectTransform>();
            overlayRect.anchorMin = new Vector2(0.5f, 0.5f);
            overlayRect.anchorMax = new Vector2(0.5f, 0.5f);
            overlayRect.anchoredPosition = Vector2.zero;
            overlayRect.sizeDelta = effectOverlaySize;
            overlayGo.transform.SetAsLastSibling();

            // 4) 实例化特效到世界中，并放到 effectLayer 上（让相机只渲染它）
            effect = Instantiate(successEffectPrefab);
            effect.name = successEffectPrefab.name + "(Runtime)";
            SetLayerRecursively(effect, effectLayer);
            effect.transform.position = Vector3.zero;
            effect.transform.rotation = Quaternion.identity;
            effect.transform.localScale = Vector3.one * Mathf.Max(0.01f, effectScale * 0.1f);

            // 5) 播放所有粒子系统（包含子发射器）
            var systems = effect.GetComponentsInChildren<ParticleSystem>(true);
            if (systems == null || systems.Length == 0)
            {
                Debug.LogError("[LevelController] ❌ 成功特效预制件中未找到 ParticleSystem 组件!");
            }
            else
            {
                foreach (var ps in systems)
                {
                    ps.Play(true);
                }
            }
        }
        
        // 显示连击次数
        if (runtimeComboText != null && GameData.ConsecutiveCorrect > 1)
        {
            runtimeComboText.gameObject.SetActive(true);
            runtimeComboText.text = $"{GameData.ConsecutiveCorrect} 杀";
            runtimeComboText.transform.SetAsLastSibling(); // 确保在最上层显示
            
            // 动画效果
            runtimeComboText.transform.localScale = Vector3.zero;
            float elapsed = 0f;
            while (elapsed < effectDuration * 0.5f)
            {
                elapsed += Time.deltaTime;
                float t = elapsed / (effectDuration * 0.5f);
                runtimeComboText.transform.localScale = Vector3.Lerp(Vector3.zero, Vector3.one * 5f, t);
                yield return null;
            }
            
            // 等待一段时间
            yield return new WaitForSeconds(effectDuration * 0.5f);
            
            runtimeComboText.gameObject.SetActive(false);
        }
        else
        {
            yield return new WaitForSeconds(effectDuration);
        }

        if (effect != null) Destroy(effect);
        if (camGo != null) Destroy(camGo);
        if (overlayGo != null) Destroy(overlayGo);
        if (rt != null)
        {
            rt.Release();
            Destroy(rt);
        }
        
        // 特效显示完成后进入下一关
        ShowResult(true);
    }

    private static void SetLayerRecursively(GameObject root, int layer)
    {
        if (root == null) return;
        root.layer = layer;
        foreach (Transform t in root.transform)
        {
            if (t != null)
                SetLayerRecursively(t.gameObject, layer);
        }
    }
    
    // 忙币按钮点击事件
    private void OnBusyCoinClicked()
    {
        if (hasSelected || hasUsedBusyCoin || GameData.BusyCoinCount <= 0)
        {
            return; // 已经选择过答案、已经使用过忙币或没有忙币
        }
        
        // 高亮显示不同的色块并闪动3次
        HighlightOddBlock();
        hasUsedBusyCoin = true;
    }
    
    // 高亮显示不同的色块
    private void HighlightOddBlock()
    {
        // 找到不同的色块
        Transform[] blocks = gridParent.GetComponentsInChildren<Transform>();
        foreach (Transform block in blocks)
        {
            if (block != gridParent)
            {
                // 计算这个块的位置
                int siblingIndex = block.GetSiblingIndex();
                int row = siblingIndex / cols;
                int col = siblingIndex % cols;
                
                if (row == oddPosition.x && col == oddPosition.y)
                {
                    highlightedBlock = block.gameObject;
                    StartCoroutine(FlashBlock(highlightedBlock));
                    break;
                }
            }
        }
    }
    
    // 闪动效果协程
    private IEnumerator FlashBlock(GameObject block)
    {
        Image blockImage = block.GetComponent<Image>();
        if (blockImage == null) yield break;
        
        Color originalColor = blockImage.color;
        Color highlightColor = Color.white; // 高亮颜色，可以根据需要调整
        
        // 闪动3次
        for (int i = 0; i < 3; i++)
        {
            // 高亮
            blockImage.color = highlightColor;
            yield return new WaitForSeconds(0.1f);
            
            // 恢复原始颜色
            blockImage.color = originalColor;
            yield return new WaitForSeconds(0.1f);
        }
    }
    
    // 扣除忙币（在玩家选择正确答案后调用）
    private void DeductBusyCoin()
    {
        if (hasUsedBusyCoin && GameData.BusyCoinCount > 0)
        {
            GameData.BusyCoinCount--;
            UpdateBusyCoinUI();
            Debug.Log("扣除 1 个忙币，剩余：" + GameData.BusyCoinCount);
        }
    }
    
    // 观看广告增加忙币（暂时模拟，后续接入广告 SDK）
    public void AddBusyCoinFromAd(int amount = 1)
    {
        GameData.BusyCoinCount += amount;
        UpdateBusyCoinUI();
        Debug.Log("观看广告获得" + amount + "个忙币，当前总数：" + GameData.BusyCoinCount);
    }
    
    // 更新忙币 UI 显示
    private void UpdateBusyCoinUI()
    {
        if (busyCoinCountText != null)
        {
            busyCoinCountText.text = GameData.BusyCoinCount.ToString();
        }
    }
    
    /// <summary>
    /// 返回按钮点击事件
    /// </summary>
    private void OnReturnClicked()
    {
        // 停止倒计时
        if (countdownCoroutine != null)
        {
            StopCoroutine(countdownCoroutine);
            countdownCoroutine = null;
        }
        
        // 返回主菜单
        SceneManager.LoadScene("Start");
    }
}
