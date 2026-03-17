#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查Start场景中LeaderboardPanel的配置
"""
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
        
        # 加载Start场景
        print("加载Start场景...")
        call_msg = {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/call',
            'params': {'name': 'manage_scene', 'arguments': {'action': 'load', 'build_index': 0}}}
        async with session.post(MCP_URL, headers=headers, json=call_msg) as r:
            async for line in r.content:
                line_text = line.decode().strip()
                if line_text.startswith('data:'):
                    data = json.loads(line_text[5:])
                    result = data.get('result', {}).get('structuredContent', {})
                    print(f"加载结果: {result.get('success', False)}")
                    break
        
        await asyncio.sleep(0.5)
        
        # 查找LeaderboardPanel
        print("\n查找LeaderboardPanel...")
        call_msg = {'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call',
            'params': {'name': 'find_gameobjects', 'arguments': {'search_term': 'LeaderboardPanel', 'search_method': 'by_name'}}}
        async with session.post(MCP_URL, headers=headers, json=call_msg) as r:
            async for line in r.content:
                line_text = line.decode().strip()
                if line_text.startswith('data:'):
                    data = json.loads(line_text[5:])
                    result = data.get('result', {}).get('structuredContent', {})
                    if result.get('success') and result.get('data', {}).get('instanceIDs'):
                        panel_id = result['data']['instanceIDs'][0]
                        print(f"LeaderboardPanel ID: {panel_id}")
                        
                        # 检查父对象
                        print("\n检查层级结构...")
                        call_msg2 = {'jsonrpc': '2.0', 'id': 4, 'method': 'resources/read',
                            'params': {'uri': f'mcpforunity://scene/gameobject/{panel_id}'}}
                        async with session.post(MCP_URL, headers=headers, json=call_msg2) as r2:
                            async for line in r.content:
                                line_text = line.decode().strip()
                                if line_text.startswith('data:'):
                                    data = json.loads(line_text[5:])
                                    contents = data.get('result', {}).get('contents', [])
                                    if contents:
                                        text = contents[0].get('text', '{}')
                                        obj_data = json.loads(text)
                                        print(f"名称: {obj_data.get('data', {}).get('name')}")
                                        print(f"父对象ID: {obj_data.get('data', {}).get('parentID')}")
                                        print(f"根场景: {obj_data.get('data', {}).get('scenePath')}")
                                        break
                    break
        
        # 查找LeaderboardManager
        print("\n查找LeaderboardManager...")
        call_msg = {'jsonrpc': '2.0', 'id': 5, 'method': 'tools/call',
            'params': {'name': 'find_gameobjects', 'arguments': {'search_term': 'LeaderboardManager', 'search_method': 'by_name'}}}
        async with session.post(MCP_URL, headers=headers, json=call_msg) as r:
            async for line in r.content:
                line_text = line.decode().strip()
                if line_text.startswith('data:'):
                    data = json.loads(line_text[5:])
                    result = data.get('result', {}).get('structuredContent', {})
                    print(f"LeaderboardManager: {json.dumps(result, ensure_ascii=False)}")
                    break

asyncio.run(main())
