import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def correct_text_modify():
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
                'clientInfo': {'name': 'correct-text-modify', 'version': '1.0.0'}
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
        
        print("🔄 步骤1: 查找所有Text组件 (使用正确的search_method)...")
        
        # 使用正确的search_method: by_component
        find_text_call = {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'tools/call',
            'params': {
                'name': 'find_gameobjects',
                'arguments': {
                    'search_term': 'Text',
                    'search_method': 'by_component'
                }
            }
        }
        
        text_instance_ids = []
        async with session.post(url, headers=headers, json=find_text_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        result = data.get('result', {}).get('structuredContent', {})
                        instance_ids = result.get('data', {}).get('instanceIDs', [])
                        text_instance_ids = instance_ids
                        print(f"✅ 找到 {len(instance_ids)} 个Text组件: {instance_ids}")
                        break
        
        if not text_instance_ids:
            print("❌ 未找到任何Text组件")
            return
        
        await asyncio.sleep(0.3)
        
        print(f"\n🔄 步骤2: 尝试修改每个Text组件的文字...")
        
        success = False
        for instance_id in text_instance_ids:
            print(f"\n   尝试修改 instanceID: {instance_id}")
            
            # 使用正确的search_method: by_id
            set_text_call = {
                'jsonrpc': '2.0',
                'id': 3,
                'method': 'tools/call',
                'params': {
                    'name': 'manage_components',
                    'arguments': {
                        'action': 'set_property',
                        'target': str(instance_id),
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
                                success = True
                            else:
                                print(f"   ❌ 失败: {result.get('error', 'Unknown')}")
                                # 打印完整错误信息
                                print(f"   详细信息: {json.dumps(result, ensure_ascii=False, indent=4)}")
                            break
            
            if success:
                break
            
            await asyncio.sleep(0.3)
        
        if success:
            print("\n✅ 文字修改成功!")
        else:
            print("\n⚠️ 无法修改文字")
        
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
    asyncio.run(correct_text_modify())
