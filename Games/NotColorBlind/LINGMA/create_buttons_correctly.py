#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
正确地在ResultScene和LevelScene中创建按钮，并获取Start场景的sprite
"""

import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def init_session(session, url):
    base_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream'
    }
    
    init_message = {
        'jsonrpc': '2.0',
        'id': 0,
        'method': 'initialize',
        'params': {
            'protocolVersion': '2024-11-05',
            'capabilities': {},
            'clientInfo': {'name': 'python-script', 'version': '1.0'}
        }
    }
    
    async with session.post(url, headers=base_headers, json=init_message) as response:
        session_id = response.headers.get('mcp-session-id')
        return session_id

async def call_tool(session, url, headers, tool_name, arguments, tool_id=1):
    """调用MCP工具并返回结果"""
    request = {
        'jsonrpc': '2.0',
        'id': tool_id,
        'method': 'tools/call',
        'params': {
            'name': tool_name,
            'arguments': arguments
        }
    }
    
    async with session.post(url, headers=headers, json=request) as response:
        text = await response.text()
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('data:'):
                data = json.loads(line[5:])
                structured = data.get('result', {}).get('structuredContent', {})
                return structured
        return {}

async def read_resource(session, url, headers, uri):
    """通过resource读取数据"""
    request = {
        'jsonrpc': '2.0',
        'id': 100,
        'method': 'resources/read',
        'params': {
            'uri': uri
        }
    }
    
    async with session.post(url, headers=headers, json=request) as response:
        text = await response.text()
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('data:'):
                data = json.loads(line[5:])
                return data
        return {}

async def delete_all_buttons_by_name(session, url, headers, button_name):
    """删除所有同名按钮"""
    find_result = await call_tool(session, url, headers, 'find_gameobjects', {
        'search_term': button_name,
        'search_method': 'by_name'
    }, tool_id=10)
    
    if find_result:
        existing_ids = find_result.get('data', {}).get('instanceIDs', [])
        if existing_ids:
            print(f"找到 {len(existing_ids)} 个{button_name}，删除...")
            for btn_id in existing_ids:
                result = await call_tool(session, url, headers, 'manage_gameobject', {
                    'action': 'delete',
                    'target': str(btn_id)
                }, tool_id=11)
                if result and result.get('success'):
                    print(f"✅ 删除成功: ID={btn_id}")
            await asyncio.sleep(0.5)
    
    return True

async def create_button(session, url, headers, button_name, button_text):
    """创建按钮"""
    
    print(f"\n{'='*60}")
    print(f"创建按钮: {button_name}")
    print('='*60)
    
    # 删除已存在的
    await delete_all_buttons_by_name(session, url, headers, button_name)
    
    # 创建GameObject
    print(f"[1/8] 创建GameObject...")
    create_result = await call_tool(session, url, headers, 'manage_gameobject', {
        'action': 'create',
        'name': button_name,
        'parent': 'Canvas'
    }, tool_id=12)
    
    if not create_result or not create_result.get('success'):
        print(f"❌ 创建失败: {create_result}")
        return False
    
    button_id = create_result.get('data', {}).get('instanceID')
    if not button_id:
        print(f"❌ 未返回instanceID")
        return False
    
    print(f"✅ 创建成功: ID={button_id}")
    await asyncio.sleep(0.3)
    
    # 添加RectTransform
    print(f"[2/8] 添加RectTransform...")
    result = await call_tool(session, url, headers, 'manage_components', {
        'action': 'add',
        'target': button_name,
        'search_method': 'by_name',
        'component_type': 'RectTransform'
    }, tool_id=13)
    if result and result.get('success'):
        print(f"✅ RectTransform添加成功")
    await asyncio.sleep(0.3)
    
    # 添加Image
    print(f"[3/8] 添加Image...")
    result = await call_tool(session, url, headers, 'manage_components', {
        'action': 'add',
        'target': button_name,
        'search_method': 'by_name',
        'component_type': 'UnityEngine.UI.Image'
    }, tool_id=14)
    if result and result.get('success'):
        print(f"✅ Image添加成功")
    await asyncio.sleep(0.3)
    
    # 添加Button
    print(f"[4/8] 添加Button...")
    result = await call_tool(session, url, headers, 'manage_components', {
        'action': 'add',
        'target': button_name,
        'search_method': 'by_name',
        'component_type': 'UnityEngine.UI.Button'
    }, tool_id=15)
    if result and result.get('success'):
        print(f"✅ Button添加成功")
    await asyncio.sleep(0.3)
    
    # 设置RectTransform属性
    print(f"[5/8] 设置RectTransform属性...")
    
    await call_tool(session, url, headers, 'manage_components', {
        'action': 'set_property',
        'target': button_name,
        'search_method': 'by_name',
        'component_type': 'RectTransform',
        'property': 'anchorMin',
        'value': {'x': 1, 'y': 1}
    }, tool_id=16)
    await asyncio.sleep(0.2)
    
    await call_tool(session, url, headers, 'manage_components', {
        'action': 'set_property',
        'target': button_name,
        'search_method': 'by_name',
        'component_type': 'RectTransform',
        'property': 'anchorMax',
        'value': {'x': 1, 'y': 1}
    }, tool_id=17)
    await asyncio.sleep(0.2)
    
    await call_tool(session, url, headers, 'manage_components', {
        'action': 'set_property',
        'target': button_name,
        'search_method': 'by_name',
        'component_type': 'RectTransform',
        'property': 'anchoredPosition',
        'value': {'x': -100, 'y': -50}
    }, tool_id=18)
    await asyncio.sleep(0.2)
    
    await call_tool(session, url, headers, 'manage_components', {
        'action': 'set_property',
        'target': button_name,
        'search_method': 'by_name',
        'component_type': 'RectTransform',
        'property': 'sizeDelta',
        'value': {'x': 200, 'y': 75}
    }, tool_id=19)
    await asyncio.sleep(0.2)
    
    await call_tool(session, url, headers, 'manage_components', {
        'action': 'set_property',
        'target': button_name,
        'search_method': 'by_name',
        'component_type': 'RectTransform',
        'property': 'pivot',
        'value': {'x': 0.5, 'y': 0.5}
    }, tool_id=20)
    
    print(f"✅ RectTransform属性设置完成")
    await asyncio.sleep(0.3)
    
    # 创建Text子对象
    print(f"[6/8] 创建Text子对象...")
    text_result = await call_tool(session, url, headers, 'manage_gameobject', {
        'action': 'create',
        'name': 'Text',
        'parent': f'Canvas/{button_name}'
    }, tool_id=21)
    
    text_id = None
    if text_result and text_result.get('success'):
        text_id = text_result.get('data', {}).get('instanceID')
        print(f"✅ Text对象创建成功: ID={text_id}")
    
    await asyncio.sleep(0.3)
    
    # 为Text添加组件
    if text_id:
        await call_tool(session, url, headers, 'manage_components', {
            'action': 'add',
            'target': str(text_id),
            'search_method': 'by_id',
            'component_type': 'RectTransform'
        }, tool_id=22)
        
        print(f"[7/8] 添加Text组件...")
        result = await call_tool(session, url, headers, 'manage_components', {
            'action': 'add',
            'target': str(text_id),
            'search_method': 'by_id',
            'component_type': 'UnityEngine.UI.Text',
            'properties': {
                'text': button_text,
                'fontSize': 32,
                'alignment': 4
            }
        }, tool_id=23)
        
        if result and result.get('success'):
            print(f"✅ Text组件添加成功: '{button_text}'")
        
        # 设置Text的RectTransform
        print(f"[8/8] 设置Text的RectTransform...")
        await call_tool(session, url, headers, 'manage_components', {
            'action': 'set_property',
            'target': str(text_id),
            'search_method': 'by_id',
            'component_type': 'RectTransform',
            'property': 'anchorMin',
            'value': {'x': 0, 'y': 0}
        }, tool_id=24)
        await asyncio.sleep(0.2)
        
        await call_tool(session, url, headers, 'manage_components', {
            'action': 'set_property',
            'target': str(text_id),
            'search_method': 'by_id',
            'component_type': 'RectTransform',
            'property': 'anchorMax',
            'value': {'x': 1, 'y': 1}
        }, tool_id=25)
        await asyncio.sleep(0.2)
        
        await call_tool(session, url, headers, 'manage_components', {
            'action': 'set_property',
            'target': str(text_id),
            'search_method': 'by_id',
            'component_type': 'RectTransform',
            'property': 'offsetMin',
            'value': {'x': 0, 'y': 0}
        }, tool_id=26)
        await asyncio.sleep(0.2)
        
        await call_tool(session, url, headers, 'manage_components', {
            'action': 'set_property',
            'target': str(text_id),
            'search_method': 'by_id',
            'component_type': 'RectTransform',
            'property': 'offsetMax',
            'value': {'x': 0, 'y': 0}
        }, tool_id=27)
        
        print(f"✅ Text的RectTransform设置完成")
    
    return True

async def get_start_sprite(session, url, headers):
    """获取Start场景LeaderboardButton的sprite信息"""
    print("\n[1/5] 获取Start场景LeaderboardButton的sprite...")
    
    # 查找LeaderboardButton
    find_result = await call_tool(session, url, headers, 'find_gameobjects', {
        'search_term': 'LeaderboardButton',
        'search_method': 'by_name'
    }, tool_id=30)
    
    button_id = None
    if find_result:
        ids = find_result.get('data', {}).get('instanceIDs', [])
        if ids:
            button_id = ids[0]
            print(f"✅ 找到LeaderboardButton: ID={button_id}")
    
    if not button_id:
        print("❌ 未找到LeaderboardButton")
        return None
    
    await asyncio.sleep(0.5)
    
    # 通过resource读取Image组件
    print(f"[2/5] 读取Image组件...")
    resource_uri = f'mcpforunity://scene/gameobject/{button_id}/component/UnityEngine.UI.Image'
    resource_result = await read_resource(session, url, headers, resource_uri)
    
    print(f"Resource结果: {json.dumps(resource_result, indent=2)}")
    
    sprite_id = None
    if resource_result:
        result = resource_result.get('result', {})
        content = result.get('contents', [])
        if content:
            text_content = content[0].get('text', '')
            try:
                data = json.loads(text_content)
                props = data.get('properties', {})
                sprite = props.get('sprite', {})
                sprite_id = sprite.get('instanceID')
                print(f"✅ Sprite ID: {sprite_id}")
                print(f"  Sprite Name: {sprite.get('name', 'N/A')}")
            except Exception as e:
                print(f"解析失败: {e}")
    
    return sprite_id

async def apply_sprite(session, url, headers, button_name, sprite_id):
    """应用sprite到按钮"""
    if not sprite_id:
        print(f"⚠️ 没有sprite ID，跳过应用")
        return
    
    print(f"\n应用sprite到 {button_name}...")
    result = await call_tool(session, url, headers, 'manage_components', {
        'action': 'set_property',
        'target': button_name,
        'search_method': 'by_name',
        'component_type': 'UnityEngine.UI.Image',
        'property': 'sprite',
        'value': sprite_id
    }, tool_id=40)
    
    if result and result.get('success'):
        print(f"✅ Sprite应用成功")
    else:
        print(f"⚠️ Sprite应用: {result}")

async def main():
    url = 'http://127.0.0.1:8080/mcp'
    base_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream'
    }
    
    print("="*70)
    print("正确创建按钮并获取sprite")
    print("="*70)
    
    async with aiohttp.ClientSession() as session:
        session_id = await init_session(session, url)
        if not session_id:
            print("❌ 无法获取session ID")
            return
        
        print(f"✅ Session ID: {session_id}")
        headers = {**base_headers, 'mcp-session-id': session_id}
        
        await session.post(url, headers=headers, json={
            'jsonrpc': '2.0',
            'method': 'notifications/initialized'
        })
        
        await asyncio.sleep(0.5)
        
        # 步骤1: 清理StartScene的错误按钮
        print("\n" + "="*70)
        print("步骤1: 清理StartScene的错误按钮")
        print("="*70)
        
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'load',
            'scene_name': 'StartScene'
        }, tool_id=1)
        
        if result and result.get('success'):
            print("✅ StartScene加载成功")
        
        await asyncio.sleep(3)  # 增加等待时间
        
        print("\n清理StartScene中的错误按钮...")
        await delete_all_buttons_by_name(session, url, headers, 'ReturnButton')
        await delete_all_buttons_by_name(session, url, headers, 'ResultLeaderboardButton')
        
        # 获取sprite
        sprite_id = await get_start_sprite(session, url, headers)
        
        print("\n保存StartScene...")
        await call_tool(session, url, headers, 'manage_scene', {
            'action': 'save'
        }, tool_id=50)
        print("✅ StartScene保存成功")
        
        await asyncio.sleep(2)
        
        # 步骤2: 在ResultScene创建按钮
        print("\n" + "="*70)
        print("步骤2: 在ResultScene创建排行榜按钮")
        print("="*70)
        
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'load',
            'scene_name': 'ResultScene'
        }, tool_id=60)
        
        if result and result.get('success'):
            print("✅ ResultScene加载成功")
        
        await asyncio.sleep(3)
        
        success = await create_button(session, url, headers, 'ResultLeaderboardButton', '排行榜')
        
        if success and sprite_id:
            await apply_sprite(session, url, headers, 'ResultLeaderboardButton', sprite_id)
        
        if success:
            print("\n保存ResultScene...")
            result = await call_tool(session, url, headers, 'manage_scene', {
                'action': 'save'
            }, tool_id=70)
            if result and result.get('success'):
                print("✅ ResultScene保存成功")
        
        await asyncio.sleep(2)
        
        # 步骤3: 在LevelScene创建按钮
        print("\n" + "="*70)
        print("步骤3: 在LevelScene创建返回按钮")
        print("="*70)
        
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'load',
            'scene_name': 'LevelScene'
        }, tool_id=80)
        
        if result and result.get('success'):
            print("✅ LevelScene加载成功")
        
        await asyncio.sleep(3)
        
        success = await create_button(session, url, headers, 'ReturnButton', '返回')
        
        if success and sprite_id:
            await apply_sprite(session, url, headers, 'ReturnButton', sprite_id)
        
        if success:
            print("\n保存LevelScene...")
            result = await call_tool(session, url, headers, 'manage_scene', {
                'action': 'save'
            }, tool_id=90)
            if result and result.get('success'):
                print("✅ LevelScene保存成功")
        
        print("\n" + "="*70)
        print("✅ 所有操作完成!")
        print("="*70)

if __name__ == '__main__':
    asyncio.run(main())
