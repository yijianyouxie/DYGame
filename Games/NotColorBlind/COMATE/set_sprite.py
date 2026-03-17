#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置TestImage的sprite为bg_btn
"""
import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

MCP_URL = 'http://127.0.0.1:8080/mcp'

async def init_mcp_session(session):
    """初始化MCP会话"""
    headers = {
        'Accept': 'application/json,text/event-stream',
        'Content-Type': 'application/json'
    }
    
    init_msg = {
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'initialize',
        'params': {
            'protocolVersion': '2024-11-05',
            'capabilities': {},
            'clientInfo': {'name': 'comate-test', 'version': '1.0.0'}
        }
    }
    
    session_id = None
    async with session.post(MCP_URL, headers=headers, json=init_msg) as response:
        session_id = response.headers.get('mcp-session-id')
        if response.status == 200:
            async for line in response.content:
                if line.decode('utf-8').strip().startswith('data:'):
                    break
    
    if session_id:
        headers['mcp-session-id'] = session_id
        await session.post(MCP_URL, headers=headers, json={
            'jsonrpc': '2.0',
            'method': 'notifications/initialized',
            'params': {}
        })
    
    return session_id, headers

async def call_tool(session, headers, tool_name, arguments, request_id=1):
    """调用MCP工具"""
    call_msg = {
        'jsonrpc': '2.0',
        'id': request_id,
        'method': 'tools/call',
        'params': {
            'name': tool_name,
            'arguments': arguments
        }
    }
    
    result = None
    async with session.post(MCP_URL, headers=headers, json=call_msg) as response:
        if response.status == 200:
            async for line in response.content:
                line_text = line.decode('utf-8').strip()
                if line_text.startswith('data:'):
                    data = json.loads(line_text[5:])
                    result = data.get('result', {}).get('structuredContent', {})
                    break
    
    return result

async def main():
    print("设置TestImage的sprite为bg_btn")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # 初始化会话
        print("\n[1] 初始化MCP会话...")
        session_id, headers = await init_mcp_session(session)
        print(f"Session ID: {session_id}")
        
        # 加载xtest场景
        print("\n[2] 加载xtest场景...")
        result = await call_tool(session, headers, 'manage_scene', {
            'action': 'load',
            'name': 'xtest'
        }, request_id=2)
        print(f"加载场景: {result.get('success', False)}")
        
        await asyncio.sleep(0.3)
        
        # 查找TestImage
        print("\n[3] 查找TestImage...")
        result = await call_tool(session, headers, 'find_gameobjects', {
            'search_term': 'TestImage',
            'search_method': 'by_name'
        }, request_id=3)
        
        image_id = None
        if result.get('success') and result.get('data', {}).get('instanceIDs'):
            image_id = result['data']['instanceIDs'][0]
            print(f"找到TestImage, ID: {image_id}")
        else:
            print(f"未找到TestImage: {result}")
            return
        
        await asyncio.sleep(0.3)
        
        # 设置sprite - 尝试多种方式
        print("\n[4] 设置sprite为bg_btn...")
        
        # 方式1: 使用资源路径
        result = await call_tool(session, headers, 'manage_components', {
            'action': 'set_property',
            'target': str(image_id),
            'search_method': 'by_id',
            'component_type': 'Image',
            'property': 'sprite',
            'value': 'Assets/Textures/bg_btn.png'
        }, request_id=4)
        print(f"方式1(路径): {result}")
        
        if not result.get('success'):
            await asyncio.sleep(0.3)
            # 方式2: 只使用文件名
            result = await call_tool(session, headers, 'manage_components', {
                'action': 'set_property',
                'target': str(image_id),
                'search_method': 'by_id',
                'component_type': 'Image',
                'property': 'sprite',
                'value': 'bg_btn'
            }, request_id=5)
            print(f"方式2(名称): {result}")
        
        await asyncio.sleep(0.3)
        
        # 保存场景
        print("\n[5] 保存场景...")
        result = await call_tool(session, headers, 'manage_scene', {
            'action': 'save'
        }, request_id=6)
        print(f"保存: {result.get('success', False)}")
        
        print("\n完成!")

if __name__ == '__main__':
    asyncio.run(main())
