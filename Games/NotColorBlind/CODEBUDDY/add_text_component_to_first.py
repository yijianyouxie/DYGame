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
        
        # 找到ResultLeaderboardButton
        print("查找ResultLeaderboardButton...")
        result = await call_tool(session, url, headers, 'find_gameobjects', {
            'search_term': 'ResultLeaderboardButton',
            'search_method': 'by_name'
        }, tool_id=100)
        
        if not result or not result.get('data', {}).get('instanceIDs'):
            print("[!] 未找到ResultLeaderboardButton")
            return
        
        btn_id = result['data']['instanceIDs'][0]
        print(f"[+] 找到ResultLeaderboardButton，ID: {btn_id}")
        
        # 列出所有Text对象
        print("\n列出所有Text对象...")
        result = await call_tool(session, url, headers, 'find_gameobjects', {
            'search_term': 'Text',
            'search_method': 'by_name'
        }, tool_id=101)
        
        if not result or not result.get('data', {}).get('instanceIDs'):
            print("[!] 未找到Text对象")
            return
        
        text_ids = result['data']['instanceIDs']
        print(f"找到 {len(text_ids)} 个Text对象: {text_ids}")
        
        # 找到parent_id为btn_id的Text对象
        print(f"\n查找parent_id为{btn_id}的Text...")
        for text_id in text_ids:
            print(f"\n检查Text对象 {text_id}...")
            
            # 使用manage_components的modify action设置parent（如果需要）
            # 先尝试添加Text组件
            result = await call_tool(session, url, headers, 'manage_components', {
                'action': 'add',
                'target': text_id,
                'component_type': 'UnityEngine.UI.Text'
            }, tool_id=200 + text_id % 10)
            
            print(f"添加Text组件结果: {result}")
            
            if result and result.get('success'):
                print(f"[+] Text对象 {text_id} 的Text组件添加成功")
                
                # 设置属性
                result = await call_tool(session, url, headers, 'manage_components', {
                    'action': 'modify',
                    'target': {
                        'id': text_id,
                        'scene_name': 'ResultScene',
                        'component_type': 'UnityEngine.UI.Text'
                    },
                    'properties': {
                        'text': 'Leaderboard',
                        'font': 'Assets/Font/FZLTH-GBK.TTF',
                        'fontSize': 32,
                        'alignment': 4
                    }
                }, tool_id=300 + text_id % 10)
                
                print(f"设置属性结果: {result}")
                
                if result and result.get('success'):
                    print("[+] 属性设置成功")
                    break  # 成功设置一个即可
            else:
                print(f"[!] Text对象 {text_id} 的Text组件添加失败（可能已有）")
                
                # 检查是否已有Text组件
                result = await call_tool(session, url, headers, 'find_gameobjects', {
                    'search_term': str(text_id)
                }, tool_id=400 + text_id % 10)
        
        # 保存场景
        print("\n保存ResultScene...")
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'save'
        }, tool_id=500)
        
        if result and result.get('success'):
            print("[+] 保存成功")

if __name__ == '__main__':
    asyncio.run(main())
