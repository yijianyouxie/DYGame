import asyncio
import aiohttp
import json

async def fix_with_correct_params():
    """使用正确的 MCP 参数进行修复"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🎯 使用正确的 MCP 参数进行修复 ===\n")
        
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
                        "name": "correct-fix",
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
            print(f"\n✅ 使用字体 GUID: {font_guid}")
            
            # ========== 步骤 1: 列出场景中的所有对象 ==========
            print("\n🔍 步骤 1: 获取场景中的所有 GameObject...")
            
            find_all_call = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "find_gameobjects",
                    "arguments": {
                        "search_term": "",
                        "search_method": "by_name",  # 修正为 by_name
                        "include_inactive": True,
                        "page_size": 500
                    }
                }
            }
            
            all_objects = []
            rankitem_path = None
            
            async with session.post(url, headers=headers_with_session, json=find_all_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            
                            # 直接处理响应数据
                            if 'result' in data:
                                tools_result = data['result']
                                content_list = tools_result.get('content', [])
                                
                                if content_list and len(content_list) > 0:
                                    content_item = content_list[0]
                                    text_content = content_item.get('text', '')
                                    
                                    try:
                                        result = json.loads(text_content)
                                        if result.get('success'):
                                            all_objects = result.get('data', {}).get('gameObjects', [])
                                            print(f"   ✅ 找到 {len(all_objects)} 个对象")
                                            
                                            # 查找 RankItemPrefab
                                            for obj in all_objects:
                                                name = obj.get('name', '')
                                                path = obj.get('path', '')
                                                
                                                if 'RankItem' in name or 'RankItemPrefab' in name:
                                                    rankitem_path = path
                                                    print(f"   ✅ 找到 RankItemPrefab: {name} (路径：{rankitem_path})")
                                                    break
                                            
                                            if not rankitem_path:
                                                print(f"\n   ℹ️ 未找到 RankItemPrefab，显示前 30 个对象:")
                                                for i, obj in enumerate(all_objects[:30], 1):
                                                    print(f"      {i}. {obj.get('name', 'N/A')} - 路径：{obj.get('path', 'N/A')}")
                                        
                                        else:
                                            error_msg = result.get('error', 'Unknown error')
                                            print(f"   ❌ 获取失败：{error_msg}")
                                    
                                    except Exception as e:
                                        print(f"   ⚠️ 解析失败：{e}")
                                        print(f"   原始响应 (前 300 字符): {text_content[:300]}")
                            break
            
            await asyncio.sleep(0.3)
            
            # ========== 步骤 2: 为 Background 添加 Image 组件 ==========
            if rankitem_path:
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
                print("\n💡 请在 Hierarchy 中确认:")
                print("1. RankItemPrefab 是否存在")
                print("2. 如果存在，请告诉我它的完整路径")
                print("3. 或者它可能在 Project 窗口的 Prefabs 文件夹中，需要打开编辑")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_with_correct_params())
