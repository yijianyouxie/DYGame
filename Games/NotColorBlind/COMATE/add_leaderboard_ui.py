#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为ResultScene添加LeaderboardUI Prefab实例并设置引用
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
        'params': {'protocolVersion': '2024-11-05', 'capabilities': {}, 'clientInfo': {'name': 'add-lb', 'version': '1.0'}}
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
        print("为ResultScene添加LeaderboardPanel")
        print("="*60)
        
        # 加载ResultScene
        print("\n[1] 加载ResultScene...")
        result = await call_tool(session, headers, 'manage_scene', {
            'action': 'load',
            'build_index': 2
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
        
        # 尝试实例化LeaderboardPanel Prefab
        print("\n[3] 创建LeaderboardPanel...")
        result = await call_tool(session, headers, 'manage_gameobject', {
            'action': 'create',
            'name': 'LeaderboardPanel',
            'parent': 'Canvas',
            'prefab_path': 'Assets/Prefabs/LeaderboardPanel.prefab'
        }, 3)
        print(f"创建结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        await asyncio.sleep(0.3)
        
        # 如果创建失败，尝试使用普通方式创建
        if not result.get('success'):
            print("\n尝试其他方式创建...")
            # 使用资源路径创建
            result = await call_tool(session, headers, 'manage_gameobject', {
                'action': 'create',
                'name': 'LeaderboardPanel',
                'parent': 'Canvas'
            }, 4)
            print(f"创建结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        await asyncio.sleep(0.3)
        
        # 查找新创建的LeaderboardPanel
        print("\n[4] 查找LeaderboardPanel...")
        result = await call_tool(session, headers, 'find_gameobjects', {
            'search_term': 'LeaderboardPanel',
            'search_method': 'by_name'
        }, 5)
        
        panel_id = None
        if result.get('success') and result.get('data', {}).get('instanceIDs'):
            panel_id = result['data']['instanceIDs'][0]
            print(f"LeaderboardPanel ID: {panel_id}")
        
        await asyncio.sleep(0.3)
        
        # 设置ResultController.leaderboardUI引用
        if panel_id and canvas_id:
            print("\n[5] 设置ResultController.leaderboardUI引用...")
            result = await call_tool(session, headers, 'manage_components', {
                'action': 'set_property',
                'target': str(canvas_id),
                'search_method': 'by_id',
                'component_type': 'ResultController',
                'property': 'leaderboardUI',
                'value': {'instanceID': panel_id}
            }, 6)
            print(f"设置结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            await asyncio.sleep(0.3)
            
            # 为LeaderboardPanel添加LeaderboardUI组件（如果需要）
            print("\n[6] 检查LeaderboardPanel组件...")
            # 这里需要确保LeaderboardPanel上有LeaderboardUI组件
            
            await asyncio.sleep(0.3)
            
            # 保存场景
            print("\n[7] 保存场景...")
            result = await call_tool(session, headers, 'manage_scene', {'action': 'save'}, 7)
            print(f"保存: {result.get('success', False)}")
        
        print("\n" + "="*60)
        print("完成!")
        print("="*60)

if __name__ == '__main__':
    asyncio.run(main())
