import asyncio
import aiohttp
import json

async def add_scripts_correctly():
    """使用正确的参数添加脚本组件"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🎯 使用正确参数添加脚本 ===\n")
        
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
                        "name": "script-adder",
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
            print("\n📋 查询 manage_components 工具的正确参数...")
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
                                components_tool = next((t for t in data['result']['tools'] if t['name'] == 'manage_components'), None)
                                if components_tool:
                                    print("\n✅ manage_components 工具定义:")
                                    input_schema = components_tool.get('inputSchema', {})
                                    properties = input_schema.get('properties', {})
                                    
                                    print(f"   可用 actions: {properties.get('action', {}).get('enum', [])}")
                                    print(f"   必需参数:")
                                    for key, value in properties.items():
                                        if isinstance(value, dict):
                                            print(f"      • {key}: {value.get('type', 'unknown')} - {value.get('description', '')[:50]}")
                            break
            
            await asyncio.sleep(0.5)
            
            # ========== 使用正确的参数添加脚本 ==========
            print("\n🎨 开始添加脚本组件（使用正确的参数）...")
            
            # LeaderboardPanel 添加 LeaderboardUI 脚本
            print("\n为 LeaderboardPanel 添加 LeaderboardUI 脚本:")
            add_script_call = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "manage_components",
                    "arguments": {
                        "action": "add",
                        "target": "LeaderboardPanel",
                        "search_method": "by_name",
                        "component_type": "LeaderboardUI"  # 使用 component_type 而不是 component
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=add_script_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'error' in data:
                                print(f"   ⚠️ 失败：{data['error']}")
                            elif 'result' in data:
                                print(f"   ✅ LeaderboardUI 脚本添加成功!")
                            break
            
            await asyncio.sleep(0.5)
            
            # RankItemPrefab 添加 LeaderboardRankItem 脚本
            print("\n为 RankItemPrefab 添加 LeaderboardRankItem 脚本:")
            add_rank_script_call = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "manage_components",
                    "arguments": {
                        "action": "add",
                        "target": "RankItemPrefab",
                        "search_method": "by_name",
                        "component_type": "LeaderboardRankItem"
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=add_rank_script_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'error' in data:
                                print(f"   ⚠️ 失败：{data['error']}")
                            elif 'result' in data:
                                print(f"   ✅ LeaderboardRankItem 脚本添加成功!")
                            break
            
            await asyncio.sleep(0.5)
            
            # 为子对象添加 Unity 内置组件（如果还没有）
            print("\n🔧 检查并完善子对象组件...")
            
            child_components = [
                ("CloseButton", "Button"),
                ("CloseButton", "Text"),
                ("ScrollContainer", "RectTransform"),
                ("Background", "Image"),
                ("RankText", "Text"),
                ("NameText", "Text"),
                ("LevelText", "Text")
            ]
            
            for obj_name, comp_type in child_components:
                print(f"\n为 {obj_name} 添加 {comp_type}...")
                add_comp_call = {
                    "jsonrpc": "2.0",
                    "id": 5,
                    "method": "tools/call",
                    "params": {
                        "name": "manage_components",
                        "arguments": {
                            "action": "add",
                            "target": obj_name,
                            "search_method": "by_name",
                            "component_type": comp_type
                        }
                    }
                }
                
                async with session.post(url, headers=headers_with_session, json=add_comp_call) as response:
                    if response.status == 200:
                        async for line in response.content:
                            line_text = line.decode('utf-8').strip()
                            if line_text.startswith('data:'):
                                data = json.loads(line_text[5:])
                                if 'error' in data:
                                    print(f"   ⚠️ {comp_type}: {data['error']}")
                                elif 'result' in data:
                                    print(f"   ✅ {comp_type}: 成功")
                                break
                
                await asyncio.sleep(0.2)
            
            print("\n=== ✅ 所有脚本和组件添加完成 ===\n")
            print("📋 请在 Unity Inspector中验证:")
            print()
            print("1. LeaderboardPanel:")
            print("   ✓ LeaderboardUI 脚本 ✓")
            print("   ├─ CloseButton (Button + Text)")
            print("   └─ ScrollContainer (RectTransform)")
            print()
            print("2. RankItemPrefab:")
            print("   ✓ LeaderboardRankItem 脚本 ✓")
            print("   ├─ Background (Image)")
            print("   ├─ RankText (Text)")
            print("   ├─ NameText (Text)")
            print("   └─ LevelText (Text)")
            print()
            print("下一步操作:")
            print("1. 在 Unity 中查看 Hierarchy，确认所有组件都已挂接")
            print("2. 配置 LeaderboardUI 组件的引用字段")
            print("3. 保存预制件更新（拖拽到 Assets/Prefabs/并替换）")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(add_scripts_correctly())
