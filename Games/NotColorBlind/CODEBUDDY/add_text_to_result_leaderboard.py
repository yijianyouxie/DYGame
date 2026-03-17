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
        print(f"[+] 找到ResultLeaderboardButton，ID: {btn_id}\n")
        
        # 创建新的Text子对象
        print("创建Text子对象...")
        result = await call_tool(session, url, headers, 'manage_gameobject', {
            'action': 'create',
            'name': 'Text',
            'parent': btn_id
        }, tool_id=200)
        
        print(f"创建结果: {result}")
        
        if not result or not result.get('success'):
            print("[!] Text对象创建失败")
            return
        
        print("[+] Text对象创建成功\n")
        
        # 查找刚创建的Text对象
        print("查找Text对象...")
        result = await call_tool(session, url, headers, 'find_gameobjects', {
            'search_term': 'Text',
            'search_method': 'by_name'
        }, tool_id=201)
        
        if not result or not result.get('data', {}).get('instanceIDs'):
            print("[!] 未找到Text对象")
            return
        
        # 获取最新的Text对象ID（最后一个）
        text_ids = result['data']['instanceIDs']
        text_id = text_ids[-1]  # 取最后一个
        print(f"[+] 找到Text对象，ID: {text_id}\n")
        
        # 添加RectTransform组件
        print("添加RectTransform组件...")
        result = await call_tool(session, url, headers, 'manage_components', {
            'action': 'add',
            'target': text_id,
            'component_type': 'UnityEngine.RectTransform'
        }, tool_id=210)
        
        if result and result.get('success'):
            print("[+] RectTransform添加成功")
        else:
            print("[!] RectTransform添加失败")
        
        # 设置RectTransform属性
        result = await call_tool(session, url, headers, 'manage_components', {
            'action': 'set_property',
            'target': text_id,
            'component_type': 'UnityEngine.RectTransform',
            'property': 'anchorMin',
            'value': {'x': 0, 'y': 0}
        }, tool_id=211)
        
        result = await call_tool(session, url, headers, 'manage_components', {
            'action': 'set_property',
            'target': text_id,
            'component_type': 'UnityEngine.RectTransform',
            'property': 'anchorMax',
            'value': {'x': 1, 'y': 1}
        }, tool_id=212)
        
        result = await call_tool(session, url, headers, 'manage_components', {
            'action': 'set_property',
            'target': text_id,
            'component_type': 'UnityEngine.RectTransform',
            'property': 'pivot',
            'value': {'x': 0.5, 'y': 0.5}
        }, tool_id=213)
        
        result = await call_tool(session, url, headers, 'manage_components', {
            'action': 'set_property',
            'target': text_id,
            'component_type': 'UnityEngine.RectTransform',
            'property': 'sizeDelta',
            'value': {'x': 0, 'y': 0}
        }, tool_id=214)
        
        print("[+] RectTransform属性设置完成")
        
        # 添加CanvasRenderer
        print("添加CanvasRenderer...")
        result = await call_tool(session, url, headers, 'manage_components', {
            'action': 'add',
            'target': text_id,
            'component_type': 'UnityEngine.UI.CanvasRenderer'
        }, tool_id=220)
        
        if result and result.get('success'):
            print("[+] CanvasRenderer添加成功")
        
        # 添加Text组件
        print("添加Text组件...")
        result = await call_tool(session, url, headers, 'manage_components', {
            'action': 'add',
            'target': text_id,
            'component_type': 'UnityEngine.UI.Text'
        }, tool_id=230)
        
        if result and result.get('success'):
            print("[+] Text组件添加成功")
        else:
            print("[!] Text组件添加失败")
            return
        
        # 设置Text属性
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
                'alignment': 4,
                'color': {'r': 1, 'g': 1, 'b': 1, 'a': 1}
            }
        }, tool_id=231)
        
        print(f"设置Text属性结果: {result}")
        
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
