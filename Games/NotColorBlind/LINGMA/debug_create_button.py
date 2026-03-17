#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调试创建GameObject的问题"""
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
    
    print(f"\n调用请求: {json.dumps(request, indent=2, ensure_ascii=False)}")
    
    async with session.post(url, headers=headers, json=request) as response:
        text = await response.text()
        print(f"响应状态: {response.status}")
        print(f"完整响应: {text}")
        
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
        
        # 加载ResultScene
        print("\n" + "=" * 80)
        print("加载ResultScene")
        print("=" * 80)
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'load',
            'build_index': 2
        }, tool_id=1)
        
        if result and result.get('success'):
            print("✅ 场景加载成功")
        else:
            print(f"❌ 场景加载失败")
            return
        
        await asyncio.sleep(2)
        
        # 创建GameObject
        print("\n" + "=" * 80)
        print("创建GameObject")
        print("=" * 80)
        result = await call_tool(session, url, headers, 'manage_gameobject', {
            'action': 'create',
            'type': 'UnityEditor.UI.Button'
        }, tool_id=2)
        
        print(f"\n结果: {json.dumps(result, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    asyncio.run(main())
