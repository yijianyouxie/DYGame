#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""正确提取LeaderboardButton的样式信息"""
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
    base_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream'
    }
    
    async with aiohttp.ClientSession() as session:
        # 初始化
        async with session.post(url, headers=base_headers, json={
            'jsonrpc': '2.0',
            'id': 0,
            'method': 'initialize',
            'params': {
                'protocolVersion': '2024-11-05',
                'capabilities': {},
                'clientInfo': {'name': 'python-script', 'version': '1.0'}
            }
        }) as response:
            session_id = response.headers.get('mcp-session-id')
            print(f"✅ Session ID: {session_id}")
            await response.text()
        
        headers = {**base_headers, 'mcp-session-id': session_id}
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
        
        # 解析数据 - 注意mimeType是text/plain，text字段是JSON字符串
        content = result['result']['contents'][0]
        text_content = content.get('text', '')
        data = json.loads(text_content)
        components = data.get('data', {}).get('components', [])
        
        print(f"\n找到 {len(components)} 个组件:")
        
        sprite_path = None
        font_path = None
        
        for comp in components:
            comp_type = comp.get('typeName', '')
            props = comp.get('properties', {})
            
            if comp_type == 'UnityEngine.UI.Image':
                print(f"\n✅ Image组件:")
                print(f"   instanceID: {comp.get('instanceID')}")
                # 提取sprite信息
                sprite_data = props.get('sprite') or props.get('m_Sprite', {})
                print(f"   sprite: {sprite_data}")
                print(f"   sprite类型: {type(sprite_data)}")
                # sprite可能是字符串路径或对象
                if isinstance(sprite_data, str):
                    sprite_path = sprite_data
                    print(f"   sprite路径: {sprite_path}")
                elif isinstance(sprite_data, dict) and sprite_data.get('name'):
                    sprite_name = sprite_data.get('name')
                    print(f"   sprite.name: {sprite_name}")
                    # sprite通常有asset路径信息
                    if sprite_name:
                        # 尝试常见的sprite路径格式
                        sprite_path = f"Assets/Textures/{sprite_name}.png"
                        print(f"   推测路径: {sprite_path}")
                
            elif comp_type == 'UnityEngine.UI.Text':
                print(f"\n✅ Text组件:")
                print(f"   instanceID: {comp.get('instanceID')}")
                print(f"   text: {props.get('text', '')}")
                print(f"   fontSize: {props.get('fontSize', '')}")
                # 提取font信息
                font_data = props.get('font') or props.get('m_Font', {})
                print(f"   font: {font_data}")
                print(f"   font类型: {type(font_data)}")
                # font可能是字符串路径或对象
                if isinstance(font_data, str):
                    font_path = font_data
                    print(f"   font路径: {font_path}")
                elif isinstance(font_data, dict) and font_data.get('name'):
                    font_name = font_data.get('name')
                    print(f"   font.name: {font_name}")
                    if font_name:
                        # 尝试常见的font路径格式
                        font_path = f"Assets/Fonts/{font_name}.ttf"
                        print(f"   推测路径: {font_path}")
        
        # 获取Text子对象的字体
        print("\n获取Text子对象...")
        children_resource = f'mcpforunity://scene/gameobject/{leaderboard_id}/children'
        children_result = await get_resource(session, url, headers, children_resource, resource_id=4)
        
        if children_result and children_result.get('result', {}).get('contents'):
            child_content = children_result['result']['contents'][0]
            child_text = child_content.get('text', '')
            child_data = json.loads(child_text)
            child_id = child_data.get('data', {}).get('instanceID')
            
            if child_id:
                print(f"✅ 找到子对象: ID={child_id}")
                
                # 获取子对象的组件
                child_components_resource = f'mcpforunity://scene/gameobject/{child_id}/components'
                child_components_result = await get_resource(session, url, headers, child_components_resource, resource_id=5)
                
                if child_components_result and child_components_result.get('result', {}).get('contents'):
                    child_comp_content = child_components_result['result']['contents'][0]
                    child_comp_text = child_comp_content.get('text', '')
                    child_comp_data = json.loads(child_comp_text)
                    child_components = child_comp_data.get('data', {}).get('components', [])
                    
                    print(f"\n子对象的 {len(child_components)} 个组件:")
                    for comp in child_components:
                        comp_type = comp.get('typeName', '')
                        props = comp.get('properties', {})
                        
                        if comp_type == 'UnityEngine.UI.Text':
                            print(f"✅ Text组件:")
                            font_data = props.get('font') or props.get('m_Font', {})
                            print(f"   font: {font_data}")
                            print(f"   font类型: {type(font_data)}")
                            if isinstance(font_data, str):
                                font_path = font_data
                                print(f"   font路径: {font_path}")
                            elif isinstance(font_data, dict) and font_data.get('name'):
                                font_name = font_data.get('name')
                                print(f"   font.name: {font_name}")
                                if font_name:
                                    font_path = f"Assets/Fonts/{font_name}.ttf"
                                    print(f"   推测路径: {font_path}")
        
        # 如果没有找到sprite，尝试从已知信息获取
        if not sprite_path:
            print("\n⚠️ 未找到sprite信息，使用已知路径")
            sprite_path = "Assets/Textures/bg_btn.png"
            print(f"   使用路径: {sprite_path}")
        
        print(f"\n" + "=" * 80)
        print("提取到的样式:")
        print(f"  Sprite: {sprite_path}")
        print(f"  Font: {font_path}")
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
