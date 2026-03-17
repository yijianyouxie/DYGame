import asyncio
import aiohttp
import json

async def fix_rankitem_with_known_path():
    """使用已知正确路径修复 RankItemPrefab"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🎯 使用已知正确路径修复 RankItemPrefab ===\n")
        
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
            
            await session.post(url, headers=headers_with_session, json={
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            })
            
            # ========== 关键信息 ==========
            font_guid = "04d2c4a712831164ea7b25868878b4f4"
            rankitem_path = "RankItemPrefab"  # 已知的准确路径
            background_target = f"{rankitem_path}/Background"
            
            print(f"\n✅ 使用字体 GUID: {font_guid}")
            print(f"✅ RankItemPrefab 路径：{rankitem_path}")
            print(f"✅ Background 目标：{background_target}")
            
            # ========== 步骤 1: 验证 RankItemPrefab 是否存在 ==========
            print(f"\n🔍 步骤 1: 验证 {rankitem_path} 是否存在...")
            
            verify_call = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "find_gameobjects",
                    "arguments": {
                        "search_term": rankitem_path,
                        "search_method": "by_name"
                    }
                }
            }
            
            found = False
            async with session.post(url, headers=headers_with_session, json=verify_call) as response:
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
                                                found = True
                                                actual_path = objects[0].get('path', rankitem_path)
                                                print(f"   ✅ 找到 RankItemPrefab (路径：{actual_path})")
                                                
                                                # 更新为实际路径
                                                rankitem_path = actual_path
                                                background_target = f"{rankitem_path}/Background"
                                            else:
                                                print(f"   ❌ 未找到 RankItemPrefab")
                                        else:
                                            error_msg = result.get('error', 'Unknown error')
                                            print(f"   ❌ 查找失败：{error_msg}")
                                    except Exception as e:
                                        print(f"   ⚠️ 解析失败：{e}")
                            break
            
            await asyncio.sleep(0.3)
            
            if not found:
                print(f"\n❌ RankItemPrefab 不在场景中")
                print(f"💡 请在 Hierarchy 中确认:")
                print(f"   1. Start 场景是否已打开")
                print(f"   2. RankItemPrefab 是否在场景根目录")
                print(f"   3. 或者它可能是一个 Prefab 资产，需要从 Project 窗口拖入场景")
                return
            
            # ========== 步骤 2: 为 Background 添加 Image 组件 ==========
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
                            
                            if 'result' in data:
                                tools_result = data['result']
                                content_list = tools_result.get('content', [])
                                
                                if content_list and len(content_list) > 0:
                                    content_item = content_list[0]
                                    text_content = content_item.get('text', '')
                                    
                                    try:
                                        result = json.loads(text_content)
                                        if result.get('success'):
                                            print(f"   ✅ Image 组件添加成功!")
                                        else:
                                            error_msg = result.get('error', 'Unknown error')
                                            if "already" in error_msg.lower():
                                                print(f"   ℹ️  Background 已经有 Image 组件了")
                                            else:
                                                print(f"   ⚠️ 添加失败：{error_msg}")
                                    except:
                                        pass
                            break
            
            await asyncio.sleep(0.5)
            
            # ========== 步骤 3: 设置所有 Text组件的字体 ==========
            print(f"\n📝 步骤 3: 设置所有 Text组件使用字体 GUID: {font_guid}...")
            
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
                                
                                if 'result' in data:
                                    tools_result = data['result']
                                    content_list = tools_result.get('content', [])
                                    
                                    if content_list and len(content_list) > 0:
                                        content_item = content_list[0]
                                        text_content = content_item.get('text', '')
                                        
                                        try:
                                            result = json.loads(text_content)
                                            if result.get('success'):
                                                print(f"      ✅ 字体 GUID 设置为 {font_guid}")
                                            else:
                                                error_msg = result.get('error', 'Unknown error')
                                                print(f"      ⚠️ 字体设置失败：{error_msg}")
                                        except:
                                            pass
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
                                    
                                    if 'result' in data:
                                        tools_result = data['result']
                                        content_list = tools_result.get('content', [])
                                        
                                        if content_list and len(content_list) > 0:
                                            content_item = content_list[0]
                                            text_content = content_item.get('text', '')
                                            
                                            try:
                                                result = json.loads(text_content)
                                                if result.get('success'):
                                                    print(f"      ✅ 文本内容设置为 '{default_text}'")
                                            except:
                                                pass
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
                                
                                if 'result' in data:
                                    tools_result = data['result']
                                    content_list = tools_result.get('content', [])
                                    
                                    if content_list and len(content_list) > 0:
                                        content_item = content_list[0]
                                        text_content = content_item.get('text', '')
                                        
                                        try:
                                            result = json.loads(text_content)
                                            if result.get('success'):
                                                print(f"      ✅ 字号设置为 {font_size}")
                                        except:
                                            pass
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
                                
                                if 'result' in data:
                                    tools_result = data['result']
                                    content_list = tools_result.get('content', [])
                                    
                                    if content_list and len(content_list) > 0:
                                        content_item = content_list[0]
                                        text_content = content_item.get('text', '')
                                        
                                        try:
                                            result = json.loads(text_content)
                                            if result.get('success'):
                                                print(f"      ✅ 对齐方式为 {align_names.get(alignment, 'Unknown')}")
                                        except:
                                            pass
                                break
                        
                        await asyncio.sleep(0.2)
            
            print("\n=== ✅ 修复完成 ===\n")
            print("📋 已完成的操作:")
            print(f"   • 字体 GUID: {font_guid} (FZLTH-GBK)")
            print(f"   • RankItemPrefab 路径：{rankitem_path}")
            print(f"   • Background 目标：{background_target}")
            print()
            print("📝 配置的 Text组件列表:")
            print("   • CloseButton.Text: Font=FZLTH-GBK, Size=28, Text='×'")
            print("   • RankText: Font=FZLTH-GBK, Size=24")
            print("   • NameText: Font=FZLTH-GBK, Size=20")
            print("   • LevelText: Font=FZLTH-GBK, Size=18")
            print()
            print("⚠️ 重要提示:")
            print("1. 在 Unity Inspector中验证所有设置是否正确")
            print("2. 如果字体仍未改变，需要手动设置（见下方说明）")
            print("3. 保存预制件更新以确保变更持久化")
            print()
            print("📋 下一步操作:")
            print("1. 在Hierarchy中选中 RankItemPrefab")
            print("2. 检查 Background 是否有 Image 组件")
            print("3. 逐个检查 Text组件的 Font 字段")
            print("4. 如果字体不对，手动拖拽 Assets/Font/FZLTH-GBK.TTF 到 Font 字段")
            print("5. 保存预制件：将 RankItemPrefab 拖到 Assets/Prefabs/RankItemPrefab.prefab 并替换")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_rankitem_with_known_path())
