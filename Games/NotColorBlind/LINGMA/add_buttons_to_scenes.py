#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1. 在ResultScene中添加排行榜按钮
2. 在LevelScene中添加返回按钮
3. 查看当前代码实现场景跳转
"""
import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def open_scene(scene_name):
    """打开指定场景"""
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
                'clientInfo': {'name': 'open-scene', 'version': '1.0.0'}
            }
        }
        
        async with session.post(url, headers=headers, json=init_msg) as response:
            session_id = response.headers.get('mcp-session-id')
            if response.status == 200:
                async for line in response.content:
                    if line.decode('utf-8').strip().startswith('data:'):
                        break
        
        if not session_id:
            return None
        
        headers['mcp-session-id'] = session_id
        
        await session.post(url, headers=headers, json={
            'jsonrpc': '2.0',
            'method': 'notifications/initialized',
            'params': {}
        })
        
        # 打开场景
        load_call = {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'tools/call',
            'params': {
                'name': 'manage_scene',
                'arguments': {
                    'action': 'load',
                    'scene_name': scene_name
                }
            }
        }
        
        async with session.post(url, headers=headers, json=load_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        break
        
        return session_id

async def duplicate_button(session_id, button_name, target_scene):
    """复制LeaderboardButton到指定场景"""
    url = 'http://127.0.0.1:8080/mcp'
    headers = {
        'Accept': 'application/json,text/event-stream',
        'Content-Type': 'application/json',
        'mcp-session-id': session_id
    }
    
    # 查找Start场景的LeaderboardButton
    print(f"🔄 在Start场景中查找LeaderboardButton...")
    find_button = {
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'tools/call',
        'params': {
            'name': 'find_gameobjects',
            'arguments': {
                'search_term': 'LeaderboardButton',
                'search_method': 'by_name'
            }
        }
    }
    
    button_id = None
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=find_button) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        result = data.get('result', {}).get('structuredContent', {})
                        instance_ids = result.get('data', {}).get('instanceIDs', [])
                        if instance_ids:
                            button_id = instance_ids[0]
                            print(f"✅ 找到LeaderboardButton, instanceID: {button_id}")
                        break
        
        if not button_id:
            print("❌ 未找到LeaderboardButton")
            return None
        
        # 复制按钮
        print(f"\n🔄 复制按钮为{button_name}...")
        duplicate_call = {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'tools/call',
            'params': {
                'name': 'manage_gameobject',
                'arguments': {
                    'action': 'duplicate',
                    'search_method': 'by_id',
                    'search_term': str(button_id),
                    'new_name': button_name
                }
            }
        }
        
        new_button_id = None
        async with session.post(url, headers=headers, json=duplicate_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        result = data.get('result', {}).get('structuredContent', {})
                        new_button_id = result.get('instanceID')
                        print(f"✅ 按钮复制成功, 新ID: {new_button_id}")
                        break
        
        await asyncio.sleep(0.3)
        
        # 设置大小为Button的一半 (200x75)
        print(f"\n🔄 设置按钮大小为200x75...")
        set_size = {
            'jsonrpc': '2.0',
            'id': 3,
            'method': 'tools/call',
            'params': {
                'name': 'manage_components',
                'arguments': {
                    'action': 'set_property',
                    'target': button_name,
                    'search_method': 'by_name',
                    'component_type': 'RectTransform',
                    'property': 'sizeDelta',
                    'value': {'x': 200, 'y': 75}
                }
            }
        }
        
        async with session.post(url, headers=headers, json=set_size) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        print(f"✅ 大小设置成功")
                        break
        
        await asyncio.sleep(0.3)
        
        # 设置锚点到右上角
        print(f"\n🔄 设置锚点到右上角...")
        set_anchor_min = {
            'jsonrpc': '2.0',
            'id': 4,
            'method': 'tools/call',
            'params': {
                'name': 'manage_components',
                'arguments': {
                    'action': 'set_property',
                    'target': button_name,
                    'search_method': 'by_name',
                    'component_type': 'RectTransform',
                    'property': 'anchorMin',
                    'value': {'x': 1.0, 'y': 1.0}
                }
            }
        }
        
        async with session.post(url, headers=headers, json=set_anchor_min) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        print(f"✅ anchorMin设置成功")
                        break
        
        await asyncio.sleep(0.3)
        
        set_anchor_max = {
            'jsonrpc': '2.0',
            'id': 5,
            'method': 'tools/call',
            'params': {
                'name': 'manage_components',
                'arguments': {
                    'action': 'set_property',
                    'target': button_name,
                    'search_method': 'by_name',
                    'component_type': 'RectTransform',
                    'property': 'anchorMax',
                    'value': {'x': 1.0, 'y': 1.0}
                }
            }
        }
        
        async with session.post(url, headers=headers, json=set_anchor_max) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        print(f"✅ anchorMax设置成功")
                        break
        
        await asyncio.sleep(0.3)
        
        # 设置Pivot到右上角
        print(f"\n🔄 设置Pivot到右上角...")
        set_pivot = {
            'jsonrpc': '2.0',
            'id': 6,
            'method': 'tools/call',
            'params': {
                'name': 'manage_components',
                'arguments': {
                    'action': 'set_property',
                    'target': button_name,
                    'search_method': 'by_name',
                    'component_type': 'RectTransform',
                    'property': 'pivot',
                    'value': {'x': 1.0, 'y': 1.0}
                }
            }
        }
        
        async with session.post(url, headers=headers, json=set_pivot) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        print(f"✅ Pivot设置成功")
                        break
        
        await asyncio.sleep(0.3)
        
        # 设置位置
        print(f"\n🔄 设置按钮位置...")
        set_position = {
            'jsonrpc': '2.0',
            'id': 7,
            'method': 'tools/call',
            'params': {
                'name': 'manage_components',
                'arguments': {
                    'action': 'set_property',
                    'target': button_name,
                    'search_method': 'by_name',
                    'component_type': 'RectTransform',
                    'property': 'anchoredPosition',
                    'value': {'x': -20, 'y': -20}
                }
            }
        }
        
        async with session.post(url, headers=headers, json=set_position) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        print(f"✅ 位置设置成功")
                        break
        
        # 修改文字
        await asyncio.sleep(0.3)
        print(f"\n🔄 修改按钮文字...")
        
        # 查找所有Text组件
        find_text = {
            'jsonrpc': '2.0',
            'id': 8,
            'method': 'tools/call',
            'params': {
                'name': 'find_gameobjects',
                'arguments': {
                    'search_term': 'Text',
                    'search_method': 'by_component'
                }
            }
        }
        
        text_id = None
        async with session.post(url, headers=headers, json=find_text) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        result = data.get('result', {}).get('structuredContent', {})
                        instance_ids = result.get('data', {}).get('instanceIDs', [])
                        # 使用最后一个Text（新复制的按钮的Text）
                        if instance_ids:
                            text_id = instance_ids[-1]
                            print(f"找到Text ID: {text_id}")
                        break
        
        # 设置文字和字体大小
        if target_scene == 'ResultScene':
            text_value = '排行榜'
        else:  # LevelScene
            text_value = '返回'
        
        await asyncio.sleep(0.3)
        print(f"\n🔄 设置文字为'{text_value}'...")
        set_text = {
            'jsonrpc': '2.0',
            'id': 9,
            'method': 'tools/call',
            'params': {
                'name': 'manage_components',
                'arguments': {
                    'action': 'set_property',
                    'target': str(text_id),
                    'search_method': 'by_id',
                    'component_type': 'Text',
                    'property': 'text',
                    'value': text_value
                }
            }
        }
        
        async with session.post(url, headers=headers, json=set_text) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        print(f"✅ 文字设置成功")
                        break
        
        await asyncio.sleep(0.3)
        print(f"\n🔄 设置字体大小为32...")
        set_font_size = {
            'jsonrpc': '2.0',
            'id': 10,
            'method': 'tools/call',
            'params': {
                'name': 'manage_components',
                'arguments': {
                    'action': 'set_property',
                    'target': str(text_id),
                    'search_method': 'by_id',
                    'component_type': 'Text',
                    'property': 'fontSize',
                    'value': 32
                }
            }
        }
        
        async with session.post(url, headers=headers, json=set_font_size) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        print(f"✅ 字体大小设置成功")
                        break
        
        # 保存场景
        await asyncio.sleep(0.3)
        print(f"\n🔄 保存场景...")
        save_call = {
            'jsonrpc': '2.0',
            'id': 11,
            'method': 'tools/call',
            'params': {
                'name': 'manage_scene',
                'arguments': {
                    'action': 'save'
                }
            }
        }
        
        async with session.post(url, headers=headers, json=save_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        print(f"✅ 场景已保存")
                        break
        
        print(f"\n✅ {target_scene}的{button_name}按钮添加完成!")
        return new_button_id

async def main():
    print("=" * 60)
    print("🎯 开始添加按钮到场景")
    print("=" * 60)
    
    # 1. 在ResultScene中添加排行榜按钮
    print("\n" + "=" * 60)
    print("📍 步骤1: 在ResultScene中添加排行榜按钮")
    print("=" * 60)
    session_id = await open_scene('ResultScene')
    if session_id:
        await duplicate_button(session_id, 'ResultLeaderboardButton', 'ResultScene')
    
    await asyncio.sleep(1)
    
    # 2. 在LevelScene中添加返回按钮
    print("\n" + "=" * 60)
    print("📍 步骤2: 在LevelScene中添加返回按钮")
    print("=" * 60)
    session_id = await open_scene('LevelScene')
    if session_id:
        await duplicate_button(session_id, 'ReturnButton', 'LevelScene')
    
    print("\n" + "=" * 60)
    print("✅ 所有按钮添加完成!")
    print("=" * 60)

asyncio.run(main())
