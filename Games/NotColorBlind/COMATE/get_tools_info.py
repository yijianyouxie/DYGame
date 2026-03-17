#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查看MCP工具的详细参数"""
import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def main():
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
                'clientInfo': {'name': 'test', 'version': '1.0'}
            }
        }
        async with session.post(url, headers=headers, json=init_msg) as r:
            sid = r.headers.get('mcp-session-id')
            async for line in r.content:
                if line.decode().strip().startswith('data:'):
                    break
        
        headers['mcp-session-id'] = sid
        await session.post(url, headers=headers, json={
            'jsonrpc': '2.0',
            'method': 'notifications/initialized',
            'params': {}
        })
        
        # 获取工具列表
        tools_msg = {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list', 'params': {}}
        async with session.post(url, headers=headers, json=tools_msg) as r:
            async for line in r.content:
                line_text = line.decode().strip()
                if line_text.startswith('data:'):
                    data = json.loads(line_text[5:])
                    tools = data.get('result', {}).get('tools', [])
                    
                    # 只显示关键工具
                    key_tools = ['manage_scene', 'manage_gameobject', 'manage_components', 'find_gameobjects']
                    for t in tools:
                        if t['name'] in key_tools:
                            print(f"\n{'='*60}")
                            print(f"工具: {t['name']}")
                            print(f"描述: {t.get('description', 'N/A')}")
                            schema = t.get('inputSchema', {})
                            props = schema.get('properties', {})
                            if props:
                                print("\n参数:")
                                for prop_name, prop_info in props.items():
                                    print(f"  - {prop_name}: {prop_info.get('description', 'N/A')}")
                                    if 'enum' in prop_info:
                                        print(f"    可选值: {prop_info['enum']}")
                    break

asyncio.run(main())
