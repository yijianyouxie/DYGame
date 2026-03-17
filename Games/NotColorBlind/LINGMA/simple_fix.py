import asyncio
import aiohttp
import json

async def simple_fix():
    """简化版本：直接为已知路径添加组件和设置字体"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🎯 简化修复：直接操作 ===\n")
        
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
                        "name": "simple-fixer",
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
            
            # ========== 关键信息 ==========
            font_guid = "04d2c4a712831164ea7b25868878b4f4"
            print(f"\n✅ 使用字体 GUID: {font_guid}")
            
            # 可能的 RankItemPrefab 路径
            possible_paths = [
                "RankItemPrefab",
                "Canvas/RankItemPrefab",
                "LeaderboardPanel/RankItemPrefab",
                "UI/Canvas/RankItemPrefab",
                "LeaderboardUI/RankItemPrefab"
            ]
            
            rankitem_path = None
            
            # ========== 尝试查找 RankItemPrefab ==========
            print("\n🔍 尝试查找 RankItemPrefab...")
            
            for test_path in possible_paths:
                print(f"   测试路径：{test_path}")
                find_call = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": "find_gameobjects",
                        "arguments": {
                            "search_term": test_path,
                            "search_method": "by_path"
                        }
                    }
                }
                
                async with session.post(url, headers=headers_with_session, json=find_call) as response:
                    if response.status == 200:
                        async for line in response.content:
                            line_text = line.decode('utf-8').strip()
                            if line_text.startswith('data:'):
                                data = json.loads(line_text[5:])
                                if 'result' in data and 'content' in data['result']:
                                    content_text = data['result']['content'][0]['text']
                                    try:
                                        result = json.loads(content_text)
                                        if result.get('success'):
                                            objects = result.get('data', {}).get('gameObjects', [])
                                            if objects:
                                                rankitem_path = test_path
                                                print(f"   ✅ 找到 RankItemPrefab: {rankitem_path}")
                                                break
                                    except Exception as e:
                                        pass
                                break
                
                if rankitem_path:
                    break
                
                await asyncio.sleep(0.2)
            
            # ========== 为 Background 添加 Image 组件 ==========
            if rankitem_path:
                background_target = f"{rankitem_path}/Background"
                print(f"\n📐 为 {background_target} 添加 Image 组件...")
                
                add_image_call = {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "manage_components",
                        "arguments": {
                            "action": "add",
                            "target": background_target,
                            "search_method": "by_path",
                            "component_type": "Image"
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
                                    error_msg = str(data['error'])
                                    if "already added" in error_msg or "already exists" in error_msg:
                                        print(f"   ℹ️  Background 已经有 Image 组件了")
                                    else:
                                        print(f"   ⚠️ 添加失败：{error_msg}")
                                elif 'result' in data:
                                    print(f"   ✅ Image 组件添加成功!")
                                break
                
                await asyncio.sleep(0.5)
                
                # ========== 设置所有 Text组件的字体 ==========
                print(f"\n📝 设置所有 Text组件使用字体 GUID: {font_guid}...")
                
                text_objects = [
                    ("CloseButton", "×", 28, 4),
                    ("RankText", "", 24, 4),
                    ("NameText", "", 20, 3),
                    ("LevelText", "", 18, 5)
                ]
                
                for obj_name, default_text, font_size, alignment in text_objects:
                    print(f"\n   配置 {obj_name}.Text:")
                    
                    # 设置字体
                    set_font_call = {
                        "jsonrpc": "2.0",
                        "id": 4,
                        "method": "tools/call",
                        "params": {
                            "name": "manage_components",
                            "arguments": {
                                "action": "set_property",
                                "target": obj_name,
                                "search_method": "by_name",
                                "component_type": "Text",
                                "property": "m_FontData.m_Font",
                                "value": {
                                    "fileID": 10102,
                                    "guid": font_guid,
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
                                    if 'error' in data:
                                        print(f"      ⚠️ 字体设置失败：{data['error']}")
                                    elif 'result' in data:
                                        print(f"      ✅ 字体 GUID 设置为 {font_guid}")
                                    break
                    
                    await asyncio.sleep(0.2)
                    
                    # 设置文本内容
                    if default_text:
                        set_text_call = {
                            "jsonrpc": "2.0",
                            "id": 5,
                            "method": "tools/call",
                            "params": {
                                "name": "manage_components",
                                "arguments": {
                                    "action": "set_property",
                                    "target": obj_name,
                                    "search_method": "by_name",
                                    "component_type": "Text",
                                    "property": "text",
                                    "value": default_text
                                }
                            }
                        }
                        
                        async with session.post(url, headers=headers_with_session, json=set_text_call) as response:
                            if response.status == 200:
                                async for line in response.content:
                                    line_text = line.decode('utf-8').strip()
                                    if line_text.startswith('data:'):
                                        data = json.loads(line_text[5:])
                                        if 'error' not in data:
                                            print(f"      ✅ 文本内容设置为 '{default_text}'")
                                        break
                        
                        await asyncio.sleep(0.2)
                    
                    # 设置字号
                    set_fontsize_call = {
                        "jsonrpc": "2.0",
                        "id": 6,
                        "method": "tools/call",
                        "params": {
                            "name": "manage_components",
                            "arguments": {
                                "action": "set_property",
                                "target": obj_name,
                                "search_method": "by_name",
                                "component_type": "Text",
                                "property": "fontSize",
                                "value": font_size
                            }
                        }
                    }
                    
                    async with session.post(url, headers=headers_with_session, json=set_fontsize_call) as response:
                        if response.status == 200:
                            async for line in response.content:
                                line_text = line.decode('utf-8').strip()
                                if line_text.startswith('data:'):
                                    data = json.loads(line_text[5:])
                                    if 'error' not in data:
                                        print(f"      ✅ 字号设置为 {font_size}")
                                    break
                        
                        await asyncio.sleep(0.2)
                    
                    # 设置对齐方式
                    align_names = {3: "MiddleLeft", 4: "MiddleCenter", 5: "MiddleRight"}
                    set_alignment_call = {
                        "jsonrpc": "2.0",
                        "id": 7,
                        "method": "tools/call",
                        "params": {
                            "name": "manage_components",
                            "arguments": {
                                "action": "set_property",
                                "target": obj_name,
                                "search_method": "by_name",
                                "component_type": "Text",
                                "property": "alignment",
                                "value": alignment
                            }
                        }
                    }
                    
                    async with session.post(url, headers=headers_with_session, json=set_alignment_call) as response:
                        if response.status == 200:
                            async for line in response.content:
                                line_text = line.decode('utf-8').strip()
                                if line_text.startswith('data:'):
                                    data = json.loads(line_text[5:])
                                    if 'error' not in data:
                                        print(f"      ✅ 对齐方式为 {align_names.get(alignment, 'Unknown')}")
                                    break
                        
                        await asyncio.sleep(0.2)
                
                print("\n=== ✅ 修复完成 ===\n")
                print("📋 关键信息:")
                print(f"   • 字体 GUID: {font_guid}")
                print(f"   • RankItemPrefab 路径：{rankitem_path}")
                print(f"   • Background 目标：{background_target}")
                print()
                print("下一步操作:")
                print("1. 在 Unity Inspector中验证所有设置")
                print("2. 保存预制件更新")
            else:
                print("\n❌ 未找到 RankItemPrefab")
                print("\n💡 请在 Hierarchy 中确认 RankItemPrefab 的准确路径")
                print("然后告诉我正确的路径，我可以再次尝试")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(simple_fix())
