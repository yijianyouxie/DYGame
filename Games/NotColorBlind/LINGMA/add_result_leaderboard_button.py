#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
在ResultScene中添加排行榜按钮
"""
import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def add_result_leaderboard_button():
    """在ResultScene中添加排行榜按钮"""
    url = 'http://127.0.0.1:8080/mcp'
    headers = {
        'Accept': 'application/json,text/event-stream',
        'Content-Type': 'application/json'
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 在ResultScene中添加排行榜按钮 ===\n")
        
        # 初始化
        init_msg = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'initialize',
            'params': {
                'protocolVersion': '2024-11-05',
                'capabilities': {},
                'clientInfo': {'name': 'add-result-button', 'version': '1.0.0'}
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
        
        # 步骤1: 创建GameObject
        print("步骤1: 创建ResultLeaderboardButton GameObject...")
        create_go = {
            'jsonrpc': '2.0',
            'id': 2,
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
        
        button_id = None
        async with session.post(url, headers=headers, json=create_go) as response:
            if response.status == 200:
                response_text = await response.text()
                for line in response_text.split('\n'):
                    line = line.strip()
                    if line.startswith('data:'):
                        data = json.loads(line[5:])
                        if 'result' in data:
                            tools_result = data['result']
                            structured = tools_result.get('structuredContent', {})
                            if structured and structured.get('success'):
                                button_id = structured.get('data', {}).get('instanceID')
                                print(f"✅ ResultLeaderboardButton创建成功, ID: {button_id}")
        
        if not button_id:
            print("❌ ResultLeaderboardButton创建失败")
            return
        
        # 步骤2: 添加RectTransform
        print("\n步骤2: 添加RectTransform...")
        add_rect = {
            'jsonrpc': '2.0',
            'id': 3,
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
        
        async with session.post(url, headers=headers, json=add_rect) as response:
            if response.status == 200:
                response_text = await response.text()
                for line in response_text.split('\n'):
                    line = line.strip()
                    if line.startswith('data:'):
                        data = json.loads(line[5:])
                        structured = data.get('result', {}).get('structuredContent', {})
                        if structured and structured.get('success'):
                            print(f"✅ RectTransform添加成功")
        
        # 步骤3: 设置RectTransform属性
        print("\n步骤3: 设置RectTransform属性...")
        
        async def set_property(prop_name, value):
            set_prop = {
                'jsonrpc': '2.0',
                'id': 100,
                'method': 'tools/call',
                'params': {
                    'name': 'manage_components',
                    'arguments': {
                        'action': 'set_property',
                        'search_method': 'by_name',
                        'target': 'ResultLeaderboardButton',
                        'component_type': 'RectTransform',
                        'property': prop_name,
                        'value': value
                    }
                }
            }
            async with session.post(url, headers=headers, json=set_prop) as response:
                if response.status == 200:
                    response_text = await response.text()
                    for line in response_text.split('\n'):
                        line = line.strip()
                        if line.startswith('data:'):
                            data = json.loads(line[5:])
                            structured = data.get('result', {}).get('structuredContent', {})
                            if structured and structured.get('success'):
                                print(f"  ✅ {prop_name}设置成功")
        
        await set_property('anchorMin', {'x': 1, 'y': 1})
        await asyncio.sleep(0.3)
        await set_property('anchorMax', {'x': 1, 'y': 1})
        await asyncio.sleep(0.3)
        await set_property('anchoredPosition', {'x': -100, 'y': -50})
        await asyncio.sleep(0.3)
        await set_property('sizeDelta', {'x': 200, 'y': 75})
        
        # 步骤4: 添加Image
        print("\n步骤4: 添加Image...")
        add_image = {
            'jsonrpc': '2.0',
            'id': 5,
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
        
        async with session.post(url, headers=headers, json=add_image) as response:
            if response.status == 200:
                response_text = await response.text()
                for line in response_text.split('\n'):
                    line = line.strip()
                    if line.startswith('data:'):
                        data = json.loads(line[5:])
                        structured = data.get('result', {}).get('structuredContent', {})
                        if structured and structured.get('success'):
                            print(f"✅ Image组件添加成功")
        
        # 步骤5: 添加Button
        print("\n步骤5: 添加Button...")
        add_button = {
            'jsonrpc': '2.0',
            'id': 6,
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
        
        async with session.post(url, headers=headers, json=add_button) as response:
            if response.status == 200:
                response_text = await response.text()
                for line in response_text.split('\n'):
                    line = line.strip()
                    if line.startswith('data:'):
                        data = json.loads(line[5:])
                        structured = data.get('result', {}).get('structuredContent', {})
                        if structured and structured.get('success'):
                            print(f"✅ Button组件添加成功")
        
        # 步骤6: 创建Text子对象
        print("\n步骤6: 创建Text子对象...")
        create_text = {
            'jsonrpc': '2.0',
            'id': 7,
            'method': 'tools/call',
            'params': {
                'name': 'manage_gameobject',
                'arguments': {
                    'action': 'create',
                    'name': 'Text',
                    'parent': str(button_id)
                }
            }
        }
        
        text_id = None
        async with session.post(url, headers=headers, json=create_text) as response:
            if response.status == 200:
                response_text = await response.text()
                for line in response_text.split('\n'):
                    line = line.strip()
                    if line.startswith('data:'):
                        data = json.loads(line[5:])
                        structured = data.get('result', {}).get('structuredContent', {})
                        if structured and structured.get('success'):
                            text_id = structured.get('data', {}).get('instanceID')
                            print(f"✅ Text创建成功, ID: {text_id}")
        
        if text_id:
            # 步骤7: 添加Text的RectTransform
            print("\n步骤7: 添加Text的RectTransform并设置属性...")
            add_text_rect = {
                'jsonrpc': '2.0',
                'id': 8,
                'method': 'tools/call',
                'params': {
                    'name': 'manage_components',
                    'arguments': {
                        'action': 'add',
                        'target': str(text_id),
                        'search_method': 'by_instance_id',
                        'component_type': 'RectTransform'
                    }
                }
            }
            
            async with session.post(url, headers=headers, json=add_text_rect) as response:
                if response.status == 200:
                    response_text = await response.text()
                    for line in response_text.split('\n'):
                        line = line.strip()
                        if line.startswith('data:'):
                            pass
            
            # 设置Text的RectTransform属性
            async def set_text_rect_property(prop_name, value):
                set_prop = {
                    'jsonrpc': '2.0',
                    'id': 100,
                    'method': 'tools/call',
                    'params': {
                        'name': 'manage_components',
                        'arguments': {
                            'action': 'set_property',
                            'search_method': 'by_instance_id',
                            'target': str(text_id),
                            'component_type': 'RectTransform',
                            'property': prop_name,
                            'value': value
                        }
                    }
                }
                async with session.post(url, headers=headers, json=set_prop) as response:
                    pass
            
            await set_text_rect_property('anchorMin', {'x': 0, 'y': 0})
            await set_text_rect_property('anchorMax', {'x': 1, 'y': 1})
            await set_text_rect_property('anchoredPosition', {'x': 0, 'y': 0})
            await set_text_rect_property('sizeDelta', {'x': 0, 'y': 0})
            
            # 步骤8: 添加Text组件
            print("\n步骤8: 添加Text组件并设置属性...")
            add_text_comp = {
                'jsonrpc': '2.0',
                'id': 9,
                'method': 'tools/call',
                'params': {
                    'name': 'manage_components',
                    'arguments': {
                        'action': 'add',
                        'target': str(text_id),
                        'search_method': 'by_instance_id',
                        'component_type': 'UnityEngine.UI.Text'
                    }
                }
            }
            
            async with session.post(url, headers=headers, json=add_text_comp) as response:
                if response.status == 200:
                    response_text = await response.text()
                    for line in response_text.split('\n'):
                        line = line.strip()
                        if line.startswith('data:'):
                            data = json.loads(line[5:])
                            structured = data.get('result', {}).get('structuredContent', {})
                            if structured and structured.get('success'):
                                print(f"✅ Text组件添加成功")
            
            # 设置Text属性
            async def set_text_prop(prop_name, value):
                set_prop = {
                    'jsonrpc': '2.0',
                    'id': 100,
                    'method': 'tools/call',
                    'params': {
                        'name': 'manage_components',
                        'arguments': {
                            'action': 'set_property',
                            'search_method': 'by_instance_id',
                            'target': str(text_id),
                            'component_type': 'UnityEngine.UI.Text',
                            'property': prop_name,
                            'value': value
                        }
                    }
                }
                async with session.post(url, headers=headers, json=set_prop) as response:
                    if response.status == 200:
                        response_text = await response.text()
                        for line in response_text.split('\n'):
                            line = line.strip()
                            if line.startswith('data:'):
                                data = json.loads(line[5:])
                                structured = data.get('result', {}).get('structuredContent', {})
                                if structured and structured.get('success'):
                                    print(f"  ✅ Text.{prop_name}设置成功")
            
            await set_text_prop('fontSize', 32)
            await set_text_prop('text', '排行榜')
            
            # 步骤9: 保存场景
            print("\n步骤9: 保存ResultScene...")
            save_scene = {
                'jsonrpc': '2.0',
                'id': 10,
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
                    response_text = await response.text()
                    for line in response_text.split('\n'):
                        line = line.strip()
                        if line.startswith('data:'):
                            data = json.loads(line[5:])
                            structured = data.get('result', {}).get('structuredContent', {})
                            if structured and structured.get('success'):
                                print(f"✅ ResultScene保存成功")
            
            print("\n🎉 ResultScene排行榜按钮添加完成！")

if __name__ == '__main__':
    asyncio.run(add_result_leaderboard_button())
