#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查Text组件的详细信息
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
                if data.get('result', {}).get('contents'):
                    content = data['result']['contents'][0]
                    inner_text = content.get('text', '')
                    if inner_text:
                        try:
                            inner_data = json.loads(inner_text)
                            return inner_data
                        except:
                            return None
                return data
        return {}

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
        
        # 加载ResultScene
        print("\n加载ResultScene...")
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'load',
            'build_index': 2
        }, tool_id=100)
        
        if not result or not result.get('success'):
            print("❌ 场景加载失败")
            return
        
        print("✅ ResultScene加载成功")
        
        # 查找ResultLeaderboardButton
        print("\n查找ResultLeaderboardButton...")
        result = await call_tool(session, url, headers, 'find_gameobjects', {
            'search_term': 'ResultLeaderboardButton',
            'search_method': 'by_name'
        }, tool_id=101)
        
        if not result or not result.get('data', {}).get('instanceIDs'):
            print("❌ 未找到ResultLeaderboardButton")
            return
        
        btn_id = str(result['data']['instanceIDs'][0])
        print(f"✅ 按钮ID: {btn_id}")
        
        # 查找所有Text对象
        print("\n查找所有Text对象...")
        result = await call_tool(session, url, headers, 'find_gameobjects', {
            'search_term': 'Text',
            'search_method': 'by_name'
        }, tool_id=102)
        
        if not result or not result.get('data', {}).get('instanceIDs'):
            print("❌ 未找到Text对象")
            return
        
        text_ids = result['data']['instanceIDs']
        print(f"✅ 找到 {len(text_ids)} 个Text对象: {text_ids}")
        
        # 检查每个Text对象的详细信息和父对象
        for text_id in text_ids:
            print(f"\n" + "=" * 80)
            print(f"检查Text对象 ID: {text_id}")
            print("=" * 80)
            
            # 获取组件
            uri = f'mcpforunity://scene/gameobject/{text_id}/components'
            data = await get_resource(session, url, headers, uri)
            
            if not data or not data.get('data', {}).get('components'):
                print("  ❌ 无法获取组件")
                continue
            
            components = data['data']['components']
            print(f"\n组件列表 ({len(components)} 个):")
            for comp in components:
                comp_type = comp.get('typeName', '')
                print(f"  - {comp_type}")
                
                # 如果是Text组件，打印属性
                if comp_type == 'UnityEngine.UI.Text':
                    props = comp.get('properties', {})
                    print(f"\nText组件属性:")
                    for key, value in props.items():
                        print(f"  {key}: {value}")
            
            # 获取Transform组件查看父对象
            for comp in components:
                if comp.get('typeName') == 'UnityEngine.Transform':
                    props = comp.get('properties', {})
                    parent_id = props.get('parent') or props.get('m_Father')
                    print(f"\n父对象ID: {parent_id}")
                    print(f"按钮ID: {btn_id}")
                    if parent_id == btn_id:
                        print("✅ 这是ResultLeaderboardButton的子Text对象!")
                    else:
                        print(f"⚠️ 这不是ResultLeaderboardButton的子对象")

if __name__ == "__main__":
    asyncio.run(main())
