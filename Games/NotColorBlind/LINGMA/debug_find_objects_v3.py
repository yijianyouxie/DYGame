import asyncio
import aiohttp
import json

async def debug_find_objects():
    """调试查找对象功能 - 详细调试版本"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🔍 调试查找对象功能 - 详细版本 ===\n")
        
        try:
            # ========== 初始化连接 ==========
            init_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "debug-object-finder",
                        "version": "1.0.0"
                    }
                }
            }
            
            session_id = None
            async with session.post(url, headers=base_headers, json=init_message) as response:
                session_id = response.headers.get('mcp-session-id')
                
                if not session_id:
                    print("❌ 未获取到 Session ID")
                    return
                
                if response.status == 200:
                    async for line in response.content:
                        if line.decode('utf-8').strip().startswith('data:'):
                            break
            
            headers_with_session = {**base_headers, 'mcp-session-id': session_id}
            
            await session.post(url, headers=headers_with_session, json={
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            })
            
            # ========== 1. 获取可用工具列表 ==========
            print("\n📋 步骤 1: 获取可用工具列表...")
            
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            available_tools = []
            async with session.post(url, headers=headers_with_session, json=tools_request) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'result' in data:
                                tools = data['result'].get('tools', [])
                                available_tools = [t.get('name', '') for t in tools]
                                print(f"   ✅ 可用工具 ({len(tools)} 个):")
                                for tool in tools[:10]:  # 只显示前 10 个
                                    tool_name = tool.get('name', 'Unknown')
                                    print(f"      • {tool_name}")
                                if len(tools) > 10:
                                    print(f"      ... 还有 {len(tools) - 10} 个工具")
                            break
            
            await asyncio.sleep(0.3)
            
            # ========== 2. 使用 by_path 直接访问已知对象 ==========
            print("\n📋 步骤 2: 使用 by_path 直接访问已知对象...")
            
            known_paths = [
                "Canvas",
                "Canvas/Button",
                "Main Camera",
                "Directional Light",
                "EventSystem"
            ]
            
            for path in known_paths:
                print(f"\n   🔍 访问路径：{path}")
                
                access_call = {
                    "jsonrpc": "2.0",
                    "id": 5,
                    "method": "tools/call",
                    "params": {
                        "name": "find_gameobjects",
                        "arguments": {
                            "search_term": path,
                            "search_method": "by_path"
                        }
                    }
                }
                
                async with session.post(url, headers=headers_with_session, json=access_call) as response:
                    if response.status == 200:
                        async for line in response.content:
                            line_text = line.decode('utf-8').strip()
                            if line_text.startswith('data:'):
                                data = json.loads(line_text[5:])
                                
                                if 'result' in data:
                                    tools_result = data['result']
                                    content_list = tools_result.get('content', [])
                                    
                                    if content_list and len(content_list) > 0:
                                        content_item = content_list[0]
                                        text_content = content_item.get('text', '')
                                        
                                        print(f"      📄 响应内容：{text_content[:200]}")
                                        
                                        try:
                                            result = json.loads(text_content)
                                            
                                            if result.get('success'):
                                                objects = result.get('data', {}).get('gameObjects', [])
                                                if objects:
                                                    print(f"      ✅ 成功访问:")
                                                    for obj in objects:
                                                        name = obj.get('name', 'Unknown')
                                                        obj_path = obj.get('path', 'Unknown')
                                                        print(f"         • {name} - {obj_path}")
                                                else:
                                                    print(f"      ⚠️ 对象不存在")
                                            else:
                                                error_msg = result.get('message', result.get('error', 'Unknown error'))
                                                print(f"      ❌ 失败：{error_msg}")
                                        except json.JSONDecodeError as e:
                                            print(f"      ❌ JSON 解析失败：{e}")
                                            print(f"      原始文本：{text_content}")
                                break
                
                await asyncio.sleep(0.3)
            
            # ========== 3. 测试不同的搜索方式 ==========
            print("\n📋 步骤 3: 测试不同的搜索方式...")
            
            test_cases = [
                ("Main Camera", "by_name"),
                ("Canvas", "by_name"),
                ("Button", "by_name"),
            ]
            
            for term, method in test_cases:
                print(f"\n   🔍 搜索：term='{term}', method='{method}'")
                
                search_call = {
                    "jsonrpc": "2.0",
                    "id": 6,
                    "method": "tools/call",
                    "params": {
                        "name": "find_gameobjects",
                        "arguments": {
                            "search_term": term,
                            "search_method": method
                        }
                    }
                }
                
                async with session.post(url, headers=headers_with_session, json=search_call) as response:
                    if response.status == 200:
                        async for line in response.content:
                            line_text = line.decode('utf-8').strip()
                            if line_text.startswith('data:'):
                                data = json.loads(line_text[5:])
                                
                                if 'result' in data:
                                    tools_result = data['result']
                                    content_list = tools_result.get('content', [])
                                    
                                    if content_list and len(content_list) > 0:
                                        content_item = content_list[0]
                                        text_content = content_item.get('text', '')
                                        
                                        print(f"      📄 响应内容：{text_content[:200]}")
                                        
                                        try:
                                            result = json.loads(text_content)
                                            
                                            if result.get('success'):
                                                objects = result.get('data', {}).get('gameObjects', [])
                                                if objects:
                                                    print(f"      ✅ 找到 {len(objects)} 个对象:")
                                                    for obj in objects:
                                                        name = obj.get('name', 'Unknown')
                                                        path = obj.get('path', 'Unknown')
                                                        print(f"         • {name} - {path}")
                                                else:
                                                    print(f"      ⚠️ 未找到对象")
                                            else:
                                                error_msg = result.get('message', result.get('error', 'Unknown error'))
                                                print(f"      ❌ 失败：{error_msg}")
                                        except json.JSONDecodeError as e:
                                            print(f"      ❌ JSON 解析失败：{e}")
                                            print(f"      原始文本：{text_content}")
                                break
                
                await asyncio.sleep(0.3)
            
            print("\n=== ✅ 调试完成 ===\n")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_find_objects())
