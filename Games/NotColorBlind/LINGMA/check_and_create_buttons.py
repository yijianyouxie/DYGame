#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查场景并创建按钮
"""
import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def check_and_create():
    """检查场景并创建按钮"""
    url = 'http://127.0.0.1:8080/mcp'
    headers = {
        'Accept': 'application/json,text/event-stream',
        'Content-Type': 'application/json'
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 检查场景并创建按钮 ===\n")
        
        # 初始化
        init_msg = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'initialize',
            'params': {
                'protocolVersion': '2024-11-05',
                'capabilities': {},
                'clientInfo': {'name': 'check-create', 'version': '1.0.0'}
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
        
        # 获取当前场景信息
        print("获取当前场景信息...")
        get_active = {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'tools/call',
            'params': {
                'name': 'manage_scene',
                'arguments': {
                    'action': 'get_active'
                }
            }
        }
        
        async with session.post(url, headers=headers, json=get_active) as response:
            if response.status == 200:
                response_text = await response.text()
                print(f"当前场景信息:\n{response_text}")
        
        # 列出所有场景
        print("\n列出所有场景...")
        list_scenes = {
            'jsonrpc': '2.0',
            'id': 3,
            'method': 'tools/call',
            'params': {
                'name': 'manage_scene',
                'arguments': {
                    'action': 'list'
                }
            }
        }
        
        async with session.post(url, headers=headers, json=list_scenes) as response:
            if response.status == 200:
                response_text = await response.text()
                print(f"所有场景:\n{response_text}")

if __name__ == '__main__':
    asyncio.run(check_and_create())
