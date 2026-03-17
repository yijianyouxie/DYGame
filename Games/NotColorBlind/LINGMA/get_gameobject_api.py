#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查询manage_gameobject工具的API"""
import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def main():
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream'
    }
    
    async with aiohttp.ClientSession() as session:
        # 初始化
        async with session.post(url, headers=base_headers, json={
            'jsonrpc': '2.0',
            'id': 0,
            'method': 'initialize',
            'params': {
                'protocolVersion': '2024-11-05',
                'capabilities': {},
                'clientInfo': {'name': 'python-script', 'version': '1.0'}
            }
        }) as response:
            session_id = response.headers.get('mcp-session-id')
            await response.text()
        
        headers = {**base_headers, 'mcp-session-id': session_id}
        await asyncio.sleep(0.5)
        
        # 查询工具列表
        request = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'tools/list'
        }
        
        async with session.post(url, headers=headers, json=request) as response:
            full_response = await response.text()
            tools = None
            for line in full_response.split('\n'):
                line = line.strip()
                if line.startswith('data:'):
                    data = json.loads(line[5:])
                    tools = data.get('result', {})
                    break
            
            if tools:
                # 打印 manage_gameobject 工具
                for tool in tools.get('tools', []):
                    if tool['name'] == 'manage_gameobject':
                        print("\n" + "=" * 80)
                        print("manage_gameobject 工具:")
                        print("=" * 80)
                        print(json.dumps(tool, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
