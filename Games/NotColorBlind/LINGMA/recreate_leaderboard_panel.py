import asyncio
import aiohttp
import json

async def recreate_leaderboard_panel():
    """重新创建 LeaderboardPanel（带正确的 RectTransform）"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🎯 重新创建 LeaderboardPanel（使用 RectTransform）===\n")
        
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
                        "name": "leaderboard-recreator",
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
            
            # ========== 步骤 1: 保存子对象信息 ==========
            print("\n📋 步骤 1: 记录当前子对象...")
            print("   需要记住的子对象:")
            print("   - CloseButton")
            print("   - ScrollContainer")
            
            # ========== 步骤 2: 删除旧的 LeaderboardPanel ==========
            print("\n🗑️ 步骤 2: 删除旧的 LeaderboardPanel...")
            delete_call = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "manage_gameobject",
                    "arguments": {
                        "action": "delete",
                        "target": "LeaderboardPanel",
                        "search_method": "by_name"
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=delete_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'error' in data:
                                print(f"   ⚠️ 删除失败：{data['error']}")
                            elif 'result' in data:
                                print(f"   ✅ 旧 LeaderboardPanel 已删除")
                            break
            
            await asyncio.sleep(0.5)
            
            # ========== 步骤 3: 创建新的 LeaderboardPanel（带 RectTransform） ==========
            print("\n✨ 步骤 3: 创建新的 LeaderboardPanel（带 RectTransform）...")
            
            # 注意：不指定 primitive_type 会创建空 GameObject，然后我们手动添加 RectTransform
            create_call = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "manage_gameobject",
                    "arguments": {
                        "action": "create",
                        "name": "LeaderboardPanel"
                        # 不指定 primitive_type，创建空对象
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=create_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'error' in data:
                                print(f"   ⚠️ 创建失败：{data['error']}")
                            elif 'result' in data:
                                print(f"   ✅ 新 LeaderboardPanel 创建成功")
                            break
            
            await asyncio.sleep(0.5)
            
            # ========== 步骤 4: 添加 RectTransform 作为第一个组件 ==========
            print("\n📐 步骤 4: 添加 RectTransform 组件...")
            add_rect_call = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "manage_components",
                    "arguments": {
                        "action": "add",
                        "target": "LeaderboardPanel",
                        "search_method": "by_name",
                        "component_type": "RectTransform"
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=add_rect_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'error' in data:
                                print(f"   ⚠️ 添加失败：{data['error']}")
                            elif 'result' in data:
                                print(f"   ✅ RectTransform 添加成功!")
                            break
            
            await asyncio.sleep(0.5)
            
            # ========== 步骤 5: 添加其他必要组件 ==========
            print("\n🎨 步骤 5: 添加其他组件...")
            components_to_add = ["CanvasRenderer", "Image", "LeaderboardUI"]
            
            for comp_type in components_to_add:
                add_comp_call = {
                    "jsonrpc": "2.0",
                    "id": 5,
                    "method": "tools/call",
                    "params": {
                        "name": "manage_components",
                        "arguments": {
                            "action": "add",
                            "target": "LeaderboardPanel",
                            "search_method": "by_name",
                            "component_type": comp_type
                        }
                    }
                }
                
                async with session.post(url, headers=headers_with_session, json=add_comp_call) as response:
                    if response.status == 200:
                        async for line in response.content:
                            line_text = line.decode('utf-8').strip()
                            if line_text.startswith('data:'):
                                data = json.loads(line_text[5:])
                                if 'error' not in data:
                                    print(f"   ✅ {comp_type}: 成功")
                                break
                
                await asyncio.sleep(0.2)
            
            # ========== 步骤 6: 重新创建子对象 ==========
            print("\n👶 步骤 6: 重新创建子对象...")
            
            # 创建 CloseButton
            print("\n创建 CloseButton...")
            create_close_btn = {
                "jsonrpc": "2.0",
                "id": 6,
                "method": "tools/call",
                "params": {
                    "name": "manage_gameobject",
                    "arguments": {
                        "action": "create",
                        "name": "CloseButton",
                        "parent": "LeaderboardPanel"
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=create_close_btn) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'result' in data:
                                print("✅ CloseButton 创建成功")
                            break
            
            # 为 CloseButton 添加组件
            for comp in ["RectTransform", "Button", "Text"]:
                add_comp_call = {
                    "jsonrpc": "2.0",
                    "id": 7,
                    "method": "tools/call",
                    "params": {
                        "name": "manage_components",
                        "arguments": {
                            "action": "add",
                            "target": "CloseButton",
                            "search_method": "by_name",
                            "component_type": comp
                        }
                    }
                }
                
                async with session.post(url, headers=headers_with_session, json=add_comp_call) as response:
                    if response.status == 200:
                        async for line in response.content:
                            line_text = line.decode('utf-8').strip()
                            if line_text.startswith('data:'):
                                data = json.loads(line_text[5:])
                                if 'error' not in data:
                                    print(f"   ✅ {comp}: 成功")
                                break
                
                await asyncio.sleep(0.2)
            
            # 创建 ScrollContainer
            print("\n创建 ScrollContainer...")
            create_scroll = {
                "jsonrpc": "2.0",
                "id": 8,
                "method": "tools/call",
                "params": {
                    "name": "manage_gameobject",
                    "arguments": {
                        "action": "create",
                        "name": "ScrollContainer",
                        "parent": "LeaderboardPanel"
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=create_scroll) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'result' in data:
                                print("✅ ScrollContainer 创建成功")
                            break
            
            # 为 ScrollContainer 添加 RectTransform
            add_rect_call = {
                "jsonrpc": "2.0",
                "id": 9,
                "method": "tools/call",
                "params": {
                    "name": "manage_components",
                    "arguments": {
                        "action": "add",
                        "target": "ScrollContainer",
                        "search_method": "by_name",
                        "component_type": "RectTransform"
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=add_rect_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'error' not in data:
                                print("   ✅ RectTransform: 成功")
                            break
            
            print("\n=== ✅ 重新创建完成 ===\n")
            print("📋 请在 Unity 中验证:")
            print()
            print("1. LeaderboardPanel 现在应该有:")
            print("   ✓ RectTransform (不再是 Transform!) ← 关键修复!")
            print("   ✓ CanvasRenderer")
            print("   ✓ Image")
            print("   ✓ LeaderboardUI 脚本")
            print("   ├─ CloseButton (RectTransform + Button + Text)")
            print("   └─ ScrollContainer (RectTransform)")
            print()
            print("2. 现在可以将 LeaderboardPanel 自身拖到 Panel Root 字段了!")
            print()
            print("下一步操作:")
            print("1. 在 Unity Inspector 中确认是 RectTransform 而不是 Transform")
            print("2. 配置 LeaderboardUI 组件的所有引用字段")
            print("3. 保存预制件更新（拖拽到 Assets/Prefabs/并替换）")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(recreate_leaderboard_panel())
