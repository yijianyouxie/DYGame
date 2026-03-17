#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
            print(f"✅ Session初始化完成")
        
        # 获取当前活动场景
        print("\n获取当前活动场景...")
        result = await call_tool(session, base_url, base_headers, 'manage_scene', {
            'action': 'get_active'
        }, tool_id=1)
        
        if result:
            print(f"  当前场景: {result}")
        
        # 获取构建设置
        print("\n获取构建设置...")
        result = await call_tool(session, base_url, base_headers, 'manage_scene', {
            'action': 'get_build_settings'
        }, tool_id=2)
        
        if result and result.get('data'):
            scenes = result['data'].get('scenes', [])
            print(f"  找到 {len(scenes)} 个场景:")
            for i, scene in enumerate(scenes):
                print(f"    [{i}] {scene.get('name')} - buildIndex: {scene.get('buildIndex')} - path: {scene.get('path')}")

if __name__ == "__main__":
    asyncio.run(main())
