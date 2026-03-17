#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细检查Canvas下的所有子对象
"""
import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

MCP_URL = 'http://127.0.0.1:8080/mcp'

async def init_mcp_session(session):
    headers = {
        'Accept': 'application/json,text/event-stream',
        'Content-Type': 'application/json'
    }
    init_msg = {
        'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
        'params': {'protocolVersion': '2024-11-05', 'capabilities': {}, 'clientInfo': {'name': 'check', 'version': '1.0'}}
    }
    session_id = None
    async with session.post(MCP_URL, headers=headers, json=init_msg) as r:
        session_id = r.headers.get('mcp-session-id')
        async for line in r.content:
            if line.decode().strip().startswith('data:'): break
    if session_id:
        headers['mcp-session-id'] = session_id
        await session.post(MCP_URL, headers=headers, json={'jsonrpc': '2.0', 'method': 'notifications/initialized', 'params': {}})
    return session_id, headers

async def call_tool(session, headers, tool_name, arguments, request_id=1):
    call_msg = {'jsonrpc': '2.0', 'id': request_id, 'method': 'tools/call', 'params': {'name': tool_name, 'arguments': arguments}}
    result = None
    async with session.post(MCP_URL, headers=headers, json=call_msg) as r:
        if r.status == 200:
            async for line in r.content:
                line_text = line.decode().strip()
                if line_text.startswith('data:'):
                    data = json.loads(line_text[5:])
                    result = data.get('result', {}).get('structuredContent', {})
                    break
    return result

async def read_resource(session, headers, uri):
    """读取资源"""
    call_msg = {'jsonrpc': '2.0', 'id': 1, 'method': 'resources/read', 'params': {'uri': uri}}
    async with session.post(MCP_URL, headers=headers, json=call_msg) as r:
        if r.status == 200:
            async for line in r.content:
                line_text = line.decode().strip()
                if line_text.startswith('data:'):
                    data = json.loads(line_text[5:])
                    contents = data.get('result', {}).get('contents', [])
                    if contents:
                        text = contents[0].get('text', '{}')
                        try:
                            return json.loads(text)
                        except:
                            return {}
    return {}

async def print_hierarchy(session, headers, obj_id, depth=0, max_depth=5):
    """打印层级结构"""
    indent = "  " * depth
    
    # 获取对象详情
    result = await read_resource(session, headers, f'mcpforunity://scene/gameobject/{obj_id}')
    if not result.get('success'):
        return
    
    data = result.get('data', {})
    name = data.get('name', 'unknown')
    components = data.get('componentTypes', [])
    
    # 检查Button
    has_button = any('Button' in str(c) for c in components)
    button_marker = " [BUTTON]" if has_button else ""
    
    print(f"{indent}{name}{button_marker}")
    if has_button:
        print(f"{indent}  组件: {components}")
    
    # 获取子对象
    children_result = await read_resource(session, headers, f'mcpforunity://scene/gameobject/{obj_id}/children')
    if children_result.get('success'):
        items = children_result.get('data', {}).get('items', [])
        for item in items:
            child_id = item.get('instanceID')
            if depth < max_depth:
                await print_hierarchy(session, headers, child_id, depth+1, max_depth)

async def check_scene(session, headers, scene_name):
    """检查场景"""
    print(f"\n{'='*60}")
    print(f"场景: {scene_name}")
    print('='*60)
    
    # 加载场景
    await call_tool(session, headers, 'manage_scene', {'action': 'load', 'name': scene_name}, 1)
    await asyncio.sleep(0.5)
    
    # 获取根对象
    result = await call_tool(session, headers, 'manage_scene', {
        'action': 'get_hierarchy',
        'max_depth': 5,
        'max_children_per_node': 100
    }, 2)
    
    if result.get('success'):
        items = result.get('data', {}).get('items', [])
        for item in items:
            iid = item.get('instanceID')
            await print_hierarchy(session, headers, iid, 0, 5)

async def main():
    async with aiohttp.ClientSession() as session:
        session_id, headers = await init_mcp_session(session)
        print(f"Session ID: {session_id}")
        
        for scene in ['Start', 'LevelScene', 'ResultScene']:
            await check_scene(session, headers, scene)
            await asyncio.sleep(0.5)

if __name__ == '__main__':
    asyncio.run(main())
