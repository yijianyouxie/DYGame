#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取Start场景中LeaderboardButton的样式
"""
import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def get_button_style():
    """获取Start场景中LeaderboardButton的样式"""
    url = 'http://127.0.0.1:8080/mcp'
    headers = {
        'Accept': 'application/json,text/event-stream',
        'Content-Type': 'application/json'
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 获取Start场景中LeaderboardButton的样式 ===\n")
        
        # 初始化
        init_msg = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'initialize',
            'params': {
                'protocolVersion': '2024-11-05',
                'capabilities': {},
                'clientInfo': {'name': 'get-style', 'version': '1.0.0'}
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
        
        # 查找LeaderboardButton
        print("查找LeaderboardButton...")
        find_button = {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'tools/call',
            'params': {
                'name': 'find_gameobjects',
                'arguments': {
                    'search_term': 'LeaderboardButton',
                    'search_method': 'by_name'
                }
            }
        }
        
        button_id = None
        async with session.post(url, headers=headers, json=find_button) as response:
            if response.status == 200:
                response_text = await response.text()
                for line in response_text.split('\n'):
                    line = line.strip()
                    if line.startswith('data:'):
                        data = json.loads(line[5:])
                        structured = data.get('result', {}).get('structuredContent', {})
                        if structured:
                            instance_ids = structured.get('data', {}).get('instanceIDs', [])
                            if instance_ids:
                                button_id = instance_ids[0]
                                print(f"✅ 找到LeaderboardButton, ID: {button_id}")
        
        if button_id:
            # 获取Image组件属性
            print("\n获取Image组件属性...")
            get_image = {
                'jsonrpc': '2.0',
                'id': 3,
                'method': 'tools/call',
                'params': {
                    'name': 'manage_components',
                    'arguments': {
                        'action': 'get',
                        'target': str(button_id),
                        'search_method': 'by_id',
                        'component_type': 'UnityEngine.UI.Image'
                    }
                }
            }
            
            async with session.post(url, headers=headers, json=get_image) as response:
                if response.status == 200:
                    response_text = await response.text()
                    print(f"Image组件响应:\n{response_text}")
            
            # 获取RectTransform属性
            print("\n获取RectTransform属性...")
            get_rect = {
                'jsonrpc': '2.0',
                'id': 4,
                'method': 'tools/call',
                'params': {
                    'name': 'manage_components',
                    'arguments': {
                        'action': 'get',
                        'target': str(button_id),
                        'search_method': 'by_id',
                        'component_type': 'RectTransform'
                    }
                }
            }
            
            async with session.post(url, headers=headers, json=get_rect) as response:
                if response.status == 200:
                    response_text = await response.text()
                    print(f"RectTransform响应:\n{response_text}")

if __name__ == '__main__':
    asyncio.run(get_button_style())
