import asyncio
import aiohttp
import json

async def setup_leaderboard_properties():
    """为排行榜预设添加完整的属性配置和 Font 设置"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🎯 配置排行榜预设的完整属性 ===\n")
        
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
                        "name": "leaderboard-config",
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
            
            # ========== 分析脚本属性需求 ==========
            print("\n📋 LeaderboardUI 脚本需要的属性:")
            print("   UI 组件引用:")
            print("   • panelRoot (RectTransform)")
            print("   • closeButton (Button)")
            print("   • contentParent (Transform)")
            print("   • rankItemPrefab (GameObject)")
            print("   前三名特殊标识:")
            print("   • crownImage (Image)")
            print("   颜色配置:")
            print("   • goldColor, silverColor, bronzeColor, normalColor")
            print()
            print("LeaderboardRankItem 脚本需要的属性:")
            print("   UI 组件:")
            print("   • rankText (Text)")
            print("   • nameText (Text)")
            print("   • levelText (Text)")
            print("   • avatarImage (Image)")
            print("   • background (Image)")
            print("   前三名标识:")
            print("   • crownPrefab (GameObject)")
            print()
            print("⚠️ 注意：所有 Text 组件需要使用 Font/FZLTH-GBK 字体")
            
            await asyncio.sleep(0.5)
            
            # ========== 为 RankItemPrefab 添加缺失的组件 ==========
            print("\n🔧 为 RankItemPrefab 添加缺失的组件...")
            
            # 检查并添加 Avatar Image
            print("\n为 Background 子对象添加 Image 组件（如果还没有）...")
            add_bg_image = {
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
            
            async with session.post(url, headers=headers_with_session, json=add_bg_image) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'error' not in data:
                                print("✅ Background Image 已存在或添加成功")
                            break
            
            await asyncio.sleep(0.3)
            
            # ========== 设置 Text 组件的字体属性 ==========
            print("\n📝 设置所有 Text 组件使用 Font/FZLTH-GBK 字体...")
            
            text_objects = ["CloseButton/Text", "RankText", "NameText", "LevelText"]
            
            for text_path in text_objects:
                full_path = f"LeaderboardPanel/{text_path}" if "/" not in text_path else f"LeaderboardPanel/{text_path}"
                
                # 对于 RankItemPrefab 的子对象
                if text_path in ["RankText", "NameText", "LevelText"]:
                    full_path = f"RankItemPrefab/{text_path}"
                
                print(f"\n设置 {text_path} 的字体...")
                
                # 使用 set_property 设置字体
                set_font_call = {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "manage_components",
                        "arguments": {
                            "action": "set_property",
                            "target": text_path.split("/")[-1],  # 只取最后的对象名
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
                                    print(f"   ⚠️ 设置字体失败：{data['error']}")
                                    print(f"   💡 可能需要在 Unity 中手动指定字体路径")
                                elif 'result' in data:
                                    print(f"   ✅ 字体设置成功!")
                                break
                
                await asyncio.sleep(0.2)
            
            # ========== 设置 Text 的其他属性 ==========
            print("\n🎨 设置 Text 组件的其他属性...")
            
            # CloseButton 的 Text
            print("\n设置 CloseButton.Text...")
            close_text_props = [
                ("text", "×"),
                ("fontSize", 28),
                ("alignment", 4)  # MiddleCenter
            ]
            
            for prop_name, prop_value in close_text_props:
                set_prop_call = {
                    "jsonrpc": "2.0",
                    "id": 4,
                    "method": "tools/call",
                    "params": {
                        "name": "manage_components",
                        "arguments": {
                            "action": "set_property",
                            "target": "CloseButton",
                            "search_method": "by_name",
                            "component_type": "Text",
                            "property": prop_name,
                            "value": prop_value
                        }
                    }
                }
                
                async with session.post(url, headers=headers_with_session, json=set_prop_call) as response:
                    if response.status == 200:
                        async for line in response.content:
                            line_text = line.decode('utf-8').strip()
                            if line_text.startswith('data:'):
                                data = json.loads(line_text[5:])
                                if 'error' not in data:
                                    print(f"   ✅ 设置 {prop_name} = {prop_value}")
                                break
                
                await asyncio.sleep(0.2)
            
            # RankText 属性
            print("\n设置 RankText...")
            rank_text_props = [
                ("fontSize", 24),
                ("alignment", 4)
            ]
            
            for prop_name, prop_value in rank_text_props:
                set_prop_call = {
                    "jsonrpc": "2.0",
                    "id": 5,
                    "method": "tools/call",
                    "params": {
                        "name": "manage_components",
                        "arguments": {
                            "action": "set_property",
                            "target": "RankText",
                            "search_method": "by_name",
                            "component_type": "Text",
                            "property": prop_name,
                            "value": prop_value
                        }
                    }
                }
                
                async with session.post(url, headers=headers_with_session, json=set_prop_call) as response:
                    if response.status == 200:
                        async for line in response.content:
                            line_text = line.decode('utf-8').strip()
                            if line_text.startswith('data:'):
                                data = json.loads(line_text[5:])
                                if 'error' not in data:
                                    print(f"   ✅ 设置 {prop_name} = {prop_value}")
                                break
                
                await asyncio.sleep(0.2)
            
            # NameText 属性
            print("\n设置 NameText...")
            name_text_props = [
                ("fontSize", 20),
                ("alignment", 3)  # MiddleLeft
            ]
            
            for prop_name, prop_value in name_text_props:
                set_prop_call = {
                    "jsonrpc": "2.0",
                    "id": 6,
                    "method": "tools/call",
                    "params": {
                        "name": "manage_components",
                        "arguments": {
                            "action": "set_property",
                            "target": "NameText",
                            "search_method": "by_name",
                            "component_type": "Text",
                            "property": prop_name,
                            "value": prop_value
                        }
                    }
                }
                
                async with session.post(url, headers=headers_with_session, json=set_prop_call) as response:
                    if response.status == 200:
                        async for line in response.content:
                            line_text = line.decode('utf-8').strip()
                            if line_text.startswith('data:'):
                                data = json.loads(line_text[5:])
                                if 'error' not in data:
                                    print(f"   ✅ 设置 {prop_name} = {prop_value}")
                                break
                
                await asyncio.sleep(0.2)
            
            # LevelText 属性
            print("\n设置 LevelText...")
            level_text_props = [
                ("fontSize", 18),
                ("alignment", 5)  # MiddleRight
            ]
            
            for prop_name, prop_value in level_text_props:
                set_prop_call = {
                    "jsonrpc": "2.0",
                    "id": 7,
                    "method": "tools/call",
                    "params": {
                        "name": "manage_components",
                        "arguments": {
                            "action": "set_property",
                            "target": "LevelText",
                            "search_method": "by_name",
                            "component_type": "Text",
                            "property": prop_name,
                            "value": prop_value
                        }
                    }
                }
                
                async with session.post(url, headers=headers_with_session, json=set_prop_call) as response:
                    if response.status == 200:
                        async for line in response.content:
                            line_text = line.decode('utf-8').strip()
                            if line_text.startswith('data:'):
                                data = json.loads(line_text[5:])
                                if 'error' not in data:
                                    print(f"   ✅ 设置 {prop_name} = {prop_value}")
                                break
                
                await asyncio.sleep(0.2)
            
            print("\n=== ✅ 属性配置完成 ===\n")
            print("📋 总结:")
            print()
            print("LeaderboardPanel 预制件:")
            print("   ✓ RectTransform, CanvasRenderer, Image, LeaderboardUI 脚本")
            print("   ✓ 子对象：CloseButton (带 Button、Text)、ScrollContainer (带 RectTransform)")
            print("   ⚠️ Inspector 中需要手动配置的字段:")
            print("      • panelRoot: 拖入自身")
            print("      • closeButton: 拖入 CloseButton 子对象")
            print("      • contentParent: 拖入 ScrollContainer")
            print("      • rankItemPrefab: 拖入 Assets/Prefabs/RankItemPrefab.prefab")
            print("      • crownImage: (可选，留空)")
            print("      • 颜色配置已在脚本中设置默认值")
            print()
            print("RankItemPrefab 预制件:")
            print("   ✓ RectTransform, CanvasRenderer, Image, LeaderboardRankItem 脚本")
            print("   ✓ 子对象：Background (Image)、RankText (Text)、NameText (Text)、LevelText (Text)")
            print("   ✓ Text 组件已设置:")
            print("      • 字体：Font/FZLTH-GBK (如果 MCP 支持)")
            print("      • fontSize: RankText=24, NameText=20, LevelText=18")
            print("      • alignment: 自动对齐")
            print("   ⚠️ Inspector 中需要手动配置的字段:")
            print("      • rankText: 拖入 RankText 子对象")
            print("      • nameText: 拖入 NameText 子对象")
            print("      • levelText: 拖入 LevelText 子对象")
            print("      • avatarImage: (可选，留空)")
            print("      • background: 拖入 Background 子对象")
            print("      • crownPrefab: (可选，留空)")
            print()
            print("下一步操作:")
            print("1. 在 Unity Inspector 中查看并确认所有字段赋值")
            print("2. 如果字体设置未生效，需要在每个 Text 组件的 Font 字段手动选择:")
            print("   Assets/Resources/Fonts/FZLTH-GBK.ttf")
            print("3. 保存预制件更新（拖拽到 Assets/Prefabs/并替换）")
            print("4. 测试运行游戏查看效果")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(setup_leaderboard_properties())
