#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""获取当前Unity项目的所有场景列表"""
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
        
        # 获取构建设置中的场景列表
        print("\n获取Build Settings中的场景列表...")
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'get_build_settings'
        }, tool_id=1)
        
        print(f"\n结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # 获取当前活动场景
        print("\n" + "=" * 80)
        print("获取当前活动场景...")
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'get_active'
        }, tool_id=2)
        
        print(f"\n结果: {json.dumps(result, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    asyncio.run(main())
