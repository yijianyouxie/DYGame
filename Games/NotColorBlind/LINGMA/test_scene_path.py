#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试场景加载的path参数"""
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

async def main():
    url = "http://127.0.0.1:8080/mcp"
    
    async with aiohttp.ClientSession() as session:
        session_id = await init_session(session, url)
        if not session_id:
            print("❌ 初始化失败")
            return
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream',
            'mcp-session-id': session_id
        }
        
        await asyncio.sleep(1)
        
        # 尝试使用path参数
        test_paths = [
            'Assets/Scenes/Start.scene',
            'Assets/Scenes/Start',
            'Assets/Scenes/ResultScene.unity',
            'Assets/Scenes/ResultScene',
            'Assets/Scenes/LevelScene.unity',
            'Assets/Scenes/LevelScene'
        ]
        
        for path in test_paths:
            print(f"\n测试加载path: '{path}'")
            result = await call_tool(session, url, headers, 'manage_scene', {
                'action': 'load',
                'path': path
            })
            
            if result and result.get('success'):
                print(f"  ✅ 成功!")
                print(f"  返回: {result}")
            else:
                print(f"  ❌ 失败: {result.get('error', result.get('code', '未知错误'))}")
            
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
