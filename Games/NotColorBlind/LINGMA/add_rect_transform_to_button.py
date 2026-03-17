import asyncio
import aiohttp
import json

async def add_rect_transform_to_button():
    """为 LeaderboardButton 添加 RectTransform 组件"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🎯 为 LeaderboardButton 添加 RectTransform ===\n")
        
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
                        "name": "recttransform-adder",
                        "version": "1.0.0"
                    }
                }
            }
            
            session_id = None
            async with session.post(url, headers=base_headers, json=init_message) as response:
                session_id = response.headers.get('mcp-session-id')
                
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
            
            # ========== 步骤 1: 添加 RectTransform 组件 ==========
            print("\n📐 步骤 1: 为 LeaderboardButton 添加 RectTransform 组件...")
            
            add_rect_call = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "manage_components",
                    "arguments": {
                        "action": "add",
                        "target": "LeaderboardButton",
                        "search_method": "by_name",
                        "component_type": "RectTransform"
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=add_rect_call) as response:
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
                                            print(f"   ✅ RectTransform 组件添加成功!")
                                        else:
                                            error_msg = result.get('error', 'Unknown error')
                                            print(f"   ⚠️ 添加失败：{error_msg}")
                                            print(f"   💡 可能需要手动添加 RectTransform")
                                    except Exception as e:
                                        print(f"   ⚠️ 解析失败：{e}")
                                        print(f"   原始响应：{text_content[:200]}")
                            break
            
            await asyncio.sleep(0.5)
            
            # ========== 步骤 2: 设置 RectTransform 属性 ==========
            print("\n📐 步骤 2: 设置 RectTransform 属性（右上角）...")
            
            # 设置锚点
            set_anchor_max = {
                "jsonrpc": "2.0",
                "id": 3,
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
            
            async with session.post(url, headers=headers_with_session, json=set_anchor_max) as response:
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
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.3)
            
            set_anchor_min = {
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
                        "property": "anchorMin",
                        "value": {"x": 1, "y": 1}
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=set_anchor_min) as response:
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
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.3)
            
            set_position = {
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
                        "property": "anchoredPosition",
                        "value": {"x": -50, "y": -30}
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=set_position) as response:
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
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.3)
            
            set_size = {
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
                        "property": "sizeDelta",
                        "value": {"x": 80, "y": 40}
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=set_size) as response:
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
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.3)
            
            print("\n=== ✅ RectTransform 配置完成 ===\n")
            print("📋 按钮 RectTransform 设置:")
            print("   • 锚点：右上角 (1,1)")
            print("   • 位置：(-50,-30)")
            print("   • 大小：80x40")
            print()
            print("⚠️ 如果 MCP 无法添加 RectTransform，需要手动操作:")
            print("1. 在 Unity 中选中 LeaderboardButton")
            print("2. 在 Inspector 中点击 Add Component")
            print("3. 搜索并添加 RectTransform")
            print("4. 然后按照上述参数设置")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(add_rect_transform_to_button())
