#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取Canvas子对象
"""
import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def get_canvas_children():
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
                'clientInfo': {'name': 'get-canvas-children', 'version': '1.0.0'}
            }
        }
        
        async with session.post(url, headers=headers, json=init_msg) as response:
            session_id = response.headers.get('mcp-session-id')
            if response.status == 200:
                async for line in response.content:
                    if line.decode('utf-8').strip().startswith('data:'):
                        break
        
        if not session_id:
            print("无法获取session ID")
            return
        
        headers['mcp-session-id'] = session_id
        
        # 发送initialized
        await session.post(url, headers=headers, json={
            'jsonrpc': '2.0',
            'method': 'notifications/initialized',
            'params': {}
        })
        
        # 获取Canvas的子对象
        print("获取Canvas子对象...")
        get_children = {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'tools/call',
            'params': {
                'name': 'manage_scene',
                'arguments': {
                    'action': 'get_hierarchy',
                    'search_term': 'Canvas',
                    'search_method': 'by_id'
                }
            }
        }
        
        async with session.post(url, headers=headers, json=get_children) as response:
            if response.status == 200:
                all_data = []
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        all_data.append(data)
                
                print(f"\n收到的数据:")
                print(json.dumps(all_data, ensure_ascii=False, indent=2))

asyncio.run(get_canvas_children())
