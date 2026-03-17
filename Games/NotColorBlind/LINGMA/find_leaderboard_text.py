import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def find_text():
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
                'clientInfo': {'name': 'find-text', 'version': '1.0.0'}
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
        
        # 尝试查找所有包含"Text"的对象
        search_terms = ['Text', 'Legacy']
        
        for term in search_terms:
            print(f"\n🔍 搜索包含 '{term}' 的对象...")
            find_call = {
                'jsonrpc': '2.0',
                'id': 2,
                'method': 'tools/call',
                'params': {
                    'name': 'find_gameobjects',
                    'arguments': {
                        'search_term': term,
                        'search_method': 'by_name'
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
                            print(f"找到 {len(instance_ids)} 个对象: {instance_ids}")
                            break

if __name__ == "__main__":
    asyncio.run(find_text())
