import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def find_and_modify_text():
    url = 'http://127.0.0.1:8080/mcp'
    headers = {
        'Accept': 'application/json,text/event-stream',
        'Content-Type': 'application/json'
    }
    
    async with aiohttp.ClientSession() as session:
        # 初始化
        init_msg = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'initialize',
            'params': {
                'protocolVersion': '2024-11-05',
                'capabilities': {},
                'clientInfo': {'name': 'find-modify-text', 'version': '1.0.0'}
            }
        }
        
        async with session.post(url, headers=headers, json=init_msg) as response:
            session_id = response.headers.get('mcp-session-id')
            if response.status == 200:
                async for line in response.content:
                    if line.decode('utf-8').strip().startswith('data:'):
                        break
        
        if not session_id:
            return
        
        headers['mcp-session-id'] = session_id
        
        await session.post(url, headers=headers, json={
            'jsonrpc': '2.0',
            'method': 'notifications/initialized',
            'params': {}
        })
        
        print("🔄 步骤1: 尝试通过LeaderboardButton查找Text组件...")
        
        # 先获取LeaderboardButton的instanceID
        find_button_call = {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'tools/call',
            'params': {
                'name': 'find_gameobjects',
                'arguments': {
                    'search_term': 'LeaderboardButton',
                    'search_method': 'by_name'
                }
            }
        }
        
        button_id = None
        async with session.post(url, headers=headers, json=find_button_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        result = data.get('result', {}).get('structuredContent', {})
                        instance_ids = result.get('data', {}).get('instanceIDs', [])
                        if instance_ids:
                            button_id = instance_ids[0]
                            print(f"✅ 找到LeaderboardButton, instanceID: {button_id}")
                        break
        
        if not button_id:
            print("❌ 未找到LeaderboardButton")
            return
        
        await asyncio.sleep(0.3)
        
        # 尝试使用组件类型查找
        print(f"\n🔄 步骤2: 搜索UnityEngine.UI.Text组件...")
        find_text_call = {
            'jsonrpc': '2.0',
            'id': 3,
            'method': 'tools/call',
            'params': {
                'name': 'find_gameobjects',
                'arguments': {
                    'search_term': 'UnityEngine.UI.Text',
                    'search_method': 'component'
                }
            }
        }
        
        text_ids = []
        async with session.post(url, headers=headers, json=find_text_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        result = data.get('result', {}).get('structuredContent', {})
                        instance_ids = result.get('data', {}).get('instanceIDs', [])
                        text_ids = instance_ids
                        print(f"✅ 找到 {len(instance_ids)} 个Text组件: {instance_ids}")
                        break
        
        if text_ids:
            await asyncio.sleep(0.3)
            
            # 尝试修改每个Text组件
            print(f"\n🔄 步骤3: 尝试修改Text组件...")
            success = False
            
            for text_id in text_ids:
                print(f"   尝试修改 instanceID: {text_id}")
                
                # 先获取Text对象的信息
                get_info_call = {
                    'jsonrpc': '2.0',
                    'id': 4,
                    'method': 'tools/call',
                    'params': {
                        'name': 'manage_gameobject',
                        'arguments': {
                            'action': 'get_info',
                            'target': str(text_id),
                            'search_method': 'by_instance_id'
                        }
                    }
                }
                
                async with session.post(url, headers=headers, json=get_info_call) as response:
                    if response.status == 200:
                        async for line in response.content:
                            line_text = line.decode('utf-8').strip()
                            if line_text.startswith('data:'):
                                data = json.loads(line_text[5:])
                                result = data.get('result', {}).get('structuredContent', {})
                                if result.get('success'):
                                    obj_data = result.get('data', {})
                                    obj_name = obj_data.get('name', '')
                                    parent_id = obj_data.get('parentInstanceID', 0)
                                    print(f"   - Name: {obj_name}, ParentID: {parent_id}")
                                    
                                    # 如果父对象是LeaderboardButton,就修改这个Text
                                    if parent_id == button_id or 'Leaderboard' in obj_name:
                                        print(f"   ✅ 这个Text属于LeaderboardButton!")
                await asyncio.sleep(0.2)
                
                # 尝试修改文字
                set_text_call = {
                    'jsonrpc': '2.0',
                    'id': 5,
                    'method': 'tools/call',
                    'params': {
                        'name': 'manage_components',
                        'arguments': {
                            'action': 'set_property',
                            'target': str(text_id),
                            'search_method': 'by_instance_id',
                            'component_type': 'Text',
                            'property': 'text',
                            'value': '排行榜'
                        }
                    }
                }
                
                async with session.post(url, headers=headers, json=set_text_call) as response:
                    if response.status == 200:
                        async for line in response.content:
                            line_text = line.decode('utf-8').strip()
                            if line_text.startswith('data:'):
                                data = json.loads(line_text[5:])
                                result = data.get('result', {}).get('structuredContent', {})
                                if result.get('success'):
                                    print(f"   ✅ 成功修改文字为'排行榜'!")
                                    success = True
                                else:
                                    print(f"   ❌ 失败: {result.get('error', 'Unknown')}")
                                break
                
                if success:
                    break
                
                await asyncio.sleep(0.3)
            
            if success:
                print("\n✅ 文字修改成功!")
            else:
                print("\n⚠️ 无法自动修改文字")
        else:
            print("❌ 未找到任何Text组件")
        
        # 保存场景
        print("\n🔄 保存场景...")
        save_scene_call = {
            'jsonrpc': '2.0',
            'id': 99,
            'method': 'tools/call',
            'params': {
                'name': 'manage_scene',
                'arguments': {
                    'action': 'save'
                }
            }
        }
        
        async with session.post(url, headers=headers, json=save_scene_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        print(f"✅ 场景保存成功")
                        break

if __name__ == "__main__":
    asyncio.run(find_and_modify_text())
