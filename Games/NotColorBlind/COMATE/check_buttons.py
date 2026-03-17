#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查各场景中的按钮配置情况
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

async def check_scene_buttons(session, headers, scene_name):
    """检查场景中的按钮配置"""
    print(f"\n{'='*60}")
    print(f"检查场景: {scene_name}")
    print('='*60)
    
    # 加载场景
    result = await call_tool(session, headers, 'manage_scene', {'action': 'load', 'name': scene_name}, 1)
    await asyncio.sleep(0.3)
    
    # 获取场景层级
    result = await call_tool(session, headers, 'manage_scene', {'action': 'get_hierarchy'}, 2)
    
    if not result.get('success'):
        print(f"获取层级失败: {result}")
        return
    
    items = result.get('data', {}).get('items', [])
    print(f"\n场景根对象: {[i['name'] for i in items]}")
    
    # 查找Button类型的对象
    result = await call_tool(session, headers, 'find_gameobjects', {
        'search_term': 'Button',
        'search_method': 'by_component'
    }, 3)
    
    if result.get('success'):
        button_ids = result.get('data', {}).get('instanceIDs', [])
        print(f"\n找到 {len(button_ids)} 个按钮对象")
        
        for bid in button_ids:
            # 获取按钮详情
            result = await call_tool(session, headers, 'find_gameobjects', {
                'search_term': str(bid),
                'search_method': 'by_id'
            }, 4)
            if result.get('success'):
                items = result.get('data', {}).get('items', [])
                if items:
                    btn = items[0]
                    print(f"  - {btn['name']} (ID: {bid})")
    
    # 查找LeaderboardUI
    result = await call_tool(session, headers, 'find_gameobjects', {
        'search_term': 'Leaderboard',
        'search_method': 'by_name'
    }, 5)
    
    if result.get('success'):
        lb_ids = result.get('data', {}).get('instanceIDs', [])
        if lb_ids:
            print(f"\n找到排行榜相关对象: {len(lb_ids)} 个")
            for lid in lb_ids:
                result = await call_tool(session, headers, 'find_gameobjects', {
                    'search_term': str(lid),
                    'search_method': 'by_id'
                }, 6)
                if result.get('success'):
                    items = result.get('data', {}).get('items', [])
                    if items:
                        print(f"  - {items[0]['name']} (ID: {lid})")

async def main():
    async with aiohttp.ClientSession() as session:
        session_id, headers = await init_mcp_session(session)
        print(f"Session ID: {session_id}")
        
        # 检查各场景
        for scene in ['Start', 'LevelScene', 'ResultScene']:
            await check_scene_buttons(session, headers, scene)
            await asyncio.sleep(0.5)

if __name__ == '__main__':
    asyncio.run(main())
