import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def find_leaderboard_child_text():
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
                'clientInfo': {'name': 'find-child-text', 'version': '1.0.0'}
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
        
        print(f"\n🔄 步骤3: 检查每个Text组件是否属于LeaderboardButton...")
        
        # 尝试使用manage_gameobject的modify action来获取子对象信息
        # 或者尝试其他方法来确定父对象关系
        
        # 先尝试修改每个Text组件,看哪个成功了
        # 因为之前已经修改过第一个了,我们需要找到正确的那个
        
        # 让我们尝试一个不同的方法:使用modify action来获取对象信息
        print(f"\n🔄 步骤4: 尝试不同的方法...")
        
        # 方法1: 尝试使用modify操作获取对象信息
        modify_call = {
            'jsonrpc': '2.0',
            'id': 4,
            'method': 'tools/call',
            'params': {
                'name': 'manage_gameobject',
                'arguments': {
                    'action': 'modify',
                    'target': str(button_id),
                    'search_method': 'by_id',
                    'name': 'LeaderboardButton'
                }
            }
        }
        
        async with session.post(url, headers=headers, json=modify_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        result = data.get('result', {}).get('structuredContent', {})
                        if result.get('success'):
                            obj_data = result.get('data', {})
                            print(f"✅ 获取到按钮信息:")
                            print(json.dumps(obj_data, ensure_ascii=False, indent=2))
                        else:
                            print(f"❌ 修改失败: {result.get('error', 'Unknown')}")
                        break
        
        await asyncio.sleep(0.3)
        
        # 方法2: 尝试复制按钮,看能否获取子对象信息
        print(f"\n🔄 步骤5: 尝试复制按钮以获取完整信息...")
        
        duplicate_call = {
            'jsonrpc': '2.0',
            'id': 5,
            'method': 'tools/call',
            'params': {
                'name': 'manage_gameobject',
                'arguments': {
                    'action': 'duplicate',
                    'target': 'Canvas/LeaderboardButton',
                    'search_method': 'by_path',
                    'new_name': 'TempButton'
                }
            }
        }
        
        async with session.post(url, headers=headers, json=duplicate_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        result = data.get('result', {}).get('structuredContent', {})
                        if result.get('success'):
                            obj_data = result.get('data', {}).get('duplicatedObject', {})
                            print(f"✅ 复制成功,获取到完整信息:")
                            print(json.dumps(obj_data, ensure_ascii=False, indent=2))
                            
                            # 删除临时按钮
                            await asyncio.sleep(0.5)
                            delete_call = {
                                'jsonrpc': '2.0',
                                'id': 6,
                                'method': 'tools/call',
                                'params': {
                                    'name': 'manage_gameobject',
                                    'arguments': {
                                        'action': 'delete',
                                        'target': 'TempButton',
                                        'search_method': 'by_name'
                                    }
                                }
                            }
                            
                            async with session.post(url, headers=headers, json=delete_call) as response:
                                if response.status == 200:
                                    async for line in response.content:
                                        line_text = line.decode('utf-8').strip()
                                        if line_text.startswith('data:'):
                                            break
                        else:
                            print(f"❌ 复制失败: {result.get('error', 'Unknown')}")
                        break
        
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
    asyncio.run(find_leaderboard_child_text())
