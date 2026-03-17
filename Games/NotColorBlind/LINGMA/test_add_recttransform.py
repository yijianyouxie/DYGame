#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试添加RectTransform
"""
import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def test_add_rect():
    """测试添加RectTransform"""
    url = 'http://127.0.0.1:8080/mcp'
    headers = {
        'Accept': 'application/json,text/event-stream',
        'Content-Type': 'application/json'
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 测试添加RectTransform ===\n")
        
        # 初始化
        init_msg = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'initialize',
            'params': {
                'protocolVersion': '2024-11-05',
                'capabilities': {},
                'clientInfo': {'name': 'test-rect', 'version': '1.0.0'}
            }
        }
        
        async with session.post(url, headers=headers, json=init_msg) as response:
            session_id = response.headers.get('mcp-session-id')
            if response.status == 200:
                async for line in response.content:
                    if line.decode('utf-8').strip().startswith('data:'):
                        break
        
        if not session_id:
            print("无法获取session ID")
            return
        
        headers['mcp-session-id'] = session_id
        
        # 发送initialized
        await session.post(url, headers=headers, json={
            'jsonrpc': '2.0',
            'method': 'notifications/initialized'
        })
        
        # 尝试添加RectTransform
        print("为ReturnButton添加RectTransform...")
        add_rect = {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'tools/call',
            'params': {
                'name': 'manage_gameobject',
                'arguments': {
                    'action': 'add_component',
                    'target': 'ReturnButton',
                    'component_type': 'RectTransform'
                }
            }
        }
        
        async with session.post(url, headers=headers, json=add_rect) as response:
            if response.status == 200:
                response_text = await response.text()
                print(f"添加RectTransform响应:\n{response_text}")

if __name__ == '__main__':
    asyncio.run(test_add_rect())
