import asyncio
import aiohttp
import json
import re

async def fix_rankitem_proper():
    """使用正确的 MCP 方法修复 RankItemPrefab"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🎯 使用正确的 MCP 方法修复 RankItemPrefab ===\n")
        
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
                        "name": "rankitem-fixer",
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
            
            # ========== 步骤 1: 搜索 Assets/Font/FZLTH-GBK.TTF 获取 GUID ==========
            print("\n📝 步骤 1: 搜索字体资源获取 GUID...")
            
            font_guid = None
            search_font_call = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "manage_asset",
                    "arguments": {
                        "action": "search",
                        "search_term": "FZLTH-GBK",
                        "search_type": "name"
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=search_font_call) as response:
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
                                        assets = result.get('data', {}).get('assets', [])
                                        for asset in assets:
                                            name = asset.get('name', '')
                                            path = asset.get('path', '')
                                            guid = asset.get('guid')
                                            print(f"   找到资源：{name} (路径：{path})")
                                            if 'FZLTH' in name:
                                                font_guid = guid
                                                print(f"   ✅ 获取字体 GUID: {font_guid}")
                                                break
                                    else:
                                        print(f"   ⚠️ 搜索失败：{result.get('error', 'Unknown error')}")
                                except Exception as e:
                                    print(f"   ⚠️ 解析失败：{e}")
                                    print(f"   原始响应：{content_text[:200]}")
                            break
            
            await asyncio.sleep(0.3)
            
            if not font_guid:
                print("   ⚠️ 未找到 FZLTH-GBK 字体，尝试直接读取 meta 文件...")
                # 尝试读取 meta 文件内容
                read_meta_call = {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "manage_asset",
                        "arguments": {
                            "action": "get_info",
                            "path": "Assets/Font/FZLTH-GBK.TTF"
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
                                    try:
                                        result = json.loads(content_text)
                                        if result.get('success'):
                                            # 从返回信息中提取 GUID
                                            info = result.get('data', {})
                                            font_guid = info.get('guid')
                                            if font_guid:
                                                print(f"   ✅ 从 get_info 获取 GUID: {font_guid}")
                                            else:
                                                print(f"   ℹ️ 资源信息：{info}")
                                        else:
                                            print(f"   ⚠️ get_info 失败：{result.get('error', 'Unknown error')}")
                                    except Exception as e:
                                        print(f"   ⚠️ 解析失败：{e}")
                                break
                
                await asyncio.sleep(0.3)
            
            if not font_guid:
                print("   ⚠️ 使用默认字体 GUID（需要在 Inspector中手动指定）")
                font_guid = "0000000000000000e000000000000000"
            
            # ========== 步骤 2: 列出 Hierarchy 中的所有对象 ==========
            print("\n🔍 步骤 2: 获取 Hierarchy 中的所有 GameObject...")
            list_all_call = {
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
            
            all_objects = []
            rankitem_path = None
            
            async with session.post(url, headers=headers_with_session, json=list_all_call) as response:
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
                                        all_objects = result.get('data', {}).get('gameObjects', [])
                                        print(f"   ✅ 场景中共有 {len(all_objects)} 个对象")
                                        
                                        # 查找 RankItemPrefab
                                        for obj in all_objects:
                                            name = obj.get('name', '')
                                            path = obj.get('path', '')
                                            if 'RankItem' in name or 'RankItemPrefab' in name:
                                                rankitem_path = path
                                                print(f"   ✅ 找到 RankItemPrefab: {name} (路径：{rankitem_path})")
                                                break
                                        
                                        if not rankitem_path:
                                            print(f"\n   ℹ️ 未找到 RankItemPrefab，列出前 20 个对象:")
                                            for i, obj in enumerate(all_objects[:20], 1):
                                                print(f"      {i}. {obj.get('name', 'N/A')} - 路径：{obj.get('path', 'N/A')}")
                                except Exception as e:
                                    print(f"   ⚠️ 解析失败：{e}")
                            break
            
            await asyncio.sleep(0.3)
            
            if not rankitem_path:
                # 如果找不到，尝试直接使用名称搜索
                print("\n   尝试直接搜索 'RankItemPrefab'...")
                find_by_name_call = {
                    "jsonrpc": "2.0",
                    "id": 5,
                    "method": "tools/call",
                    "params": {
                        "name": "find_gameobjects",
                        "arguments": {
                            "search_term": "RankItemPrefab",
                            "search_method": "name"
                        }
                    }
                }
                
                async with session.post(url, headers=headers_with_session, json=find_by_name_call) as response:
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
                                                rankitem_path = objects[0].get('path')
                                                print(f"   ✅ 找到 RankItemPrefab (路径：{rankitem_path})")
                                    except:
                                        pass
                                break
                        
                        await asyncio.sleep(0.3)
            
            # ========== 步骤 3: 为 Background 添加 Image 组件 ==========
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
                
                # ========== 步骤 4: 设置所有 Text组件的字体 ==========
                print(f"\n📝 步骤 4: 设置所有 Text组件使用字体 GUID: {font_guid}...")
                
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
                    
                    # 设置文本内容
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
                    
                    # 设置字号
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
                    
                    # 设置对齐方式
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
                print(f"📋 关键信息:")
                print(f"   • 字体 GUID: {font_guid}")
                print(f"   • RankItemPrefab 路径：{rankitem_path}")
                print(f"   • Background 目标：{background_target}")
                print()
                print("下一步操作:")
                print("1. 在 Unity Inspector 中验证所有设置")
                print("2. 保存预制件更新")
            else:
                print("\n❌ 未找到 RankItemPrefab")
                print("\n请在 Hierarchy 中确认:")
                print("1. RankItemPrefab 是否存在")
                print("2. 查看它的准确名称和路径")
                print("3. 可能需要在 Project 窗口中打开预制件进行编辑")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_rankitem_proper())
