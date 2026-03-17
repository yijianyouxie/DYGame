import asyncio
import aiohttp
import json

async def fix_rankitem_with_correct_paths():
    """使用正确的路径和 GUID 修复 RankItemPrefab"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🎯 使用正确路径和 GUID 修复 RankItemPrefab ===\n")
        
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
                        "name": "rankitem-path-fixer",
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
            
            # ========== 步骤 1: 查找 RankItemPrefab 的完整路径 ==========
            print("\n🔍 步骤 1: 查找 RankItemPrefab 对象...")
            find_rankitem_call = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "find_gameobjects",
                    "arguments": {
                        "search_term": "RankItemPrefab",
                        "search_method": "by_name"
                    }
                }
            }
            
            rankitem_path = None
            async with session.post(url, headers=headers_with_session, json=find_rankitem_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'result' in data and 'content' in data['result']:
                                content = json.loads(data['result']['content'][0]['text'])
                                if content.get('success'):
                                    objects = content.get('data', {}).get('gameObjects', [])
                                    for obj in objects:
                                        if 'path' in obj:
                                            rankitem_path = obj['path']
                                            print(f"   ✅ 找到 RankItemPrefab (路径：{rankitem_path})")
                                            break
                            break
            
            await asyncio.sleep(0.3)
            
            if not rankitem_path:
                print("   ⚠️ 未找到 RankItemPrefab，尝试使用默认路径")
                rankitem_path = "RankItemPrefab"
            
            # ========== 步骤 2: 为 RankItemPrefab/Background 添加 Image 组件 ==========
            background_target = f"{rankitem_path}/Background"
            print(f"\n📐 步骤 2: 为 {background_target} 添加 Image 组件...")
            
            add_image_call = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "manage_components",
                    "arguments": {
                        "action": "add",
                        "target": background_target,
                        "search_method": "by_path",  # 使用路径搜索，确保精确定位
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
            
            # ========== 步骤 3: 设置所有 Text 组件的字体（使用 GUID） ==========
            print("\n📝 步骤 3: 设置所有 Text 组件使用 FZLTH-GBK 字体（通过 GUID）...")
            
            # Unity 内置默认字体的 GUID
            font_guid = "0000000000000000e000000000000000"
            
            # 尝试查找 FZLTH-GBK 字体的 GUID
            print("   查询 FZLTH-GBK 字体的 GUID...")
            find_font_call = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "find_assets",
                    "arguments": {
                        "search_term": "FZLTH-GBK",
                        "search_method": "by_name"
                    }
                }
            }
            
            try:
                async with session.post(url, headers=headers_with_session, json=find_font_call) as response:
                    if response.status == 200:
                        async for line in response.content:
                            line_text = line.decode('utf-8').strip()
                            if line_text.startswith('data:'):
                                data = json.loads(line_text[5:])
                                if 'result' in data and 'content' in data['result']:
                                    content_text = data['result']['content'][0]['text']
                                    try:
                                        content = json.loads(content_text)
                                        if content.get('success'):
                                            assets = content.get('data', {}).get('assets', [])
                                            for asset in assets:
                                                if 'FZLTH' in asset.get('name', ''):
                                                    font_guid = asset.get('guid')
                                                    print(f"   ✅ 找到字体 GUID: {font_guid}")
                                                    break
                                    except Exception as e:
                                        print(f"   ⚠️ 解析字体信息失败：{e}")
                                    break
            except Exception as e:
                print(f"   ⚠️ 查询字体失败：{e}")
            
            await asyncio.sleep(0.3)
            print(f"   使用字体 GUID: {font_guid}")
            
            text_objects = [
                ("CloseButton", "×", 28, 4),      # MiddleCenter
                ("RankText", "", 24, 4),           # MiddleCenter
                ("NameText", "", 20, 3),           # MiddleLeft
                ("LevelText", "", 18, 5)           # MiddleRight
            ]
            
            for obj_name, default_text, font_size, alignment in text_objects:
                print(f"\n   配置 {obj_name}.Text:")
                
                # 1. 设置字体（使用 GUID）
                set_font_call = {
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
                
                # 2. 设置文本内容（如果是 CloseButton）
                if default_text:
                    set_text_call = {
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
                
                # 3. 设置字号
                set_fontsize_call = {
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
                
                # 4. 设置对齐方式
                align_names = {3: "MiddleLeft", 4: "MiddleCenter", 5: "MiddleRight"}
                set_alignment_call = {
                    "jsonrpc": "2.0",
                    "id": 8,
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
            print("📋 本次修正的关键点:")
            print()
            print("1. ✅ 使用精确路径搜索:")
            print(f"   - Background 目标路径：{background_target}")
            print("   - search_method: by_path (不是 by_name)")
            print()
            print("2. ✅ 使用 GUID 设置字体:")
            print(f"   - 字体 GUID: {font_guid}")
            print("   - fileID: 10102")
            print("   - type: 0")
            print()
            print("📝 配置的 Text 组件列表:")
            print("   • CloseButton.Text: Font GUID=" + font_guid + ", Size=28")
            print("   • RankText: Font GUID=" + font_guid + ", Size=24")
            print("   • NameText: Font GUID=" + font_guid + ", Size=20")
            print("   • LevelText: Font GUID=" + font_guid + ", Size=18")
            print()
            print("下一步操作:")
            print("1. 在 Unity Inspector 中验证 RankItemPrefab/Background 的 Image 组件")
            print("2. 检查所有 Text 组件的 Font 字段是否正确引用 FZLTH-GBK")
            print("3. 保存预制件更新（拖拽到 Assets/Prefabs/并替换）")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_rankitem_with_correct_paths())
