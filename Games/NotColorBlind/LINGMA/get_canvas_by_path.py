#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通过路径获取Canvas子对象
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
                    'scope': 'children',
                    'path': 'Canvas'
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
                
                print(f"\nCanvas子对象:")
                print(f"完整数据: {json.dumps(all_data, ensure_ascii=False, indent=2)}")
                structured = all_data[0].get('result', {}).get('structuredContent', {})
                items = structured.get('data', {}).get('items', [])
                
                button_id = None
                leaderboard_id = None
                
                for item in items:
                    name = item.get('name')
                    obj_id = item.get('instanceID')
                    print(f"  - {name} (ID: {obj_id})")
                    
                    if name == 'Button':
                        button_id = obj_id
                    elif name == 'LeaderboardButton':
                        leaderboard_id = obj_id
                
                return button_id, leaderboard_id

async def adjust_size():
    button_id, leaderboard_id = await get_canvas_children()
    
    if not button_id or not leaderboard_id:
        print("\n❌ 无法找到Button或LeaderboardButton")
        return
    
    print(f"\n找到:")
    print(f"  Button ID: {button_id}")
    print(f"  LeaderboardButton ID: {leaderboard_id}")
    
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
                'clientInfo': {'name': 'adjust-size', 'version': '1.0.0'}
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
        
        # 获取Button大小
        print(f"\n获取Button大小...")
        async with session.get(f'http://127.0.0.1:8080/mcpforunity://scene/gameobject/{button_id}/components', headers=headers) as comp_resp:
            if comp_resp.status == 200:
                comp_data = await comp_resp.json()
                components = comp_data.get('components', [])
                for comp in components:
                    if comp.get('componentType') == 'RectTransform':
                        properties = comp.get('properties', {})
                        size_delta = properties.get('m_SizeDelta', {})
                        button_size_x = size_delta.get('x', 0)
                        button_size_y = size_delta.get('y', 0)
                        print(f"  Button大小: x={button_size_x}, y={button_size_y}")
        
        # 计算一半大小
        half_size_x = button_size_x / 2
        half_size_y = button_size_y / 2
        
        print(f"\n计算LeaderboardButton目标大小: {half_size_x} x {half_size_y}")
        
        # 修改LeaderboardButton大小
        print(f"\n修改LeaderboardButton大小...")
        modify_size = {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'tools/call',
            'params': {
                'name': 'manage_gameobject',
                'arguments': {
                    'action': 'modify',
                    'search_method': 'by_id',
                    'search_term': str(leaderboard_id),
                    'properties': {
                        'm_SizeDelta': {
                            'x': half_size_x,
                            'y': half_size_y
                        }
                    }
                }
            }
        }
        
        async with session.post(url, headers=headers, json=modify_size) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        result = data.get('result', {})
                        print(f"修改结果: {result.get('structuredContent', '成功')}")
        
        # 保存场景
        print(f"\n保存场景...")
        save_scene = {
            'jsonrpc': '2.0',
            'id': 3,
            'method': 'tools/call',
            'params': {
                'name': 'manage_scene',
                'arguments': {
                    'action': 'save'
                }
            }
        }
        
        async with session.post(url, headers=headers, json=save_scene) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        print(f"场景已保存")
        
        print(f"\n✅ 完成!")
        print(f"LeaderboardButton大小已调整为Button的一半: {half_size_x} x {half_size_y}")

asyncio.run(adjust_size())
