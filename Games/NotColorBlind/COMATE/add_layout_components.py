"""
添加布局组件到排行榜的 ScrollContainer
解决排行榜项都堆在 (0,0) 位置的问题
"""
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))
from mcp_init import init_session, call_tool

def main():
    # 初始化 MCP
    session_id = init_session()
    if not session_id:
        print("[FAIL] 无法初始化 MCP 连接")
        return

    print("已连接到 Unity MCP")

    # 1. 加载 LeaderboardPanel Prefab
    print("\n1. 加载 LeaderboardPanel Prefab...")
    result = call_tool('unity.open_asset', {
        'path': 'Assets/Prefabs/LeaderboardPanel.prefab'
    })

    if result.get('error'):
        print(f"[FAIL] 加载 Prefab 失败: {result['error']}")
        return

    print("[OK] Prefab 加载成功")

    # 2. 给 ScrollContainer 添加 VerticalLayoutGroup 组件
    print("\n2. 给 ScrollContainer 添加 VerticalLayoutGroup 组件...")
    result = call_tool('unity.add_component', {
        'target': 6153998875634657607,  # ScrollContainer 的 ID
        'component': 'UnityEngine.UI.VerticalLayoutGroup'
    })

    if result.get('error'):
        print(f"[FAIL] 添加 VerticalLayoutGroup 失败: {result['error']}")
        return

    vlg_id = result.get('id')
    print(f"[OK] VerticalLayoutGroup 组件已添加，ID: {vlg_id}")

    # 3. 给 ScrollContainer 添加 ContentSizeFitter 组件
    print("\n3. 给 ScrollContainer 添加 ContentSizeFitter 组件...")
    result = call_tool('unity.add_component', {
        'target': 6153998875634657607,  # ScrollContainer 的 ID
        'component': 'UnityEngine.UI.ContentSizeFitter'
    })

    if result.get('error'):
        print(f"[FAIL] 添加 ContentSizeFitter 失败: {result['error']}")
        return

    csf_id = result.get('id')
    print(f"[OK] ContentSizeFitter 组件已添加，ID: {csf_id}")

    # 4. 配置 VerticalLayoutGroup 的属性
    print("\n4. 配置 VerticalLayoutGroup 属性...")
    vlg_properties = {
        'childAlignment': 0,  # UpperLeft (0)
        'childControlHeight': True,
        'childControlWidth': True,
        'childForceExpandHeight': False,
        'childForceExpandWidth': True,
        'spacing': 10.0  # 子项之间的间距
    }

    for prop_name, prop_value in vlg_properties.items():
        result = call_tool('unity.set_property', {
            'target': vlg_id,
            'property': prop_name,
            'value': prop_value
        })

        if result.get('error'):
            print(f"  [WARN] 设置 {prop_name} 失败: {result['error']}")
        else:
            print(f"  [OK] {prop_name} = {prop_value}")

    # 5. 配置 ContentSizeFitter 的属性
    print("\n5. 配置 ContentSizeFitter 属性...")
    csf_properties = {
        'verticalFit': 2,  # Preferred Size (2)
        'horizontalFit': 0  # Unconstrained (0)
    }

    for prop_name, prop_value in csf_properties.items():
        result = call_tool('unity.set_property', {
            'target': csf_id,
            'property': prop_name,
            'value': prop_value
        })

        if result.get('error'):
            print(f"  [WARN] 设置 {prop_name} 失败: {result['error']}")
        else:
            print(f"  [OK] {prop_name} = {prop_value}")

    # 6. 保存 Prefab
    print("\n6. 保存 LeaderboardPanel Prefab...")
    result = call_tool('unity.save', {
        'path': 'Assets/Prefabs/LeaderboardPanel.prefab'
    })

    if result.get('error'):
        print(f"[FAIL] 保存 Prefab 失败: {result['error']}")
        return

    print("[OK] Prefab 已保存")

    print("\n" + "="*50)
    print("[OK] 完成！已为排行榜 ScrollContainer 添加布局组件")
    print("="*50)
    print("\n已添加的组件:")
    print("  - VerticalLayoutGroup: 垂直排列子项，间距 10")
    print("  - ContentSizeFitter: 根据内容自动调整大小")
    print("\n现在排行榜项应该会自动垂直排列了。")

if __name__ == "__main__":
    main()
