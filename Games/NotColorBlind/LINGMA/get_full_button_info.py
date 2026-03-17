#!/usr/bin/env python3
"""
获取Start场景中LeaderboardButton的完整配置信息
"""
import json
import httpx

async def call_tool(session, url, headers, tool_name, arguments, tool_id=1):
    """调用MCP工具"""
    response = await session.post(url, headers=headers, json={
        "jsonrpc": "2.0",
        "id": tool_id,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    })
    result = response.json()
    return result.get("result")

async def get_resource(session, url, headers, uri, resource_id=1):
    """获取资源"""
    response = await session.get(f"{url}/{uri}", headers=headers)
    if response.status_code != 200:
        print(f"  ❌ 获取资源失败 ({uri}): {response.status_code}")
        return None
    result = response.json()
    
    # 解析text字段中的JSON
    if result.get("result", {}).get("contents"):
        content = result["result"]["contents"][0]
        text = content.get("text", "")
        if text:
            return json.loads(text)
    return result

async def main():
    session = httpx.AsyncClient(timeout=60)
    
    # 从文件读取MCP session信息，去除BOM
    with open("mcp-session-id.txt", "r", encoding="utf-8-sig") as f:
        mcp_session_id = f.read().strip()
    
    url = f"http://localhost:{mcp_session_id}/sse"
    headers = {"Accept": "application/json"}
    
    print("=" * 80)
    print("获取Start场景中LeaderboardButton的完整配置")
    print("=" * 80)
    
    # 加载Start场景
    print("\n加载Start场景 (build_index: 0)...")
    result = await call_tool(session, url, headers, 'manage_scene', {
        'action': 'load',
        'build_index': 0
    }, tool_id=1)
    
    if result and result.get("success"):
        print("  ✅ 场景加载成功")
    else:
        print(f"  ❌ 场景加载失败: {result}")
        return
    
    # 查找LeaderboardButton
    print("\n查找LeaderboardButton...")
    result = await call_tool(session, url, headers, 'find_gameobjects', {
        'search_term': 'LeaderboardButton',
        'search_method': 'by_name'
    }, tool_id=2)
    
    button_ids = []
    if result and result.get("data", {}).get("instanceIDs"):
        button_ids = result["data"]["instanceIDs"]
        print(f"  ✅ 找到 {len(button_ids)} 个LeaderboardButton")
    
    if not button_ids:
        print("  ❌ 未找到LeaderboardButton")
        return
    
    button_id = str(button_ids[0])
    print(f"  使用按钮ID: {button_id}")
    
    # 获取按钮的完整组件信息
    print(f"\n获取按钮的组件信息...")
    uri = f"mcpforunity://scene/gameobject/{button_id}/components"
    data = await get_resource(session, url, headers, uri)
    
    if not data or not data.get("data", {}).get("components"):
        print(f"  ❌ 获取组件失败")
        return
    
    components = data["data"]["components"]
    print(f"\n按钮的 {len(components)} 个组件:")
    
    button_config = {
        "name": "LeaderboardButton",
        "components": {},
        "text_child": None
    }
    
    for comp in components:
        comp_type = comp.get("typeName", "")
        props = comp.get("properties", {})
        
        if comp_type == "UnityEngine.Transform":
            print(f"\n1. Transform组件:")
            button_config["components"]["Transform"] = props
        
        elif comp_type == "UnityEngine.RectTransform":
            print(f"\n2. RectTransform组件:")
            rect_info = {}
            for key in ["anchoredPosition", "sizeDelta", "anchorMin", "anchorMax", "pivot"]:
                if key in props:
                    print(f"   {key}: {props[key]}")
                    rect_info[key] = props[key]
            button_config["components"]["RectTransform"] = rect_info
        
        elif comp_type == "UnityEngine.UI.Image":
            print(f"\n3. Image组件:")
            image_info = {}
            sprite = props.get("sprite") or props.get("m_Sprite", {})
            if isinstance(sprite, str) and sprite:
                print(f"   sprite: {sprite}")
                image_info["sprite"] = sprite
            elif isinstance(sprite, dict):
                print(f"   sprite: {sprite}")
                image_info["sprite"] = sprite
            
            color = props.get("color") or props.get("m_Color")
            if color:
                print(f"   color: {color}")
                image_info["color"] = color
            
            type_val = props.get("type") or props.get("m_Type", "Simple")
            print(f"   type: {type_val}")
            image_info["type"] = type_val
            
            button_config["components"]["Image"] = image_info
        
        elif comp_type == "UnityEngine.UI.Button":
            print(f"\n4. Button组件:")
            button_info = {}
            target = props.get("onClick") or props.get("m_OnClick")
            if target:
                print(f"   onClick: {target}")
                button_info["onClick"] = target
            transition = props.get("transition") or props.get("m_Transition", "ColorTint")
            print(f"   transition: {transition}")
            button_info["transition"] = transition
            
            colors = props.get("colors") or props.get("m_Colors")
            if colors:
                print(f"   colors: {colors}")
                button_info["colors"] = colors
            
            button_config["components"]["Button"] = button_info
    
    # 保存配置到文件
    with open("button_config.json", "w", encoding="utf-8") as f:
        json.dump(button_config, f, indent=2, ensure_ascii=False)
    
    print(f"\n" + "=" * 80)
    print("配置已保存到 button_config.json")
    print("=" * 80)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
