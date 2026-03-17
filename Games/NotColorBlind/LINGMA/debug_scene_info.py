import asyncio
import aiohttp
import json

async def get_scene_info():
    """获取当前场景信息（调试版本）"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🎬 获取当前场景信息（调试版本）===\n")
        
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
                        "name": "scene-info-getter",
                        "version": "1.0.0"
                    }
                }
            }
            
            session_id = None
            async with session.post(url, headers=base_headers, json=init_message) as response:
                session_id = response.headers.get('mcp-session-id')
                print(f"✅ Session ID: {session_id}")
                
                if not session_id:
                    print("❌ 未获取到 Session ID")
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
            
            print("\n🔍 尝试获取场景中的 GameObject...")
            
            # ========== 获取场景中的所有对象 ==========
            get_all_objects_call = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "find_gameobjects",
                    "arguments": {
                        "search_term": "",
                        "search_method": "by_name"
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=get_all_objects_call) as response:
                print(f"\n📊 HTTP 响应状态码：{response.status}")
                
                if response.status == 200:
                    full_content = []
                    async for line in response.content:
                        line_text = line.decode('utf-8')
                        full_content.append(line_text)
                        print(f"📄 收到数据：{line_text[:200]}")
                    
                    print(f"\n📄 完整响应行数：{len(full_content)}")
                    
                    # 尝试解析所有 data: 行
                    for line in full_content:
                        line_text = line.strip()
                        if line_text.startswith('data:'):
                            json_str = line_text[5:]  # 去掉 'data:' 前缀
                            print(f"\n🔍 尝试解析 JSON: {json_str[:100]}")
                            
                            try:
                                data = json.loads(json_str)
                                print(f"✅ JSON 解析成功")
                                
                                if 'result' in data:
                                    tools_result = data['result']
                                    print(f"📦 Tools Result: {json.dumps(tools_result, indent=2)[:500]}")
                                    
                                    content_list = tools_result.get('content', [])
                                    if content_list and len(content_list) > 0:
                                        content_item = content_list[0]
                                        text_content = content_item.get('text', '')
                                        print(f"\n📄 Text Content: {text_content[:500]}")
                                        
                                        try:
                                            result = json.loads(text_content)
                                            print(f"\n✅ 最终结果解析成功")
                                            
                                            if result.get('success'):
                                                objects = result.get('data', {}).get('gameObjects', [])
                                                print(f"\n📊 找到 {len(objects)} 个对象")
                                                
                                                # 显示前 20 个对象
                                                for i, obj in enumerate(objects[:20], 1):
                                                    name = obj.get('name', 'Unknown')
                                                    path = obj.get('path', '')
                                                    print(f"{i}. {name} - {path}")
                                                
                                                if len(objects) > 20:
                                                    print(f"... 还有 {len(objects) - 20} 个对象")
                                            else:
                                                print(f"❌ 操作失败：{result.get('error', 'Unknown error')}")
                                        except json.JSONDecodeError as e:
                                            print(f"❌ 最终结果 JSON 解析失败：{e}")
                                            print(f"原始文本：{text_content}")
                                else:
                                    print(f"❌ 没有找到 result 字段")
                                    print(f"完整数据：{json.dumps(data, indent=2)}")
                                    
                            except json.JSONDecodeError as e:
                                print(f"❌ JSON 解析失败：{e}")
                                print(f"原始字符串：{json_str}")
                            except Exception as e:
                                print(f"❌ 其他错误：{e}")
                                import traceback
                                traceback.print_exc()
                else:
                    print(f"❌ HTTP 错误：{response.status}")
                    error_text = await response.text()
                    print(f"错误内容：{error_text}")
            
            print("\n=== ✅ 调试完成 ===\n")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(get_scene_info())
