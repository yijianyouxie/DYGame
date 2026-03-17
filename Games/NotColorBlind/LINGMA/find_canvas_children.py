import asyncio
import aiohttp
import json

async def find_canvas_children():
    """查找 Canvas 下的所有子对象"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🔍 查找 Canvas 下的所有子对象 ===\n")
        
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
                        "name": "canvas-children-finder",
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
            
            await session.post(url, headers=headers_with_session, json={
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            })
            
            # ========== 查找 Canvas 下的所有对象 ==========
            print("\n📋 Canvas 的子对象:")
            print("-" * 50)
            
            find_all_call = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "find_gameobjects",
                    "arguments": {
                        "search_term": "",
                        "search_method": "by_name",
                        "include_inactive": True,
                        "page_size": 100
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=find_all_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            
                            if 'result' in data:
                                tools_result = data['result']
                                content_list = tools_result.get('content', [])
                                
                                if content_list and len(content_list) > 0:
                                    content_item = content_list[0]
                                    text_content = content_item.get('text', '')
                                    
                                    try:
                                        result = json.loads(text_content)
                                        if result.get('success'):
                                            objects = result.get('data', {}).get('gameObjects', [])
                                            
                                            # 筛选 Canvas 的子对象
                                            canvas_children = []
                                            for obj in objects:
                                                path = obj.get('path', '')
                                                # 只取 Canvas 的直接子对象
                                                if path.startswith('Canvas/') and path.count('/') == 1:
                                                    canvas_children.append(obj)
                                            
                                            if canvas_children:
                                                for i, child in enumerate(canvas_children, 1):
                                                    name = child.get('name', 'Unknown')
                                                    path = child.get('path', '')
                                                    print(f"{i}. {name}")
                                                    print(f"   路径：{path}")
                                                    print()
                                            else:
                                                print("Canvas 下没有子对象")
                                        else:
                                            print(f"查找失败：{result.get('error', 'Unknown error')}")
                                    except Exception as e:
                                        print(f"解析失败：{e}")
                            break
            
            print("-" * 50)
            print("\n💡 提示:")
            print("如果 Canvas 下没有 Button 对象，需要手动创建一个作为模板")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(find_canvas_children())
