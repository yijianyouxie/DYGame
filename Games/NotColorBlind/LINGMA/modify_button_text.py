import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def modify_button_text():
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
                'clientInfo': {'name': 'modify-text', 'version': '1.0.0'}
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
        find_call = {
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
        
        button_instance_id = None
        async with session.post(url, headers=headers, json=find_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        result = data.get('result', {}).get('structuredContent', {})
                        instance_ids = result.get('data', {}).get('instanceIDs', [])
                        if instance_ids:
                            button_instance_id = instance_ids[0]
                            print(f"✅ 找到LeaderboardButton, instanceID: {button_instance_id}")
                        else:
                            print("❌ 未找到LeaderboardButton")
                            return
                        break
        
        if not button_instance_id:
            return
        
        await asyncio.sleep(0.3)
        
        # 步骤2: 通过instanceID获取按钮的详细信息
        print(f"\n🔄 步骤2: 获取LeaderboardButton的详细信息...")
        get_info_call = {
            'jsonrpc': '2.0',
            'id': 3,
            'method': 'tools/call',
            'params': {
                'name': 'manage_gameobject',
                'arguments': {
                    'action': 'get_info',
                    'target': str(button_instance_id),
                    'search_method': 'by_instance_id'
                }
            }
        }
        
        button_info = None
        async with session.post(url, headers=headers, json=get_info_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        result = data.get('result', {}).get('structuredContent', {})
                        if result.get('success'):
                            button_info = result.get('data')
                            print(f"✅ 获取到按钮信息")
                            print(f"   组件: {button_info.get('componentNames', [])}")
                        break
        
        await asyncio.sleep(0.3)
        
        # 步骤3: 尝试使用manage_components直接获取按钮的Text组件
        print(f"\n🔄 步骤3: 尝试获取Text组件...")
        
        # 尝试不同的搜索方法
        search_methods = [
            ('by_instance_id', str(button_instance_id)),
            ('by_name', 'LeaderboardButton'),
        ]
        
        text_found = False
        for search_method, target in search_methods:
            print(f"   尝试: {search_method} - {target}")
            
            # 首先尝试获取所有组件信息
            get_components_call = {
                'jsonrpc': '2.0',
                'id': 4,
                'method': 'tools/call',
                'params': {
                    'name': 'manage_components',
                    'arguments': {
                        'action': 'get_components',
                        'target': target,
                        'search_method': search_method
                    }
                }
            }
            
            async with session.post(url, headers=headers, json=get_components_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            result = data.get('result', {}).get('structuredContent', {})
                            if result.get('success'):
                                components = result.get('data', {}).get('components', [])
                                print(f"   找到组件: {[c.get('type') for c in components]}")
                                
                                # 检查是否有Text组件
                                for comp in components:
                                    comp_type = comp.get('type', '')
                                    if 'Text' in comp_type:
                                        print(f"   ✅ 找到Text组件: {comp_type}")
                                        text_found = True
                                        break
                            break
            
            if text_found:
                break
            
            await asyncio.sleep(0.3)
        
        # 步骤4: 如果找到Text组件,尝试修改
        if text_found:
            print(f"\n🔄 步骤4: 修改Text组件属性...")
            
            for search_method, target in search_methods:
                set_text_call = {
                    'jsonrpc': '2.0',
                    'id': 5,
                    'method': 'tools/call',
                    'params': {
                        'name': 'manage_components',
                        'arguments': {
                            'action': 'set_property',
                            'target': target,
                            'search_method': search_method,
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
                                    print(f"✅ 成功修改文字为'排行榜'!")
                                    
                                    # 保存场景
                                    await save_scene(session, headers)
                                    return
                                else:
                                    print(f"❌ 失败: {result.get('error', 'Unknown')}")
                                break
                
                await asyncio.sleep(0.3)
        else:
            print("\n⚠️ 未找到Text组件")
            print("💡 LeaderboardButton可能需要包含Text子对象")
        
        # 保存场景
        await save_scene(session, headers)

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
    asyncio.run(modify_button_text())
