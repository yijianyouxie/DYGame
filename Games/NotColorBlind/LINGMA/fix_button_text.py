import asyncio
import aiohttp
import json

async def fix_button_text():
    """修复 LeaderboardButton 的 Text 内容"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🎯 修复 LeaderboardButton 的 Text 内容 ===\n")
        
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
                        "name": "text-fixer",
                        "version": "1.0.0"
                    }
                }
            }
            
            session_id = None
            async with session.post(url, headers=base_headers, json=init_message) as response:
                session_id = response.headers.get('mcp-session-id')
                
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
            
            # ========== 查找 LeaderboardButton 下的 Text 子对象 ==========
            print("\n🔍 查找 LeaderboardButton 下的 Text 子对象...")
            
            find_text_call = {
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
            
            text_paths = []
            async with session.post(url, headers=headers_with_session, json=find_text_call) as response:
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
                                            
                                            # 查找 LeaderboardButton 下的 Text
                                            for obj in objects:
                                                path = obj.get('path', '')
                                                if path.startswith('Canvas/LeaderboardButton/') and 'Text' in path:
                                                    text_paths.append(path)
                                                    print(f"   ✅ 找到 Text: {path}")
                                            
                                            if not text_paths:
                                                print(f"   ⚠️ 未找到 Text 子对象")
                                        else:
                                            print(f"   ❌ 查找失败")
                                    except Exception as e:
                                        print(f"   ⚠️ 解析失败：{e}")
                            break
            
            await asyncio.sleep(0.3)
            
            # ========== 修改 Text 内容 ==========
            if text_paths:
                print("\n📝 修改 Text 内容为'排行榜'...")
                
                for text_path in text_paths:
                    set_text_call = {
                        "jsonrpc": "2.0",
                        "id": 3,
                        "method": "tools/call",
                        "params": {
                            "name": "manage_components",
                            "arguments": {
                                "action": "set_property",
                                "target": text_path,
                                "search_method": "by_path",
                                "component_type": "Text",
                                "property": "text",
                                "value": "排行榜"
                            }
                        }
                    }
                    
                    async with session.post(url, headers=headers_with_session, json=set_text_call) as response:
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
                                                    print(f"   ✅ {text_path}: Text 修改成功")
                                                else:
                                                    print(f"   ⚠️ {text_path}: 设置失败 - {result.get('error', 'Unknown error')}")
                                            except:
                                                pass
                                    break
                    
                    await asyncio.sleep(0.3)
                
                print("\n=== ✅ Text 内容修复完成 ===\n")
            else:
                print("\n❌ 没有找到需要修改的 Text 对象")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_button_text())
