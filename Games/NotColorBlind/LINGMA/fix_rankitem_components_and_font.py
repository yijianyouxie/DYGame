import asyncio
import aiohttp
import json

async def fix_rankitem_components_and_font():
    """为 RankItemPrefab 添加完整组件并设置字体"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🎯 修复 RankItemPrefab 组件和字体设置 ===\n")
        
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
            
            # ========== 步骤 1: 为 Background 添加 Image 组件 ==========
            print("\n📐 步骤 1: 为 Background 添加 Image 组件...")
            add_image_call = {
                "jsonrpc": "2.0",
                "id": 2,
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
                                print(f"   ⚠️ 添加失败：{data['error']}")
                            elif 'result' in data:
                                print(f"   ✅ Image 组件添加成功!")
                            break
            
            await asyncio.sleep(0.3)
            
            # ========== 步骤 2: 设置所有 Text 组件的字体为 FZLTH-GBK ==========
            print("\n📝 步骤 2: 设置所有 Text 组件使用 Font/FZLTH-GBK...")
            
            text_objects = [
                ("CloseButton", "×", 28),
                ("RankText", "", 24),
                ("NameText", "", 20),
                ("LevelText", "", 18)
            ]
            
            for obj_name, default_text, font_size in text_objects:
                print(f"\n设置 {obj_name}.Text 的字体和属性...")
                
                # 设置字体
                set_font_call = {
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
                            "property": "font",
                            "value": {"asset_path": "Assets/Resources/Fonts/FZLTH-GBK.ttf"}
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
                                    print(f"   ⚠️ 字体设置失败：{data['error']}")
                                    print(f"   💡 可能需要在 Unity 中手动选择字体")
                                elif 'result' in data:
                                    print(f"   ✅ 字体设置成功!")
                                break
                
                await asyncio.sleep(0.2)
                
                # 设置文本内容（如果是 CloseButton）
                if default_text:
                    set_text_call = {
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
                                        print(f"   ✅ 文本内容设置为：{default_text}")
                                    break
                    
                    await asyncio.sleep(0.2)
                
                # 设置字号
                set_fontsize_call = {
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
                                    print(f"   ✅ 字号设置为：{font_size}")
                                break
                    
                    await asyncio.sleep(0.2)
                
                # 设置对齐方式
                alignment = 4  # MiddleCenter
                if obj_name == "NameText":
                    alignment = 3  # MiddleLeft
                elif obj_name == "LevelText":
                    alignment = 5  # MiddleRight
                
                set_alignment_call = {
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
                                    align_names = {3: "MiddleLeft", 4: "MiddleCenter", 5: "MiddleRight"}
                                    print(f"   ✅ 对齐方式设置为：{align_names.get(alignment, 'Unknown')}")
                                break
                    
                    await asyncio.sleep(0.2)
            
            print("\n=== ✅ 组件和字体配置完成 ===\n")
            print("📋 请在 Unity Inspector 中验证以下内容:")
            print()
            print("1. RankItemPrefab/Background:")
            print("   ✓ RectTransform")
            print("   ✓ Image ← 刚刚添加!")
            print()
            print("2. 所有 Text 组件的字体设置:")
            print("   • CloseButton.Text: Font=FZLTH-GBK, Size=28, Text='×', Alignment=MiddleCenter")
            print("   • RankText: Font=FZLTH-GBK, Size=24, Alignment=MiddleCenter")
            print("   • NameText: Font=FZLTH-GBK, Size=20, Alignment=MiddleLeft")
            print("   • LevelText: Font=FZLTH-GBK, Size=18, Alignment=MiddleRight")
            print()
            print("⚠️ 重要提示:")
            print("如果 MCP 设置的字体未生效，需要在 Unity 中手动指定:")
            print("1. 选中包含 Text 的对象（如 CloseButton、RankText 等）")
            print("2. 在 Inspector 中找到 Text 组件")
            print("3. 点击 Font 字段旁边的圆圈 🔍")
            print("4. 搜索 'FZLTH' 并选择 'FZLTH-GBK'")
            print("5. 或者直接从 Assets/Resources/Fonts/拖拽 FZLTH-GBK.ttf 到 Font 字段")
            print()
            print("下一步操作:")
            print("1. 在 Unity 中确认所有组件和字体设置正确")
            print("2. 配置 LeaderboardRankItem 脚本的字段:")
            print("   - rankText: 拖入 RankText")
            print("   - nameText: 拖入 NameText")
            print("   - levelText: 拖入 LevelText")
            print("   - background: 拖入 Background")
            print("3. 保存预制件更新（拖拽到 Assets/Prefabs/并替换）")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_rankitem_components_and_font())
