using UnityEngine;

public class ExampleCube : MonoBehaviour
{
    private GameObject _cube;

    void Awake()
    {
        _cube = GameObject.CreatePrimitive(PrimitiveType.Cube);
        Reset();
    }

    public void Reset()
    {
        if (_cube != null)
        {
            _cube.transform.position = new Vector3(0, 1f, 0.0f);
            _cube.transform.localScale = new Vector3(1.5f, 1.5f, 1.5f);
            _cube.transform.rotation = Quaternion.identity;
        }
    }

    public void Rotate(float xAngle = 1, float yAngle = 1, float zAngle = 1)
    {
        _cube?.transform?.Rotate(xAngle, yAngle, zAngle, Space.Self);
    }

    public void Show()
    {
        _cube?.SetActive(true);
    }
    
    public void Hide()
    {
        _cube?.SetActive(false);
    }
}