import asyncio
import aiohttp
import json

async def get_gameobject_details():
    """获取 GameObject 详细信息"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 🎮 获取 GameObject 详细信息 ===\n")
        
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
                        "name": "gameobject-details",
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
            
            # ========== 获取对象列表 ==========
            print("\n📋 步骤 1: 获取 Canvas 对象...")
            
            find_canvas_call = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "find_gameobjects",
                    "arguments": {
                        "search_term": "Canvas",
                        "search_method": "by_path"
                    }
                }
            }
            
            instance_ids = []
            async with session.post(url, headers=headers_with_session, json=find_canvas_call) as response:
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
                                        data_obj = result.get('data', {})
                                        ids = data_obj.get('instanceIDs', [])
                                        if ids:
                                            instance_ids = ids
                                            print(f"   ✅ 找到对象 IDs: {ids}")
                                    else:
                                        print(f"   ❌ 失败：{result.get('message', 'Unknown error')}")
                            break
            
            await asyncio.sleep(0.3)
            
            # ========== 获取对象详细信息 ==========
            if instance_ids:
                print("\n📋 步骤 2: 获取对象详细信息...")
                
                for instance_id in instance_ids:
                    print(f"\n   🔍 获取 Instance ID: {instance_id} 的详细信息...")
                    
                    # 使用 manage_gameobject 的 modify 动作来获取信息
                    get_info_call = {
                        "jsonrpc": "2.0",
                        "id": 3,
                        "method": "tools/call",
                        "params": {
                            "name": "manage_gameobject",
                            "arguments": {
                                "action": "modify",
                                "instance_id": instance_id,
                                "search_method": "by_instance_id"
                            }
                        }
                    }
                    
                    async with session.post(url, headers=headers_with_session, json=get_info_call) as response:
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
                                            
                                            print(f"      📄 响应：{text_content[:300]}")
                                    break
                    
                    await asyncio.sleep(0.3)
            
            # ========== 尝试获取场景层级 ==========
            print("\n📋 步骤 3: 尝试获取场景所有对象...")
            
            get_all_call = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "find_gameobjects",
                    "arguments": {
                        "search_term": "",
                        "search_method": "by_name"
                    }
                }
            }
            
            async with session.post(url, headers=headers_with_session, json=get_all_call) as response:
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
                                        data_obj = result.get('data', {})
                                        ids = data_obj.get('instanceIDs', [])
                                        print(f"   ✅ 找到 {len(ids)} 个对象")
                                        print(f"   📊 Instance IDs: {ids}")
                                    else:
                                        print(f"   ❌ 失败：{result.get('message', 'Unknown error')}")
                            break
            
            print("\n=== ✅ 调试完成 ===\n")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(get_gameobject_details())
