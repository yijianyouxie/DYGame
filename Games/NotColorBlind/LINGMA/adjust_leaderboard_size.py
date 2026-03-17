#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调整LeaderboardButton大小为Button的一半
"""
import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def adjust_leaderboard_size():
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
        
        # 查找所有对象
        print("查找Button对象...")
        find_button = {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'tools/call',
            'params': {
                'name': 'find_gameobjects',
                'arguments': {
                    'search_term': '',
                    'search_method': 'by_name'
                }
            }
        }
        
        button_id = None
        button_size = None
        
        async with session.post(url, headers=headers, json=find_button) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        result = data.get('result', {})
                        objects = result.get('content', [])
                        
                        for obj in objects:
                            if obj.get('name') == 'Button':
                                button_id = obj.get('id')
                                print(f"找到Button: ID={button_id}")
                                
                                # 获取Button的Transform组件
                                async with session.get(f'http://127.0.0.1:8080/mcpforunity://scene/gameobject/{button_id}/components', headers=headers) as comp_resp:
                                    if comp_resp.status == 200:
                                        comp_data = await comp_resp.json()
                                        components = comp_data.get('components', [])
                                        for comp in components:
                                            if comp.get('componentType') == 'RectTransform':
                                                properties = comp.get('properties', {})
                                                size_delta = properties.get('m_SizeDelta', {})
                                                button_size = {
                                                    'x': size_delta.get('x', 0),
                                                    'y': size_delta.get('y', 0)
                                                }
                                                print(f"Button原始大小: {button_size['x']} x {button_size['y']}")
                                break
        
        if not button_id or not button_size:
            print("无法找到Button或获取其大小")
            return
        
        # 计算一半大小
        half_size = {
            'x': button_size['x'] / 2,
            'y': button_size['y'] / 2
        }
        print(f"设置LeaderboardButton大小为: {half_size['x']} x {half_size['y']}")
        
        # 查找LeaderboardButton
        print("查找LeaderboardButton...")
        find_leaderboard = {
            'jsonrpc': '2.0',
            'id': 3,
            'method': 'tools/call',
            'params': {
                'name': 'find_gameobjects',
                'arguments': {
                    'search_term': 'LeaderboardButton',
                    'search_method': 'by_name'
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
                        
                        for obj in objects:
                            if obj.get('name') == 'LeaderboardButton':
                                leaderboard_id = obj.get('id')
                                print(f"找到LeaderboardButton: ID={leaderboard_id}")
                                break
        
        if not leaderboard_id:
            print("无法找到LeaderboardButton")
            return
        
        # 修改LeaderboardButton的大小
        print("修改LeaderboardButton大小...")
        modify_size = {
            'jsonrpc': '2.0',
            'id': 4,
            'method': 'tools/call',
            'params': {
                'name': 'manage_gameobject',
                'arguments': {
                    'action': 'modify',
                    'search_method': 'by_id',
                    'search_term': str(leaderboard_id),
                    'properties': {
                        'm_SizeDelta': {
                            'x': half_size['x'],
                            'y': half_size['y']
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
                        print(f"大小修改结果: {result.get('content', '成功')}")
        
        # 保存场景
        print("保存场景...")
        save_scene = {
            'jsonrpc': '2.0',
            'id': 5,
            'method': 'tools/call',
            'params': {
                'name': 'manage_scene',
                'arguments': {
                    'action': 'save',
                    'scene_name': 'Start'
                }
            }
        }
        
        async with session.post(url, headers=headers, json=save_scene) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        print(f"场景保存: 成功")
        
        print("\n✅ 完成!")
        print(f"LeaderboardButton大小已调整为Button的一半: {half_size['x']} x {half_size['y']}")

asyncio.run(adjust_leaderboard_size())
