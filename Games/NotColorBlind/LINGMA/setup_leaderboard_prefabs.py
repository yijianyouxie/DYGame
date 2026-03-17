import asyncio
import aiohttp
import json

async def setup_leaderboard_prefabs():
    """使用 MCP 为排行榜预设添加脚本和子对象 - 修正版"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🎯 开始配置排行榜预设（修正参数错误）===\n")
        
        try:
            # ========== 步骤 1: 初始化并获取 Session ID ==========
            print("🔌 步骤 1: 初始化连接...")
            init_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "leaderboard-setup",
                        "version": "1.0.0"
                    }
                }
            }
            
            session_id = None
            async with session.post(url, headers=base_headers, json=init_message) as response:
                session_id = response.headers.get('mcp-session-id')
                print(f"✅ Session ID: {session_id}")
                
                if not session_id:
                    print("❌ 无法获取 Session ID")
                    return
                
                if response.status == 200:
                    async for line in response.content:
                        if line.decode('utf-8').strip().startswith('data:'):
                            break
            
            headers_with_session = {**base_headers, 'mcp-session-id': session_id}
            
            # ========== 步骤 2: 发送 initialized 通知 ==========
            print("\n📋 步骤 2: 发送 initialized 通知...")
            await session.post(url, headers=headers_with_session, json={
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            })
            print("✅ 完成\n")
            
            # ========== 步骤 3: 查询工具列表获取正确参数 ==========
            print("📋 步骤 3: 查询工具定义...")
            tools_list_call = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            async with session.post(url, headers=headers_with_session, json=tools_list_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'result' in data and 'tools' in data['result']:
                                # 查找 manage_gameobject 工具的定义
                                gameobject_tool = next((t for t in data['result']['tools'] if t['name'] == 'manage_gameobject'), None)
                                if gameobject_tool:
                                    print("\n✅ manage_gameobject 工具定义:")
                                    print(f"   描述：{gameobject_tool.get('description', '')}")
                                    
                                    # 打印可用的 actions
                                    input_schema = gameobject_tool.get('inputSchema', {})
                                    properties = input_schema.get('properties', {})
                                    if 'action' in properties:
                                        action_enum = properties['action'].get('enum', [])
                                        print(f"   可用 actions: {action_enum}")
                                    
                                    # 打印其他参数
                                    print(f"   其他参数：{list(properties.keys())}")
                            break
            
            await asyncio.sleep(0.5)
            
            # ========== 步骤 4: 创建 CloseButton 子对象 ==========
            print("\n🔘 步骤 4: 创建 CloseButton 子对象...")
            create_button_call = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "manage_gameobject",
                    "arguments": {
                        "action": "create",
                        "name": "CloseButton",
                        "parent": "LeaderboardPanel"  # 修正：使用 'parent' 而不是 'parent_path'
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=create_button_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'result' in data:
                                print("✅ CloseButton 创建成功")
                            break
            
            await asyncio.sleep(0.5)
            
            # ========== 步骤 5: 创建 ScrollContainer 子对象 ==========
            print("\n📦 步骤 5: 创建 ScrollContainer 子对象...")
            create_scroll_call = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "manage_gameobject",
                    "arguments": {
                        "action": "create",
                        "name": "ScrollContainer",
                        "parent": "LeaderboardPanel"
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=create_scroll_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'result' in data:
                                print("✅ ScrollContainer 创建成功")
                            break
            
            await asyncio.sleep(0.5)
            
            # ========== 步骤 6: 为 RankItemPrefab 创建子元素 ==========
            print("\n👶 步骤 6: 为 RankItemPrefab 创建子元素...")
            
            child_elements = ["Background", "RankText", "NameText", "LevelText"]
            
            for element_name in child_elements:
                print(f"\n   - 创建 {element_name}...")
                create_child_call = {
                    "jsonrpc": "2.0",
                    "id": 5,
                    "method": "tools/call",
                    "params": {
                        "name": "manage_gameobject",
                        "arguments": {
                            "action": "create",
                            "name": element_name,
                            "parent": "RankItemPrefab"
                        }
                    }
                }
                
                async with session.post(url, headers=headers_with_session, json=create_child_call) as response:
                    if response.status == 200:
                        async for line in response.content:
                            line_text = line.decode('utf-8').strip()
                            if line_text.startswith('data:'):
                                data = json.loads(line_text[5:])
                                if 'result' in data:
                                    print(f"      ✅ {element_name} 创建成功")
                                break
                
                await asyncio.sleep(0.3)
            
            print("\n=== ✅ MCP 调用完成 ===\n")
            print("📋 重要说明：")
            print("MCP 的 manage_gameobject 工具不支持 'add_component' action")
            print("需要使用 Unity 编辑器手动添加组件，或使用其他方法")
            print()
            print("下一步操作：")
            print("1. 在 Unity Hierarchy 中查看创建的 GameObject")
            print("2. 手动为各对象添加所需的组件:")
            print("   • LeaderboardPanel: RectTransform, CanvasRenderer, Image, LeaderboardUI 脚本")
            print("   • CloseButton: RectTransform, Button, Text")
            print("   • ScrollContainer: RectTransform")
            print("   • RankItemPrefab: RectTransform, CanvasRenderer, Image, LeaderboardRankItem 脚本")
            print("   • Background: RectTransform, Image")
            print("   • RankText/NameText/LevelText: RectTransform, Text")
            print()
            print("3. 保存预制件更新")
            print("4. 在 Inspector 中配置 LeaderboardUI 组件的引用字段")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(setup_leaderboard_prefabs())
