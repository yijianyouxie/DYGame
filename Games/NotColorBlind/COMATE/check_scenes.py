#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查可用场景"""
import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

MCP_URL = 'http://127.0.0.1:8080/mcp'

async def main():
    headers = {
        'Accept': 'application/json,text/event-stream',
        'Content-Type': 'application/json'
    }
    
    async with aiohttp.ClientSession() as session:
        # 初始化
        init_msg = {'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
            'params': {'protocolVersion': '2024-11-05', 'capabilities': {}, 'clientInfo': {'name': 'check', 'version': '1.0'}}}
        async with session.post(MCP_URL, headers=headers, json=init_msg) as r:
            sid = r.headers.get('mcp-session-id')
            async for line in r.content:
                if line.decode().strip().startswith('data:'): break
        
        headers['mcp-session-id'] = sid
        await session.post(MCP_URL, headers=headers, json={'jsonrpc': '2.0', 'method': 'notifications/initialized', 'params': {}})
        
        # 获取Build Settings中的场景
        print("="*50)
        print("Build Settings中的场景:")
        print("="*50)
        call_msg = {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/call', 
            'params': {'name': 'manage_scene', 'arguments': {'action': 'get_build_settings'}}}
        async with session.post(MCP_URL, headers=headers, json=call_msg) as r:
            async for line in r.content:
                line_text = line.decode().strip()
                if line_text.startswith('data:'):
                    data = json.loads(line_text[5:])
                    result = data.get('result', {}).get('structuredContent', {})
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                    break
        
        await asyncio.sleep(0.3)
        
        # 获取当前活动场景
        print("\n" + "="*50)
        print("当前活动场景:")
        print("="*50)
        call_msg = {'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call', 
            'params': {'name': 'manage_scene', 'arguments': {'action': 'get_active'}}}
        async with session.post(MCP_URL, headers=headers, json=call_msg) as r:
            async for line in r.content:
                line_text = line.decode().strip()
                if line_text.startswith('data:'):
                    data = json.loads(line_text[5:])
                    result = data.get('result', {}).get('structuredContent', {})
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                    break

asyncio.run(main())
