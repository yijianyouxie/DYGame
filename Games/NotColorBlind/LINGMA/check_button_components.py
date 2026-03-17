#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查按钮的实际组件情况
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

async def get_resource(session, url, headers, resource_path, resource_id=1):
    """通过resource获取数据"""
    request = {
        'jsonrpc': '2.0',
        'id': resource_id,
        'method': 'resources/read',
        'params': {
            'uri': resource_path
        }
    }
    
    async with session.post(url, headers=headers, json=request) as response:
        text = await response.text()
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('data:'):
                data = json.loads(line[5:])
                # 获取contents中的text字段
                if data.get('result', {}).get('contents'):
                    content = data['result']['contents'][0]
                    inner_text = content.get('text', '')
                    if inner_text:
                        # text字段是另一个JSON字符串
                        try:
                            inner_data = json.loads(inner_text)
                            return inner_data
                        except:
                            return None
                return data
        return {}

async def check_object_components(session, url, headers, obj_id, obj_name):
    """检查对象的组件"""
    print(f"\n检查 {obj_name} (ID: {obj_id}) 的组件:")
    
    uri = f'mcpforunity://scene/gameobject/{obj_id}/components'
    data = await get_resource(session, url, headers, uri)
    
    if not data or not data.get('data', {}).get('components'):
        print(f"  ❌ 无法获取组件信息")
        return
    
    components = data['data']['components']
    print(f"  找到 {len(components)} 个组件:")
    
    for comp in components:
        comp_type = comp.get('typeName', '')
        print(f"    ✅ {comp_type}")

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
        
        # 检查ResultScene
        print("\n" + "=" * 80)
        print("检查 ResultScene")
        print("=" * 80)
        
        print("\n加载ResultScene...")
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'load',
            'build_index': 2
        }, tool_id=100)
        
        if result and result.get('success'):
            print("  ✅ ResultScene加载成功")
            
            # 查找ResultLeaderboardButton
            print("\n查找ResultLeaderboardButton...")
            result = await call_tool(session, url, headers, 'find_gameobjects', {
                'search_term': 'ResultLeaderboardButton',
                'search_method': 'by_name'
            }, tool_id=101)
            
            if result and result.get('data', {}).get('instanceIDs'):
                btn_id = str(result['data']['instanceIDs'][0])
                await check_object_components(session, url, headers, btn_id, 'ResultLeaderboardButton')
                
                # 查找Text子对象
                print("\n查找Text子对象...")
                result = await call_tool(session, url, headers, 'find_gameobjects', {
                    'search_term': 'Text',
                    'search_method': 'by_name'
                }, tool_id=102)
                
                if result and result.get('data', {}).get('instanceIDs'):
                    text_ids = result['data']['instanceIDs']
                    text_id = str(text_ids[-1])
                    await check_object_components(session, url, headers, text_id, 'Text')
        
        # 检查LevelScene
        print("\n" + "=" * 80)
        print("检查 LevelScene")
        print("=" * 80)
        
        print("\n加载LevelScene...")
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'load',
            'build_index': 1
        }, tool_id=200)
        
        if result and result.get('success'):
            print("  ✅ LevelScene加载成功")
            
            # 查找ReturnButton
            print("\n查找ReturnButton...")
            result = await call_tool(session, url, headers, 'find_gameobjects', {
                'search_term': 'ReturnButton',
                'search_method': 'by_name'
            }, tool_id=201)
            
            if result and result.get('data', {}).get('instanceIDs'):
                btn_id = str(result['data']['instanceIDs'][0])
                await check_object_components(session, url, headers, btn_id, 'ReturnButton')
                
                # 查找Text子对象
                print("\n查找Text子对象...")
                result = await call_tool(session, url, headers, 'find_gameobjects', {
                    'search_term': 'Text',
                    'search_method': 'by_name'
                }, tool_id=202)
                
                if result and result.get('data', {}).get('instanceIDs'):
                    text_ids = result['data']['instanceIDs']
                    text_id = str(text_ids[-1])
                    await check_object_components(session, url, headers, text_id, 'Text')

if __name__ == "__main__":
    asyncio.run(main())
