#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复场景中的按钮引用配置 - 使用场景路径加载
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
        'params': {'protocolVersion': '2024-11-05', 'capabilities': {}, 'clientInfo': {'name': 'fix-config', 'version': '1.0'}}
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

async def fix_level_scene(session, headers):
    """修复LevelScene中ReturnButton的引用"""
    print("\n" + "="*60)
    print("修复 LevelScene")
    print("="*60)
    
    # 使用路径加载LevelScene
    print("\n[1] 加载LevelScene...")
    result = await call_tool(session, headers, 'manage_scene', {
        'action': 'load',
        'path': 'Assets/Scenes/LevelScene.unity'
    }, 1)
    print(f"加载结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    if not result.get('success'):
        print("场景加载失败!")
        return False
    
    await asyncio.sleep(0.5)
    
    # 获取场景层级
    print("\n[2] 获取场景层级...")
    result = await call_tool(session, headers, 'manage_scene', {'action': 'get_hierarchy'}, 2)
    print(f"场景对象: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}...")
    
    await asyncio.sleep(0.3)
    
    # 查找ReturnButton
    print("\n[3] 查找ReturnButton...")
    result = await call_tool(session, headers, 'find_gameobjects', {
        'search_term': 'ReturnButton',
        'search_method': 'by_name'
    }, 3)
    
    button_id = None
    if result.get('success') and result.get('data', {}).get('instanceIDs'):
        button_id = result['data']['instanceIDs'][0]
        print(f"找到ReturnButton, ID: {button_id}")
    else:
        print(f"未找到ReturnButton: {json.dumps(result, ensure_ascii=False)}")
    
    await asyncio.sleep(0.3)
    
    # 查找Canvas
    print("\n[4] 查找Canvas...")
    result = await call_tool(session, headers, 'find_gameobjects', {
        'search_term': 'Canvas',
        'search_method': 'by_name'
    }, 4)
    
    canvas_id = None
    if result.get('success') and result.get('data', {}).get('instanceIDs'):
        canvas_id = result['data']['instanceIDs'][0]
        print(f"找到Canvas, ID: {canvas_id}")
    
    await asyncio.sleep(0.3)
    
    # 如果找到了按钮和Canvas，设置引用
    if button_id and canvas_id:
        print("\n[5] 设置LevelController.returnButton引用...")
        result = await call_tool(session, headers, 'manage_components', {
            'action': 'set_property',
            'target': str(canvas_id),
            'search_method': 'by_id',
            'component_type': 'LevelController',
            'property': 'returnButton',
            'value': {'instanceID': button_id}
        }, 5)
        print(f"设置结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        await asyncio.sleep(0.3)
    
    # 保存场景
    print("\n[6] 保存场景...")
    result = await call_tool(session, headers, 'manage_scene', {'action': 'save'}, 6)
    print(f"保存: {result.get('success', False)}")
    
    return True

async def fix_result_scene(session, headers):
    """修复ResultScene中排行榜按钮的引用"""
    print("\n" + "="*60)
    print("修复 ResultScene")
    print("="*60)
    
    # 使用路径加载ResultScene
    print("\n[1] 加载ResultScene...")
    result = await call_tool(session, headers, 'manage_scene', {
        'action': 'load',
        'path': 'Assets/Scenes/ResultScene.unity'
    }, 1)
    print(f"加载结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    if not result.get('success'):
        print("场景加载失败!")
        return False
    
    await asyncio.sleep(0.5)
    
    # 查找ResultLeaderboardButton
    print("\n[2] 查找ResultLeaderboardButton...")
    result = await call_tool(session, headers, 'find_gameobjects', {
        'search_term': 'ResultLeaderboardButton',
        'search_method': 'by_name'
    }, 2)
    
    button_id = None
    if result.get('success') and result.get('data', {}).get('instanceIDs'):
        button_id = result['data']['instanceIDs'][0]
        print(f"找到ResultLeaderboardButton, ID: {button_id}")
    else:
        print(f"未找到ResultLeaderboardButton")
    
    await asyncio.sleep(0.3)
    
    # 查找Canvas
    print("\n[3] 查找Canvas...")
    result = await call_tool(session, headers, 'find_gameobjects', {
        'search_term': 'Canvas',
        'search_method': 'by_name'
    }, 3)
    
    canvas_id = None
    if result.get('success') and result.get('data', {}).get('instanceIDs'):
        canvas_id = result['data']['instanceIDs'][0]
        print(f"找到Canvas, ID: {canvas_id}")
    
    await asyncio.sleep(0.3)
    
    # 如果找到了按钮和Canvas，设置引用
    if button_id and canvas_id:
        print("\n[4] 设置ResultController.leaderboardButton引用...")
        result = await call_tool(session, headers, 'manage_components', {
            'action': 'set_property',
            'target': str(canvas_id),
            'search_method': 'by_id',
            'component_type': 'ResultController',
            'property': 'leaderboardButton',
            'value': {'instanceID': button_id}
        }, 4)
        print(f"设置结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        await asyncio.sleep(0.3)
    
    # 保存场景
    print("\n[5] 保存场景...")
    result = await call_tool(session, headers, 'manage_scene', {'action': 'save'}, 5)
    print(f"保存: {result.get('success', False)}")
    
    return True

async def main():
    async with aiohttp.ClientSession() as session:
        session_id, headers = await init_mcp_session(session)
        print(f"Session ID: {session_id}")
        
        # 修复LevelScene
        await fix_level_scene(session, headers)
        
        await asyncio.sleep(1)
        
        # 修复ResultScene
        await fix_result_scene(session, headers)
        
        print("\n" + "="*60)
        print("配置修复完成!")
        print("="*60)

if __name__ == '__main__':
    asyncio.run(main())
