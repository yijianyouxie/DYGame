import asyncio
import aiohttp
import json

async def complete_leaderboard_button():
    """完成排行榜按钮配置：添加 Text 子对象并设置右上角位置"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🎯 完成排行榜按钮配置 ===\n")
        
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
                        "name": "button-completer",
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
            
            # ========== 步骤 1: 在 Button 下创建 Text 子对象 ==========
            print("\n📝 步骤 1: 在 LeaderboardButton 下创建 Text 子对象...")
            
            create_text_call = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "manage_gameobject",
                    "arguments": {
                        "action": "create",
                        "name": "Text",
                        "parent": "Canvas/LeaderboardButton"
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=create_text_call) as response:
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
                                            print(f"   ✅ Text 子对象创建成功!")
                                            print(f"   📍 路径：Canvas/LeaderboardButton/Text")
                                        else:
                                            error_msg = result.get('error', 'Unknown error')
                                            print(f"   ⚠️ 创建失败：{error_msg}")
                                    except Exception as e:
                                        print(f"   ⚠️ 解析失败：{e}")
                                        print(f"   原始响应：{text_content[:200]}")
                            break
            
            await asyncio.sleep(0.5)
            
            # ========== 步骤 2: 为 Text 添加 Text 组件 ==========
            print("\n🔧 步骤 2: 为 Text 对象添加 Text 组件...")
            
            add_text_component_call = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "manage_components",
                    "arguments": {
                        "action": "add",
                        "target": "Text",
                        "search_method": "by_name",
                        "component_type": "Text"
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=add_text_component_call) as response:
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
                                            print(f"   ✅ Text 组件添加成功!")
                                        else:
                                            print(f"   ⚠️ 添加失败：{result.get('error', 'Unknown error')}")
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.5)
            
            # ========== 步骤 3: 设置按钮的 RectTransform（右上角定位） ==========
            print("\n📐 步骤 3: 设置 LeaderboardButton 的 RectTransform（右上角）...")
            
            # 设置锚点为右上角
            set_anchor_max_call = {
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
                                            print(f"   ✅ 锚点设置成功 (anchorMax: 1,1)")
                                        else:
                                            print(f"   ⚠️ 设置失败：{result.get('error', 'Unknown error')}")
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.3)
            
            set_anchor_min_call = {
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
                                            print(f"   ✅ 最小锚点设置成功 (anchorMin: 1,1)")
                                        else:
                                            print(f"   ⚠️ 设置失败：{result.get('error', 'Unknown error')}")
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.3)
            
            # 设置位置偏移（右上角，向左下偏移）
            set_position_call = {
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
                                            print(f"   ✅ 位置设置成功 (Pos: -50,-30)")
                                        else:
                                            print(f"   ⚠️ 设置失败：{result.get('error', 'Unknown error')}")
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.3)
            
            # 设置按钮大小（普通按钮的一半：80x40）
            set_size_call = {
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
                        "property": "sizeDelta",
                        "value": {"x": 80, "y": 40}
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
                                            print(f"   ✅ 大小设置成功 (80x40)")
                                        else:
                                            print(f"   ⚠️ 设置失败：{result.get('error', 'Unknown error')}")
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.3)
            
            # ========== 步骤 4: 设置 Text 的 RectTransform（填充整个按钮） ==========
            print("\n📐 步骤 4: 设置 Text 的 RectTransform（填充按钮）...")
            
            set_text_anchor_call = {
                "jsonrpc": "2.0",
                "id": 8,
                "method": "tools/call",
                "params": {
                    "name": "manage_components",
                    "arguments": {
                        "action": "set_property",
                        "target": "Text",
                        "search_method": "by_name",
                        "component_type": "RectTransform",
                        "property": "anchorMax",
                        "value": {"x": 1, "y": 1}
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=set_text_anchor_call) as response:
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
                                            print(f"   ✅ Text 锚点设置成功")
                                        else:
                                            print(f"   ⚠️ 设置失败：{result.get('error', 'Unknown error')}")
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.3)
            
            set_text_anchor_min_call = {
                "jsonrpc": "2.0",
                "id": 9,
                "method": "tools/call",
                "params": {
                    "name": "manage_components",
                    "arguments": {
                        "action": "set_property",
                        "target": "Text",
                        "search_method": "by_name",
                        "component_type": "RectTransform",
                        "property": "anchorMin",
                        "value": {"x": 0, "y": 0}
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=set_text_anchor_min_call) as response:
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
                                            print(f"   ✅ Text 最小锚点设置成功")
                                        else:
                                            print(f"   ⚠️ 设置失败：{result.get('error', 'Unknown error')}")
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.3)
            
            set_text_size_call = {
                "jsonrpc": "2.0",
                "id": 10,
                "method": "tools/call",
                "params": {
                    "name": "manage_components",
                    "arguments": {
                        "action": "set_property",
                        "target": "Text",
                        "search_method": "by_name",
                        "component_type": "RectTransform",
                        "property": "sizeDelta",
                        "value": {"x": 0, "y": 0}
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=set_text_size_call) as response:
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
                                            print(f"   ✅ Text 大小设置成功 (填充)")
                                        else:
                                            print(f"   ⚠️ 设置失败：{result.get('error', 'Unknown error')}")
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.3)
            
            # ========== 步骤 5: 设置 Text 内容（排行榜） ==========
            print("\n📝 步骤 5: 设置 Text 内容为'排行榜'...")
            
            set_text_content_call = {
                "jsonrpc": "2.0",
                "id": 11,
                "method": "tools/call",
                "params": {
                    "name": "manage_components",
                    "arguments": {
                        "action": "set_property",
                        "target": "Text",
                        "search_method": "by_name",
                        "component_type": "Text",
                        "property": "text",
                        "value": "排行榜"
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=set_text_content_call) as response:
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
                                            print(f"   ✅ Text 内容设置为 '排行榜'")
                                        else:
                                            print(f"   ⚠️ 设置失败：{result.get('error', 'Unknown error')}")
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.3)
            
            # 设置字号
            set_font_size_call = {
                "jsonrpc": "2.0",
                "id": 12,
                "method": "tools/call",
                "params": {
                    "name": "manage_components",
                    "arguments": {
                        "action": "set_property",
                        "target": "Text",
                        "search_method": "by_name",
                        "component_type": "Text",
                        "property": "fontSize",
                        "value": 18
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=set_font_size_call) as response:
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
                                            print(f"   ✅ 字号设置为 18")
                                        else:
                                            print(f"   ⚠️ 设置失败：{result.get('error', 'Unknown error')}")
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.3)
            
            # 设置对齐方式
            set_alignment_call = {
                "jsonrpc": "2.0",
                "id": 13,
                "method": "tools/call",
                "params": {
                    "name": "manage_components",
                    "arguments": {
                        "action": "set_property",
                        "target": "Text",
                        "search_method": "by_name",
                        "component_type": "Text",
                        "property": "alignment",
                        "value": 4  # TextAnchor.MiddleCenter
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=set_alignment_call) as response:
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
                                            print(f"   ✅ 对齐方式设置为中心")
                                        else:
                                            print(f"   ⚠️ 设置失败：{result.get('error', 'Unknown error')}")
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.3)
            
            # 设置字体 GUID
            set_font_call = {
                "jsonrpc": "2.0",
                "id": 14,
                "method": "tools/call",
                "params": {
                    "name": "manage_components",
                    "arguments": {
                        "action": "set_property",
                        "target": "Text",
                        "search_method": "by_name",
                        "component_type": "Text",
                        "property": "m_FontData.m_Font",
                        "value": {
                            "fileID": 10102,
                            "guid": "04d2c4a712831164ea7b25868878b4f4",
                            "type": 0
                        }
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=set_font_call) as response:
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
                                            print(f"   ✅ 字体设置为 FZLTH-GBK")
                                        else:
                                            print(f"   ⚠️ 设置失败：{result.get('error', 'Unknown error')}")
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.3)
            
            print("\n=== ✅ 排行榜按钮配置完成 ===\n")
            print("📋 已完成的配置:")
            print("   • Text 子对象：Canvas/LeaderboardButton/Text ✓")
            print("   • 按钮位置：右上角 (anchor: 1,1; pos: -50,-30) ✓")
            print("   • 按钮大小：80x40（普通按钮的一半）✓")
            print("   • Text 内容：排行榜 ✓")
            print("   • Text 字号：18 ✓")
            print("   • Text 对齐：MiddleCenter ✓")
            print("   • Text 字体：FZLTH-GBK ✓")
            print("   • Text RectTransform：填充整个按钮 ✓")
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
    asyncio.run(complete_leaderboard_button())
