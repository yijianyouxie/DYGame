#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""获取Start场景LeaderboardButton的完整信息"""

import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def get_session_and_hierarchy():
    url = 'http://127.0.0.1:8080/mcp'
    base_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream'
    }
    
    print("="*60)
    print("获取Start场景LeaderboardButton信息")
    print("="*60)
    
    async with aiohttp.ClientSession() as session:
        # 初始化session
        print("\n[1/7] 初始化MCP session...")
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
        
        session_id = None
        async with session.post(url, headers=base_headers, json=init_message) as response:
            session_id = response.headers.get('mcp-session-id')
            print(f"✅ Session ID: {session_id}")
        
        if not session_id:
            print("❌ 无法获取session ID")
            return
        
        headers = {**base_headers, 'mcp-session-id': session_id}
        
        # 发送initialized
        await session.post(url, headers=headers, json={
            'jsonrpc': '2.0',
            'method': 'notifications/initialized'
        })
        
        await asyncio.sleep(0.5)
        
        # 加载Start场景
        print("\n[2/7] 加载Start场景...")
        load_scene = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'tools/call',
            'params': {
                'name': 'manage_scene',
                'arguments': {
                    'action': 'load',
                    'scene_name': 'StartScene'
                }
            }
        }
        
        async with session.post(url, headers=headers, json=load_scene) as response:
            text = await response.text()
            if 'success' in text:
                print("✅ Start场景加载成功")
            else:
                print(f"响应: {text[:200]}")
        
        await asyncio.sleep(2)
        
        # 获取层级
        print("\n[3/7] 获取场景层级...")
        get_hierarchy = {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'tools/call',
            'params': {
                'name': 'manage_scene',
                'arguments': {
                    'action': 'get_hierarchy'
                }
            }
        }
        
        hierarchy = None
        async with session.post(url, headers=headers, json=get_hierarchy) as response:
            text = await response.text()
            for line in text.split('\n'):
                line = line.strip()
                if line.startswith('data:'):
                    data = json.loads(line[5:])
                    structured = data.get('result', {}).get('structuredContent', {})
                    if structured and structured.get('success'):
                        hierarchy = structured
                        print(f"✅ 获取到层级，节点数: {len(structured.get('hierarchy', []))}")
        
        await asyncio.sleep(0.5)
        
        # 查找LeaderboardButton
        print("\n[4/7] 查找LeaderboardButton...")
        find_button = {
            'jsonrpc': '2.0',
            'id': 3,
            'method': 'tools/call',
            'params': {
                'name': 'manage_gameobject',
                'arguments': {
                    'action': 'find',
                    'search_method': 'by_name',
                    'name': 'LeaderboardButton'
                }
            }
        }
        
        button_info = None
        async with session.post(url, headers=headers, json=find_button) as response:
            text = await response.text()
            for line in text.split('\n'):
                line = line.strip()
                if line.startswith('data:'):
                    data = json.loads(line[5:])
                    structured = data.get('result', {}).get('structuredContent', {})
                    if structured and structured.get('success'):
                        game_objects = structured.get('game_objects', [])
                        if game_objects:
                            button_info = game_objects[0]
                            button_id = button_info.get('instanceID')
                            button_path = button_info.get('path', '')
                            print(f"✅ 找到按钮: ID={button_id}, Path={button_path}")
        
        if not button_info:
            print("❌ 未找到LeaderboardButton")
            return
        
        # 获取RectTransform
        print(f"\n[5/7] 获取RectTransform...")
        get_rect = {
            'jsonrpc': '2.0',
            'id': 4,
            'method': 'tools/call',
            'params': {
                'name': 'manage_components',
                'arguments': {
                    'action': 'get',
                    'search_method': 'by_id',
                    'id': button_id,
                    'component_type': 'RectTransform'
                }
            }
        }
        
        rect_props = {}
        async with session.post(url, headers=headers, json=get_rect) as response:
            text = await response.text()
            for line in text.split('\n'):
                line = line.strip()
                if line.startswith('data:'):
                    data = json.loads(line[5:])
                    structured = data.get('result', {}).get('structuredContent', {})
                    if structured and structured.get('success'):
                        props = structured.get('properties', {})
                        rect_props = {
                            'anchorMin': props.get('anchorMin'),
                            'anchorMax': props.get('anchorMax'),
                            'anchoredPosition': props.get('anchoredPosition'),
                            'sizeDelta': props.get('sizeDelta'),
                            'pivot': props.get('pivot')
                        }
                        print(f"✅ RectTransform: {json.dumps(rect_props, indent=2)}")
        
        # 获取Image sprite
        print(f"\n[6/7] 获取Image组件...")
        get_image = {
            'jsonrpc': '2.0',
            'id': 5,
            'method': 'tools/call',
            'params': {
                'name': 'manage_components',
                'arguments': {
                    'action': 'get',
                    'search_method': 'by_id',
                    'id': button_id,
                    'component_type': 'Image'
                }
            }
        }
        
        image_info = {}
        async with session.post(url, headers=headers, json=get_image) as response:
            text = await response.text()
            for line in text.split('\n'):
                line = line.strip()
                if line.startswith('data:'):
                    data = json.loads(line[5:])
                    structured = data.get('result', {}).get('structuredContent', {})
                    if structured and structured.get('success'):
                        props = structured.get('properties', {})
                        sprite = props.get('sprite', {})
                        image_info = {
                            'spriteName': sprite.get('name', ''),
                            'spritePath': sprite.get('path', ''),
                            'color': props.get('color')
                        }
                        print(f"✅ Image: {json.dumps(image_info, indent=2)}")
        
        # 获取Text
        print(f"\n[7/7] 获取Text组件...")
        text_path = f"{button_path}/Text"
        find_text = {
            'jsonrpc': '2.0',
            'id': 6,
            'method': 'tools/call',
            'params': {
                'name': 'manage_gameobject',
                'arguments': {
                    'action': 'find',
                    'search_method': 'by_path',
                    'path': text_path
                }
            }
        }
        
        text_info = {}
        async with session.post(url, headers=headers, json=find_text) as response:
            text = await response.text()
            for line in text.split('\n'):
                line = line.strip()
                if line.startswith('data:'):
                    data = json.loads(line[5:])
                    structured = data.get('result', {}).get('structuredContent', {})
                    if structured and structured.get('success'):
                        game_objects = structured.get('game_objects', [])
                        if game_objects:
                            text_id = game_objects[0].get('instanceID')
                            print(f"✅ 找到Text对象: ID={text_id}")
                            
                            # 获取Text组件
                            get_text_comp = {
                                'jsonrpc': '2.0',
                                'id': 7,
                                'method': 'tools/call',
                                'params': {
                                    'name': 'manage_components',
                                    'arguments': {
                                        'action': 'get',
                                        'search_method': 'by_id',
                                        'id': text_id,
                                        'component_type': 'Text'
                                    }
                                }
                            }
                            
                            await asyncio.sleep(0.3)
                            async with session.post(url, headers=headers, json=get_text_comp) as resp:
                                resp_text = await resp.text()
                                for l in resp_text.split('\n'):
                                    l = l.strip()
                                    if l.startswith('data:'):
                                        d = json.loads(l[5:])
                                        s = d.get('result', {}).get('structuredContent', {})
                                        if s and s.get('success'):
                                            p = s.get('properties', {})
                                            text_info = {
                                                'text': p.get('text'),
                                                'fontSize': p.get('fontSize'),
                                                'font': p.get('font', {}).get('name', ''),
                                                'alignment': p.get('alignment'),
                                                'color': p.get('color')
                                            }
                                            print(f"✅ Text: {json.dumps(text_info, indent=2)}")
        
        print("\n" + "="*60)
        print("汇总信息:")
        print("="*60)
        result = {
            'button': {
                'instanceID': button_id,
                'path': button_path
            },
            'rectTransform': rect_props,
            'image': image_info,
            'text': text_info
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 保存到文件
        with open('leaderboard_button_info.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print("\n✅ 信息已保存到 leaderboard_button_info.json")

if __name__ == '__main__':
    asyncio.run(get_session_and_hierarchy())
