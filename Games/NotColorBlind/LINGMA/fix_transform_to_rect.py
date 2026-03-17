import asyncio
import aiohttp
import json

async def fix_transform_to_rect():
    """将 Transform 替换为 RectTransform"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🎯 将 Transform 替换为 RectTransform ===\n")
        
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
                        "name": "transform-fixer",
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
            print("\n📋 查询可用的组件操作...")
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
                                    input_schema = components_tool.get('inputSchema', {})
                                    properties = input_schema.get('properties', {})
                                    print(f"\n✅ manage_components 可用 actions: {properties.get('action', {}).get('enum', [])}")
                            break
            
            await asyncio.sleep(0.5)
            
            # ========== 方法 1: 尝试使用 modify action 转换组件类型 ==========
            print("\n🔧 方法 1: 尝试转换组件类型...")
            
            modify_call = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "manage_gameobject",
                    "arguments": {
                        "action": "modify",
                        "target": "LeaderboardPanel",
                        "search_method": "by_name",
                        "components_to_add": ["RectTransform"]
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
                                print(f"   ⚠️ 转换失败：{data['error']}")
                            elif 'result' in data:
                                print(f"   ✅ 组件转换成功!")
                            break
            
            await asyncio.sleep(0.5)
            
            # ========== 方法 2: 如果方法 1 失败，尝试使用 Unity 的 Convert To RectTransform API ==========
            print("\n🔧 方法 2: 使用脚本转换...")
            
            # 通过设置属性来转换
            convert_call = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "manage_components",
                    "arguments": {
                        "action": "set_property",
                        "target": "LeaderboardPanel",
                        "search_method": "by_name",
                        "component_type": "RectTransform",
                        "property": "sizeDelta",
                        "value": {"x": 0, "y": 0}
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=convert_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'error' in data:
                                print(f"   ⚠️ 设置属性失败：{data['error']}")
                                print(f"   💡 这说明需要先有 RectTransform 组件")
                            elif 'result' in data:
                                print(f"   ✅ RectTransform 组件已存在并设置了属性!")
                            break
            
            await asyncio.sleep(0.5)
            
            # ========== 验证当前组件状态 ==========
            print("\n🔍 验证 LeaderboardPanel 的组件状态...")
            
            verify_call = {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "find_gameobjects",
                    "arguments": {
                        "search_term": "LeaderboardPanel",
                        "search_method": "by_name"
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=verify_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'result' in data and 'content' in data['result']:
                                content = json.loads(data['result']['content'][0]['text'])
                                if content.get('success'):
                                    instance_ids = content.get('data', {}).get('instanceIDs', [])
                                    print(f"✅ 找到 LeaderboardPanel (InstanceID: {instance_ids[0] if instance_ids else 'N/A'})")
                                    print(f"\n📋 重要提示:")
                                    print(f"Unity 中 Transform 和 RectTransform 是互斥的")
                                    print(f"如果 MCP API 不支持直接转换，需要在 Unity 编辑器中手动操作:")
                                    print(f"\n在 Unity 中的操作步骤:")
                                    print(f"1. 选中 LeaderboardPanel")
                                    print(f"2. 在 Inspector 中找到 Transform 组件")
                                    print(f"3. 右键点击 Transform 组件 → Remove Component")
                                    print(f"4. 然后点击 Add Component → 搜索 'Rect Transform'")
                                    print(f"5. 或者使用菜单：GameObject → Convert To RectTransform")
                                    break
            
            print("\n=== ✅ 尝试完成 ===\n")
            print("📋 总结:")
            print("MCP API 可能无法直接将 Transform 转换为 RectTransform")
            print("这是因为 Unity 的底层限制：一个 GameObject 只能有 Transform 或 RectTransform 之一")
            print()
            print("推荐的解决方案（在 Unity 编辑器中手动操作）:")
            print("方法 1 - 使用 Unity 菜单:")
            print("  1. 在 Hierarchy 中选中 LeaderboardPanel")
            print("  2. 点击顶部菜单：GameObject → Convert To RectTransform")
            print("  3. Unity 会自动替换组件")
            print()
            print("方法 2 - 手动替换:")
            print("  1. 在 Inspector 中右键点击 Transform 组件标题")
            print("  2. 选择 'Remove Component'")
            print("  3. 点击 'Add Component'")
            print("  4. 搜索并添加 'Rect Transform'")
            print()
            print("完成后再继续配置 LeaderboardUI 脚本的引用字段")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_transform_to_rect())
