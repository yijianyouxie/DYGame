import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def check_and_fix_text():
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
                'clientInfo': {'name': 'check-fix-text', 'version': '1.0.0'}
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
        
        print(f"\n🔄 步骤3: 检查每个Text组件的父对象...")
        
        # 检查每个Text组件,看哪个的父对象是LeaderboardButton
        for text_id in text_ids:
            print(f"\n   检查 Text ID: {text_id}")
            
            # 使用modify获取Text对象信息
            modify_text_call = {
                'jsonrpc': '2.0',
                'id': 4,
                'method': 'tools/call',
                'params': {
                    'name': 'manage_gameobject',
                    'arguments': {
                        'action': 'modify',
                        'target': str(text_id),
                        'search_method': 'by_id',
                        'name': 'Text'
                    }
                }
            }
            
            async with session.post(url, headers=headers, json=modify_text_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            result = data.get('result', {}).get('structuredContent', {})
                            if result.get('success'):
                                obj_data = result.get('data', {})
                                parent_id = obj_data.get('parentInstanceID', 0)
                                obj_name = obj_data.get('name', '')
                                print(f"   - 名称: {obj_name}")
                                print(f"   - 父对象ID: {parent_id}")
                                print(f"   - LeaderboardButton ID: {button_id}")
                                
                                if parent_id == button_id:
                                    print(f"   ✅ 这个Text属于LeaderboardButton!")
                                    
                                    # 修改这个Text的文字
                                    print(f"   正在修改文字为'排行榜'...")
                                    set_text_call = {
                                        'jsonrpc': '2.0',
                                        'id': 5,
                                        'method': 'tools/call',
                                        'params': {
                                            'name': 'manage_components',
                                            'arguments': {
                                                'action': 'set_property',
                                                'target': str(text_id),
                                                'search_method': 'by_id',
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
                                                        
                                                        # 保存场景
                                                        await save_scene(session, headers)
                                                        return
                                                    else:
                                                        print(f"   ❌ 修改失败: {result.get('error', 'Unknown')}")
                                                    break
                                break
            
            await asyncio.sleep(0.2)
        
        print("\n❌ 未找到LeaderboardButton的Text子对象")

async def save_scene(session, headers):
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
    asyncio.run(check_and_fix_text())
