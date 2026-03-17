#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重置场景状态"""
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
        session_id = await init_session(session, url)
        if not session_id:
            print("❌ 初始化失败")
            return
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream',
            'mcp-session-id': session_id
        }
        
        await asyncio.sleep(0.5)
        
        # 保存当前场景
        print("保存当前场景...")
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'save'
        }, tool_id=1)
        
        if result and result.get('success'):
            print("✅ 场景保存成功")
        else:
            print(f"⚠️ 场景保存: {result}")
        
        # 加载Start场景（build_index: 0）
        print("\n加载Start场景...")
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'load',
            'build_index': 0
        }, tool_id=2)
        
        if result and result.get('success'):
            print("✅ Start场景加载成功")
        else:
            print(f"❌ Start场景加载失败: {result}")
        
        await asyncio.sleep(2)
        
        # 查找Canvas
        print("\n查找Start场景的Canvas...")
        result = await call_tool(session, url, headers, 'find_gameobjects', {
            'search_term': 'Canvas',
            'search_method': 'by_name'
        }, tool_id=3)
        
        if result and result.get('data', {}).get('instanceIDs'):
            canvas_ids = result['data']['instanceIDs']
            print(f"✅ 找到 {len(canvas_ids)} 个Canvas:")
            for i, canvas_id in enumerate(canvas_ids, 1):
                print(f"   Canvas {i}: ID={canvas_id}")
        else:
            print("❌ 未找到Canvas")

if __name__ == "__main__":
    asyncio.run(main())
