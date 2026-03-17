#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证按钮是否存在于正确的场景中
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

async def check_buttons_in_scene(session, url, headers, scene_name, build_index, expected_buttons):
    """检查场景中的按钮"""
    print("\n" + "=" * 80)
    print(f"检查 {scene_name} (build_index: {build_index})")
    print("=" * 80)
    
    # 加载场景
    print(f"\n加载 {scene_name}...")
    result = await call_tool(session, url, headers, 'manage_scene', {
        'action': 'load',
        'build_index': build_index
    }, tool_id=100 + build_index)
    
    if not result or not result.get('success'):
        print(f"  ❌ 场景加载失败")
        return False
    
    print(f"  ✅ 场景加载成功")
    
    # 检查每个预期按钮
    for button_name in expected_buttons:
        print(f"\n查找 {button_name}...")
        result = await call_tool(session, url, headers, 'find_gameobjects', {
            'search_term': button_name,
            'search_method': 'by_name'
        }, tool_id=200 + build_index * 10 + expected_buttons.index(button_name))
        
        if result and result.get('data', {}).get('instanceIDs'):
            ids = result['data']['instanceIDs']
            print(f"  ✅ 找到 {len(ids)} 个 {button_name}: {ids}")
        else:
            print(f"  ❌ 未找到 {button_name}")
            return False
    
    return True

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
        await asyncio.sleep(1)
        
        # 检查各个场景
        results = []
        
        # StartScene - 应该有 LeaderboardButton
        result = await check_buttons_in_scene(
            session, url, headers, 'Start', 0, ['LeaderboardButton']
        )
        results.append(('Start', result))
        
        # LevelScene - 应该有 ReturnButton
        result = await check_buttons_in_scene(
            session, url, headers, 'LevelScene', 1, ['ReturnButton']
        )
        results.append(('LevelScene', result))
        
        # ResultScene - 应该有 ResultLeaderboardButton
        result = await check_buttons_in_scene(
            session, url, headers, 'ResultScene', 2, ['ResultLeaderboardButton']
        )
        results.append(('ResultScene', result))
        
        # 输出总结
        print("\n" + "=" * 80)
        print("验证结果总结")
        print("=" * 80)
        
        for scene_name, success in results:
            status = "✅ 通过" if success else "❌ 失败"
            print(f"  {scene_name}: {status}")

if __name__ == "__main__":
    asyncio.run(main())
