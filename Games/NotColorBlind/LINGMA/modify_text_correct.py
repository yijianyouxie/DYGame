import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def modify_text_correct():
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
                'clientInfo': {'name': 'modify-text-correct', 'version': '1.0.0'}
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
        
        print("🔄 步骤1: 查找所有包含'Text'的对象...")
        
        # 搜索所有Text组件
        find_call = {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'tools/call',
            'params': {
                'name': 'find_gameobjects',
                'arguments': {
                    'search_term': 'Text',
                    'search_method': 'component'
                }
            }
        }
        
        text_instance_ids = []
        async with session.post(url, headers=headers, json=find_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        result = data.get('result', {}).get('structuredContent', {})
                        instance_ids = result.get('data', {}).get('instanceIDs', [])
                        text_instance_ids = instance_ids
                        print(f"✅ 找到 {len(instance_ids)} 个Text对象: {instance_ids}")
                        break
        
        if not text_instance_ids:
            print("❌ 未找到任何Text对象")
            return
        
        await asyncio.sleep(0.3)
        
        # 步骤2: 尝试通过instanceID修改每个Text对象
        print(f"\n🔄 步骤2: 尝试修改Text对象的文字...")
        
        success = False
        for instance_id in text_instance_ids:
            print(f"   尝试修改 instanceID: {instance_id}")
            
            set_text_call = {
                'jsonrpc': '2.0',
                'id': 3,
                'method': 'tools/call',
                'params': {
                    'name': 'manage_components',
                    'arguments': {
                        'action': 'set_property',
                        'target': str(instance_id),
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
                                print(f"   ✅ 成功修改 instanceID {instance_id} 的文字为'排行榜'!")
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
            print("💡 可能在Unity中找到以下Text对象,请手动修改:")
            
            # 尝试获取每个Text对象的信息
            for instance_id in text_instance_ids[:3]:  # 只显示前3个
                get_info_call = {
                    'jsonrpc': '2.0',
                    'id': 4,
                    'method': 'tools/call',
                    'params': {
                        'name': 'manage_gameobject',
                        'arguments': {
                            'action': 'get_info',
                            'target': str(instance_id),
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
                                    print(f"   - InstanceID: {instance_id}, Name: {obj_data.get('name')}")
                                break
                await asyncio.sleep(0.2)
        
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
    asyncio.run(modify_text_correct())
