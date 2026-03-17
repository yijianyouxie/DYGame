#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""使用sprite路径来应用样式"""

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

async def apply_sprite_to_button(session, url, headers, button_name):
    """应用sprite到指定按钮"""
    print(f"\n{'='*60}")
    print(f"应用sprite到: {button_name}")
    print('='*60)
    
    # 从Start场景获取的sprite路径
    sprite_path = "Assets/Textures/bg_btn.png"
    
    # 尝试通过m_Sprite属性设置（对应Unity内部字段）
    print(f"[1/3] 设置sprite为 {sprite_path}...")
    result = await call_tool(session, url, headers, 'manage_components', {
        'action': 'set_property',
        'target': button_name,
        'search_method': 'by_name',
        'component_type': 'UnityEngine.UI.Image',
        'property': 'sprite',
        'value': sprite_path
    }, tool_id=10)
    
    if result and result.get('success'):
        print(f"✅ sprite设置成功")
    else:
        print(f"⚠️ sprite设置: {result}")
    
    await asyncio.sleep(0.3)
    
    # 尝试设置overrideSprite
    print(f"[2/3] 设置overrideSprite...")
    result = await call_tool(session, url, headers, 'manage_components', {
        'action': 'set_property',
        'target': button_name,
        'search_method': 'by_name',
        'component_type': 'UnityEngine.UI.Image',
        'property': 'overrideSprite',
        'value': sprite_path
    }, tool_id=11)
    
    if result and result.get('success'):
        print(f"✅ overrideSprite设置成功")
    else:
        print(f"⚠️ overrideSprite设置: {result}")
    
    await asyncio.sleep(0.3)
    
    # 尝试通过m_Sprite设置（Unity序列化字段）
    print(f"[3/3] 设置m_Sprite...")
    result = await call_tool(session, url, headers, 'manage_components', {
        'action': 'set_property',
        'target': button_name,
        'search_method': 'by_name',
        'component_type': 'UnityEngine.UI.Image',
        'property': 'm_Sprite',
        'value': sprite_path
    }, tool_id=12)
    
    if result and result.get('success'):
        print(f"✅ m_Sprite设置成功")
    else:
        print(f"⚠️ m_Sprite设置: {result}")

async def main():
    url = 'http://127.0.0.1:8080/mcp'
    base_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream'
    }
    
    print("="*70)
    print("应用sprite到ResultScene和LevelScene的按钮")
    print("="*70)
    
    async with aiohttp.ClientSession() as session:
        session_id = await init_session(session, url)
        if not session_id:
            print("❌ 无法获取session ID")
            return
        
        print(f"✅ Session ID: {session_id}")
        headers = {**base_headers, 'mcp-session-id': session_id}
        
        await session.post(url, headers=headers, json={
            'jsonrpc': '2.0',
            'method': 'notifications/initialized'
        })
        
        await asyncio.sleep(0.5)
        
        # ResultScene
        print("\n" + "="*70)
        print("处理ResultScene")
        print("="*70)
        
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'load',
            'scene_name': 'ResultScene'
        }, tool_id=1)
        
        await asyncio.sleep(2)
        
        await apply_sprite_to_button(session, url, headers, 'ResultLeaderboardButton')
        
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'save'
        }, tool_id=2)
        if result and result.get('success'):
            print("✅ ResultScene保存成功")
        
        await asyncio.sleep(1)
        
        # LevelScene
        print("\n" + "="*70)
        print("处理LevelScene")
        print("="*70)
        
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'load',
            'scene_name': 'LevelScene'
        }, tool_id=3)
        
        await asyncio.sleep(2)
        
        await apply_sprite_to_button(session, url, headers, 'ReturnButton')
        
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'save'
        }, tool_id=4)
        if result and result.get('success'):
            print("✅ LevelScene保存成功")
        
        print("\n" + "="*70)
        print("✅ 完成!")
        print("="*70)

if __name__ == '__main__':
    asyncio.run(main())
