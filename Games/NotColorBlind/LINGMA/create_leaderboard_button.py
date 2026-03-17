import asyncio
import aiohttp
import json

async def create_leaderboard_button():
    """在 Start 场景的 Canvas 右上角添加排行榜按钮"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🎯 在 Canvas 右上角添加排行榜按钮 ===\n")
        
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
                        "name": "leaderboard-button-creator",
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
            
            # ========== 步骤 1: 查找 Canvas ==========
            print("\n🔍 步骤 1: 查找 Canvas 对象...")
            
            find_canvas_call = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "find_gameobjects",
                    "arguments": {
                        "search_term": "Canvas",
                        "search_method": "by_name"
                    }
                }
            }
            
            canvas_path = None
            async with session.post(url, headers=headers_with_session, json=find_canvas_call) as response:
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
                                                # 找到根目录的 Canvas（不是子对象）
                                                if '/' not in path and obj.get('name') == 'Canvas':
                                                    canvas_path = path
                                                    print(f"   ✅ 找到 Canvas: {canvas_path}")
                                                    break
                                        else:
                                            print(f"   ❌ 查找失败：{result.get('error', 'Unknown error')}")
                                    except Exception as e:
                                        print(f"   ⚠️ 解析失败：{e}")
                            break
            
            await asyncio.sleep(0.3)
            
            if not canvas_path:
                print("   ❌ 未找到 Canvas 对象！")
                return
            
            # ========== 步骤 2: 创建排行榜按钮 ==========
            print("\n📐 步骤 2: 创建排行榜按钮...")
            
            create_button_call = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "manage_gameobject",
                    "arguments": {
                        "action": "create_ui_button",
                        "parent": canvas_path,
                        "name": "LeaderboardButton"
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
                                tools_result = data['result']
                                content_list = tools_result.get('content', [])
                                
                                if content_list and len(content_list) > 0:
                                    content_item = content_list[0]
                                    text_content = content_item.get('text', '')
                                    
                                    try:
                                        result = json.loads(text_content)
                                        if result.get('success'):
                                            print(f"   ✅ 排行榜按钮创建成功!")
                                        else:
                                            error_msg = result.get('error', 'Unknown error')
                                            print(f"   ⚠️ 创建失败：{error_msg}")
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.5)
            
            # ========== 步骤 3: 设置按钮位置（右上角） ==========
            print("\n📍 步骤 3: 设置按钮位置（右上角）...")
            
            set_position_call = {
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
                        "property": "anchoredPosition",
                        "value": {"x": -100, "y": -50}
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
                                            print(f"   ✅ 按钮位置设置成功!")
                                        else:
                                            print(f"   ⚠️ 设置失败：{result.get('error', 'Unknown error')}")
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.3)
            
            # ========== 步骤 4: 设置按钮大小为普通按钮的一半 ==========
            print("\n📏 步骤 4: 设置按钮大小（普通按钮的一半）...")
            
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
                                            print(f"   ✅ 按钮大小设置成功!")
                                        else:
                                            print(f"   ⚠️ 设置失败：{result.get('error', 'Unknown error')}")
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.3)
            
            # ========== 步骤 5: 设置按钮文本为【排行榜】 ==========
            print("\n📝 步骤 5: 设置按钮文本为【排行榜】...")
            
            set_text_call = {
                "jsonrpc": "2.0",
                "id": 6,
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
                                            print(f"   ✅ 按钮文本设置成功!")
                                        else:
                                            print(f"   ⚠️ 设置失败：{result.get('error', 'Unknown error')}")
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.3)
            
            # ========== 步骤 6: 设置字体和字号 ==========
            print("\n 步骤 6: 设置字体和字号...")
            
            set_font_call = {
                "jsonrpc": "2.0",
                "id": 7,
                "method": "tools/call",
                "params": {
                    "name": "manage_components",
                    "arguments": {
                        "action": "set_property",
                        "target": "LeaderboardButton",
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
                                            print(f"   ✅ 字体设置成功!")
                                        else:
                                            print(f"   ⚠️ 字体设置失败：{result.get('error', 'Unknown error')}")
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.3)
            
            # 设置字号
            set_fontsize_call = {
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
                        "property": "fontSize",
                        "value": 18
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=set_fontsize_call) as response:
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
                                            print(f"   ✅ 字号设置成功!")
                                        else:
                                            print(f"   ⚠️ 字号设置失败：{result.get('error', 'Unknown error')}")
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.3)
            
            # ========== 步骤 7: 设置锚点为右上角 ==========
            print("\n🎯 步骤 7: 设置锚点为右上角...")
            
            set_anchor_call = {
                "jsonrpc": "2.0",
                "id": 9,
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
            
            async with session.post(url, headers=headers_with_session, json=set_anchor_call) as response:
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
                                            print(f"   ✅ 锚点设置成功!")
                                        else:
                                            print(f"   ⚠️ 锚点设置失败：{result.get('error', 'Unknown error')}")
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.3)
            
            set_anchormin_call = {
                "jsonrpc": "2.0",
                "id": 10,
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
            
            async with session.post(url, headers=headers_with_session, json=set_anchormin_call) as response:
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
                                            print(f"   ✅ 最小锚点设置成功!")
                                        else:
                                            print(f"   ⚠️ 最小锚点设置失败：{result.get('error', 'Unknown error')}")
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.3)
            
            print("\n=== ✅ 排行榜按钮创建完成 ===\n")
            print("📋 已完成的配置:")
            print("   • 按钮名称：LeaderboardButton")
            print("   • 父对象：Canvas")
            print("   • 位置：右上角")
            print("   • 大小：80x40（普通按钮的一半）")
            print("   • 文本：排行榜")
            print("   • 字体：FZLTH-GBK")
            print("   • 字号：18")
            print("   • 锚点：右上角")
            print()
            print("⚠️ 下一步操作:")
            print("1. 在 Unity Hierarchy 中查看 Canvas/LeaderboardButton")
            print("2. 在 Inspector 中确认 RectTransform 的位置和大小")
            print("3. 在 MainMenuController 中绑定按钮点击事件:")
            print("   • 选中 Canvas（挂载 MainMenuController 的对象）")
            print("   • 在 Inspector 的 MainMenuController 组件中")
            print("   • 将 LeaderboardButton 字段拖入新创建的按钮")
            print("4. 运行游戏测试按钮功能")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_leaderboard_button())
