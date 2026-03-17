#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查manage_scene工具的正确参数"""
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
            
            # 读取所有数据
            full_response = await response.text()
            for line in full_response.split('\n'):
                if line.strip().startswith('data:'):
                    pass
        
        headers = {**base_headers, 'mcp-session-id': session_id}
        
        # 等待初始化完成
        await asyncio.sleep(0.5)
        
        # 发送 initialized 通知
        await session.post(url, headers=headers, json={
            'jsonrpc': '2.0',
            'method': 'notifications/initialized'
        })
        
        await asyncio.sleep(0.5)
        
        # 查询工具列表
        request = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'tools/list'
        }
        
        async with session.post(url, headers=headers, json=request) as response:
            full_response = await response.text()
            tools = None
            for line in full_response.split('\n'):
                line = line.strip()
                if line.startswith('data:'):
                    data = json.loads(line[5:])
                    tools = data.get('result', {})
                    break
            
            if tools:
                # 打印 manage_scene 工具的详细信息
                for tool in tools.get('tools', []):
                    if tool['name'] == 'manage_scene':
                        print("\n" + "=" * 80)
                        print("MANAGE_SCENE TOOL:")
                        print("=" * 80)
                        print(json.dumps(tool, indent=2, ensure_ascii=False))
        
        await asyncio.sleep(0.5)
        
        # 尝试不同的参数组合来加载场景
        print("\n" + "=" * 80)
        print("尝试加载场景...")
        print("=" * 80)
        
        # 尝试1: 使用 name
        print("\n尝试1: 使用 'name' 参数")
        request = {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'tools/call',
            'params': {
                'name': 'manage_scene',
                'arguments': {
                    'action': 'load',
                    'name': 'StartScene'
                }
            }
        }
        
        async with session.post(url, headers=headers, json=request) as response:
            full_response = await response.text()
            for line in full_response.split('\n'):
                line = line.strip()
                if line.startswith('data:'):
                    data = json.loads(line[5:])
                    result = data.get('result', {}).get('structuredContent', {})
                    print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
                    break
        
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
