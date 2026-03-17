#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证场景配置
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
        'params': {'protocolVersion': '2024-11-05', 'capabilities': {}, 'clientInfo': {'name': 'verify', 'version': '1.0'}}
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

async def verify_scene(session, headers, scene_name, build_index, expected_config):
    """验证场景配置"""
    print(f"\n{'='*60}")
    print(f"验证 {scene_name} (buildIndex={build_index})")
    print('='*60)
    
    # 加载场景
    result = await call_tool(session, headers, 'manage_scene', {
        'action': 'load',
        'build_index': build_index
    }, 1)
    
    if not result.get('success'):
        print(f"加载失败: {result}")
        return False
    
    await asyncio.sleep(0.3)
    
    # 查找Canvas
    result = await call_tool(session, headers, 'find_gameobjects', {
        'search_term': 'Canvas',
        'search_method': 'by_name'
    }, 2)
    
    if result.get('success') and result.get('data', {}).get('instanceIDs'):
        canvas_id = result['data']['instanceIDs'][0]
        print(f"Canvas ID: {canvas_id}")
        
        # 获取Canvas组件信息
        components_result = await read_resource(session, headers, f'mcpforunity://scene/gameobject/{canvas_id}/components')
        if components_result.get('success'):
            components = components_result.get('data', {}).get('components', [])
            for comp in components:
                comp_type = comp.get('type', '')
                if 'Controller' in comp_type:
                    print(f"\n找到 {comp_type}:")
                    # 这里可以进一步检查组件属性
        
        # 查找预期的按钮
        for btn_name in expected_config.get('buttons', []):
            result = await call_tool(session, headers, 'find_gameobjects', {
                'search_term': btn_name,
                'search_method': 'by_name'
            }, 3)
            if result.get('success') and result.get('data', {}).get('instanceIDs'):
                print(f"  - {btn_name}: 存在")
            else:
                print(f"  - {btn_name}: 不存在")
        
        # 查找LeaderboardUI
        if expected_config.get('needs_leaderboard_ui'):
            result = await call_tool(session, headers, 'find_gameobjects', {
                'search_term': 'LeaderboardPanel',
                'search_method': 'by_name'
            }, 4)
            if result.get('success') and result.get('data', {}).get('instanceIDs'):
                print(f"  - LeaderboardPanel: 存在")
            else:
                print(f"  - LeaderboardPanel: 不存在 (需要添加)")
    
    return True

async def main():
    async with aiohttp.ClientSession() as session:
        session_id, headers = await init_mcp_session(session)
        print(f"Session ID: {session_id}")
        
        # 验证LevelScene
        await verify_scene(session, headers, 'LevelScene', 1, {
            'buttons': ['ReturnButton'],
            'needs_leaderboard_ui': False
        })
        
        await asyncio.sleep(0.5)
        
        # 验证ResultScene
        await verify_scene(session, headers, 'ResultScene', 2, {
            'buttons': ['ResultLeaderboardButton'],
            'needs_leaderboard_ui': True
        })
        
        await asyncio.sleep(0.5)
        
        # 验证Start场景
        await verify_scene(session, headers, 'Start', 0, {
            'buttons': ['LeaderboardButton'],
            'needs_leaderboard_ui': True
        })
        
        print("\n" + "="*60)
        print("验证完成!")
        print("="*60)

if __name__ == '__main__':
    asyncio.run(main())
