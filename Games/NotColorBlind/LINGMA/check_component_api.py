#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看manage_components工具的正确用法
"""
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

async def main():
    url = "http://127.0.0.1:8080/mcp"
    
    async with aiohttp.ClientSession() as session:
        # 初始化session
        print("初始化MCP session...")
        session_id = await init_session(session, url)
        if not session_id:
            print("❌ 初始化失败")
            return
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream',
            'mcp-session-id': session_id
        }
        
        print(f"✅ MCP连接成功")
        
        # 列出所有工具
        print("\n列出所有工具...")
        request = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'tools/list'
        }
        
        async with session.post(url, headers=headers, json=request) as response:
            text = await response.text()
            data = json.loads(text)
            tools = data.get('result', {}).get('tools', [])
            
            # 查找manage_components工具
            for tool in tools:
                name = tool.get('name', '')
                if 'component' in name.lower():
                    print(f"\n工具: {name}")
                    desc = tool.get('description', '')
                    input_schema = tool.get('inputSchema', {})
                    print(f"描述: {desc}")
                    print(f"参数: {json.dumps(input_schema, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    asyncio.run(main())
