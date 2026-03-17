#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调试获取子对象"""
import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def main():
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream'
    }
    
    async with aiohttp.ClientSession() as session:
        # 初始化
        async with session.post(url, headers=base_headers, json={
            'jsonrpc': '2.0',
            'id': 0,
            'method': 'initialize',
            'params': {
                'protocolVersion': '2024-11-05',
                'capabilities': {},
                'clientInfo': {'name': 'python-script', 'version': '1.0'}
            }
        }) as response:
            session_id = response.headers.get('mcp-session-id')
            print(f"✅ Session ID: {session_id}")
            await response.text()
        
        headers = {**base_headers, 'mcp-session-id': session_id}
        await asyncio.sleep(0.5)
        
        # 加载Start场景
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'load',
            'build_index': 0
        }, tool_id=1)
        
        if not result or not result.get('success'):
            print(f"❌ 场景加载失败")
            return
        
        await asyncio.sleep(2)
        
        # 查找LeaderboardButton
        find_result = await call_tool(session, url, headers, 'find_gameobjects', {
            'search_term': 'LeaderboardButton',
            'search_method': 'by_name'
        }, tool_id=2)
        
        if not find_result or not find_result.get('data', {}).get('instanceIDs'):
            print("❌ 未找到LeaderboardButton")
            return
        
        leaderboard_id = str(find_result['data']['instanceIDs'][0])
        print(f"✅ LeaderboardButton ID: {leaderboard_id}")
        
        # 获取子对象
        print("\n获取子对象...")
        resource_path = f'mcpforunity://scene/gameobject/{leaderboard_id}/children'
        
        request = {
            'jsonrpc': '2.0',
            'id': 3,
            'method': 'resources/read',
            'params': {
                'uri': resource_path
            }
        }
        
        async with session.post(url, headers=headers, json=request) as response:
            text = await response.text()
            print(f"响应: {text[:1000]}")
            
            for line in text.split('\n'):
                line = line.strip()
                if line.startswith('data:'):
                    data = json.loads(line[5:])
                    if data.get('result', {}).get('contents'):
                        content = data['result']['contents'][0]
                        print(f"\nContent type: {content.get('mimeType')}")
                        text_content = content.get('text', '')
                        print(f"Text content: {text_content}")
                        try:
                            parsed = json.loads(text_content)
                            print(f"\n解析后: {json.dumps(parsed, indent=2, ensure_ascii=False)}")
                        except Exception as e:
                            print(f"JSON解析失败: {e}")

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

if __name__ == "__main__":
    asyncio.run(main())
