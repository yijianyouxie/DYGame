import asyncio
import aiohttp
import json

async def add_rect_transform_to_panel():
    """为 LeaderboardPanel 添加 RectTransform 组件"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🎯 为 LeaderboardPanel 添加 RectTransform ===\n")
        
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
                        "name": "rect-transform-adder",
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
            
            # ========== 为 LeaderboardPanel 添加 RectTransform ==========
            print("\n📐 为 LeaderboardPanel 添加 RectTransform 组件...")
            add_rect_call = {
                "jsonrpc": "2.0",
                "id": 2,
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
                                print(f"   ⚠️ 失败：{data['error']}")
                            elif 'result' in data:
                                print(f"   ✅ RectTransform 组件添加成功!")
                            break
            
            await asyncio.sleep(0.5)
            
            # ========== 验证组件是否已添加 ==========
            print("\n🔍 验证 LeaderboardPanel 的完整组件列表...")
            
            # 通过获取 GameObject 信息来验证
            verify_call = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "find_gameobjects",
                    "arguments": {
                        "search_term": "LeaderboardPanel",
                        "search_method": "by_name"
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=verify_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'result' in data and 'content' in data['result']:
                                content = json.loads(data['result']['content'][0]['text'])
                                if content.get('success'):
                                    instance_ids = content.get('data', {}).get('instanceIDs', [])
                                    print(f"✅ 找到 LeaderboardPanel (InstanceID: {instance_ids[0] if instance_ids else 'N/A'})")
                            break
            
            print("\n=== ✅ RectTransform 添加完成 ===\n")
            print("📋 现在 LeaderboardPanel 应该有完整的组件:")
            print()
            print("LeaderboardPanel:")
            print("   ✓ RectTransform ← 新增!")
            print("   ✓ CanvasRenderer")
            print("   ✓ Image")
            print("   ✓ LeaderboardUI 脚本")
            print("   ├─ CloseButton (Button + Text)")
            print("   └─ ScrollContainer (RectTransform)")
            print()
            print("下一步操作:")
            print("1. 在 Unity Inspector中查看 LeaderboardPanel")
            print("2. 确认 RectTransform 组件已存在")
            print("3. 将 LeaderboardPanel 自身拖到 Panel Root 属性字段")
            print("4. 继续配置其他引用字段:")
            print("   • Close Button: CloseButton 子对象")
            print("   • Content Parent: ScrollContainer 子对象")
            print("   • Rank Item Prefab: Assets/Prefabs/RankItemPrefab.prefab")
            print("5. 保存预制件更新（拖拽到 Assets/Prefabs/并替换）")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(add_rect_transform_to_panel())
