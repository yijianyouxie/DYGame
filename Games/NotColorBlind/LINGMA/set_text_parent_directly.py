#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接设置Text对象的父对象
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

async def fix_scene_text_parent(session, url, headers, scene_name, build_index, button_name):
    """修复场景中Text的父对象"""
    print("\n" + "=" * 80)
    print(f"处理 {scene_name}")
    print("=" * 80)
    
    # 加载场景
    print(f"\n加载 {scene_name}...")
    result = await call_tool(session, url, headers, 'manage_scene', {
        'action': 'load',
        'build_index': build_index
    }, tool_id=100)
    
    if not result or not result.get('success'):
        print(f"  ❌ 场景加载失败")
        return False
    
    print(f"  ✅ 场景加载成功")
    
    # 查找按钮
    print(f"\n查找 {button_name}...")
    result = await call_tool(session, url, headers, 'find_gameobjects', {
        'search_term': button_name,
        'search_method': 'by_name'
    }, tool_id=200)
    
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
    }, tool_id=300)
    
    if not result or not result.get('data', {}).get('instanceIDs'):
        print(f"  ❌ 未找到Text对象")
        return False
    
    text_ids = result['data']['instanceIDs']
    print(f"  找到 {len(text_ids)} 个Text对象: {text_ids}")
    
    # 找到有Text组件的Text对象
    print(f"\n查找有Text组件的Text对象...")
    for text_id in text_ids:
        # 使用get_hierarchy查看对象关系
        # 或者直接尝试将Text对象移动到按钮下
        
        print(f"\n尝试将 Text {text_id} 的父对象设置为 {button_name} ({btn_id})...")
        
        # 方法1: 使用manage_gameobject的modify action设置parent
        result = await call_tool(session, url, headers, 'manage_gameobject', {
            'action': 'modify',
            'target': str(text_id),
            'parent': btn_id
        }, tool_id=400 + text_ids.index(text_id))
        
        if result and result.get('success'):
            print(f"  ✅ 父对象设置成功")
        else:
            print(f"  ⚠️ 父对象设置失败: {result}")
    
    # 保存场景
    print(f"\n保存场景...")
    result = await call_tool(session, url, headers, 'manage_scene', {
        'action': 'save'
    }, tool_id=500)
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
        await fix_scene_text_parent(session, url, headers, 'ResultScene', 2, 'ResultLeaderboardButton')
        
        # 修复LevelScene
        await fix_scene_text_parent(session, url, headers, 'LevelScene', 1, 'ReturnButton')
        
        print("\n" + "=" * 80)
        print("✅ 任务完成！")
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
