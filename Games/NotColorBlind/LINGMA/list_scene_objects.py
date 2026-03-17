import asyncio
import aiohttp
import json

async def list_scene_objects():
    """列出场景中的所有 GameObject"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 📋 列出场景中的所有 GameObject ===\n")
        
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
                        "name": "scene-lister",
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
            
            # ========== 获取所有 GameObject ==========
            print("🔍 正在获取场景中的所有 GameObject...\n")
            
            find_all_call = {
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
            
            async with session.post(url, headers=headers_with_session, json=find_all_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            if 'result' in data and 'content' in data['result']:
                                content_text = data['result']['content'][0]['text']
                                
                                # 尝试多种解析方式
                                try:
                                    # 方式 1: 直接解析 JSON
                                    result = json.loads(content_text)
                                    if result.get('success'):
                                        all_objects = result.get('data', {}).get('gameObjects', [])
                                        print(f"✅ 场景中共有 {len(all_objects)} 个对象\n")
                                        
                                        # 分组显示：根对象和子对象
                                        root_objects = [obj for obj in all_objects if '/' not in obj.get('path', '')]
                                        child_objects = [obj for obj in all_objects if '/' in obj.get('path', '')]
                                        
                                        print(f"📁 根对象 ({len(root_objects)} 个):")
                                        for i, obj in enumerate(root_objects, 1):
                                            name = obj.get('name', 'N/A')
                                            path = obj.get('path', 'N/A')
                                            print(f"   {i}. {name}")
                                        
                                        print(f"\n📂 子对象 ({len(child_objects)} 个):")
                                        # 按父对象分组
                                        parent_dict = {}
                                        for obj in child_objects:
                                            path = obj.get('path', '')
                                            parts = path.split('/')
                                            if len(parts) > 1:
                                                parent = parts[0]
                                                if parent not in parent_dict:
                                                    parent_dict[parent] = []
                                                parent_dict[parent].append(obj)
                                        
                                        for parent, children in sorted(parent_dict.items()):
                                            print(f"\n   {parent}/ ({len(children)} 个子对象):")
                                            for child in children[:15]:  # 每个父对象最多显示 15 个子对象
                                                name = child.get('name', 'N/A')
                                                full_path = child.get('path', 'N/A')
                                                indent = "      "
                                                print(f"{indent}- {name}")
                                            
                                            if len(children) > 15:
                                                print(f"{indent}... 还有 {len(children) - 15} 个")
                                        
                                        # 查找可能的相关对象
                                        print("\n\n🔎 搜索可能相关的对象:")
                                        keywords = ["Rank", "Item", "Leaderboard", "Prefab"]
                                        for keyword in keywords:
                                            matches = [obj for obj in all_objects if keyword.lower() in obj.get('name', '').lower()]
                                            if matches:
                                                print(f"\n   包含 '{keyword}' 的对象 ({len(matches)} 个):")
                                                for match in matches:
                                                    print(f"      • {match.get('name')} - 路径：{match.get('path')}")
                                        
                                        break
                                    else:
                                        print(f"❌ 获取失败：{result.get('error', 'Unknown error')}")
                                except Exception as e:
                                    print(f"⚠️ 解析失败：{e}")
                                    print(f"原始响应 (前 500 字符): {content_text[:500]}")
                            break
            
            print("\n\n💡 请在上面的列表中找到 RankItemPrefab 的准确路径")
            print("然后告诉我，我会使用该路径进行修复")
            
        except Exception as e:
            print(f"\n✗ 发生错误：{e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(list_scene_objects())
