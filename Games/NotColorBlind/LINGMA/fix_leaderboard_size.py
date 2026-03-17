#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正LeaderboardButton大小
使用正确的参数名称
"""
import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def fix_leaderboard_size():
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
                'clientInfo': {'name': 'fix-size', 'version': '1.0.0'}
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
        
        # 查找LeaderboardButton
        print("查找LeaderboardButton...")
        find_leaderboard = {
            'jsonrpc': '2.0',
            'id': 2,
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
                        result = data.get('result', {}).get('structuredContent', {})
                        instance_ids = result.get('data', {}).get('instanceIDs', [])
                        if instance_ids:
                            leaderboard_id = instance_ids[0]
                            print(f"✅ 找到LeaderboardButton, instanceID: {leaderboard_id}")
                        break
        
        if not leaderboard_id:
            print("❌ 未找到LeaderboardButton")
            return
        
        # Button实际大小是400x150，所以一半是200x75
        half_size_x = 200
        half_size_y = 75
        
        print(f"\n设置LeaderboardButton大小为Button的一半: {half_size_x} x {half_size_y}")
        
        # 使用正确的参数名称：target_object
        modify_size = {
            'jsonrpc': '2.0',
            'id': 3,
            'method': 'tools/call',
            'params': {
                'name': 'manage_gameobject',
                'arguments': {
                    'action': 'modify',
                    'search_method': 'by_id',
                    'target_object': str(leaderboard_id),
                    'property_changes': {
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
                        structured = result.get('structuredContent', {})
                        if structured:
                            print(f"修改结果: {json.dumps(structured, ensure_ascii=False)}")
                        else:
                            print(f"修改结果: 成功")
        
        # 保存场景
        print(f"\n保存场景...")
        save_scene = {
            'jsonrpc': '2.0',
            'id': 4,
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
        print(f"LeaderboardButton大小已设置为Button的一半: {half_size_x} x {half_size_y}")

asyncio.run(fix_leaderboard_size())
