import asyncio
import aiohttp
import json

async def check_and_fix_leaderboard():
    """检查并修复排行榜对象的完整结构"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🔍 检查并修复排行榜结构 ===\n")
        
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
                        "name": "leaderboard-fixer",
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
            
            # ========== 查找 LeaderboardPanel ==========
            print("\n📋 查找 LeaderboardPanel...")
            find_call = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "find_gameobjects",
                    "arguments": {
                        "search_term": "LeaderboardPanel",
                        "search_method": "by_name"
                    }
                }
            }
            
            panel_found = False
            async with session.post(url, headers=headers_with_session, json=find_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            print(f"查找结果：{data}")
                            if 'result' in data and 'content' in data['result']:
                                content = json.loads(data['result']['content'][0]['text'])
                                if content.get('success') and content.get('data', {}).get('instanceIDs'):
                                    panel_found = True
                                    print(f"✅ 找到 LeaderboardPanel (InstanceIDs: {content['data']['instanceIDs']})")
                            break
            
            if not panel_found:
                print("❌ 未找到 LeaderboardPanel，需要重新创建")
                return
            
            await asyncio.sleep(0.5)
            
            # ========== 查找 RankItemPrefab ==========
            print("\n📋 查找 RankItemPrefab...")
            find_rank_call = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "find_gameobjects",
                    "arguments": {
                        "search_term": "RankItemPrefab",
                        "search_method": "by_name"
                    }
                }
            }
            
            rank_found = False
            async with session.post(url, headers=headers_with_session, json=find_rank_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            print(f"查找结果：{data}")
                            if 'result' in data and 'content' in data['result']:
                                content = json.loads(data['result']['content'][0]['text'])
                                if content.get('success') and content.get('data', {}).get('instanceIDs'):
                                    rank_found = True
                                    print(f"✅ 找到 RankItemPrefab (InstanceIDs: {content['data']['instanceIDs']})")
                            break
            
            if not rank_found:
                print("❌ 未找到 RankItemPrefab，需要重新创建")
                return
            
            await asyncio.sleep(0.5)
            
            # ========== 使用 manage_components 添加组件 ==========
            print("\n🎨 开始添加组件...")
            
            # 定义需要添加的组件列表
            objects_components = [
                ("LeaderboardPanel", ["RectTransform", "CanvasRenderer", "Image", "LeaderboardUI"]),
                ("CloseButton", ["RectTransform", "Button", "Text"]),
                ("ScrollContainer", ["RectTransform"]),
                ("RankItemPrefab", ["RectTransform", "CanvasRenderer", "Image", "LeaderboardRankItem"]),
                ("Background", ["RectTransform", "Image"]),
                ("RankText", ["RectTransform", "Text"]),
                ("NameText", ["RectTransform", "Text"]),
                ("LevelText", ["RectTransform", "Text"])
            ]
            
            for obj_name, components in objects_components:
                print(f"\n为 {obj_name} 添加组件:")
                
                for component in components:
                    add_component_call = {
                        "jsonrpc": "2.0",
                        "id": 4,
                        "method": "tools/call",
                        "params": {
                            "name": "manage_components",
                            "arguments": {
                                "action": "add",
                                "target": obj_name,
                                "search_method": "by_name",
                                "component": component
                            }
                        }
                    }
                    
                    async with session.post(url, headers=headers_with_session, json=add_component_call) as response:
                        if response.status == 200:
                            async for line in response.content:
                                line_text = line.decode('utf-8').strip()
                                if line_text.startswith('data:'):
                                    data = json.loads(line_text[5:])
                                    if 'error' in data:
                                        print(f"   ⚠️ {component}: 失败 - {data['error']}")
                                    elif 'result' in data:
                                        print(f"   ✅ {component}: 成功")
                                    break
                    
                    await asyncio.sleep(0.2)
            
            await asyncio.sleep(0.5)
            
            # ========== 创建子对象（如果不存在） ==========
            print("\n👶 创建子对象结构...")
            
            # 创建 CloseButton
            print("\n创建 CloseButton...")
            create_close_btn = {
                "jsonrpc": "2.0",
                "id": 5,
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
            
            # 创建 ScrollContainer
            print("\n创建 ScrollContainer...")
            create_scroll = {
                "jsonrpc": "2.0",
                "id": 6,
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
            
            # 创建 RankItemPrefab 的子对象
            print("\n创建 RankItemPrefab 的子对象...")
            for child_name in ["Background", "RankText", "NameText", "LevelText"]:
                create_child = {
                    "jsonrpc": "2.0",
                    "id": 7,
                    "method": "tools/call",
                    "params": {
                        "name": "manage_gameobject",
                        "arguments": {
                            "action": "create",
                            "name": child_name,
                            "parent": "RankItemPrefab"
                        }
                    }
                }
                
                async with session.post(url, headers=headers_with_session, json=create_child) as response:
                    if response.status == 200:
                        async for line in response.content:
                            line_text = line.decode('utf-8').strip()
                            if line_text.startswith('data:'):
                                data = json.loads(line_text[5:])
                                if 'result' in data:
                                    print(f"✅ {child_name} 创建成功")
                                break
                
                await asyncio.sleep(0.2)
            
            print("\n=== ✅ 修复完成 ===\n")
            print("📋 请在 Unity 中检查以下内容:")
            print()
            print("1. LeaderboardPanel:")
            print("   ✓ RectTransform, CanvasRenderer, Image, LeaderboardUI 脚本")
            print("   ├─ CloseButton (带 RectTransform, Button, Text)")
            print("   └─ ScrollContainer (带 RectTransform)")
            print()
            print("2. RankItemPrefab:")
            print("   ✓ RectTransform, CanvasRenderer, Image, LeaderboardRankItem 脚本")
            print("   ├─ Background (带 RectTransform, Image)")
            print("   ├─ RankText (带 RectTransform, Text)")
            print("   ├─ NameText (带 RectTransform, Text)")
            print("   └─ LevelText (带 RectTransform, Text)")
            print()
            print("3. 下一步操作:")
            print("   • 在 Inspector 中配置 LeaderboardUI 组件的引用字段")
            print("   • 调整 UI 布局和 Text 内容")
            print("   • 保存预制件更新（拖拽到 Assets/Prefabs/并替换）")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_and_fix_leaderboard())
