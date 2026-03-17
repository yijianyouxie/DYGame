#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试MCP连接：创建场景和Image
1. 创建名为xtest的场景
2. 在场景中添加一个Image
3. 设置Image的sprite为bg_btn
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
    print("=" * 60)
    print("MCP测试: 创建场景xtest和Image")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # 1. 初始化会话
        print("\n[1] 初始化MCP会话...")
        session_id, headers = await init_mcp_session(session)
        if not session_id:
            print("ERROR: 无法初始化会话")
            return
        print(f"Session ID: {session_id}")
        
        # 2. 创建新场景xtest
        print("\n[2] 创建场景 'xtest'...")
        result = await call_tool(session, headers, 'manage_scene', {
            'action': 'create',
            'name': 'xtest',
            'path': 'Assets/Scenes/xtest.unity'
        }, request_id=2)
        print(f"创建场景结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        await asyncio.sleep(0.5)
        
        # 3. 获取当前场景层级
        print("\n[3] 获取当前场景层级...")
        result = await call_tool(session, headers, 'manage_scene', {
            'action': 'get_hierarchy'
        }, request_id=3)
        print(f"场景层级: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        await asyncio.sleep(0.3)
        
        # 4. 创建Canvas（UI需要Canvas）
        print("\n[4] 创建Canvas...")
        result = await call_tool(session, headers, 'manage_gameobject', {
            'action': 'create',
            'name': 'Canvas',
            'components_to_add': ['Canvas', 'CanvasScaler', 'GraphicRaycaster']
        }, request_id=4)
        print(f"创建Canvas结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        await asyncio.sleep(0.3)
        
        # 5. 创建EventSystem
        print("\n[5] 创建EventSystem...")
        result = await call_tool(session, headers, 'manage_gameobject', {
            'action': 'create',
            'name': 'EventSystem',
            'components_to_add': ['EventSystem', 'StandaloneInputModule']
        }, request_id=5)
        print(f"创建EventSystem结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        await asyncio.sleep(0.3)
        
        # 6. 创建Image对象（作为Canvas的子对象）
        print("\n[6] 创建Image对象...")
        result = await call_tool(session, headers, 'manage_gameobject', {
            'action': 'create',
            'name': 'TestImage',
            'parent': 'Canvas',
            'components_to_add': ['RectTransform', 'CanvasRenderer', 'Image']
        }, request_id=6)
        print(f"创建Image结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        # 获取新创建Image的ID
        image_id = None
        if result.get('success') and result.get('data', {}).get('instanceID'):
            image_id = result['data']['instanceID']
        
        await asyncio.sleep(0.3)
        
        # 7. 设置Image的sprite为bg_btn
        if image_id:
            print(f"\n[7] 设置Image的sprite为bg_btn...")
            result = await call_tool(session, headers, 'manage_components', {
                'action': 'set_property',
                'target': str(image_id),
                'search_method': 'by_id',
                'component_type': 'Image',
                'property': 'sprite',
                'value': 'bg_btn'
            }, request_id=7)
            print(f"设置sprite结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            # 尝试通过名称设置
            print(f"\n[7] 通过名称设置Image的sprite为bg_btn...")
            result = await call_tool(session, headers, 'manage_components', {
                'action': 'set_property',
                'target': 'TestImage',
                'search_method': 'by_name',
                'component_type': 'Image',
                'property': 'sprite',
                'value': 'bg_btn'
            }, request_id=7)
            print(f"设置sprite结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        await asyncio.sleep(0.3)
        
        # 8. 保存场景
        print("\n[8] 保存场景...")
        result = await call_tool(session, headers, 'manage_scene', {
            'action': 'save'
        }, request_id=8)
        print(f"保存场景结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        print("\n" + "=" * 60)
        print("测试完成! 请在Unity中检查xtest场景")
        print("=" * 60)

if __name__ == '__main__':
    asyncio.run(main())
