import asyncio
import aiohttp
import json

async def fix_all_text_fonts():
    """修正所有 Text 组件的字体为正确的路径"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🎯 修正所有 Text 组件的字体（使用正确路径）===\n")
        
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
                        "name": "font-fixer",
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
            
            # ========== 确认正确的字体路径 ==========
            correct_font_path = "Assets/Font/FZLTH-GBK.TTF"
            print(f"\n📝 使用正确的字体路径：{correct_font_path}")
            print("⚠️ 之前的错误路径：Assets/Resources/Fonts/FZLTH-GBK.ttf")
            
            # ========== 设置所有 Text 组件的字体 ==========
            print("\n🔧 开始设置所有 Text 组件的字体...")
            
            text_objects = [
                ("CloseButton", "×", 28, 4),      # MiddleCenter
                ("RankText", "", 24, 4),           # MiddleCenter
                ("NameText", "", 20, 3),           # MiddleLeft
                ("LevelText", "", 18, 5)           # MiddleRight
            ]
            
            for obj_name, default_text, font_size, alignment in text_objects:
                print(f"\n设置 {obj_name}.Text:")
                
                # 1. 设置字体（使用正确路径）
                print(f"   1. 设置字体为 FZLTH-GBK...")
                set_font_call = {
                    "jsonrpc": "2.0",
                    "id": 2,
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
                                    print(f"      ✅ 字体设置成功!")
                                break
                
                await asyncio.sleep(0.3)
                
                # 2. 设置文本内容（如果是 CloseButton）
                if default_text:
                    print(f"   2. 设置文本内容为 '{default_text}'...")
                    set_text_call = {
                        "jsonrpc": "2.0",
                        "id": 3,
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
                                        print(f"      ✅ 文本内容设置成功!")
                                    break
                    
                    await asyncio.sleep(0.2)
                
                # 3. 设置字号
                print(f"   3. 设置字号为 {font_size}...")
                set_fontsize_call = {
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
                                    print(f"      ✅ 字号设置成功!")
                                break
                    
                    await asyncio.sleep(0.2)
                
                # 4. 设置对齐方式
                align_names = {3: "MiddleLeft", 4: "MiddleCenter", 5: "MiddleRight"}
                print(f"   4. 设置对齐方式为 {align_names.get(alignment, 'Unknown')}...")
                set_alignment_call = {
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
                                    print(f"      ✅ 对齐方式设置成功!")
                                break
                    
                    await asyncio.sleep(0.2)
            
            print("\n=== ✅ 所有 Text 组件字体配置完成 ===\n")
            print("📋 重要说明:")
            print()
            print("❌ 之前的错误:")
            print(f"   - 错误的字体路径：Assets/Resources/Fonts/FZLTH-GBK.ttf")
            print(f"   - Background 已有 Image 组件，不需要重复添加")
            print()
            print("✅ 本次修正:")
            print(f"   - 正确的字体路径：{correct_font_path}")
            print("   - 已确认 Background 不需要添加 Image（已存在）")
            print()
            print("📝 配置的 Text 组件列表:")
            print("   • CloseButton.Text: Font=FZLTH-GBK, Size=28, Text='×', Alignment=MiddleCenter")
            print("   • RankText: Font=FZLTH-GBK, Size=24, Alignment=MiddleCenter")
            print("   • NameText: Font=FZLTH-GBK, Size=20, Alignment=MiddleLeft")
            print("   • LevelText: Font=FZLTH-GBK, Size=18, Alignment=MiddleRight")
            print()
            print("⚠️ 如果 MCP 设置的字体仍未生效，需要在 Unity Inspector中手动操作:")
            print("   1. 选中包含 Text 的对象")
            print("   2. 在 Inspector 中找到 Text 组件")
            print(f"   3. 从 Project 窗口拖拽 Assets/Font/FZLTH-GBK.TTF 到 Font 字段")
            print("   4. 或者点击 Font 字段旁的圆圈 🔍，搜索 'FZLTH' 并选择")
            print()
            print("下一步操作:")
            print("1. 在 Unity Inspector 中验证所有 Text 组件的字体是否正确")
            print("2. 如果字体未改变，按上述步骤手动设置")
            print("3. 保存预制件更新（拖拽到 Assets/Prefabs/并替换）")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_all_text_fonts())
