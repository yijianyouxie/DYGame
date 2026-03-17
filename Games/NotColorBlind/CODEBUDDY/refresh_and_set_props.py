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
        
        # 重新查找Text对象
        print("查找Text对象...")
        result = await call_tool(session, url, headers, 'find_gameobjects', {
            'search_term': 'Text',
            'search_method': 'by_name'
        }, tool_id=100)
        
        if not result or not result.get('data', {}).get('instanceIDs'):
            print("[!] 未找到Text对象")
            return
        
        text_ids = result['data']['instanceIDs']
        print(f"找到 {len(text_ids)} 个Text对象: {text_ids}")
        
        # 尝试给每个Text对象设置属性
        for text_id in text_ids:
            print(f"\n尝试为Text对象 {text_id} 设置属性...")
            
            props = [
                ('text', 'Leaderboard'),
                ('fontSize', 32),
                ('alignment', 4),
                ('font', 'Assets/Font/FZLTH-GBK.TTF')
            ]
            
            for prop_name, prop_value in props:
                print(f"  设置 {prop_name} = {prop_value}...")
                result = await call_tool(session, url, headers, 'manage_components', {
                    'action': 'set_property',
                    'target': text_id,
                    'component_type': 'UnityEngine.UI.Text',
                    'property': prop_name,
                    'value': prop_value
                }, tool_id=200 + text_ids.index(text_id) * 10 + props.index((prop_name, prop_value)))
                
                print(f"  结果: {result}")
                
                if result and result.get('success'):
                    print(f"  [+] {prop_name} 设置成功")
                    break  # 成功一个就退出
        
        # 保存场景
        print("\n保存ResultScene...")
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'save'
        }, tool_id=500)
        
        if result and result.get('success'):
            print("[+] 保存成功")

if __name__ == '__main__':
    asyncio.run(main())
