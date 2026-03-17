#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
切换场景并创建按钮
"""
import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def create_buttons():
    """创建所有按钮"""
    url = 'http://127.0.0.1:8080/mcp'
    headers = {
        'Accept': 'application/json,text/event-stream',
        'Content-Type': 'application/json'
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 创建所有按钮 ===\n")
        
        # 初始化
        init_msg = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'initialize',
            'params': {
                'protocolVersion': '2024-11-05',
                'capabilities': {},
                'clientInfo': {'name': 'create-buttons', 'version': '1.0.0'}
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
            'method': 'notifications/initialized'
        })
        
        # 加载Start场景获取按钮样式
        print("\n=== 步骤1: 加载Start场景获取LeaderboardButton样式 ===\n")
        load_start = {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'tools/call',
            'params': {
                'name': 'manage_scene',
                'arguments': {
                    'action': 'load',
                    'scene_name': 'Start'
                }
            }
        }
        
        async with session.post(url, headers=headers, json=load_start) as response:
            if response.status == 200:
                response_text = await response.text()
                for line in response_text.split('\n'):
                    line = line.strip()
                    if line.startswith('data:'):
                        data = json.loads(line[5:])
                        structured = data.get('result', {}).get('structuredContent', {})
                        if structured:
                            if structured.get('success'):
                                print(f"✅ Start场景加载成功")
                            else:
                                print(f"⚠️ Start场景加载: {structured}")
        
        await asyncio.sleep(1)
        
        # 查找LeaderboardButton
        print("\n查找LeaderboardButton...")
        find_button = {
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
        
        button_id = None
        async with session.post(url, headers=headers, json=find_button) as response:
            if response.status == 200:
                response_text = await response.text()
                for line in response_text.split('\n'):
                    line = line.strip()
                    if line.startswith('data:'):
                        data = json.loads(line[5:])
                        structured = data.get('result', {}).get('structuredContent', {})
                        if structured:
                            instance_ids = structured.get('data', {}).get('instanceIDs', [])
                            if instance_ids:
                                button_id = instance_ids[0]
                                print(f"✅ 找到LeaderboardButton, ID: {button_id}")
        
        if not button_id:
            print("❌ 在Start场景中未找到LeaderboardButton")
            print("请确保Start场景中有LeaderboardButton")
            return
        
        # 获取组件属性
        print("\n获取LeaderboardButton的组件属性...")
        get_components = {
            'jsonrpc': '2.0',
            'id': 4,
            'method': 'tools/call',
            'params': {
                'name': 'manage_components',
                'arguments': {
                    'action': 'get',
                    'target': str(button_id),
                    'search_method': 'by_id'
                }
            }
        }
        
        async with session.post(url, headers=headers, json=get_components) as response:
            if response.status == 200:
                response_text = await response.text()
                print(f"组件属性:\n{response_text}")
        
        # 加载LevelScene并创建/更新ReturnButton
        print("\n=== 步骤2: 加载LevelScene ===\n")
        load_level = {
            'jsonrpc': '2.0',
            'id': 5,
            'method': 'tools/call',
            'params': {
                'name': 'manage_scene',
                'arguments': {
                    'action': 'load',
                    'scene_name': 'Level'
                }
            }
        }
        
        async with session.post(url, headers=headers, json=load_level) as response:
            if response.status == 200:
                response_text = await response.text()
                for line in response_text.split('\n'):
                    line = line.strip()
                    if line.startswith('data:'):
                        data = json.loads(line[5:])
                        structured = data.get('result', {}).get('structuredContent', {})
                        if structured and structured.get('success'):
                            print(f"✅ LevelScene加载成功")
        
        await asyncio.sleep(1)
        
        # 加载ResultScene并创建/更新ResultLeaderboardButton
        print("\n=== 步骤3: 加载ResultScene ===\n")
        load_result = {
            'jsonrpc': '2.0',
            'id': 6,
            'method': 'tools/call',
            'params': {
                'name': 'manage_scene',
                'arguments': {
                    'action': 'load',
                    'scene_name': 'Result'
                }
            }
        }
        
        async with session.post(url, headers=headers, json=load_result) as response:
            if response.status == 200:
                response_text = await response.text()
                for line in response_text.split('\n'):
                    line = line.strip()
                    if line.startswith('data:'):
                        data = json.loads(line[5:])
                        structured = data.get('result', {}).get('structuredContent', {})
                        if structured and structured.get('success'):
                            print(f"✅ ResultScene加载成功")
        
        await asyncio.sleep(1)
        
        # 在ResultScene中创建ResultLeaderboardButton
        print("\n在ResultScene中创建ResultLeaderboardButton...")
        create_result_button = {
            'jsonrpc': '2.0',
            'id': 7,
            'method': 'tools/call',
            'params': {
                'name': 'manage_gameobject',
                'arguments': {
                    'action': 'create',
                    'name': 'ResultLeaderboardButton',
                    'parent': 'Canvas'
                }
            }
        }
        
        result_button_id = None
        async with session.post(url, headers=headers, json=create_result_button) as response:
            if response.status == 200:
                response_text = await response.text()
                for line in response_text.split('\n'):
                    line = line.strip()
                    if line.startswith('data:'):
                        data = json.loads(line[5:])
                        structured = data.get('result', {}).get('structuredContent', {})
                        if structured and structured.get('success'):
                            result_button_id = structured.get('data', {}).get('instanceID')
                            print(f"✅ ResultLeaderboardButton创建成功, ID: {result_button_id}")
        
        if result_button_id:
            # 添加组件（简化版本）
            print("\n添加组件...")
            
            # 添加RectTransform
            add_rect = {
                'jsonrpc': '2.0',
                'id': 8,
                'method': 'tools/call',
                'params': {
                    'name': 'manage_components',
                    'arguments': {
                        'action': 'add',
                        'target': 'ResultLeaderboardButton',
                        'search_method': 'by_name',
                        'component_type': 'RectTransform'
                    }
                }
            }
            
            await session.post(url, headers=headers, json=add_rect)
            
            # 添加Image
            add_image = {
                'jsonrpc': '2.0',
                'id': 9,
                'method': 'tools/call',
                'params': {
                    'name': 'manage_components',
                    'arguments': {
                        'action': 'add',
                        'target': 'ResultLeaderboardButton',
                        'search_method': 'by_name',
                        'component_type': 'UnityEngine.UI.Image'
                    }
                }
            }
            
            await session.post(url, headers=headers, json=add_image)
            
            # 添加Button
            add_button = {
                'jsonrpc': '2.0',
                'id': 10,
                'method': 'tools/call',
                'params': {
                    'name': 'manage_components',
                    'arguments': {
                        'action': 'add',
                        'target': 'ResultLeaderboardButton',
                        'search_method': 'by_name',
                        'component_type': 'UnityEngine.UI.Button'
                    }
                }
            }
            
            await session.post(url, headers=headers, json=add_button)
            
            print("✅ 组件添加完成")
        
        # 保存ResultScene
        print("\n保存ResultScene...")
        save_result = {
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
        
        async with session.post(url, headers=headers, json=save_result) as response:
            if response.status == 200:
                response_text = await response.text()
                for line in response_text.split('\n'):
                    line = line.strip()
                    if line.startswith('data:'):
                        data = json.loads(line[5:])
                        structured = data.get('result', {}).get('structuredContent', {})
                        if structured and structured.get('success'):
                            print(f"✅ ResultScene保存成功")
        
        print("\n🎉 完成！")
        print("\n接下来需要：")
        print("1. 手动在Unity中设置按钮的Image sprite")
        print("2. 手动设置按钮的RectTransform属性")
        print("3. 添加Text子对象并设置文字")

if __name__ == '__main__':
    asyncio.run(create_buttons())
