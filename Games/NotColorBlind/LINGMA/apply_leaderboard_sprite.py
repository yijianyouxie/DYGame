#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""获取Start场景LeaderboardButton的sprite并应用到其他场景的按钮"""

import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def init_session(session, url):
    """初始化MCP session"""
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
    """调用MCP工具"""
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
    
    print("="*70)
    print("获取Start场景LeaderboardButton的sprite并应用到其他按钮")
    print("="*70)
    
    async with aiohttp.ClientSession() as session:
        # 初始化session
        print("\n初始化MCP session...")
        session_id = await init_session(session, url)
        if not session_id:
            print("❌ 无法获取session ID")
            return
        
        print(f"✅ Session ID: {session_id}")
        headers = {**base_headers, 'mcp-session-id': session_id}
        
        # 发送initialized
        await session.post(url, headers=headers, json={
            'jsonrpc': '2.0',
            'method': 'notifications/initialized'
        })
        
        await asyncio.sleep(0.5)
        
        # 加载Start场景
        print("\n[1/4] 加载Start场景...")
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'load',
            'sceneName': 'StartScene'
        }, tool_id=1)
        
        if result and result.get('success'):
            print("✅ StartScene加载成功")
        else:
            print(f"⚠️ StartScene加载: {result}")
        
        await asyncio.sleep(2)
        
        # 查找LeaderboardButton
        print("\n[2/4] 查找Start场景的LeaderboardButton...")
        find_result = await call_tool(session, url, headers, 'find_gameobjects', {
            'search_term': 'LeaderboardButton',
            'search_method': 'by_name'
        }, tool_id=2)
        
        start_button_ids = []
        if find_result:
            start_button_ids = find_result.get('data', {}).get('instanceIDs', [])
        
        if not start_button_ids:
            print("❌ 未找到Start场景的LeaderboardButton")
            return
        
        start_button_id = start_button_ids[0]
        print(f"✅ 找到LeaderboardButton: ID={start_button_id}")
        
        # 获取Image组件的sprite
        print("\n获取Image组件的sprite信息...")
        image_result = await call_tool(session, url, headers, 'manage_components', {
            'action': 'get',
            'search_method': 'by_id',
            'target': str(start_button_id),
            'component_type': 'UnityEngine.UI.Image'
        }, tool_id=3)
        
        sprite_info = None
        if image_result and image_result.get('success'):
            props = image_result.get('properties', {})
            sprite = props.get('sprite', {})
            sprite_info = {
                'name': sprite.get('name', ''),
                'instanceID': sprite.get('instanceID', 0)
            }
            print(f"✅ Sprite: {sprite_info}")
        else:
            print(f"⚠️ Image组件获取: {image_result}")
        
        # 应用到ResultScene
        print("\n[3/4] 应用到ResultScene的ResultLeaderboardButton...")
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'load',
            'sceneName': 'ResultScene'
        }, tool_id=4)
        await asyncio.sleep(2)
        
        if sprite_info and sprite_info['instanceID']:
            # 尝试设置sprite
            set_result = await call_tool(session, url, headers, 'manage_components', {
                'action': 'set_property',
                'target': 'ResultLeaderboardButton',
                'search_method': 'by_name',
                'component_type': 'UnityEngine.UI.Image',
                'property': 'sprite',
                'value': sprite_info['instanceID']
            }, tool_id=5)
            if set_result and set_result.get('success'):
                print("✅ ResultLeaderboardButton的sprite设置成功")
            else:
                print(f"⚠️ sprite设置: {set_result}")
        
        # 应用到LevelScene
        print("\n[4/4] 应用到LevelScene的ReturnButton...")
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'load',
            'sceneName': 'LevelScene'
        }, tool_id=6)
        await asyncio.sleep(2)
        
        if sprite_info and sprite_info['instanceID']:
            set_result = await call_tool(session, url, headers, 'manage_components', {
                'action': 'set_property',
                'target': 'ReturnButton',
                'search_method': 'by_name',
                'component_type': 'UnityEngine.UI.Image',
                'property': 'sprite',
                'value': sprite_info['instanceID']
            }, tool_id=7)
            if set_result and set_result.get('success'):
                print("✅ ReturnButton的sprite设置成功")
            else:
                print(f"⚠️ sprite设置: {set_result}")
        
        # 保存场景
        print("\n保存场景...")
        await call_tool(session, url, headers, 'manage_scene', {
            'action': 'save'
        }, tool_id=8)
        print("✅ 场景保存成功")
        
        print("\n" + "="*70)
        print("✅ 完成!")
        print("="*70)

if __name__ == '__main__':
    asyncio.run(main())
