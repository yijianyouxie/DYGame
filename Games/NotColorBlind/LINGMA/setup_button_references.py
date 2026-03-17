#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为ResultController和LevelController添加按钮引用
"""
import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def setup_result_scene():
    """设置ResultScene中的按钮引用"""
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
                'clientInfo': {'name': 'setup-result', 'version': '1.0.0'}
            }
        }
        
        async with session.post(url, headers=headers, json=init_msg) as response:
            session_id = response.headers.get('mcp-session-id')
            if response.status == 200:
                async for line in response.content:
                    if line.decode('utf-8').strip().startswith('data:'):
                        break
        
        if not session_id:
            return
        
        headers['mcp-session-id'] = session_id
        
        # 发送initialized
        await session.post(url, headers=headers, json={
            'jsonrpc': '2.0',
            'method': 'notifications/initialized',
            'params': {}
        })
        
        # 打开ResultScene
        print("🔄 打开ResultScene...")
        load_call = {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'tools/call',
            'params': {
                'name': 'manage_scene',
                'arguments': {
                    'action': 'load',
                    'scene_name': 'ResultScene'
                }
            }
        }
        
        async with session.post(url, headers=headers, json=load_call) as response:
            if response.status == 200:
                async for line in response.content:
                    if line.decode('utf-8').strip().startswith('data:'):
                        break
        
        # 查找ResultController
        print("\n🔄 查找ResultController...")
        find_controller = {
            'jsonrpc': '2.0',
            'id': 3,
            'method': 'tools/call',
            'params': {
                'name': 'find_gameobjects',
                'arguments': {
                    'search_term': 'ResultController',
                    'search_method': 'by_name'
                }
            }
        }
        
        controller_id = None
        async with session.post(url, headers=headers, json=find_controller) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        result = data.get('result', {}).get('structuredContent', {})
                        instance_ids = result.get('data', {}).get('instanceIDs', [])
                        if instance_ids:
                            controller_id = instance_ids[0]
                            print(f"✅ 找到ResultController: {controller_id}")
                        break
        
        if not controller_id:
            print("❌ 未找到ResultController")
            return
        
        await asyncio.sleep(0.5)
        
        # 查找ResultLeaderboardButton
        print("\n🔄 查找ResultLeaderboardButton...")
        find_leaderboard = {
            'jsonrpc': '2.0',
            'id': 4,
            'method': 'tools/call',
            'params': {
                'name': 'find_gameobjects',
                'arguments': {
                    'search_term': 'ResultLeaderboardButton',
                    'search_method': 'by_name'
                }
            }
        }
        
        leaderboard_button_id = None
        async with session.post(url, headers=headers, json=find_leaderboard) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        result = data.get('result', {}).get('structuredContent', {})
                        instance_ids = result.get('data', {}).get('instanceIDs', [])
                        if instance_ids:
                            leaderboard_button_id = instance_ids[0]
                            print(f"✅ 找到ResultLeaderboardButton: {leaderboard_button_id}")
                        break
        
        # MCP不支持直接设置组件引用，需要用户手动在Unity中设置
        print("\n" + "=" * 60)
        print("⚠️  需要手动操作：")
        print("=" * 60)
        print("\n在Unity编辑器中，打开ResultScene，然后：")
        print("1. 找到ResultController对象")
        print("2. 在Inspector中，将以下按钮拖拽到对应的字段：")
        print(f"   - ResultLeaderboardButton → leaderboardButton字段")
        print("   - （如果有返回按钮）ReturnButton → returnButton字段")
        print("3. 保存场景")
        print("=" * 60)

async def setup_level_scene():
    """设置LevelScene中的按钮引用"""
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
                'clientInfo': {'name': 'setup-level', 'version': '1.0.0'}
            }
        }
        
        async with session.post(url, headers=headers, json=init_msg) as response:
            session_id = response.headers.get('mcp-session-id')
            if response.status == 200:
                async for line in response.content:
                    if line.decode('utf-8').strip().startswith('data:'):
                        break
        
        if not session_id:
            return
        
        headers['mcp-session-id'] = session_id
        
        # 发送initialized
        await session.post(url, headers=headers, json={
            'jsonrpc': '2.0',
            'method': 'notifications/initialized',
            'params': {}
        })
        
        # 打开LevelScene
        print("\n🔄 打开LevelScene...")
        load_call = {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'tools/call',
            'params': {
                'name': 'manage_scene',
                'arguments': {
                    'action': 'load',
                    'scene_name': 'LevelScene'
                }
            }
        }
        
        async with session.post(url, headers=headers, json=load_call) as response:
            if response.status == 200:
                async for line in response.content:
                    if line.decode('utf-8').strip().startswith('data:'):
                        break
        
        print("\n" + "=" * 60)
        print("⚠️  需要手动操作：")
        print("=" * 60)
        print("\n在Unity编辑器中，打开LevelScene，然后：")
        print("1. 找到LevelController对象")
        print("2. 在Inspector中，将ReturnButton拖拽到returnButton字段")
        print("3. 保存场景")
        print("=" * 60)

async def main():
    print("=" * 60)
    print("🎯 设置按钮引用")
    print("=" * 60)
    
    await setup_result_scene()
    await asyncio.sleep(1)
    await setup_level_scene()
    
    print("\n" + "=" * 60)
    print("✅ 完成！")
    print("=" * 60)
    print("\n请按照上述提示在Unity编辑器中完成按钮引用的设置。")

asyncio.run(main())
