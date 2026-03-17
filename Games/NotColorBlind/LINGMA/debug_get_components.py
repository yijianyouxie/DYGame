#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调试获取组件的问题"""
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
    
    async with session.post(url, headers=headers, json=request) as response:
        text = await response.text()
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('data:'):
                data = json.loads(line[5:])
                structured = data.get('result', {}).get('structuredContent', {})
                return structured
        return {}

async def get_resource(session, url, headers, resource_path, resource_id=1):
    """通过resource获取数据"""
    request = {
        'jsonrpc': '2.0',
        'id': resource_id,
        'method': 'resources/read',
        'params': {
            'uri': resource_path
        }
    }
    
    print(f"\n请求Resource: {resource_path}")
    async with session.post(url, headers=headers, json=request) as response:
        text = await response.text()
        print(f"响应状态: {response.status}")
        print(f"完整响应: {text[:500]}")
        
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('data:'):
                data = json.loads(line[5:])
                return data
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
        
        # 加载Start场景
        print("\n" + "=" * 80)
        print("加载Start场景")
        print("=" * 80)
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'load',
            'build_index': 0
        }, tool_id=1)
        
        if result and result.get('success'):
            print(f"✅ 场景加载成功: {result}")
        else:
            print(f"❌ 场景加载失败: {result}")
            return
        
        await asyncio.sleep(2)
        
        # 查找LeaderboardButton
        print("\n" + "=" * 80)
        print("查找LeaderboardButton")
        print("=" * 80)
        find_result = await call_tool(session, url, headers, 'find_gameobjects', {
            'search_term': 'LeaderboardButton',
            'search_method': 'by_name'
        }, tool_id=2)
        
        print(f"查找结果: {json.dumps(find_result, indent=2, ensure_ascii=False)}")
        
        if not find_result or not find_result.get('data', {}).get('instanceIDs'):
            print("❌ 未找到LeaderboardButton")
            return
        
        leaderboard_id = str(find_result['data']['instanceIDs'][0])
        print(f"✅ 找到 LeaderboardButton: ID={leaderboard_id}")
        
        # 获取Image组件
        print("\n" + "=" * 80)
        print("获取Image组件")
        print("=" * 80)
        resource_path = f'mcpforunity://scene/gameobject/{leaderboard_id}/components'
        result = await get_resource(session, url, headers, resource_path, resource_id=3)
        
        print(f"\n完整结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result and result.get('result', {}).get('contents'):
            print(f"\n✅ 获取到 {len(result['result']['contents'])} 个内容项")
            for i, content in enumerate(result['result']['contents'], 1):
                print(f"\n内容项 {i}:")
                print(f"  mimeType: {content.get('mimeType')}")
                if content.get('mimeType') == 'application/json':
                    text = content.get('text', '')
                    print(f"  文本长度: {len(text)}")
                    print(f"  文本内容: {text[:1000]}")
                    try:
                        data = json.loads(text)
                        print(f"  解析后: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    except:
                        print(f"  JSON解析失败")
        else:
            print("❌ 未获取到组件数据")

if __name__ == "__main__":
    asyncio.run(main())
