import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def get_components_and_modify_text():
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
                'clientInfo': {'name': 'get-components', 'version': '1.0.0'}
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
        
        print("🔄 步骤1: 获取LeaderboardButton的信息...")
        
        # 查找LeaderboardButton
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
        
        button_id = None
        async with session.post(url, headers=headers, json=find_call) as response:
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
        
        # 步骤2: 使用组件资源获取所有组件
        print(f"\n🔄 步骤2: 获取LeaderboardButton的组件信息...")
        
        # 尝试使用manage_components获取组件
        get_components_call = {
            'jsonrpc': '2.0',
            'id': 3,
            'method': 'tools/call',
            'params': {
                'name': 'manage_components',
                'arguments': {
                    'action': 'list',
                    'target': str(button_id),
                    'search_method': 'by_instance_id'
                }
            }
        }
        
        components = []
        async with session.post(url, headers=headers, json=get_components_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        result = data.get('result', {}).get('structuredContent', {})
                        if result.get('success'):
                            components = result.get('data', {}).get('components', [])
                            print(f"✅ 找到 {len(components)} 个组件")
                            for comp in components:
                                print(f"   - {comp.get('type')}")
                        else:
                            print(f"❌ 获取组件失败: {result.get('error', 'Unknown')}")
                        break
        
        await asyncio.sleep(0.3)
        
        # 步骤3: 尝试修改Text属性
        print(f"\n🔄 步骤3: 尝试修改Text属性...")
        
        # 方法1: 直接在按钮对象上尝试修改Text组件
        # 有可能Text组件是按钮的一部分
        modify_text_call = {
            'jsonrpc': '2.0',
            'id': 4,
            'method': 'tools/call',
            'params': {
                'name': 'manage_components',
                'arguments': {
                    'action': 'set_property',
                    'target': str(button_id),
                    'search_method': 'by_instance_id',
                    'component_type': 'Text',
                    'property': 'text',
                    'value': '排行榜'
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
                            print(f"✅ 成功修改按钮上的Text组件!")
                            success = True
                        else:
                            print(f"❌ 在按钮上修改Text失败: {result.get('error', 'Unknown')}")
                            success = False
                        break
        
        await asyncio.sleep(0.3)
        
        # 如果失败,尝试查找所有Text组件
        if not success:
            print(f"\n🔄 步骤4: 查找所有Text组件...")
            
            # 尝试不同的搜索术语
            search_terms = ['Text', 'UnityEngine.UI.Text', 'TextMeshPro', 'UI.Text']
            
            text_instance_id = None
            for term in search_terms:
                print(f"   搜索: '{term}'")
                
                find_text_call = {
                    'jsonrpc': '2.0',
                    'id': 5,
                    'method': 'tools/call',
                    'params': {
                        'name': 'find_gameobjects',
                        'arguments': {
                            'search_term': term,
                            'search_method': 'component'
                        }
                    }
                }
                
                async with session.post(url, headers=headers, json=find_text_call) as response:
                    if response.status == 200:
                        async for line in response.content:
                            line_text = line.decode('utf-8').strip()
                            if line_text.startswith('data:'):
                                data = json.loads(line_text[5:])
                                result = data.get('result', {}).get('structuredContent', {})
                                instance_ids = result.get('data', {}).get('instanceIDs', [])
                                if instance_ids:
                                    print(f"   ✅ 找到 {len(instance_ids)} 个Text对象: {instance_ids}")
                                    text_instance_id = instance_ids[0]
                                break
                
                if text_instance_id:
                    break
                
                await asyncio.sleep(0.2)
            
            if text_instance_id:
                print(f"\n🔄 步骤5: 修改Text组件文字...")
                
                set_text_call = {
                    'jsonrpc': '2.0',
                    'id': 6,
                    'method': 'tools/call',
                    'params': {
                        'name': 'manage_components',
                        'arguments': {
                            'action': 'set_property',
                            'target': str(text_instance_id),
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
                                    print(f"✅ 成功修改文字为'排行榜'!")
                                    success = True
                                else:
                                    print(f"❌ 修改失败: {result.get('error', 'Unknown')}")
                                break
            else:
                print("\n⚠️ 未找到任何Text组件")
        
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
        
        if success:
            print("\n✅ 所有操作完成!")
        else:
            print("\n⚠️ 部分操作需要手动完成")

if __name__ == "__main__":
    asyncio.run(get_components_and_modify_text())
