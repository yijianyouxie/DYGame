import asyncio
import aiohttp
import json

async def add_components_to_leaderboard():
    """使用 MCP 为排行榜对象添加组件"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🎯 开始添加组件到排行榜对象 ===\n")
        
        try:
            # ========== 初始化连接 ==========
            print("🔌 初始化连接...")
            init_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "component-adder",
                        "version": "1.0.0"
                    }
                }
            }
            
            session_id = None
            async with session.post(url, headers=base_headers, json=init_message) as response:
                session_id = response.headers.get('mcp-session-id')
                print(f"✅ Session ID: {session_id}")
                
                if not session_id:
                    return
                
                if response.status == 200:
                    async for line in response.content:
                        if line.decode('utf-8').strip().startswith('data:'):
                            break
            
            headers_with_session = {**base_headers, 'mcp-session-id': session_id}
            
            # 发送 initialized
            await session.post(url, headers=headers_with_session, json={
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            })
            
            # ========== 查询 manage_components 工具定义 ==========
            print("\n📋 查询 manage_components 工具...")
            tools_list_call = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            components_tool = None
            async with session.post(url, headers=headers_with_session, json=tools_list_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'result' in data and 'tools' in data['result']:
                                components_tool = next((t for t in data['result']['tools'] if t['name'] == 'manage_components'), None)
                                if components_tool:
                                    print(f"✅ 找到 manage_components 工具")
                                    print(f"   描述：{components_tool.get('description', '')[:100]}")
                                    
                                    input_schema = components_tool.get('inputSchema', {})
                                    properties = input_schema.get('properties', {})
                                    if 'action' in properties:
                                        action_enum = properties['action'].get('enum', [])
                                        print(f"   可用 actions: {action_enum}")
                            break
            
            if not components_tool:
                print("⚠️ 未找到 manage_components 工具，尝试使用 manage_gameobject 的 modify action")
            
            await asyncio.sleep(0.5)
            
            # ========== 使用 manage_gameobject 的 modify action 添加组件 ==========
            print("\n📐 使用 modify action 添加组件...")
            
            # 定义需要添加组件的对象列表
            objects_to_modify = [
                {
                    "name": "LeaderboardPanel",
                    "components": ["RectTransform", "CanvasRenderer", "Image", "LeaderboardUI"]
                },
                {
                    "name": "CloseButton",
                    "components": ["RectTransform", "Button", "Text"]
                },
                {
                    "name": "ScrollContainer",
                    "components": ["RectTransform"]
                },
                {
                    "name": "RankItemPrefab",
                    "components": ["RectTransform", "CanvasRenderer", "Image", "LeaderboardRankItem"]
                },
                {
                    "name": "Background",
                    "components": ["RectTransform", "Image"]
                },
                {
                    "name": "RankText",
                    "components": ["RectTransform", "Text"]
                },
                {
                    "name": "NameText",
                    "components": ["RectTransform", "Text"]
                },
                {
                    "name": "LevelText",
                    "components": ["RectTransform", "Text"]
                }
            ]
            
            for obj_info in objects_to_modify:
                obj_name = obj_info["name"]
                components = obj_info["components"]
                
                print(f"\n➕ 为 {obj_name} 添加组件:")
                
                for component in components:
                    # 使用 modify action 和 components_to_add 参数
                    modify_call = {
                        "jsonrpc": "2.0",
                        "id": 3,
                        "method": "tools/call",
                        "params": {
                            "name": "manage_gameobject",
                            "arguments": {
                                "action": "modify",
                                "target": obj_name,
                                "search_method": "by_name",
                                "components_to_add": [component]
                            }
                        }
                    }
                    
                    async with session.post(url, headers=headers_with_session, json=modify_call) as response:
                        if response.status == 200:
                            async for line in response.content:
                                line_text = line.decode('utf-8').strip()
                                if line_text.startswith('data:'):
                                    data = json.loads(line_text[5:])
                                    if 'error' in data:
                                        print(f"      ⚠️ {component}: 失败 - {data['error']}")
                                    elif 'result' in data:
                                        print(f"      ✅ {component}: 成功")
                                    break
                    
                    await asyncio.sleep(0.2)
            
            print("\n=== ✅ 组件添加完成 ===\n")
            print("📋 检查结果：")
            print("在 Unity Inspector 中查看以下对象是否有所需组件:")
            print()
            print("✓ LeaderboardPanel:")
            print("  - RectTransform, CanvasRenderer, Image, LeaderboardUI")
            print("  ├─ CloseButton (RectTransform, Button, Text)")
            print("  └─ ScrollContainer (RectTransform)")
            print()
            print("✓ RankItemPrefab:")
            print("  - RectTransform, CanvasRenderer, Image, LeaderboardRankItem")
            print("  ├─ Background (RectTransform, Image)")
            print("  ├─ RankText (RectTransform, Text)")
            print("  ├─ NameText (RectTransform, Text)")
            print("  └─ LevelText (RectTransform, Text)")
            print()
            print("下一步操作：")
            print("1. 保存预制件更新（右键 → Create Prefab）")
            print("2. 配置 LeaderboardUI 组件的引用字段")
            print("3. 调整 UI 布局和 Text 内容")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(add_components_to_leaderboard())
