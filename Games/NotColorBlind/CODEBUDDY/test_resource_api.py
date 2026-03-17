#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
                if data.get('result', {}).get('contents'):
                    content = data['result']['contents'][0]
                    inner_text = content.get('text', '')
                    if inner_text:
                        try:
                            return json.loads(inner_text)
                        except:
                            return None
                return data
        return {}

async def main():
    url = "http://127.0.0.1:8080/mcp"
    
    async with aiohttp.ClientSession() as session:
        print("初始化MCP session...")
        session_id = await init_session(session, url)
        if not session_id:
            print("[!] 初始化失败")
            return
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream',
            'mcp-session-id': session_id
        }
        
        print(f"[+] MCP连接成功\n")
        
        # 测试list_resources获取正确的URI
        print("获取可用资源...")
        result = await call_tool(session, url, headers, 'list_resources', {}, tool_id=100)
        
        print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False)[:1000]}")

if __name__ == '__main__':
    asyncio.run(main())
