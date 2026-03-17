import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def fix_text():
    url = 'http://127.0.0.1:8080/mcp'
    headers = {
        'Accept': 'application/json,text/event-stream',
        'Content-Type': 'application/json'
    }
    
    async with aiohttp.ClientSession() as session:
        init_msg = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'initialize',
            'params': {
                'protocolVersion': '2024-11-05',
                'capabilities': {},
                'clientInfo': {'name': 'fix-text', 'version': '1.0.0'}
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
        
        # 尝试使用组件查找
        print("🔍 查找Text组件...")
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
        
        async with session.post(url, headers=headers, json=find_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        result = data.get('result', {}).get('structuredContent', {})
                        instance_ids = result.get('data', {}).get('instanceIDs', [])
                        print(f"找到 {len(instance_ids)} 个Text组件: {instance_ids}")
                        
                        if instance_ids:
                            # 尝试使用instanceID设置文字
                            for instance_id in instance_ids:
                                print(f"\n尝试修改 instanceID: {instance_id}")
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
                                                    print(f"✅ 成功修改 instanceID {instance_id} 的文字为'排行榜'!")
                                                else:
                                                    print(f"❌ 失败: {result.get('error', 'Unknown')}")
                                                break
                                await asyncio.sleep(0.3)
                        break
        
        # 保存场景
        print("\n🔄 保存场景...")
        save_scene_call = {
            'jsonrpc': '2.0',
            'id': 4,
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
                        data = json.loads(line_text[5:])
                        result = data.get('result', {}).get('structuredContent', {})
                        if result.get('success'):
                            print(f"✅ 场景保存成功")
                        break

if __name__ == "__main__":
    asyncio.run(fix_text())
