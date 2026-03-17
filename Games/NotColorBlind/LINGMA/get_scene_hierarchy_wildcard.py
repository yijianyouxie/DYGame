import asyncio
import aiohttp
import json

async def get_scene_hierarchy():
    """获取当前场景层级（使用通配符搜索）"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🎬 获取当前场景层级 ===\n")
        
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
                        "name": "scene-hierarchy-getter",
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
            
            # ========== 搜索所有对象（使用空字符串但指定参数） ==========
            print("\n🔍 搜索场景中的所有对象...")
            
            search_call = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "find_gameobjects",
                    "arguments": {
                        "search_term": "*",
                        "search_method": "by_name",
                        "include_inactive": True
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=search_call) as response:
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
                                    
                                    result = json.loads(text_content)
                                    
                                    if result.get('success'):
                                        objects = result.get('data', {}).get('gameObjects', [])
                                        
                                        print(f"\n📊 场景对象层级结构:")
                                        print("=" * 80)
                                        
                                        # 按路径排序
                                        sorted_objects = sorted(objects, key=lambda x: x.get('path', ''))
                                        
                                        # 显示树形结构
                                        displayed_paths = set()
                                        
                                        for obj in sorted_objects:
                                            name = obj.get('name', 'Unknown')
                                            path = obj.get('path', '')
                                            
                                            # 计算层级
                                            level = path.count('/')
                                            indent = "  " * level
                                            
                                            # 显示对象
                                            print(f"{indent}📦 {name}")
                                            print(f"{indent}   路径：{path}")
                                            
                                            displayed_paths.add(path)
                                        
                                        print("=" * 80)
                                        print(f"\n📈 总计：{len(objects)} 个对象")
                                        
                                        # 特别显示 Canvas 下的对象
                                        canvas_children = [o for o in objects if o.get('path', '').startswith('Canvas/') and o.get('path', '').count('/') == 1]
                                        
                                        if canvas_children:
                                            print(f"\n🎨 Canvas 的子对象 ({len(canvas_children)} 个):")
                                            for child in canvas_children:
                                                print(f"   • {child.get('name', 'Unknown')} - {child.get('path', '')}")
                                    else:
                                        print(f"❌ 搜索失败：{result.get('message', result.get('error', 'Unknown error'))}")
                            break
            
            print("\n=== ✅ 场景信息获取完成 ===\n")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(get_scene_hierarchy())
