#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调试场景加载问题"""
import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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
    
    print(f"\n调用请求: {json.dumps(request, indent=2, ensure_ascii=False)}")
    
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
    base_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream'
    }
    
    async with aiohttp.ClientSession() as session:
        # 初始化
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
            print(f"✅ Session ID: {session_id}")
            await response.text()
        
        headers = {**base_headers, 'mcp-session-id': session_id}
        await asyncio.sleep(0.5)
        
        # 测试不同的加载方式
        print("\n" + "=" * 80)
        print("测试1: 使用name参数加载Start场景")
        print("=" * 80)
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'load',
            'name': 'Start'
        }, tool_id=1)
        print(f"结果: {result}")
        await asyncio.sleep(1)
        
        print("\n" + "=" * 80)
        print("测试2: 使用path参数加载Start场景")
        print("=" * 80)
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'load',
            'path': 'Assets/Scenes/Start.scene'
        }, tool_id=2)
        print(f"结果: {result}")
        await asyncio.sleep(1)
        
        print("\n" + "=" * 80)
        print("测试3: 使用buildIndex参数加载Start场景")
        print("=" * 80)
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'load',
            'build_index': 0
        }, tool_id=3)
        print(f"结果: {result}")
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
