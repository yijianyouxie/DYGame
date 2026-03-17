import asyncio
import aiohttp
import json

async def update_prefabs_from_hierarchy():
    """从 Hierarchy 更新预制件文件"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🎯 开始更新预制件文件 ===\n")
        
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
                        "name": "prefab-updater",
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
            
            # ========== 查询工具定义 ==========
            print("\n📋 查询 manage_gameobject 工具定义...")
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
                                gameobject_tool = next((t for t in data['result']['tools'] if t['name'] == 'manage_gameobject'), None)
                                if gameobject_tool:
                                    input_schema = gameobject_tool.get('inputSchema', {})
                                    properties = input_schema.get('properties', {})
                                    
                                    print("\n✅ manage_gameobject 参数:")
                                    if 'save_as_prefab' in properties:
                                        print(f"   save_as_prefab: {properties['save_as_prefab']}")
                                    if 'prefab_path' in properties:
                                        print(f"   prefab_path: {properties['prefab_path']}")
                                    if 'prefab_folder' in properties:
                                        print(f"   prefab_folder: {properties['prefab_folder']}")
                            break
            
            await asyncio.sleep(0.5)
            
            # ========== 使用 create action 重新创建预制件 ==========
            print("\n💾 重新创建 LeaderboardPanel.prefab...")
            create_panel_call = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "manage_gameobject",
                    "arguments": {
                        "action": "create",
                        "name": "LeaderboardPanel_Temp",  # 临时名称
                        "save_as_prefab": True,
                        "prefab_path": "Assets/Prefabs/LeaderboardPanel.prefab"
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=create_panel_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'error' in data:
                                print(f"⚠️ 创建失败：{data['error']}")
                            elif 'result' in data:
                                print("✅ LeaderboardPanel.prefab 创建成功")
                            break
            
            await asyncio.sleep(0.5)
            
            print("\n💾 重新创建 RankItemPrefab.prefab...")
            create_rank_call = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "manage_gameobject",
                    "arguments": {
                        "action": "create",
                        "name": "RankItemPrefab_Temp",
                        "save_as_prefab": True,
                        "prefab_path": "Assets/Prefabs/RankItemPrefab.prefab"
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=create_rank_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'error' in data:
                                print(f"⚠️ 创建失败：{data['error']}")
                            elif 'result' in data:
                                print("✅ RankItemPrefab.prefab 创建成功")
                            break
            
            await asyncio.sleep(0.5)
            
            # ========== 获取预制件信息 ==========
            print("\n🔍 获取预制件信息...")
            
            for prefab_name in ["LeaderboardPanel.prefab", "RankItemPrefab.prefab"]:
                prefab_path = f"Assets/Prefabs/{prefab_name}"
                get_info_call = {
                    "jsonrpc": "2.0",
                    "id": 5,
                    "method": "tools/call",
                    "params": {
                        "name": "manage_asset",
                        "arguments": {
                            "action": "get_info",
                            "path": prefab_path
                        }
                    }
                }
                
                async with session.post(url, headers=headers_with_session, json=get_info_call) as response:
                    if response.status == 200:
                        async for line in response.content:
                            line_text = line.decode('utf-8').strip()
                            if line_text.startswith('data:'):
                                data = json.loads(line_text[5:])
                                if 'result' in data and 'content' in data['result']:
                                    try:
                                        content = data['result']['content'][0]['text']
                                        result_data = json.loads(content)
                                        if result_data.get('success'):
                                            asset_info = result_data.get('data', {})
                                            components = asset_info.get('components', [])
                                            print(f"\n✅ {prefab_name}:")
                                            print(f"   组件数量：{len(components)}")
                                            if components:
                                                print(f"   组件列表:")
                                                for comp in components[:15]:
                                                    print(f"      • {comp}")
                                                if len(components) > 15:
                                                    print(f"      ... 还有 {len(components) - 15} 个组件")
                                        else:
                                            print(f"❌ {prefab_name}: 获取失败 - {result_data.get('message', '')}")
                                    except Exception as e:
                                        print(f"⚠️ 解析失败：{e}")
                                        print(f"   原始内容：{content[:200]}")
                                break
                
                await asyncio.sleep(0.3)
            
            print("\n=== ✅ 预制件更新完成 ===\n")
            print("📋 重要说明：")
            print("由于 MCP 的 save_as_prefab 参数需要配合 create action 使用，")
            print("我们使用了临时名称来触发预制件保存。")
            print()
            print("下一步操作（必须在 Unity 中手动完成）:")
            print("1. 在 Unity Project 窗口中查看 Assets/Prefabs/目录")
            print("2. 右键点击新的预制件文件 → Select")
            print("3. 在 Inspector 中确认所有组件都已正确保存")
            print("4. 如果预制件仍然缺少组件，请手动保存:")
            print("   a. 在 Hierarchy 中选中 GameObject")
            print("   b. 拖拽到 Project 窗口的 Assets/Prefabs/文件夹")
            print("   c. 选择覆盖现有预制件")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(update_prefabs_from_hierarchy())
