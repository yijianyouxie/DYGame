import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def fix_leaderboard_text_only():
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
                'clientInfo': {'name': 'fix-leaderboard-text', 'version': '1.0.0'}
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
        
        print("🔄 步骤1: 查找LeaderboardButton...")
        
        # 查找LeaderboardButton
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
        
        print(f"\n🔄 步骤2: 查找所有Text组件...")
        
        # 查找所有Text组件
        find_text_call = {
            'jsonrpc': '2.0',
            'id': 3,
            'method': 'tools/call',
            'params': {
                'name': 'find_gameobjects',
                'arguments': {
                    'search_term': 'Text',
                    'search_method': 'by_component'
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
        
        if not text_ids:
            print("❌ 未找到任何Text组件")
            return
        
        await asyncio.sleep(0.3)
        
        print(f"\n🔄 步骤3: 找到LeaderboardButton的Text子对象...")
        
        # 尝试修改按钮本身上的Text组件
        print(f"   尝试1: 修改LeaderboardButton本身的Text组件...")
        set_text_call = {
            'jsonrpc': '2.0',
            'id': 4,
            'method': 'tools/call',
            'params': {
                'name': 'manage_components',
                'arguments': {
                    'action': 'set_property',
                    'target': str(button_id),
                    'search_method': 'by_id',
                    'component_type': 'Text',
                    'property': 'text',
                    'value': '排行榜'
                }
            }
        }
        
        success = False
        async with session.post(url, headers=headers, json=set_text_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        result = data.get('result', {}).get('structuredContent', {})
                        if result.get('success'):
                            print(f"   ✅ 成功修改LeaderboardButton的Text组件!")
                            success = True
                        else:
                            print(f"   ❌ 失败: {result.get('error', 'Unknown')}")
                        break
        
        if not success:
            print(f"\n   尝试2: 查找LeaderboardButton的子对象...")
            
            # 尝试使用路径查找子对象
            child_paths = [
                'Canvas/LeaderboardButton/Text (Legacy)',
                'LeaderboardButton/Text (Legacy)',
                'LeaderboardButton/Text',
            ]
            
            for child_path in child_paths:
                print(f"   尝试路径: '{child_path}'")
                
                find_child_call = {
                    'jsonrpc': '2.0',
                    'id': 5,
                    'method': 'tools/call',
                    'params': {
                        'name': 'find_gameobjects',
                        'arguments': {
                            'search_term': child_path,
                            'search_method': 'by_path'
                        }
                    }
                }
                
                async with session.post(url, headers=headers, json=find_child_call) as response:
                    if response.status == 200:
                        async for line in response.content:
                            line_text = line.decode('utf-8').strip()
                            if line_text.startswith('data:'):
                                data = json.loads(line_text[5:])
                                result = data.get('result', {}).get('structuredContent', {})
                                instance_ids = result.get('data', {}).get('instanceIDs', [])
                                if instance_ids:
                                    child_id = instance_ids[0]
                                    print(f"   ✅ 找到子对象, instanceID: {child_id}")
                                    
                                    # 修改这个子对象的Text
                                    set_child_text_call = {
                                        'jsonrpc': '2.0',
                                        'id': 6,
                                        'method': 'tools/call',
                                        'params': {
                                            'name': 'manage_components',
                                            'arguments': {
                                                'action': 'set_property',
                                                'target': str(child_id),
                                                'search_method': 'by_id',
                                                'component_type': 'Text',
                                                'property': 'text',
                                                'value': '排行榜'
                                            }
                                        }
                                    }
                                    
                                    async with session.post(url, headers=headers, json=set_child_text_call) as response:
                                        if response.status == 200:
                                            async for line in response.content:
                                                line_text = line.decode('utf-8').strip()
                                                if line_text.startswith('data:'):
                                                    data = json.loads(line_text[5:])
                                                    result = data.get('result', {}).get('structuredContent', {})
                                                    if result.get('success'):
                                                        print(f"   ✅ 成功修改子对象的Text组件!")
                                                        success = True
                                                    else:
                                                        print(f"   ❌ 修改失败: {result.get('error', 'Unknown')}")
                                                    break
                
                if success:
                    break
                
                await asyncio.sleep(0.2)
        
        if success:
            print("\n✅ 成功修改LeaderboardButton的Text文字为'排行榜'!")
        else:
            print("\n❌ 无法修改LeaderboardButton的Text")
        
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
    asyncio.run(fix_leaderboard_text_only())
