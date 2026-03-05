using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;

/// <summary>
/// Responsible for generating the grid of colored squares and
/// handling the player's selection.
/// </summary>
public class LevelController : MonoBehaviour
{
    [Header("UI References")]
    public Text levelLabel;            // "第 x 关"
    public RectTransform gridParent;   // container for blocks
    public GameObject blockPrefab;     // simple UI Image prefab
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

    private void Start()
    {
        SetupLevel(GameData.CurrentLevel);
    }

    private void SetupLevel(int level)
    {
        levelLabel.text = $"第 {level} 关";
        ComputeGridSize(level);
        GenerateColors(level);
        BuildGrid();
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
        // clear previous
        foreach (Transform t in gridParent)
            Destroy(t.gameObject);

        var grid = gridParent.gameObject.AddComponent<GridLayoutGroup>();
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

    private void OnBlockClicked(int r, int c)
    {
        bool correct = (r == oddPosition.x && c == oddPosition.y);
        ShowResult(correct);
    }

    private void ShowResult(bool success)
    {
        // could load another scene or activate a popup
        SceneManager.LoadScene("ResultScene");
        ResultController.LastLevelSuccess = success;
    }
}
