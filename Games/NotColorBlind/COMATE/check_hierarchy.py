#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细检查场景层级结构
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

async def get_children(session, headers, parent_id, depth=0, max_depth=3):
    """递归获取子对象"""
    indent = "  " * depth
    
    # 使用resource API获取子对象
    url = f'mcpforunity://scene/gameobject/{parent_id}/children'
    call_msg = {'jsonrpc': '2.0', 'id': 1, 'method': 'resources/read', 'params': {'uri': url}}
    
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
                            result = json.loads(text)
                            items = result.get('data', {}).get('items', [])
                            for item in items:
                                name = item.get('name', 'unknown')
                                iid = item.get('instanceID', 0)
                                components = item.get('componentTypes', [])
                                child_count = item.get('childCount', 0)
                                
                                # 检查是否有Button组件
                                has_button = any('Button' in str(c) for c in components)
                                button_marker = " [BUTTON]" if has_button else ""
                                
                                print(f"{indent}- {name}{button_marker}")
                                print(f"{indent}  组件: {components}")
                                
                                if child_count > 0 and depth < max_depth:
                                    await get_children(session, headers, iid, depth+1, max_depth)
                        except:
                            pass
                    break

async def check_scene(session, headers, scene_name):
    """检查场景"""
    print(f"\n{'='*60}")
    print(f"场景: {scene_name}")
    print('='*60)
    
    # 加载场景
    await call_tool(session, headers, 'manage_scene', {'action': 'load', 'name': scene_name}, 1)
    await asyncio.sleep(0.3)
    
    # 获取根对象
    result = await call_tool(session, headers, 'manage_scene', {'action': 'get_hierarchy'}, 2)
    if result.get('success'):
        items = result.get('data', {}).get('items', [])
        for item in items:
            name = item.get('name')
            iid = item.get('instanceID')
            components = item.get('componentTypes', [])
            child_count = item.get('childCount', 0)
            print(f"\n根对象: {name}")
            print(f"  组件: {components}")
            print(f"  子对象数: {child_count}")
            
            if child_count > 0:
                await get_children(session, headers, iid, 1, 3)

async def main():
    async with aiohttp.ClientSession() as session:
        session_id, headers = await init_mcp_session(session)
        print(f"Session ID: {session_id}")
        
        for scene in ['Start', 'LevelScene', 'ResultScene']:
            await check_scene(session, headers, scene)
            await asyncio.sleep(0.5)

if __name__ == '__main__':
    asyncio.run(main())
