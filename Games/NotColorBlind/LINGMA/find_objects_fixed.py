import asyncio
import aiohttp
import json

async def find_specific_objects():
    """查找特定名称的对象（已修复 MCP 协议兼容问题）"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🔍 查找特定对象 ===\n")
        
        try:
            # ========== 初始化连接 ==========
            init_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "object-finder",
                        "version": "1.0.0"
                    }
                }
            }
            
            session_id = None
            async with session.post(url, headers=base_headers, json=init_message) as response:
                session_id = response.headers.get('mcp-session-id')
                
                if not session_id:
                    print("❌ 未获取到会话 ID")
                    return
                
                if response.status == 200:
                    async for line in response.content:
                        if line.decode('utf-8').strip().startswith('data:'):
                            break
            
            headers_with_session = {**base_headers, 'mcp-session-id': session_id}
            
            # 发送初始化完成通知
            await session.post(url, headers=headers_with_session, json={
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            })
            
            # ========== 修复：正确的搜索词 ==========
            test_searches = [
                "Canvas",
                "Main Camera",
                "Button",
                "Start",
                "Directional Light"
            ]
            
            for search_term in test_searches:
                print(f"\n🔍 搜索：'{search_term}'")
                print("-" * 50)
                
                # ======================
                # 🔥 核心修复点：工具名 + 参数结构
                # ======================
                search_call = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        # 1. 正确工具名
                        "name": "manage_gameobject",
                        # 2. 正确参数结构（严格匹配 MCP 服务端要求）
                        "arguments": {
                            "search_method": "by_name",
                            "name": search_term
                        }
                    }
                }
                
                async with session.post(url, headers=headers_with_session, json=search_call) as response:
                    if response.status == 200:
                        async for line in response.content:
                            line_text = line.decode('utf-8').strip()
                            if line_text.startswith('data:'):
                                try:
                                    data = json.loads(line_text[5:])
                                    
                                    if 'result' in data:
                                        tools_result = data['result']
                                        content_list = tools_result.get('content', [])
                                        
                                        if content_list:
                                            text_content = content_list[0].get('text', '')
                                            result = json.loads(text_content)
                                            
                                            if result.get('success'):
                                                objects = result.get('data', {}).get('gameObjects', [])
                                                
                                                if objects:
                                                    print(f"   ✅ 找到 {len(objects)} 个对象:")
                                                    for obj in objects:
                                                        name = obj.get('name', 'Unknown')
                                                        path = obj.get('path', '')
                                                        print(f"      • {name} - {path}")
                                                else:
                                                    print(f"   ⚠️ 未找到对象")
                                            else:
                                                print(f"   ❌ 错误：{result.get('message', '未知错误')}")
                                except json.JSONDecodeError:
                                    print("   ⚠️ 数据解析失败")
                                break
                
                await asyncio.sleep(0.5)
            
            print("\n=== ✅ 测试完成 ===\n")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(find_specific_objects())
