#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查询MCP工具的完整参数信息"""

import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def main():
    url = 'http://127.0.0.1:8080/mcp'
    base_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream'
    }
    
    async with aiohttp.ClientSession() as session:
        # 初始化
        init_message = {
            'jsonrpc': '2.0',
            'id': 0,
            'method': 'initialize',
            'params': {
                'protocolVersion': '2024-11-05',
                'capabilities': {},
                'clientInfo': {'name': 'python-script', 'version': '1.0'}
            }
        }
        
        async with session.post(url, headers=base_headers, json=init_message) as response:
            session_id = response.headers.get('mcp-session-id')
            print(f"Session ID: {session_id}")
        
        if not session_id:
            return
        
        headers = {**base_headers, 'mcp-session-id': session_id}
        
        # 发送initialized
        await session.post(url, headers=headers, json={
            'jsonrpc': '2.0',
            'method': 'notifications/initialized'
        })
        
        await asyncio.sleep(0.5)
        
        # 查询工具列表
        tools_request = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'tools/list',
            'params': {}
        }
        
        async with session.post(url, headers=headers, json=tools_request) as response:
            text = await response.text()
            
            tools = []
            for line in text.split('\n'):
                line = line.strip()
                if line.startswith('data:'):
                    data = json.loads(line[5:])
                    result = data.get('result', {})
                    if 'tools' in result:
                        tools = result['tools']
            
            print(f"\n找到 {len(tools)} 个工具\n")
            
            # 查找manage_scene和manage_gameobject的详细参数
            for tool in tools:
                name = tool.get('name', '')
                if name in ['manage_scene', 'manage_gameobject', 'manage_components']:
                    print(f"\n{'='*60}")
                    print(f"工具: {name}")
                    print('='*60)
                    print(json.dumps(tool, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    asyncio.run(main())
