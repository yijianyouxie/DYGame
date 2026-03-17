#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def main():
    async with aiohttp.ClientSession() as session:
        base_url = "http://localhost:8080/sse"
        base_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream'
        }
        
        # 初始化session
        print("初始化MCP session...")
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
        
        async with session.post(base_url, headers=base_headers, json=init_message) as response:
            session_id = response.headers.get('mcp-session-id')
            print(f"Session ID: {session_id}")
            
            # 尝试获取当前活动场景
            print("\n获取当前活动场景...")
            request = {
                'jsonrpc': '2.0',
                'id': 1,
                'method': 'tools/call',
                'params': {
                    'name': 'manage_scene',
                    'arguments': {
                        'action': 'get_active'
                    }
                }
            }
            
            async with session.post(base_url, headers=base_headers, json=request) as resp:
                text = await resp.text()
                print(f"响应: {text[:500]}")
            
            # 尝试列出所有工具
            print("\n列出所有可用工具...")
            request = {
                'jsonrpc': '2.0',
                'id': 2,
                'method': 'tools/list'
            }
            
            async with session.post(base_url, headers=base_headers, json=request) as resp:
                text = await resp.text()
                data = json.loads(text)
                tools = data.get('result', {}).get('tools', [])
                print(f"找到 {len(tools)} 个工具:")
                for tool in tools[:5]:
                    print(f"  - {tool.get('name')}")

if __name__ == "__main__":
    asyncio.run(main())
