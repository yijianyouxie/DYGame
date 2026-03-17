#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从头开始重新创建按钮和Text，确保所有关系正确
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

async def create_complete_button(session, url, headers, scene_name, build_index, button_name, button_text, sprite_path, font_path):
    """创建完整的按钮和Text"""
    print("\n" + "=" * 80)
    print(f"在 {scene_name} 创建 {button_name}")
    print("=" * 80)
    
    # 加载场景
    print(f"\n[1/12] 加载 {scene_name}...")
    result = await call_tool(session, url, headers, 'manage_scene', {
        'action': 'load',
        'build_index': build_index
    }, tool_id=100 + build_index)
    
    if not result or not result.get('success'):
        print(f"  ❌ 场景加载失败")
        return False
    print(f"  ✅ 场景加载成功")
    
    # 查找Canvas
    print(f"\n[2/12] 查找Canvas...")
    result = await call_tool(session, url, headers, 'find_gameobjects', {
        'search_term': 'Canvas',
        'search_method': 'by_name'
    }, tool_id=200 + build_index)
    
    if not result or not result.get('data', {}).get('instanceIDs'):
        print(f"  ❌ 未找到Canvas")
        return False
    
    canvas_id = str(result['data']['instanceIDs'][0])
    print(f"  ✅ Canvas ID: {canvas_id}")
    
    # 删除现有的按钮（如果存在）
    print(f"\n[3/12] 删除现有的 {button_name}...")
    result = await call_tool(session, url, headers, 'find_gameobjects', {
        'search_term': button_name,
        'search_method': 'by_name'
    }, tool_id=300 + build_index)
    
    if result and result.get('data', {}).get('instanceIDs'):
        btn_ids = result['data']['instanceIDs']
        for btn_id in btn_ids:
            del_result = await call_tool(session, url, headers, 'manage_gameobject', {
                'action': 'delete',
                'target': str(btn_id)
            }, tool_id=400 + build_index * 10)
            if del_result and del_result.get('success'):
                print(f"  ✅ 删除旧的按钮 ID: {btn_id}")
    
    # 创建按钮GameObject
    print(f"\n[4/12] 创建按钮GameObject: {button_name}...")
    result = await call_tool(session, url, headers, 'manage_gameobject', {
        'action': 'create',
        'name': button_name,
        'parent': canvas_id
    }, tool_id=500 + build_index)
    
    if not result or not result.get('success'):
        print(f"  ❌ 按钮创建失败")
        return False
    print(f"  ✅ 按钮创建成功")
    
    # 查找新创建的按钮
    await asyncio.sleep(0.3)
    result = await call_tool(session, url, headers, 'find_gameobjects', {
        'search_term': button_name,
        'search_method': 'by_name'
    }, tool_id=600 + build_index)
    
    if not result or not result.get('data', {}).get('instanceIDs'):
        print(f"  ❌ 未找到新创建的按钮")
        return False
    
    btn_id = str(result['data']['instanceIDs'][0])
    print(f"  ✅ 按钮ID: {btn_id}")
    
    # 添加RectTransform
    print(f"\n[5/12] 添加RectTransform...")
    result = await call_tool(session, url, headers, 'manage_components', {
        'action': 'add',
        'target': btn_id,
        'component_type': 'UnityEngine.RectTransform'
    }, tool_id=700 + build_index)
    if result and result.get('success'):
        print(f"  ✅ RectTransform已添加")
    
    # 设置RectTransform属性
    print(f"\n[6/12] 设置RectTransform属性...")
    rt_props = {
        'anchoredPosition': {'x': -20.0, 'y': -20.0},
        'sizeDelta': {'x': 200.0, 'y': 75.0},
        'anchorMin': {'x': 1.0, 'y': 1.0},
        'anchorMax': {'x': 1.0, 'y': 1.0},
        'pivot': {'x': 1.0, 'y': 1.0}
    }
    
    for prop_name, prop_value in rt_props.items():
        await call_tool(session, url, headers, 'manage_components', {
            'action': 'set_property',
            'target': btn_id,
            'component_type': 'UnityEngine.RectTransform',
            'property': prop_name,
            'value': prop_value
        }, tool_id=710 + build_index * 10 + list(rt_props.keys()).index(prop_name))
    print(f"  ✅ RectTransform属性已设置")
    
    # 添加Image组件
    print(f"\n[7/12] 添加Image组件...")
    result = await call_tool(session, url, headers, 'manage_components', {
        'action': 'add',
        'target': btn_id,
        'component_type': 'UnityEngine.UI.Image',
        'properties': {
            'sprite': sprite_path
        }
    }, tool_id=720 + build_index)
    if result and result.get('success'):
        print(f"  ✅ Image已添加 (sprite: {sprite_path})")
    
    # 添加Button组件
    print(f"\n[8/12] 添加Button组件...")
    result = await call_tool(session, url, headers, 'manage_components', {
        'action': 'add',
        'target': btn_id,
        'component_type': 'UnityEngine.UI.Button'
    }, tool_id=730 + build_index)
    if result and result.get('success'):
        print(f"  ✅ Button已添加")
    
    # 创建Text子对象（关键步骤：使用正确的parent）
    print(f"\n[9/12] 创建Text子对象（parent: {btn_id}）...")
    result = await call_tool(session, url, headers, 'manage_gameobject', {
        'action': 'create',
        'name': 'Text',
        'parent': btn_id
    }, tool_id=740 + build_index)
    
    if not result or not result.get('success'):
        print(f"  ❌ Text创建失败")
        return False
    print(f"  ✅ Text创建成功")
    
    # 查找新创建的Text（应该是最后一个）
    await asyncio.sleep(0.3)
    result = await call_tool(session, url, headers, 'find_gameobjects', {
        'search_term': 'Text',
        'search_method': 'by_name'
    }, tool_id=750 + build_index)
    
    if not result or not result.get('data', {}).get('instanceIDs'):
        print(f"  ❌ 未找到Text对象")
        return False
    
    text_ids = result['data']['instanceIDs']
    text_id = str(text_ids[-1])  # 最后一个应该是最新的
    print(f"  ✅ Text ID: {text_id}")
    
    # 添加RectTransform到Text
    print(f"\n[10/12] 添加RectTransform到Text...")
    result = await call_tool(session, url, headers, 'manage_components', {
        'action': 'add',
        'target': text_id,
        'component_type': 'UnityEngine.RectTransform'
    }, tool_id=760 + build_index)
    if result and result.get('success'):
        print(f"  ✅ Text的RectTransform已添加")
    
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
    print(f"  ✅ Text的RectTransform已设置")
    
    # 添加Text组件
    print(f"\n[11/12] 添加Text组件...")
    result = await call_tool(session, url, headers, 'manage_components', {
        'action': 'add',
        'target': text_id,
        'component_type': 'UnityEngine.UI.Text',
        'properties': {
            'text': button_text,
            'font': font_path,
            'fontSize': 32,
            'alignment': 4
        }
    }, tool_id=770 + build_index)
    if result and result.get('success'):
        print(f"  ✅ Text组件已添加: '{button_text}'")
    
    # 保存场景
    print(f"\n[12/12] 保存场景...")
    result = await call_tool(session, url, headers, 'manage_scene', {
        'action': 'save'
    }, tool_id=800 + build_index)
    if result and result.get('success'):
        print(f"  ✅ 场景保存成功")
    
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
        
        # 创建ResultScene的按钮
        success = await create_complete_button(
            session, url, headers, 
            'ResultScene', 2, 'ResultLeaderboardButton', 'Leaderboard',
            sprite_path, font_path
        )
        
        # 创建LevelScene的按钮
        success = await create_complete_button(
            session, url, headers, 
            'LevelScene', 1, 'ReturnButton', 'Return',
            sprite_path, font_path
        )
        
        print("\n" + "=" * 80)
        print("✅ 任务完成！")
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
