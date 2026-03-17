#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""获取场景层级并查找按钮"""

import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def main():
    # 读取session ID
    with open('mcp-session-id.txt', 'r') as f:
        session_id = f.read().strip()
    
    url = "http://localhost:8080/mcp"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
        'X-Session-Id': session_id
    }
    
    async with aiohttp.ClientSession() as session:
        # 加载Start场景
        print("加载Start场景...")
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
            print(f"状态码: {response.status}")
            text = await response.text()
            print(text[:800])
        
        print("\n等待3秒...")
        await asyncio.sleep(3)
        
        # 获取层级
        print("\n获取场景层级...")
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
        
        async with session.post(url, headers=headers, json=get_hierarchy) as response:
            text = await response.text()
            print(text[:3000])
            # 保存完整层级到文件
            with open('hierarchy_output.json', 'w', encoding='utf-8') as f:
                f.write(text)
            print("\n完整层级已保存到 hierarchy_output.json")

if __name__ == '__main__':
    asyncio.run(main())
