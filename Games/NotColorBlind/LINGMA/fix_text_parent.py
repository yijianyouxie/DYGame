#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复Text对象的父对象关系
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

async def fix_scene_text(session, url, headers, scene_name, build_index, button_name, button_text):
    """修复场景中的Text对象"""
    print("\n" + "=" * 80)
    print(f"处理 {scene_name}")
    print("=" * 80)
    
    # 加载场景
    print(f"\n加载 {scene_name}...")
    result = await call_tool(session, url, headers, 'manage_scene', {
        'action': 'load',
        'build_index': build_index
    }, tool_id=100 + build_index)
    
    if not result or not result.get('success'):
        print(f"  ❌ 场景加载失败")
        return False
    
    print(f"  ✅ 场景加载成功")
    
    # 查找按钮
    print(f"\n查找 {button_name}...")
    result = await call_tool(session, url, headers, 'find_gameobjects', {
        'search_term': button_name,
        'search_method': 'by_name'
    }, tool_id=200 + build_index * 10)
    
    if not result or not result.get('data', {}).get('instanceIDs'):
        print(f"  ❌ 未找到 {button_name}")
        return False
    
    btn_id = str(result['data']['instanceIDs'][0])
    print(f"  ✅ 按钮ID: {btn_id}")
    
    # 查找所有Text对象
    print(f"\n查找Text对象...")
    result = await call_tool(session, url, headers, 'find_gameobjects', {
        'search_term': 'Text',
        'search_method': 'by_name'
    }, tool_id=300 + build_index * 10)
    
    if not result or not result.get('data', {}).get('instanceIDs'):
        print(f"  ❌ 未找到Text对象")
        return False
    
    text_ids = result['data']['instanceIDs']
    print(f"  找到 {len(text_ids)} 个Text对象")
    
    # 删除所有现有的Text对象（因为它们可能不是按钮的子对象）
    print(f"\n删除现有的Text对象...")
    for text_id in text_ids:
        result = await call_tool(session, url, headers, 'manage_gameobject', {
            'action': 'delete',
            'target': str(text_id)
        }, tool_id=400 + build_index * 100 + text_ids.index(text_id))
        if result and result.get('success'):
            print(f"  ✅ 删除 Text ID: {text_id}")
    
    # 在按钮下创建新的Text对象
    print(f"\n在按钮下创建新的Text对象...")
    result = await call_tool(session, url, headers, 'manage_gameobject', {
        'action': 'create',
        'name': 'Text',
        'parent': btn_id
    }, tool_id=500 + build_index)
    
    if not result or not result.get('success'):
        print(f"  ❌ Text创建失败")
        return False
    
    print(f"  ✅ Text创建成功")
    
    # 查找新创建的Text对象
    await asyncio.sleep(0.5)
    result = await call_tool(session, url, headers, 'find_gameobjects', {
        'search_term': 'Text',
        'search_method': 'by_name'
    }, tool_id=600 + build_index)
    
    if not result or not result.get('data', {}).get('instanceIDs'):
        print(f"  ❌ 未找到新创建的Text对象")
        return False
    
    text_ids = result['data']['instanceIDs']
    text_id = str(text_ids[-1])  # 最新的一个
    print(f"  ✅ 新Text ID: {text_id}")
    
    # 添加RectTransform
    print(f"\n添加RectTransform...")
    result = await call_tool(session, url, headers, 'manage_components', {
        'action': 'add',
        'target': text_id,
        'component_type': 'UnityEngine.RectTransform'
    }, tool_id=700 + build_index)
    if result and result.get('success'):
        print(f"  ✅ RectTransform已添加")
    
    # 设置RectTransform为全拉伸
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
    print(f"  ✅ RectTransform已设置")
    
    # 添加Text组件
    print(f"\n添加Text组件...")
    result = await call_tool(session, url, headers, 'manage_components', {
        'action': 'add',
        'target': text_id,
        'component_type': 'UnityEngine.UI.Text',
        'properties': {
            'text': button_text,
            'font': 'Assets/Font/FZLTH-GBK.TTF',
            'fontSize': 32,
            'alignment': 4
        }
    }, tool_id=800 + build_index)
    if result and result.get('success'):
        print(f"  ✅ Text组件已添加: {button_text}")
    
    # 保存场景
    print(f"\n保存场景...")
    result = await call_tool(session, url, headers, 'manage_scene', {
        'action': 'save'
    }, tool_id=900 + build_index)
    if result and result.get('success'):
        print(f"  ✅ 场景保存成功")
    
    return True

async def main():
    url = "http://127.0.0.1:8080/mcp"
    
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
        
        # 修复ResultScene
        success = await fix_scene_text(session, url, headers, 'ResultScene', 2, 'ResultLeaderboardButton', 'Leaderboard')
        
        # 修复LevelScene
        success = await fix_scene_text(session, url, headers, 'LevelScene', 1, 'ReturnButton', 'Return')
        
        print("\n" + "=" * 80)
        print("✅ 任务完成！")
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
