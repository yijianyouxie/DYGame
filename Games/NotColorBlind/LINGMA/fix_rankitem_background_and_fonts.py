import asyncio
import aiohttp
import json

async def fix_rankitem_background_and_fonts():
    """修复 RankItemPrefab/Background 的 Image 组件和所有 Text 字体"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🎯 修复 RankItemPrefab/Background 的 Image 和所有 Text 字体 ===\n")
        
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
                        "name": "background-image-fixer",
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
            
            # ========== 步骤 1: 先查找 Background 对象确认位置 ==========
            print("\n🔍 步骤 1: 查找 Background 对象...")
            find_bg_call = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "find_gameobjects",
                    "arguments": {
                        "search_term": "Background",
                        "search_method": "by_name"
                    }
                }
            }
            
            background_instance_id = None
            async with session.post(url, headers=headers_with_session, json=find_bg_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'result' in data and 'content' in data['result']:
                                content = json.loads(data['result']['content'][0]['text'])
                                if content.get('success'):
                                    instance_ids = content.get('data', {}).get('instanceIDs', [])
                                    if instance_ids:
                                        background_instance_id = instance_ids[0]
                                        print(f"   ✅ 找到 Background (InstanceID: {background_instance_id})")
                                    else:
                                        print(f"   ⚠️ 未找到 Background 对象")
                            break
            
            await asyncio.sleep(0.3)
            
            # ========== 步骤 2: 为 Background 添加 Image 组件 ==========
            print("\n📐 步骤 2: 为 Background 添加 Image 组件...")
            add_image_call = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "manage_components",
                    "arguments": {
                        "action": "add",
                        "target": "Background",
                        "search_method": "by_name",
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
            
            # ========== 步骤 3: 设置所有 Text 组件的字体为 Assets/Font/FZLTH-GBK.TTF ==========
            print("\n📝 步骤 3: 设置所有 Text 组件使用正确的字体...")
            correct_font_path = "Assets/Font/FZLTH-GBK.TTF"
            print(f"   使用字体路径：{correct_font_path}")
            
            text_objects = [
                ("CloseButton", "×", 28, 4),      # MiddleCenter
                ("RankText", "", 24, 4),           # MiddleCenter
                ("NameText", "", 20, 3),           # MiddleLeft
                ("LevelText", "", 18, 5)           # MiddleRight
            ]
            
            for obj_name, default_text, font_size, alignment in text_objects:
                print(f"\n   配置 {obj_name}.Text:")
                
                # 1. 设置字体
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
                            "property": "font",
                            "value": {"asset_path": correct_font_path}
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
                                    print(f"      ✅ 字体设置为 FZLTH-GBK")
                                break
                
                await asyncio.sleep(0.2)
                
                # 2. 设置文本内容（如果是 CloseButton）
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
                
                # 3. 设置字号
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
                
                # 4. 设置对齐方式
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
            print("📋 请在 Unity Inspector中验证以下内容:")
            print()
            print("1. RankItemPrefab/Background:")
            print("   ✓ RectTransform")
            print("   ✓ Image ← 应该已添加!")
            print()
            print("2. 所有 Text 组件的字体:")
            print(f"   • CloseButton.Text: Font=FZLTH-GBK (Assets/Font/FZLTH-GBK.TTF), Size=28")
            print(f"   • RankText: Font=FZLTH-GBK, Size=24")
            print(f"   • NameText: Font=FZLTH-GBK, Size=20")
            print(f"   • LevelText: Font=FZLTH-GBK, Size=18")
            print()
            print("⚠️ 重要提示:")
            print("如果 MCP 设置的字体仍未生效，需要在 Unity 中手动操作:")
            print("1. 选中包含 Text 的对象（如 CloseButton、RankText 等）")
            print("2. 在 Inspector 中找到 Text 组件")
            print("3. 从 Project 窗口拖拽以下文件到 Font 字段:")
            print(f"   Assets/Font/FZLTH-GBK.TTF")
            print("4. 或者点击 Font 字段旁的圆圈 🔍，搜索 'FZLTH' 并选择")
            print()
            print("下一步操作:")
            print("1. 在 Unity 中打开 Hierarchy 查看 RankItemPrefab/Background")
            print("2. 确认 Image 组件是否存在")
            print("3. 逐个检查 Text 组件的 Font 字段是否正确")
            print("4. 保存预制件更新（拖拽到 Assets/Prefabs/并替换）")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_rankitem_background_and_fonts())
