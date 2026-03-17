#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
正确添加组件到按钮和Text对象
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

async def add_component(session, url, headers, target, component_type, properties=None):
    """添加组件到对象"""
    args = {
        'action': 'add',
        'target': target,
        'component_type': component_type
    }
    
    if properties:
        args['properties'] = properties
    
    result = await call_tool(session, url, headers, 'manage_components', args)
    return result

async def setup_button(session, url, headers, button_name, sprite_path, font_path, button_text):
    """设置按钮及其组件"""
    print(f"\n设置按钮: {button_name}")
    
    # 查找按钮
    print("  [1/8] 查找按钮...")
    result = await call_tool(session, url, headers, 'find_gameobjects', {
        'search_term': button_name,
        'search_method': 'by_name'
    }, tool_id=100)
    
    if not result or not result.get('data', {}).get('instanceIDs'):
        print(f"    ❌ 未找到 {button_name}")
        return False
    
    btn_id = str(result['data']['instanceIDs'][0])
    print(f"    按钮ID: {btn_id}")
    
    # 添加RectTransform
    print("  [2/8] 添加RectTransform...")
    result = await add_component(session, url, headers, btn_id, 'UnityEngine.RectTransform')
    if result and result.get('success'):
        print("    ✅ RectTransform已添加")
    else:
        print(f"    ⚠️ RectTransform添加失败: {result}")
    
    # 设置RectTransform属性
    print("  [3/8] 设置RectTransform属性...")
    rt_props = {
        'anchoredPosition': {'x': -20.0, 'y': -20.0},
        'sizeDelta': {'x': 200.0, 'y': 75.0},
        'anchorMin': {'x': 1.0, 'y': 1.0},
        'anchorMax': {'x': 1.0, 'y': 1.0},
        'pivot': {'x': 1.0, 'y': 1.0}
    }
    
    for prop_name, prop_value in rt_props.items():
        result = await call_tool(session, url, headers, 'manage_components', {
            'action': 'set_property',
            'target': btn_id,
            'component_type': 'UnityEngine.RectTransform',
            'property': prop_name,
            'value': prop_value
        })
    print("    ✅ RectTransform属性已设置")
    
    # 添加Image组件
    print("  [4/8] 添加Image组件...")
    result = await add_component(session, url, headers, btn_id, 'UnityEngine.UI.Image', {
        'sprite': sprite_path
    })
    if result and result.get('success'):
        print(f"    ✅ Image已添加，sprite: {sprite_path}")
    else:
        print(f"    ⚠️ Image添加失败: {result}")
    
    # 添加Button组件
    print("  [5/8] 添加Button组件...")
    result = await add_component(session, url, headers, btn_id, 'UnityEngine.UI.Button', {
        'transition': 1
    })
    if result and result.get('success'):
        print("    ✅ Button已添加")
    else:
        print(f"    ⚠️ Button添加失败: {result}")
    
    # 创建Text子对象
    print("  [6/8] 创建Text子对象...")
    result = await call_tool(session, url, headers, 'manage_gameobject', {
        'action': 'create',
        'name': 'Text',
        'parent': btn_id
    })
    
    if not result or not result.get('success'):
        print("    ❌ Text创建失败")
        return False
    
    # 查找Text对象
    result = await call_tool(session, url, headers, 'find_gameobjects', {
        'search_term': 'Text',
        'search_method': 'by_name'
    }, tool_id=101)
    
    if not result or not result.get('data', {}).get('instanceIDs'):
        print("    ❌ 未找到Text对象")
        return False
    
    text_ids = result['data']['instanceIDs']
    text_id = str(text_ids[-1])
    print(f"    Text ID: {text_id}")
    
    # 添加RectTransform到Text
    print("  [7/8] 添加RectTransform到Text...")
    result = await add_component(session, url, headers, text_id, 'UnityEngine.RectTransform')
    if result and result.get('success'):
        print("    ✅ Text的RectTransform已添加")
    
    # 设置Text的RectTransform为全拉伸
    await call_tool(session, url, headers, 'manage_components', {
        'action': 'set_property',
        'target': text_id,
        'component_type': 'UnityEngine.RectTransform',
        'property': 'anchorMin',
        'value': {'x': 0, 'y': 0}
    })
    await call_tool(session, url, headers, 'manage_components', {
        'action': 'set_property',
        'target': text_id,
        'component_type': 'UnityEngine.RectTransform',
        'property': 'anchorMax',
        'value': {'x': 1, 'y': 1}
    })
    await call_tool(session, url, headers, 'manage_components', {
        'action': 'set_property',
        'target': text_id,
        'component_type': 'UnityEngine.RectTransform',
        'property': 'pivot',
        'value': {'x': 0.5, 'y': 0.5}
    })
    await call_tool(session, url, headers, 'manage_components', {
        'action': 'set_property',
        'target': text_id,
        'component_type': 'UnityEngine.RectTransform',
        'property': 'anchoredPosition',
        'value': {'x': 0, 'y': 0}
    })
    await call_tool(session, url, headers, 'manage_components', {
        'action': 'set_property',
        'target': text_id,
        'component_type': 'UnityEngine.RectTransform',
        'property': 'sizeDelta',
        'value': {'x': 0, 'y': 0}
    })
    
    # 添加Text组件
    print("  [8/8] 添加Text组件...")
    result = await add_component(session, url, headers, text_id, 'UnityEngine.UI.Text', {
        'text': button_text,
        'font': font_path,
        'fontSize': 32,
        'alignment': 4  # Center
    })
    if result and result.get('success'):
        print(f"    ✅ Text组件已添加: {button_text}")
    else:
        print(f"    ⚠️ Text组件添加失败: {result}")
    
    return True

async def main():
    url = "http://127.0.0.1:8080/mcp"
    sprite_path = "Assets/Textures/bg_btn.png"
    font_path = "Assets/Font/FZLTH-GBK.TTF"
    
    async with aiohttp.ClientSession() as session:
        # 初始化session
        print("初始化MCP session...")
        session_id = await init_session(session, url)
        if not session_id:
            print("❌ 初始化失败")
            return
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream',
            'mcp-session-id': session_id
        }
        
        print(f"✅ MCP连接成功")
        await asyncio.sleep(1)
        
        # 设置ResultScene
        print("\n" + "=" * 80)
        print("处理 ResultScene")
        print("=" * 80)
        
        print("\n加载ResultScene...")
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'load',
            'build_index': 2
        }, tool_id=200)
        
        if result and result.get('success'):
            print("✅ ResultScene加载成功")
            success = await setup_button(session, url, headers, 'ResultLeaderboardButton', sprite_path, font_path, 'Leaderboard')
            
            if success:
                print("\n保存ResultScene...")
                result = await call_tool(session, url, headers, 'manage_scene', {'action': 'save'})
                if result and result.get('success'):
                    print("✅ ResultScene保存成功")
        
        # 设置LevelScene
        print("\n" + "=" * 80)
        print("处理 LevelScene")
        print("=" * 80)
        
        print("\n加载LevelScene...")
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'load',
            'build_index': 1
        }, tool_id=300)
        
        if result and result.get('success'):
            print("✅ LevelScene加载成功")
            success = await setup_button(session, url, headers, 'ReturnButton', sprite_path, font_path, 'Return')
            
            if success:
                print("\n保存LevelScene...")
                result = await call_tool(session, url, headers, 'manage_scene', {'action': 'save'})
                if result and result.get('success'):
                    print("✅ LevelScene保存成功")
        
        print("\n" + "=" * 80)
        print("✅ 任务完成！")
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
