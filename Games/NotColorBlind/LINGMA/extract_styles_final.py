#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取LeaderboardButton的样式（已知sprite，Text组件通过find获取）
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
                return data
        return {}

async def main():
    url = "http://127.0.0.1:8080/mcp"
    
    async with aiohttp.ClientSession() as session:
        # 初始化
        session_id = await init_session(session, url)
        if not session_id:
            print("❌ 初始化失败")
            return
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream',
            'mcp-session-id': session_id
        }
        
        print("✅ MCP连接成功")
        await asyncio.sleep(0.5)
        
        # 加载Start场景
        print("\n加载Start场景...")
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'load',
            'build_index': 0
        }, tool_id=1)
        
        if not result or not result.get('success'):
            print(f"❌ 场景加载失败: {result}")
            return
        
        print("✅ Start场景加载成功")
        await asyncio.sleep(2)
        
        # 查找LeaderboardButton
        print("\n查找LeaderboardButton...")
        find_result = await call_tool(session, url, headers, 'find_gameobjects', {
            'search_term': 'LeaderboardButton',
            'search_method': 'by_name'
        }, tool_id=2)
        
        if not find_result or not find_result.get('data', {}).get('instanceIDs'):
            print("❌ 未找到LeaderboardButton")
            return
        
        leaderboard_id = str(find_result['data']['instanceIDs'][0])
        print(f"✅ 找到 LeaderboardButton: ID={leaderboard_id}")
        
        # 获取组件
        print("\n获取组件信息...")
        resource_path = f'mcpforunity://scene/gameobject/{leaderboard_id}/components'
        result = await get_resource(session, url, headers, resource_path, resource_id=3)
        
        if not result or not result.get('result', {}).get('contents'):
            print("❌ 未获取到组件数据")
            return
        
        content = result['result']['contents'][0]
        text_content = content.get('text', '')
        data = json.loads(text_content)
        components = data.get('data', {}).get('components', [])
        
        sprite_path = None
        font_path = None
        
        for comp in components:
            comp_type = comp.get('typeName', '')
            props = comp.get('properties', {})
            
            if comp_type == 'UnityEngine.UI.Image':
                sprite_data = props.get('sprite') or props.get('m_Sprite', {})
                if isinstance(sprite_data, str):
                    sprite_path = sprite_data
                    print(f"✅ Sprite: {sprite_path}")
        
        # 尝试查找Text子对象 - 通过名称搜索包含Text的对象
        print("\n查找Text对象...")
        find_text_result = await call_tool(session, url, headers, 'find_gameobjects', {
            'search_term': 'Text',
            'search_method': 'by_name'
        }, tool_id=4)
        
        if find_text_result and find_text_result.get('data', {}).get('instanceIDs'):
            text_ids = find_text_result['data']['instanceIDs']
            print(f"找到 {len(text_ids)} 个Text对象")
            
            # 遍历所有Text对象，找到LeaderboardButton的子对象
            for text_id in text_ids:
                # 获取Text组件
                text_resource = f'mcpforunity://scene/gameobject/{text_id}/components'
                text_result = await get_resource(session, url, headers, text_resource, resource_id=5)
                
                if text_result and text_result.get('result', {}).get('contents'):
                    text_content = text_result['result']['contents'][0]
                    text_text = text_content.get('text', '')
                    text_data = json.loads(text_text)
                    text_components = text_data.get('data', {}).get('components', [])
                    
                    for comp in text_components:
                        if comp.get('typeName') == 'UnityEngine.UI.Text':
                            props = comp.get('properties', {})
                            font_data = props.get('font') or props.get('m_Font', {})
                            if isinstance(font_data, str):
                                font_path = font_data
                                print(f"✅ Font: {font_path}")
                                break
                            elif isinstance(font_data, dict) and font_data.get('name'):
                                font_name = font_data.get('name')
                                font_path = f"Assets/Fonts/{font_name}.ttf"
                                print(f"✅ Font: {font_path}")
                                break
                    
                    if font_path:
                        break
        
        print(f"\n" + "=" * 80)
        print("提取到的样式:")
        print(f"  Sprite: {sprite_path}")
        print(f"  Font: {font_path}")
        print("=" * 80)
        
        return sprite_path, font_path

if __name__ == "__main__":
    asyncio.run(main())
