#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查Start场景中的所有按钮，获取参考样式"""

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

async def main():
    url = 'http://127.0.0.1:8080/mcp'
    base_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream'
    }
    
    print("检查Start场景中的按钮")
    
    async with aiohttp.ClientSession() as session:
        session_id = await init_session(session, url)
        if not session_id:
            print("❌ 无法获取session ID")
            return
        
        headers = {**base_headers, 'mcp-session-id': session_id}
        
        await session.post(url, headers=headers, json={
            'jsonrpc': '2.0',
            'method': 'notifications/initialized'
        })
        
        await asyncio.sleep(0.5)
        
        # 加载Start场景
        print("\n[1/4] 加载Start场景...")
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'load',
            'scene_name': 'StartScene'
        }, tool_id=1)
        
        if result and result.get('success'):
            print("✅ StartScene加载成功")
        else:
            print(f"⚠️ StartScene加载: {result}")
        
        await asyncio.sleep(2)
        
        # 获取层级
        print("\n[2/4] 获取场景层级...")
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'get_hierarchy'
        }, tool_id=2)
        
        hierarchy = []
        if result:
            hierarchy = result.get('hierarchy', [])
            print(f"✅ 获取到 {len(hierarchy)} 个节点")
        
        # 查找所有包含"Button"的对象
        print("\n[3/4] 查找所有Button...")
        all_buttons = []
        
        for node in hierarchy:
            name = node.get('name', '')
            if 'Button' in name or 'button' in name.lower():
                obj_id = node.get('instanceID')
                path = node.get('path', '')
                print(f"  - {name} (ID: {obj_id}, Path: {path})")
                all_buttons.append({'name': name, 'id': obj_id, 'path': path})
        
        if not all_buttons:
            print("  未找到任何Button对象")
        
        # 尝试获取第一个Button的Image组件
        print("\n[4/4] 获取Button的Image组件...")
        if all_buttons:
            first_button = all_buttons[0]
            print(f"检查按钮: {first_button['name']}")
            
            # 由于get不支持，尝试使用set_property来获取当前值（有些MCP实现会返回当前值）
            result = await call_tool(session, url, headers, 'manage_components', {
                'action': 'set_property',
                'target': first_button['name'],
                'search_method': 'by_name',
                'component_type': 'UnityEngine.UI.Image',
                'property': 'sprite',
                'value': None  # 不设置值，只是读取
            }, tool_id=3)
            
            if result:
                print(f"Image组件结果: {json.dumps(result, indent=2)}")
        
        print("\n完成!")

if __name__ == '__main__':
    asyncio.run(main())
