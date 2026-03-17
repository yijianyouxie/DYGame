import asyncio
import aiohttp
import json

async def duplicate_button_direct():
    """直接使用 by_path 复制 Canvas/Button"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🎯 直接复制 Canvas/Button ===\n")
        
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
                        "name": "button-duplicator",
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
            
            await session.post(url, headers=headers_with_session, json={
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            })
            
            # ========== 步骤 1: 直接复制 Canvas/Button ==========
            print("\n📋 步骤 1: 复制 Canvas/Button...")
            
            duplicate_call = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "manage_gameobject",
                    "arguments": {
                        "action": "duplicate",
                        "target": "Canvas/Button",
                        "search_method": "by_path",
                        "new_name": "LeaderboardButton"
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=duplicate_call) as response:
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
                                    
                                    try:
                                        result = json.loads(text_content)
                                        if result.get('success'):
                                            print(f"   ✅ 按钮复制成功!")
                                            print(f"   📍 新路径：Canvas/LeaderboardButton")
                                        else:
                                            error_msg = result.get('error', 'Unknown error')
                                            print(f"   ❌ 复制失败：{error_msg}")
                                            print(f"   💡 请确认 Canvas/Button 在场景中确实存在")
                                    except Exception as e:
                                        print(f"   ❌ 解析失败：{e}")
                                        print(f"   原始响应：{text_content[:200]}")
                            break
            
            await asyncio.sleep(0.5)
            
            # ========== 步骤 2: 获取源按钮大小并设置新大小 ==========
            print("\n📏 步骤 2: 获取源按钮大小并设置一半大小...")
            
            # 获取源大小
            get_size_call = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "manage_components",
                    "arguments": {
                        "action": "get_property",
                        "target": "Canvas/Button",
                        "search_method": "by_path",
                        "component_type": "RectTransform",
                        "property": "sizeDelta"
                    }
                }
            }
            
            source_width = 160
            source_height = 80
            
            async with session.post(url, headers=headers_with_session, json=get_size_call) as response:
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
                                    
                                    try:
                                        result = json.loads(text_content)
                                        if result.get('success'):
                                            size_data = result.get('data', {})
                                            if isinstance(size_data, dict):
                                                source_width = size_data.get('x', 160)
                                                source_height = size_data.get('y', 80)
                                                print(f"   ✅ 源按钮大小：{source_width}x{source_height}")
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.3)
            
            target_width = source_width / 2
            target_height = source_height / 2
            print(f"   📐 目标大小：{target_width}x{target_height}")
            
            # 设置新大小
            set_size_call = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "manage_components",
                    "arguments": {
                        "action": "set_property",
                        "target": "LeaderboardButton",
                        "search_method": "by_name",
                        "component_type": "RectTransform",
                        "property": "sizeDelta",
                        "value": {"x": target_width, "y": target_height}
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=set_size_call) as response:
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
                                    
                                    try:
                                        result = json.loads(text_content)
                                        if result.get('success'):
                                            print(f"   ✅ 大小设置成功：{target_width}x{target_height}")
                                        else:
                                            print(f"   ⚠️ 设置失败：{result.get('error', 'Unknown error')}")
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.3)
            
            # ========== 步骤 3: 设置锚点为右上角 ==========
            print("\n🎯 步骤 3: 设置锚点为右上角...")
            
            set_anchor_max_call = {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "manage_components",
                    "arguments": {
                        "action": "set_property",
                        "target": "LeaderboardButton",
                        "search_method": "by_name",
                        "component_type": "RectTransform",
                        "property": "anchorMax",
                        "value": {"x": 1, "y": 1}
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=set_anchor_max_call) as response:
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
                                    
                                    try:
                                        result = json.loads(text_content)
                                        if result.get('success'):
                                            print(f"   ✅ anchorMax 设置成功 (1,1)")
                                        else:
                                            print(f"   ⚠️ 设置失败：{result.get('error', 'Unknown error')}")
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.3)
            
            set_anchor_min_call = {
                "jsonrpc": "2.0",
                "id": 6,
                "method": "tools/call",
                "params": {
                    "name": "manage_components",
                    "arguments": {
                        "action": "set_property",
                        "target": "LeaderboardButton",
                        "search_method": "by_name",
                        "component_type": "RectTransform",
                        "property": "anchorMin",
                        "value": {"x": 1, "y": 1}
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=set_anchor_min_call) as response:
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
                                    
                                    try:
                                        result = json.loads(text_content)
                                        if result.get('success'):
                                            print(f"   ✅ anchorMin 设置成功 (1,1)")
                                        else:
                                            print(f"   ⚠️ 设置失败：{result.get('error', 'Unknown error')}")
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.3)
            
            # ========== 步骤 4: 设置位置 ==========
            print("\n📍 步骤 4: 设置位置（右上角偏移）...")
            
            set_position_call = {
                "jsonrpc": "2.0",
                "id": 7,
                "method": "tools/call",
                "params": {
                    "name": "manage_components",
                    "arguments": {
                        "action": "set_property",
                        "target": "LeaderboardButton",
                        "search_method": "by_name",
                        "component_type": "RectTransform",
                        "property": "anchoredPosition",
                        "value": {"x": -50, "y": -30}
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=set_position_call) as response:
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
                                    
                                    try:
                                        result = json.loads(text_content)
                                        if result.get('success'):
                                            print(f"   ✅ 位置设置成功 (-50,-30)")
                                        else:
                                            print(f"   ⚠️ 设置失败：{result.get('error', 'Unknown error')}")
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.3)
            
            # ========== 步骤 5: 修改 Text 内容 ==========
            print("\n📝 步骤 5: 修改 Text 内容为'排行榜'...")
            
            set_text_call = {
                "jsonrpc": "2.0",
                "id": 8,
                "method": "tools/call",
                "params": {
                    "name": "manage_components",
                    "arguments": {
                        "action": "set_property",
                        "target": "LeaderboardButton",
                        "search_method": "by_name",
                        "component_type": "Text",
                        "property": "text",
                        "value": "排行榜"
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=set_text_call) as response:
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
                                    
                                    try:
                                        result = json.loads(text_content)
                                        if result.get('success'):
                                            print(f"   ✅ Text 内容修改成功")
                                        else:
                                            print(f"   ⚠️ 设置失败：{result.get('error', 'Unknown error')}")
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.3)
            
            print("\n=== ✅ 排行榜按钮创建完成 ===\n")
            print("📋 已完成的操作:")
            print(f"   • 复制源：Canvas/Button")
            print(f"   • 新按钮：Canvas/LeaderboardButton")
            print(f"   • 原始大小：{source_width}x{source_height}")
            print(f"   • 新大小：{target_width}x{target_height} (一半)")
            print(f"   • 位置：右上角 (anchor: 1,1; pos: -50,-30)")
            print(f"   • Text 内容：排行榜")
            print()
            print("⚠️ 下一步操作:")
            print("1. 在 Unity Hierarchy 中查看 Canvas/LeaderboardButton")
            print("2. 确认按钮位于右上角")
            print("3. 在 MainMenuController 中绑定按钮点击事件")
            print("4. 运行游戏测试按钮功能")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(duplicate_button_direct())
