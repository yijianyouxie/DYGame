#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""获取Start场景LeaderboardButton的sprite信息"""

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
    
    print("获取Start场景LeaderboardButton的sprite")
    
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
        
        # 查找LeaderboardButton（当前场景应该就是Start）
        print("\n查找LeaderboardButton...")
        find_result = await call_tool(session, url, headers, 'find_gameobjects', {
            'search_term': 'LeaderboardButton',
            'search_method': 'by_name'
        }, tool_id=1)
        
        start_button_ids = []
        if find_result:
            start_button_ids = find_result.get('data', {}).get('instanceIDs', [])
        
        if not start_button_ids:
            print("❌ 未找到LeaderboardButton")
            return
        
        start_button_id = start_button_ids[0]
        print(f"✅ 找到: ID={start_button_id}")
        
        # 获取Image组件
        print("\n获取Image组件...")
        result = await call_tool(session, url, headers, 'manage_components', {
            'action': 'get',
            'search_method': 'by_id',
            'id': str(start_button_id),
            'component_type': 'UnityEngine.UI.Image'
        }, tool_id=2)
        
        print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result and result.get('success'):
            props = result.get('properties', {})
            sprite = props.get('sprite', {})
            print(f"\nSprite信息:")
            print(f"  Name: {sprite.get('name', 'N/A')}")
            print(f"  InstanceID: {sprite.get('instanceID', 'N/A')}")
            print(f"  Path: {sprite.get('path', 'N/A')}")

if __name__ == '__main__':
    asyncio.run(main())
