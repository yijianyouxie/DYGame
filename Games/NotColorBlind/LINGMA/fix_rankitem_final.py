import asyncio
import aiohttp
import json

async def fix_rankitem_final():
    """最终版本：获取字体 GUID 并修复 RankItemPrefab"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🎯 最终修复：使用正确 GUID 和精确路径 ===\n")
        
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
                        "name": "final-fixer",
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
            
            # ========== 步骤 1: 获取 FZLTH-GBK 字体的 GUID ==========
            print("\n📝 步骤 1: 获取 FZLTH-GBK 字体的 GUID...")
            
            font_guid = "04d2c4a712831164ea7b25868878b4f4"  # 之前成功获取的 GUID
            print(f"   ✅ 使用已知字体 GUID: {font_guid}")
            
            # ========== 步骤 2: 尝试多种方式查找 RankItemPrefab ==========
            print("\n🔍 步骤 2: 多策略查找 RankItemPrefab...")
            
            rankitem_path = None
            
            # 策略 1: 搜索包含 "Rank" 的所有对象
            print("   策略 1: 搜索包含 'Rank' 的对象...")
            find_rank_call = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "find_gameobjects",
                    "arguments": {
                        "search_term": "Rank",
                        "search_method": "name"
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=find_rank_call) as response:
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
                                        print(f"      找到 {len(objects)} 个包含 'Rank' 的对象:")
                                        for obj in objects:
                                            name = obj.get('name', '')
                                            path = obj.get('path', '')
                                            print(f"         - {name} (路径：{path})")
                                            
                                            # 查找 RankItemPrefab 或 RankItem
                                            if 'RankItem' in name or 'RankItemPrefab' in name:
                                                rankitem_path = path
                                                print(f"      ✅ 找到 RankItemPrefab: {rankitem_path}")
                                except Exception as e:
                                    print(f"      ⚠️ 解析失败：{e}")
                            break
            
            await asyncio.sleep(0.3)
            
            # 策略 2: 如果没找到，尝试搜索 "Item"
            if not rankitem_path:
                print("\n   策略 2: 搜索包含 'Item' 的对象...")
                find_item_call = {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "find_gameobjects",
                        "arguments": {
                            "search_term": "Item",
                            "search_method": "name"
                        }
                    }
                }
                
                async with session.post(url, headers=headers_with_session, json=find_item_call) as response:
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
                                            for obj in objects:
                                                name = obj.get('name', '')
                                                path = obj.get('path', '')
                                                if 'Rank' in name or 'Prefab' in name:
                                                    print(f"      可能匹配：{name} (路径：{path})")
                                                    if 'RankItem' in name:
                                                        rankitem_path = path
                                                        print(f"      ✅ 找到 RankItemPrefab: {rankitem_path}")
                                                        break
                                    except:
                                        pass
                                break
                    
                    await asyncio.sleep(0.3)
            
            # 策略 3: 列出场景根目录的所有对象
            if not rankitem_path:
                print("\n   策略 3: 列出场景根目录对象...")
                find_root_call = {
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
                
                async with session.post(url, headers=headers_with_session, json=find_root_call) as response:
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
                                            print(f"      场景中共有 {len(all_objects)} 个对象")
                                            
                                            # 显示前 30 个对象
                                            for i, obj in enumerate(all_objects[:30], 1):
                                                name = obj.get('name', 'N/A')
                                                path = obj.get('path', 'N/A')
                                                print(f"         {i}. {name} - 路径：{path}")
                                                
                                                # 检查是否是 RankItemPrefab
                                                if 'RankItem' in name or 'Leaderboard' in name:
                                                    print(f"            ^^^ 可能是目标对象!")
                                    except Exception as e:
                                        print(f"      ⚠️ 解析失败：{e}")
                                break
                        
                        await asyncio.sleep(0.3)
            
            # ========== 步骤 3: 为 Background 添加 Image 组件 ==========
            if rankitem_path:
                background_target = f"{rankitem_path}/Background"
                print(f"\n📐 步骤 3: 为 {background_target} 添加 Image 组件...")
                
                add_image_call = {
                    "jsonrpc": "2.0",
                    "id": 5,
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
                        "id": 6,
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
                            "id": 7,
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
                        "id": 8,
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
                        "id": 9,
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
                print(f"   • 字体 GUID: {font_guid} (FZLTH-GBK)")
                print(f"   • RankItemPrefab 路径：{rankitem_path}")
                print(f"   • Background 目标：{background_target}")
                print()
                print("下一步操作:")
                print("1. 在 Unity Inspector中验证所有设置")
                print("2. 保存预制件更新")
            else:
                print("\n❌ 未找到 RankItemPrefab")
                print("\n💡 建议操作:")
                print("1. 在Hierarchy 中查找包含 'Rank' 或 'Item' 的对象")
                print("2. 确认 RankItemPrefab 是否已添加到场景中")
                print("3. 如果 RankItemPrefab 是 Prefab 资产，需要在 Project 窗口打开进行编辑")
                print("4. 或者将 RankItemPrefab 从 Project 拖入场景中创建实例")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_rankitem_final())
