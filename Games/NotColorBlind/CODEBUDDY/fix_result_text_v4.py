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
        
        if not result or not result.get('success'):
            print("[!] ResultScene加载失败")
            return
        
        print("[+] ResultScene加载成功\n")
        
        # 查找ResultLeaderboardButton
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
        
        # 获取按钮详细信息（包含children）
        print("\n获取按钮详细信息...")
        result = await call_tool(session, url, headers, 'find_gameobjects', {
            'search_term': 'ResultLeaderboardButton',
            'search_method': 'by_name'
        }, tool_id=101)
        
        print(f"按钮详细信息: {result}")
        
        # 查找所有Text对象，找到parent_id为btn_id的
        print("\n查找Text子对象...")
        result = await call_tool(session, url, headers, 'find_gameobjects', {
            'search_term': 'Text',
            'search_method': 'by_name'
        }, tool_id=101)
        
        if not result or not result.get('data', {}).get('instanceIDs'):
            print("[!] 未找到任何Text对象")
            return
        
        text_ids = result['data']['instanceIDs']
        print(f"[+] 找到 {len(text_ids)} 个Text对象")
        
        # 遍历找到parent_id为btn_id的
        text_id = None
        for tid in text_ids:
            result = await call_tool(session, url, headers, 'find_gameobjects', {
                'search_term': str(tid)
            }, tool_id=102 + tid % 10)
            
            print(f"  查询Text ID {tid}, result: {result}")
            
            if result and result.get('gameobjects'):
                obj = result['gameobjects'][0]
                parent_id = obj.get('parent_id')
                print(f"  Text ID {tid}, parent_id: {parent_id}")
                if parent_id == btn_id:
                    text_id = tid
                    print(f"[+] 找到ResultLeaderboardButton的子Text，ID: {text_id}")
                    break
        
        if not text_id:
            print("[!] 未找到ResultLeaderboardButton的子Text")
            return
        
        # 检查Text组件
        print("\n检查Text组件...")
        result = await call_tool(session, url, headers, 'find_gameobjects', {
            'search_method': 'by_instance_id',
            'search_term': str(text_id)
        }, tool_id=200)
        
        if not result or not result.get('gameobjects'):
            print("[!] 无法获取Text对象")
            return
        
        text_obj = result['gameobjects'][0]
        components = text_obj.get('components', [])
        print(f"  现有组件: {[c.get('type_name') for c in components]}")
        
        has_text = any('UnityEngine.UI.Text' in c.get('type_name', '') for c in components)
        
        if not has_text:
            print("\n[!] Text组件不存在，开始添加...")
            
            result = await call_tool(session, url, headers, 'manage_components', {
                'action': 'add',
                'target': text_id,
                'component_type': 'UnityEngine.UI.Text'
            }, tool_id=300)
            
            print(f"添加结果: {result}")
            
            if result and result.get('success'):
                print("[+] Text组件添加成功")
            else:
                print("[!] 添加失败")
                return
            
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
                    'fontSize': 32,
                    'alignment': 4,
                    'font': 'Assets/Font/FZLTH-GBK.TTF'
                }
            }, tool_id=301)
            
            print(f"设置属性结果: {result}")
            
            if result and result.get('success'):
                print("[+] 属性设置成功")
        else:
            print("\n[+] Text组件已存在")
        
        # 保存场景
        print("\n保存ResultScene...")
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'save'
        }, tool_id=500)
        
        if result and result.get('success'):
            print("[+] 保存成功")
        else:
            print("[!] 保存失败")

if __name__ == '__main__':
    asyncio.run(main())
