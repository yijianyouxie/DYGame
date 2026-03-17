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
                if data.get('result', {}).get('contents'):
                    content = data['result']['contents'][0]
                    inner_text = content.get('text', '')
                    if inner_text:
                        try:
                            return json.loads(inner_text)
                        except:
                            return None
                return data
        return {}

async def get_resource(session, url, headers, resource_path, resource_id=1):
    request = {
        'jsonrpc': '2.0',
        'id': resource_id,
        'method': 'resources/read',
        'params': {
            'uri': resource_path
        }
    }
    
    async with session.post(url, headers=headers, json=request) as response:
        text = await response.text()
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('data:'):
                data = json.loads(line[5:])
                if data.get('result', {}).get('contents'):
                    content = data['result']['contents'][0]
                    inner_text = content.get('text', '')
                    if inner_text:
                        try:
                            return json.loads(inner_text)
                        except:
                            return None
                return data
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
        
        # 获取场景层次结构
        print("获取场景层次结构...")
        result = await get_resource(session, url, headers, 'mcpforunity://scene/hierarchy', resource_id=100)
        
        if not result or not result.get('data', {}).get('roots'):
            print("[!] 无法获取场景层次")
            return
        
        print("[+] 获取场景层次成功\n")
        
        # 查找ResultLeaderboardButton
        def find_object_by_name(objects, name):
            for obj in objects:
                if obj.get('name') == name:
                    return obj
                if 'children' in obj:
                    found = find_object_by_name(obj['children'], name)
                    if found:
                        return found
            return None
        
        btn = find_object_by_name(result['data']['roots'], 'ResultLeaderboardButton')
        if not btn:
            print("[!] 未找到ResultLeaderboardButton")
            return
        
        btn_id = btn['id']
        print(f"[+] 找到ResultLeaderboardButton，ID: {btn_id}")
        
        # 查找Text子对象
        text_obj = find_object_by_name(btn.get('children', []), 'Text')
        if not text_obj:
            print("[!] 未找到Text子对象")
            return
        
        text_id = text_obj['id']
        print(f"[+] 找到Text子对象，ID: {text_id}\n")
        
        # 检查Text组件
        print("检查Text组件...")
        uri = f'mcpforunity://scene/gameobject/{text_id}/components'
        data = await get_resource(session, url, headers, uri, resource_id=200)
        
        if not data or not data.get('data', {}).get('components'):
            print("[!] 无法获取组件信息")
            return
        
        components = data['data']['components']
        print(f"  现有组件数量: {len(components)}")
        for comp in components:
            print(f"    - {comp.get('typeName', 'Unknown')}")
        
        has_text = any('UnityEngine.UI.Text' in comp.get('typeName', '') for comp in components)
        
        if not has_text:
            print("\n[!] Text组件不存在，开始添加...")
            
            # 添加Text组件
            result = await call_tool(session, url, headers, 'manage_components', {
                'action': 'add',
                'target': {
                    'id': text_id,
                    'scene_name': 'ResultScene'
                },
                'component_type': 'UnityEngine.UI.Text'
            }, tool_id=300)
            
            if result and result.get('success'):
                print("[+] Text组件添加成功")
            else:
                print(f"[!] Text组件添加失败: {result}")
                return
            
            # 设置Text属性
            print("设置Text属性...")
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
            
            if result and result.get('success'):
                print("[+] Text属性设置成功")
            else:
                print(f"[!] Text属性设置失败: {result}")
            
            # 验证
            print("再次验证...")
            data = await get_resource(session, url, headers, uri, resource_id=400)
            if data and data.get('data', {}).get('components'):
                components = data['data']['components']
                has_text = any('UnityEngine.UI.Text' in comp.get('typeName', '') for comp in components)
                
                if has_text:
                    print("[+] Text组件验证成功")
                    for comp in components:
                        if 'UnityEngine.UI.Text' in comp.get('typeName', ''):
                            props = comp.get('properties', {})
                            print(f"    文字: {props.get('text', '')}")
                            print(f"    字号: {props.get('fontSize', '')}")
                else:
                    print("[!] Text组件仍然不存在")
        else:
            print("\n[+] Text组件已存在")
        
        # 保存场景
        print("\n保存ResultScene...")
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'save'
        }, tool_id=500)
        
        if result and result.get('success'):
            print("[+] ResultScene保存成功")
        else:
            print("[!] ResultScene保存失败")

if __name__ == '__main__':
    asyncio.run(main())
