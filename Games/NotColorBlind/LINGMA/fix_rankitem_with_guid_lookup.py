import asyncio
import aiohttp
import json

async def fix_rankitem_with_guid_lookup():
    """使用 Unity Editor API 获取字体 GUID 并修复 RankItemPrefab"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🎯 使用 Unity Editor API 获取 GUID 并修复 RankItemPrefab ===\n")
        
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
                        "name": "guid-lookup-fixer",
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
            
            # ========== 步骤 1: 使用 AssetDatabase 获取字体 GUID ==========
            print("\n📝 步骤 1: 通过 Unity AssetDatabase 获取 FZLTH-GBK 字体 GUID...")
            
            font_guid = None
            get_guid_call = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "manage_asset",
                    "arguments": {
                        "action": "get_guid",
                        "path": "Assets/Font/FZLTH-GBK.TTF"
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=get_guid_call) as response:
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
                                        font_guid = result.get('data', {}).get('guid')
                                        print(f"   ✅ 获取字体 GUID: {font_guid}")
                                    else:
                                        print(f"   ⚠️ 获取失败：{result.get('error', 'Unknown error')}")
                                except Exception as e:
                                    print(f"   ⚠️ 解析失败：{e}")
                                    print(f"   原始响应：{content_text}")
                            break
            
            await asyncio.sleep(0.3)
            
            if not font_guid:
                print("   ⚠️ 无法通过 AssetDatabase 获取 GUID，尝试读取 meta 文件...")
                # 备用方案：直接读取 meta 文件
                read_meta_call = {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "manage_asset",
                        "arguments": {
                            "action": "read_file",
                            "path": "Assets/Font/FZLTH-GBK.TTF.meta"
                        }
                    }
                }
                
                async with session.post(url, headers=headers_with_session, json=read_meta_call) as response:
                    if response.status == 200:
                        async for line in response.content:
                            line_text = line.decode('utf-8').strip()
                            if line_text.startswith('data:'):
                                data = json.loads(line_text[5:])
                                if 'result' in data and 'content' in data['result']:
                                    content_text = data['result']['content'][0]['text']
                                    # 从 meta 文件中提取 GUID
                                    import re
                                    match = re.search(r'guid:\s*([a-f0-9]+)', content_text)
                                    if match:
                                        font_guid = match.group(1)
                                        print(f"   ✅ 从 meta 文件提取 GUID: {font_guid}")
                                    else:
                                        print(f"   ⚠️ 未在 meta 文件中找到 GUID")
                                break
                
                await asyncio.sleep(0.3)
            
            if not font_guid:
                print("   ⚠️ 使用默认字体 GUID")
                font_guid = "0000000000000000e000000000000000"
            
            # ========== 步骤 2: 查找场景中的所有 GameObject ==========
            print("\n🔍 步骤 2: 查找场景中的 RankItemPrefab...")
            find_all_call = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "find_gameobjects",
                    "arguments": {
                        "search_term": "",
                        "search_method": "by_name"
                    }
                }
            }
            
            rankitem_path = None
            async with session.post(url, headers=headers_with_session, json=find_all_call) as response:
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
                                        # 查找包含 RankItemPrefab 的对象
                                        for obj in objects:
                                            name = obj.get('name', '')
                                            path = obj.get('path', '')
                                            if 'RankItemPrefab' in name or 'RankItem' in name:
                                                rankitem_path = path
                                                print(f"   ✅ 找到 RankItemPrefab (路径：{rankitem_path})")
                                                break
                                        
                                        if not rankitem_path:
                                            print(f"   ℹ️ 未找到 RankItemPrefab，列出所有对象:")
                                            for i, obj in enumerate(objects[:10], 1):
                                                print(f"      {i}. {obj.get('name', 'N/A')} (路径：{obj.get('path', 'N/A')})")
                                            if len(objects) > 10:
                                                print(f"      ... 还有 {len(objects) - 10} 个对象")
                                except Exception as e:
                                    print(f"   ⚠️ 解析失败：{e}")
                            break
            
            await asyncio.sleep(0.3)
            
            if not rankitem_path:
                print("   ⚠️ 未找到 RankItemPrefab，尝试使用常见路径")
                # 尝试常见路径
                possible_paths = ["RankItemPrefab", "Canvas/RankItemPrefab"]
                for test_path in possible_paths:
                    test_call = {
                        "jsonrpc": "2.0",
                        "id": 5,
                        "method": "tools/call",
                        "params": {
                            "name": "find_gameobjects",
                            "arguments": {
                                "search_term": test_path,
                                "search_method": "by_path"
                            }
                        }
                    }
                    
                    async with session.post(url, headers=headers_with_session, json=test_call) as response:
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
                                                    print(f"   ✅ 找到 RankItemPrefab (路径：{rankitem_path})")
                                                    break
                                        except:
                                            pass
                                    break
                    
                    if rankitem_path:
                        break
                
                await asyncio.sleep(0.3)
            
            # ========== 步骤 3: 为 RankItemPrefab/Background 添加 Image 组件 ==========
            if rankitem_path:
                background_target = f"{rankitem_path}/Background"
                print(f"\n📐 步骤 3: 为 {background_target} 添加 Image 组件...")
                
                add_image_call = {
                    "jsonrpc": "2.0",
                    "id": 6,
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
                
                # ========== 步骤 4: 设置所有 Text组件的字体（使用获取的 GUID） ==========
                print(f"\n📝 步骤 4: 设置所有 Text组件使用字体 GUID: {font_guid}...")
                
                text_objects = [
                    ("CloseButton", "×", 28, 4),      # MiddleCenter
                    ("RankText", "", 24, 4),           # MiddleCenter
                    ("NameText", "", 20, 3),           # MiddleLeft
                    ("LevelText", "", 18, 5)           # MiddleRight
                ]
                
                for obj_name, default_text, font_size, alignment in text_objects:
                    print(f"\n   配置 {obj_name}.Text:")
                    
                    # 1. 设置字体（使用获取的 GUID）
                    set_font_call = {
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
                            "id": 8,
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
                        "id": 9,
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
                        "id": 10,
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
                print("1. ✅ 使用 Unity AssetDatabase 获取字体 GUID:")
                print(f"   - 方法：manage_asset → get_guid")
                print(f"   - 路径：Assets/Font/FZLTH-GBK.TTF")
                print(f"   - GUID: {font_guid}")
                print()
                print("2. ✅ 使用精确路径搜索 Background:")
                print(f"   - Background 目标路径：{background_target}")
                print("   - search_method: by_path")
                print()
                print("3. ✅ 使用正确的属性名设置字体:")
                print("   - property: m_FontData.m_Font")
                print("   - value: {fileID, guid, type}")
                print()
                print("📝 配置的 Text组件列表:")
                print("   • CloseButton.Text: Font GUID=" + font_guid + ", Size=28")
                print("   • RankText: Font GUID=" + font_guid + ", Size=24")
                print("   • NameText: Font GUID=" + font_guid + ", Size=20")
                print("   • LevelText: Font GUID=" + font_guid + ", Size=18")
                print()
                print("下一步操作:")
                print("1. 在 Unity Inspector 中验证 RankItemPrefab/Background 的 Image 组件")
                print("2. 检查所有 Text组件的 Font 字段是否正确引用 FZLTH-GBK")
                print("3. 保存预制件更新（拖拽到 Assets/Prefabs/并替换）")
            else:
                print("\n⚠️ 未找到 RankItemPrefab，无法继续操作")
                print("\n请在 Hierarchy 中确认:")
                print("1. RankItemPrefab 是否存在")
                print("2. 如果存在，请查看它的完整路径是什么")
                print("3. 重新运行脚本或手动指定正确的路径")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_rankitem_with_guid_lookup())
