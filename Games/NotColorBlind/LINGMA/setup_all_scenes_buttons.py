#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
在所有场景中设置按钮
"""
import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def setup_buttons_in_scene(session, headers, scene_name, button_name, button_text, url):
    """在指定场景中创建按钮"""
    print(f"\n=== 在{scene_name}中创建{button_name} ===\n")
    
    # 切换场景
    print(f"加载{scene_name}...")
    load_scene = {
        'jsonrpc': '2.0',
        'id': 100,
        'method': 'tools/call',
        'params': {
            'name': 'manage_scene',
            'arguments': {
                'action': 'load',
                'scene_name': scene_name
            }
        }
    }
    
    async with session.post(url, headers=headers, json=load_scene) as response:
        if response.status == 200:
            response_text = await response.text()
            for line in response_text.split('\n'):
                line = line.strip()
                if line.startswith('data:'):
                    data = json.loads(line[5:])
                    structured = data.get('result', {}).get('structuredContent', {})
                    if structured:
                        if structured.get('success'):
                            print(f"✅ {scene_name}加载成功")
                        else:
                            print(f"⚠️ {scene_name}: {structured}")
    
    await asyncio.sleep(1)
    
    # 检查按钮是否已存在
    print(f"\n检查{button_name}是否已存在...")
    find_button = {
        'jsonrpc': '2.0',
        'id': 101,
        'method': 'tools/call',
        'params': {
            'name': 'find_gameobjects',
            'arguments': {
                'search_term': button_name,
                'search_method': 'by_name'
            }
        }
    }
    
    existing_buttons = []
    async with session.post(url, headers=headers, json=find_button) as response:
        if response.status == 200:
            response_text = await response.text()
            for line in response_text.split('\n'):
                line = line.strip()
                if line.startswith('data:'):
                    data = json.loads(line[5:])
                    structured = data.get('result', {}).get('structuredContent', {})
                    if structured:
                        existing_buttons = structured.get('data', {}).get('instanceIDs', [])
                        print(f"找到 {len(existing_buttons)} 个{button_name}")
    
    # 如果已存在，删除所有旧的
    if existing_buttons:
        print(f"删除旧的{button_name}...")
        for btn_id in existing_buttons:
            delete_call = {
                'jsonrpc': '2.0',
                'id': 102,
                'method': 'tools/call',
                'params': {
                    'name': 'manage_gameobject',
                    'arguments': {
                        'action': 'delete',
                        'target': str(btn_id)
                    }
                }
            }
            async with session.post(url, headers=headers, json=delete_call) as response:
                pass
        await asyncio.sleep(0.5)
    
    # 创建新按钮
    print(f"\n创建{button_name}...")
    create_go = {
        'jsonrpc': '2.0',
        'id': 103,
        'method': 'tools/call',
        'params': {
            'name': 'manage_gameobject',
            'arguments': {
                'action': 'create',
                'name': button_name,
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
                    structured = data.get('result', {}).get('structuredContent', {})
                    if structured and structured.get('success'):
                        button_id = structured.get('data', {}).get('instanceID')
                        print(f"✅ {button_name}创建成功, ID: {button_id}")
    
    if not button_id:
        return False
    
    # 添加组件
    print(f"\n添加组件...")
    
    # RectTransform
    add_rect = {
        'jsonrpc': '2.0',
        'id': 104,
        'method': 'tools/call',
        'params': {
            'name': 'manage_components',
            'arguments': {
                'action': 'add',
                'target': button_name,
                'search_method': 'by_name',
                'component_type': 'RectTransform'
            }
        }
    }
    await session.post(url, headers=headers, json=add_rect)
    await asyncio.sleep(0.2)
    
    # Image
    add_image = {
        'jsonrpc': '2.0',
        'id': 105,
        'method': 'tools/call',
        'params': {
            'name': 'manage_components',
            'arguments': {
                'action': 'add',
                'target': button_name,
                'search_method': 'by_name',
                'component_type': 'UnityEngine.UI.Image'
            }
        }
    }
    await session.post(url, headers=headers, json=add_image)
    await asyncio.sleep(0.2)
    
    # Button
    add_button = {
        'jsonrpc': '2.0',
        'id': 106,
        'method': 'tools/call',
        'params': {
            'name': 'manage_components',
            'arguments': {
                'action': 'add',
                'target': button_name,
                'search_method': 'by_name',
                'component_type': 'UnityEngine.UI.Button'
            }
        }
    }
    await session.post(url, headers=headers, json=add_button)
    await asyncio.sleep(0.2)
    
    print("✅ 组件添加完成")
    
    # 设置RectTransform属性
    print(f"\n设置RectTransform属性...")
    
    async def set_property(prop_name, value):
        set_prop = {
            'jsonrpc': '2.0',
            'id': 200,
            'method': 'tools/call',
            'params': {
                'name': 'manage_components',
                'arguments': {
                    'action': 'set_property',
                    'search_method': 'by_name',
                    'target': button_name,
                    'component_type': 'RectTransform',
                    'property': prop_name,
                    'value': value
                }
            }
        }
        async with session.post(url, headers=headers, json=set_prop) as response:
            pass
    
    await set_property('anchorMin', {'x': 1, 'y': 1})
    await asyncio.sleep(0.2)
    await set_property('anchorMax', {'x': 1, 'y': 1})
    await asyncio.sleep(0.2)
    await set_property('anchoredPosition', {'x': -100, 'y': -50})
    await asyncio.sleep(0.2)
    await set_property('sizeDelta', {'x': 200, 'y': 75})
    
    print("✅ RectTransform属性设置完成")
    
    # 创建Text子对象
    print(f"\n创建Text子对象...")
    create_text = {
        'jsonrpc': '2.0',
        'id': 107,
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
        # 添加Text的RectTransform
        add_text_rect = {
            'jsonrpc': '2.0',
            'id': 108,
            'method': 'tools/call',
            'params': {
                'name': 'manage_components',
                'arguments': {
                    'action': 'add',
                    'target': str(text_id),
                    'search_method': 'by_id',
                    'component_type': 'RectTransform'
                }
            }
        }
        await session.post(url, headers=headers, json=add_text_rect)
        
        # 添加Text组件
        add_text_comp = {
            'jsonrpc': '2.0',
            'id': 109,
            'method': 'tools/call',
            'params': {
                'name': 'manage_components',
                'arguments': {
                    'action': 'add',
                    'target': str(text_id),
                    'search_method': 'by_id',
                    'component_type': 'UnityEngine.UI.Text'
                }
            }
        }
        await session.post(url, headers=headers, json=add_text_comp)
        
        # 设置Text属性
        await set_property('anchorMin', {'x': 0, 'y': 0})
        await set_property('anchorMax', {'x': 1, 'y': 1})
        await set_property('anchoredPosition', {'x': 0, 'y': 0})
        await set_property('sizeDelta', {'x': 0, 'y': 0})
        
        # 设置Text文字
        async def set_text_property(prop_name, value):
            set_prop = {
                'jsonrpc': '2.0',
                'id': 201,
                'method': 'tools/call',
                'params': {
                    'name': 'manage_components',
                    'arguments': {
                        'action': 'set_property',
                        'search_method': 'by_id',
                        'target': str(text_id),
                        'component_type': 'UnityEngine.UI.Text',
                        'property': prop_name,
                        'value': value
                    }
                }
            }
            async with session.post(url, headers=headers, json=set_prop) as response:
                pass
        
        await set_text_property('fontSize', 32)
        await set_text_property('text', button_text)
        
        print("✅ Text设置完成")
    
    # 保存场景
    print(f"\n保存{scene_name}...")
    save_scene = {
        'jsonrpc': '2.0',
        'id': 110,
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
                        print(f"✅ {scene_name}保存成功")
    
    print(f"\n🎉 {scene_name}中的{button_name}创建完成！")
    return True

async def main():
    url = 'http://127.0.0.1:8080/mcp'
    headers = {
        'Accept': 'application/json,text/event-stream',
        'Content-Type': 'application/json'
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 在所有场景中创建按钮 ===\n")
        
        # 初始化
        init_msg = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'initialize',
            'params': {
                'protocolVersion': '2024-11-05',
                'capabilities': {},
                'clientInfo': {'name': 'setup-all', 'version': '1.0.0'}
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
        
        # 在LevelScene中创建ReturnButton
        success1 = await setup_buttons_in_scene(session, headers, 'LevelScene', 'ReturnButton', '返回', url)
        
        # 在ResultScene中创建ResultLeaderboardButton
        success2 = await setup_buttons_in_scene(session, headers, 'ResultScene', 'ResultLeaderboardButton', '排行榜', url)
        
        print("\n" + "="*50)
        print("所有场景设置完成！")
        print("="*50)
        print("\n接下来需要手动完成：")
        print("1. 在Start场景中查看LeaderboardButton的Image使用的sprite")
        print("2. 将相同的sprite应用到LevelScene和ResultScene的按钮上")
        print("3. 在Unity编辑器中设置脚本中的按钮引用：")
        print("   - LevelScene: ReturnButton → LevelController.returnButton")
        print("   - ResultScene: ResultLeaderboardButton → ResultController.leaderboardButton")

if __name__ == '__main__':
    asyncio.run(main())
