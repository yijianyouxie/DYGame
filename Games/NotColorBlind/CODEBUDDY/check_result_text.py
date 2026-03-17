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
                structured = data.get('result', {}).get('structuredContent', {})
                return structured
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
        
        # 加载ResultScene
        print("加载ResultScene...")
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'load',
            'build_index': 2
        }, tool_id=1)
        
        # 查找ResultLeaderboardButton
        print("查找ResultLeaderboardButton...")
        result = await call_tool(session, url, headers, 'find_gameobjects', {
            'scene_name': 'ResultScene',
            'name_pattern': 'ResultLeaderboardButton'
        }, tool_id=100)
        
        print(f"查找结果: {result}")
        
        if not result or not result.get('gameobjects'):
            print("[!] 未找到ResultLeaderboardButton")
            return
        
        btn_id = result['gameobjects'][0]['id']
        print(f"[+] 找到ResultLeaderboardButton，ID: {btn_id}\n")
        
        # 查找Text子对象
        print("查找Text子对象...")
        result = await call_tool(session, url, headers, 'find_gameobjects', {
            'scene_name': 'ResultScene',
            'name_pattern': 'Text'
        }, tool_id=200)
        
        print(f"查找结果: {result}")
        
        if result and result.get('gameobjects'):
            for obj in result['gameobjects']:
                print(f"  - {obj.get('name')} (ID: {obj.get('id')}, Parent: {obj.get('parent_id')})")

if __name__ == '__main__':
    asyncio.run(main())
