#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通过路径查找Button和LeaderboardButton
"""
import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def find_by_path():
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
                'clientInfo': {'name': 'find-path', 'version': '1.0.0'}
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
        
        # 查找Button
        print("查找Canvas/Button...")
        find_button = {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'tools/call',
            'params': {
                'name': 'find_gameobjects',
                'arguments': {
                    'search_term': 'Canvas/Button',
                    'search_method': 'by_path'
                }
            }
        }
        
        button_id = None
        async with session.post(url, headers=headers, json=find_button) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        result = data.get('result', {})
                        objects = result.get('content', [])
                        
                        if objects:
                            button_id = objects[0].get('id')
                            print(f"找到Button: ID={button_id}")
                        else:
                            print("未找到Canvas/Button")
        
        # 查找LeaderboardButton
        print("\n查找Canvas/LeaderboardButton...")
        find_leaderboard = {
            'jsonrpc': '2.0',
            'id': 3,
            'method': 'tools/call',
            'params': {
                'name': 'find_gameobjects',
                'arguments': {
                    'search_term': 'Canvas/LeaderboardButton',
                    'search_method': 'by_path'
                }
            }
        }
        
        leaderboard_id = None
        async with session.post(url, headers=headers, json=find_leaderboard) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        result = data.get('result', {})
                        objects = result.get('content', [])
                        
                        if objects:
                            leaderboard_id = objects[0].get('id')
                            print(f"找到LeaderboardButton: ID={leaderboard_id}")
                        else:
                            print("未找到Canvas/LeaderboardButton")
        
        # 获取Button大小
        if button_id:
            print(f"\n获取Button的大小...")
            async with session.get(f'http://127.0.0.1:8080/mcpforunity://scene/gameobject/{button_id}/components', headers=headers) as comp_resp:
                if comp_resp.status == 200:
                    comp_data = await comp_resp.json()
                    components = comp_data.get('components', [])
                    for comp in components:
                        if comp.get('componentType') == 'RectTransform':
                            properties = comp.get('properties', {})
                            size_delta = properties.get('m_SizeDelta', {})
                            print(f"  Button大小: x={size_delta.get('x')}, y={size_delta.get('y')}")
        
        # 获取LeaderboardButton大小
        if leaderboard_id:
            print(f"\n获取LeaderboardButton的当前大小...")
            async with session.get(f'http://127.0.0.1:8080/mcpforunity://scene/gameobject/{leaderboard_id}/components', headers=headers) as comp_resp:
                if comp_resp.status == 200:
                    comp_data = await comp_resp.json()
                    components = comp_data.get('components', [])
                    for comp in components:
                        if comp.get('componentType') == 'RectTransform':
                            properties = comp.get('properties', {})
                            size_delta = properties.get('m_SizeDelta', {})
                            print(f"  LeaderboardButton当前大小: x={size_delta.get('x')}, y={size_delta.get('y')}")

asyncio.run(find_by_path())
