import asyncio
import aiohttp
import json

async def duplicate_button():
    """复制 Canvas/Button 并调整为排行榜按钮"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🎯 复制 Canvas/Button 创建排行榜按钮 ===\n")
        
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
            
            # ========== 步骤 1: 查找 Canvas/Button ==========
            print("\n🔍 步骤 1: 查找 Canvas/Button...")
            
            find_button_call = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "find_gameobjects",
                    "arguments": {
                        "search_term": "Button",
                        "search_method": "by_name"
                    }
                }
            }
            
            source_button_path = None
            async with session.post(url, headers=headers_with_session, json=find_button_call) as response:
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
                                            objects = result.get('data', {}).get('gameObjects', [])
                                            if objects:
                                                # 查找 Canvas/Button
                                                for obj in objects:
                                                    path = obj.get('path', '')
                                                    if path == 'Canvas/Button':
                                                        source_button_path = path
                                                        print(f"   ✅ 找到源按钮：{source_button_path}")
                                                        break
                                                
                                                if not source_button_path:
                                                    print(f"   ⚠️ 找到 {len(objects)} 个 Button，但不是 Canvas/Button")
                                                    for obj in objects:
                                                        print(f"      - {obj.get('path', '')}")
                                            else:
                                                print(f"   ❌ 未找到任何 Button")
                                        else:
                                            error_msg = result.get('error', 'Unknown error')
                                            print(f"   ❌ 查找失败：{error_msg}")
                                    except Exception as e:
                                        print(f"   ⚠️ 解析失败：{e}")
                            break
            
            await asyncio.sleep(0.3)
            
            if not source_button_path:
                print("\n💡 Canvas/Button 不存在，无法继续")
                return
            
            # ========== 步骤 2: 复制按钮 ==========
            print("\n📋 步骤 2: 复制 Canvas/Button...")
            
            duplicate_call = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "manage_gameobject",
                    "arguments": {
                        "action": "duplicate",
                        "target": source_button_path,
                        "search_method": "by_path",
                        "new_name": "LeaderboardButton"
                    }
                }
            }
            
            duplicated = False
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
                                            duplicated = True
                                        else:
                                            error_msg = result.get('error', 'Unknown error')
                                            print(f"   ⚠️ 复制失败：{error_msg}")
                                    except Exception as e:
                                        print(f"   ⚠️ 解析失败：{e}")
                                        print(f"   原始响应：{text_content[:200]}")
                            break
            
            await asyncio.sleep(0.5)
            
            if not duplicated:
                print("\n❌ 复制失败，无法继续")
                return
            
            # ========== 步骤 3: 获取源按钮的大小 ==========
            print("\n📏 步骤 3: 获取源按钮的大小...")
            
            get_size_call = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "manage_components",
                    "arguments": {
                        "action": "get_property",
                        "target": source_button_path,
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
                                            else:
                                                print(f"   ⚠️ 无法解析大小数据")
                                        else:
                                            print(f"   ⚠️ 获取失败：{result.get('error', 'Unknown error')}")
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.3)
            
            # 计算一半的大小
            target_width = source_width / 2
            target_height = source_height / 2
            print(f"   📐 目标大小：{target_width}x{target_height}")
            
            # ========== 步骤 4: 设置排行榜按钮的大小（一半） ==========
            print("\n📏 步骤 4: 设置排行榜按钮大小为一半...")
            
            set_size_call = {
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
            
            # ========== 步骤 5: 设置锚点为右上角 ==========
            print("\n🎯 步骤 5: 设置锚点为右上角...")
            
            set_anchor_max_call = {
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
                "id": 7,
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
            
            # ========== 步骤 6: 设置位置（右上角偏移） ==========
            print("\n📍 步骤 6: 设置位置（右上角偏移）...")
            
            set_position_call = {
                "jsonrpc": "2.0",
                "id": 8,
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
            
            # ========== 步骤 7: 修改 Text 内容为"排行榜" ==========
            print("\n📝 步骤 7: 修改 Text 内容为'排行榜'...")
            
            # 先查找 Text 子对象
            find_text_call = {
                "jsonrpc": "2.0",
                "id": 9,
                "method": "tools/call",
                "params": {
                    "name": "find_gameobjects",
                    "arguments": {
                        "search_term": "Text",
                        "search_method": "by_name"
                    }
                }
            }
            
            text_path = None
            async with session.post(url, headers=headers_with_session, json=find_text_call) as response:
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
                                            objects = result.get('data', {}).get('gameObjects', [])
                                            for obj in objects:
                                                path = obj.get('path', '')
                                                if path.startswith('Canvas/LeaderboardButton/') and 'Text' in path:
                                                    text_path = path
                                                    break
                                    except:
                                        pass
                            break
            
            if text_path:
                set_text_call = {
                    "jsonrpc": "2.0",
                    "id": 10,
                    "method": "tools/call",
                    "params": {
                        "name": "manage_components",
                        "arguments": {
                            "action": "set_property",
                            "target": text_path,
                            "search_method": "by_path",
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
            else:
                print(f"   ⚠️ 未找到 Text 子对象")
            
            await asyncio.sleep(0.3)
            
            print("\n=== ✅ 排行榜按钮创建完成 ===\n")
            print("📋 已完成的操作:")
            print(f"   • 复制源：{source_button_path}")
            print(f"   • 新按钮：Canvas/LeaderboardButton")
            print(f"   • 原始大小：{source_width}x{source_height}")
            print(f"   • 新大小：{target_width}x{target_height} (一半)")
            print(f"   • 位置：右上角 (anchor: 1,1; pos: -50,-30)")
            print(f"   • Text 内容：排行榜")
            print()
            print("⚠️ 下一步操作:")
            print("1. 在 Unity Hierarchy 中查看 Canvas/LeaderboardButton")
            print("2. 确认按钮位于右上角")
            print("3. 在 MainMenuController 中绑定按钮点击事件:")
            print("   • 选中 Canvas（挂载 MainMenuController 的对象）")
            print("   • 在 Inspector 的 MainMenuController 组件中")
            print("   • 将 LeaderboardButton 拖入 leaderboardButton 字段")
            print("4. 运行游戏测试按钮功能")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(duplicate_button())
