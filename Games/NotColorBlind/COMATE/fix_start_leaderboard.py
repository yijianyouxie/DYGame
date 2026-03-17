#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为Start场景添加LeaderboardPanel实例
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
        'params': {'protocolVersion': '2024-11-05', 'capabilities': {}, 'clientInfo': {'name': 'fix-start', 'version': '1.0'}}
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

async def main():
    async with aiohttp.ClientSession() as session:
        session_id, headers = await init_mcp_session(session)
        print(f"Session ID: {session_id}")
        
        print("\n" + "="*60)
        print("修复Start场景中的LeaderboardPanel")
        print("="*60)
        
        # 加载Start场景
        print("\n[1] 加载Start场景...")
        result = await call_tool(session, headers, 'manage_scene', {
            'action': 'load',
            'build_index': 0
        }, 1)
        print(f"加载: success={result.get('success', False)}")
        
        await asyncio.sleep(0.3)
        
        # 查找Canvas
        print("\n[2] 查找Canvas...")
        result = await call_tool(session, headers, 'find_gameobjects', {
            'search_term': 'Canvas',
            'search_method': 'by_name'
        }, 2)
        
        canvas_id = None
        if result.get('success') and result.get('data', {}).get('instanceIDs'):
            canvas_id = result['data']['instanceIDs'][0]
            print(f"Canvas ID: {canvas_id}")
        
        await asyncio.sleep(0.3)
        
        # 删除旧的LeaderboardPanel（如果存在）
        print("\n[3] 查找并删除旧的LeaderboardPanel...")
        result = await call_tool(session, headers, 'find_gameobjects', {
            'search_term': 'LeaderboardPanel',
            'search_method': 'by_name'
        }, 3)
        
        if result.get('success') and result.get('data', {}).get('instanceIDs'):
            old_panel_ids = result['data']['instanceIDs']
            for old_id in old_panel_ids:
                print(f"删除旧的LeaderboardPanel (ID: {old_id})...")
                await call_tool(session, headers, 'manage_gameobject', {
                    'action': 'delete',
                    'target': str(old_id),
                    'search_method': 'by_id'
                }, 4)
        
        await asyncio.sleep(0.3)
        
        # 创建新的LeaderboardPanel实例
        print("\n[4] 创建LeaderboardPanel实例...")
        result = await call_tool(session, headers, 'manage_gameobject', {
            'action': 'create',
            'name': 'LeaderboardPanel',
            'parent': 'Canvas',
            'prefab_path': 'Assets/Prefabs/LeaderboardPanel.prefab'
        }, 5)
        print(f"创建结果: success={result.get('success', False)}")
        
        if result.get('success'):
            panel_id = result.get('data', {}).get('instanceID')
            print(f"LeaderboardPanel ID: {panel_id}")
            
            await asyncio.sleep(0.3)
            
            # 设置MainMenuController.leaderboardUI引用
            if canvas_id:
                print("\n[5] 设置MainMenuController.leaderboardUI引用...")
                result = await call_tool(session, headers, 'manage_components', {
                    'action': 'set_property',
                    'target': str(canvas_id),
                    'search_method': 'by_id',
                    'component_type': 'MainMenuController',
                    'property': 'leaderboardUI',
                    'value': {'instanceID': panel_id}
                }, 6)
                print(f"设置结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
                await asyncio.sleep(0.3)
            
            # 保存场景
            print("\n[6] 保存场景...")
            result = await call_tool(session, headers, 'manage_scene', {'action': 'save'}, 7)
            print(f"保存: {result.get('success', False)}")
        
        print("\n" + "="*60)
        print("完成!")
        print("="*60)
        print("\n请在Unity Editor中检查：")
        print("1. Start场景中是否有LeaderboardPanel对象")
        print("2. Canvas上的MainMenuController组件中leaderboardUI是否正确引用")

asyncio.run(main())
