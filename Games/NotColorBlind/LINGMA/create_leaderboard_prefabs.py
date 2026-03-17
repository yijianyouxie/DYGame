import asyncio
import aiohttp
import json

async def create_leaderboard_system():
    """按照官方指南正确创建排行榜系统"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🎯 开始创建排行榜系统（遵循官方指南）===\n")
        
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
                        "name": "leaderboard-creator",
                        "version": "1.0.0"
                    }
                }
            }
            
            session_id = None
            async with session.post(url, headers=base_headers, json=init_message) as response:
                # 关键：从响应头中获取 Session ID
                session_id = response.headers.get('mcp-session-id')
                print(f"✅ 获取 Session ID: {session_id}")
                
                if not session_id:
                    print("❌ 无法获取 Session ID，终止流程")
                    return
                
                # 等待初始化完成
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            print(f"✅ 初始化成功\n")
                            break
            
            # 准备带有 Session ID 的请求头
            headers_with_session = {**base_headers, 'mcp-session-id': session_id}
            
            # ========== 步骤 2: 发送 initialized 通知 ==========
            print("📋 步骤 2: 发送 initialized 通知...")
            initialized_message = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {}
            }
            
            async with session.post(url, headers=headers_with_session, json=initialized_message) as response:
                print(f"✅ Initialized 响应：{response.status}\n")
            
            # ========== 步骤 3: 查询工具列表 ==========
            print("🔍 步骤 3: 查询可用工具...")
            tools_list_message = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            available_tools = []
            async with session.post(url, headers=headers_with_session, json=tools_list_message) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'result' in data and 'tools' in data['result']:
                                available_tools = data['result']['tools']
                                print(f"✅ 找到 {len(available_tools)} 个工具\n")
                                
                                # 显示与 GameObject 相关的工具
                                print("🎯 相关工具:")
                                for tool_name in ['manage_gameobject', 'manage_asset', 'manage_component']:
                                    tool = next((t for t in available_tools if t.get('name') == tool_name), None)
                                    if tool:
                                        print(f"  • {tool['name']}: {tool.get('description', '')[:60]}")
                                print()
                            break
            
            # ========== 步骤 4: 创建 LeaderboardPanel ==========
            print("🎨 步骤 4: 创建 LeaderboardPanel GameObject...")
            create_panel_call = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "manage_gameobject",
                    "arguments": {
                        "action": "create",
                        "name": "LeaderboardPanel",
                        "primitive_type": None  # 不创建基本形状
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
                            else:
                                print("✅ LeaderboardPanel 创建成功")
                                if 'result' in data:
                                    print(f"   结果：{data['result']}")
                            break
                else:
                    print(f"❌ 响应状态码：{response.status}")
            
            await asyncio.sleep(0.5)
            
            # ========== 步骤 5: 添加 RectTransform 组件 ==========
            print("\n📐 步骤 5: 添加 RectTransform 组件...")
            add_rect_transform_call = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "manage_gameobject",
                    "arguments": {
                        "action": "add_component",
                        "path": "LeaderboardPanel",
                        "component": "RectTransform"
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=add_rect_transform_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'error' in data:
                                print(f"⚠️ 添加失败：{data['error']}")
                            else:
                                print("✅ RectTransform 添加成功")
                            break
            
            await asyncio.sleep(0.5)
            
            # ========== 步骤 6: 添加 CanvasRenderer 组件 ==========
            print("\n🖼️ 步骤 6: 添加 CanvasRenderer 组件...")
            add_canvas_renderer_call = {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "manage_gameobject",
                    "arguments": {
                        "action": "add_component",
                        "path": "LeaderboardPanel",
                        "component": "CanvasRenderer"
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=add_canvas_renderer_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'error' in data:
                                print(f"⚠️ 添加失败：{data['error']}")
                            else:
                                print("✅ CanvasRenderer 添加成功")
                            break
            
            await asyncio.sleep(0.5)
            
            # ========== 步骤 7: 添加 Image 组件 ==========
            print("\n🎨 步骤 7: 添加 Image 组件...")
            add_image_call = {
                "jsonrpc": "2.0",
                "id": 6,
                "method": "tools/call",
                "params": {
                    "name": "manage_gameobject",
                    "arguments": {
                        "action": "add_component",
                        "path": "LeaderboardPanel",
                        "component": "Image"
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=add_image_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'error' in data:
                                print(f"⚠️ 添加失败：{data['error']}")
                            else:
                                print("✅ Image 添加成功")
                            break
            
            await asyncio.sleep(0.5)
            
            # ========== 步骤 8: 添加 LeaderboardUI 脚本 ==========
            print("\n📜 步骤 8: 添加 LeaderboardUI 脚本...")
            add_script_call = {
                "jsonrpc": "2.0",
                "id": 7,
                "method": "tools/call",
                "params": {
                    "name": "manage_gameobject",
                    "arguments": {
                        "action": "add_component",
                        "path": "LeaderboardPanel",
                        "component": "LeaderboardUI"
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
                                print(f"⚠️ 添加失败：{data['error']}")
                            else:
                                print("✅ LeaderboardUI 脚本添加成功")
                            break
            
            await asyncio.sleep(0.5)
            
            # ========== 步骤 9: 创建 RankItemPrefab ==========
            print("\n🎨 步骤 9: 创建 RankItemPrefab GameObject...")
            create_item_call = {
                "jsonrpc": "2.0",
                "id": 8,
                "method": "tools/call",
                "params": {
                    "name": "manage_gameobject",
                    "arguments": {
                        "action": "create",
                        "name": "RankItemPrefab",
                        "primitive_type": None
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=create_item_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'error' in data:
                                print(f"⚠️ 创建失败：{data['error']}")
                            else:
                                print("✅ RankItemPrefab 创建成功")
                            break
            
            await asyncio.sleep(0.5)
            
            # ========== 步骤 10: 为 RankItemPrefab 添加组件 ==========
            print("\n📐 步骤 10: 为 RankItemPrefab 添加组件...")
            
            components_to_add = ["RectTransform", "CanvasRenderer", "Image", "LeaderboardRankItem"]
            for i, component in enumerate(components_to_add, start=9):
                print(f"   - 添加 {component}...")
                add_component_call = {
                    "jsonrpc": "2.0",
                    "id": i,
                    "method": "tools/call",
                    "params": {
                        "name": "manage_gameobject",
                        "arguments": {
                            "action": "add_component",
                            "path": "RankItemPrefab",
                            "component": component
                        }
                    }
                }
                
                async with session.post(url, headers=headers_with_session, json=add_component_call) as response:
                    if response.status == 200:
                        async for line in response.content:
                            line_text = line.decode('utf-8').strip()
                            if line_text.startswith('data:'):
                                data = json.loads(line_text[5:])
                                if 'error' not in data:
                                    print(f"      ✅ {component} 添加成功")
                                else:
                                    print(f"      ⚠️ {component} 添加失败：{data.get('error', '未知')}")
                                break
                
                await asyncio.sleep(0.3)
            
            print("\n=== ✅ MCP 调用流程完成 ===\n")
            print("📋 检查结果：")
            print("1. 在 Unity Hierarchy 中查看是否创建了以下对象:")
            print("   • LeaderboardPanel (带 LeaderboardUI 脚本)")
            print("   • RankItemPrefab (带 LeaderboardRankItem 脚本)")
            print()
            print("2. 如果创建成功，请手动保存为预制件:")
            print("   右键 GameObject → Create Prefab → 保存到 Assets/Prefabs/")
            print()
            print("3. 在 Inspector 中配置 LeaderboardUI 组件的引用")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_leaderboard_system())
