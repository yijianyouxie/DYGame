import asyncio
import aiohttp
import json

async def add_image_to_background():
    """为 RankItemPrefab 的 Background 子对象添加 Image 组件"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🎯 为 Background 添加 Image 组件 ===\n")
        
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
                        "name": "background-image-adder",
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
            
            # ========== 为 Background 添加 Image 组件 ==========
            print("\n📐 为 RankItemPrefab/Background 添加 Image 组件...")
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
            
            await asyncio.sleep(0.5)
            
            # ========== 验证组件是否已添加 ==========
            print("\n🔍 验证 Background 组件状态...")
            verify_call = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "find_gameobjects",
                    "arguments": {
                        "search_term": "Background",
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
                                    print(f"✅ 找到 Background (InstanceID: {instance_ids[0] if instance_ids else 'N/A'})")
                                    print(f"   应该包含：RectTransform + Image")
                            break
            
            print("\n=== ✅ Image 组件添加完成 ===\n")
            print("📋 请在 Unity Inspector 中验证:")
            print()
            print("RankItemPrefab/Background 现在应该有:")
            print("   ✓ RectTransform")
            print("   ✓ Image ← 刚刚添加!")
            print()
            print("下一步操作:")
            print("1. 在 Unity 中查看 Background 子对象，确认 Image 组件已存在")
            print("2. 配置 LeaderboardRankItem 脚本的 background 字段:")
            print("   - 选中 RankItemPrefab 预制件")
            print("   - 在 Inspector 中找到 LeaderboardRankItem 组件")
            print("   - 将 Background 子对象拖到 background 字段")
            print("3. 保存预制件更新（拖拽到 Assets/Prefabs/并替换）")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(add_image_to_background())
