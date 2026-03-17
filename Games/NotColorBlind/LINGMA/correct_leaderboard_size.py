#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
正确设置LeaderboardButton大小为Button的一半
使用manage_components工具的set_property action
"""
import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def correct_leaderboard_size():
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        print("🔄 初始化连接...")
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "correct-size", "version": "1.0.0"}
            }
        }
        
        session_id = None
        async with session.post(url, headers=base_headers, json=init_message) as response:
            session_id = response.headers.get('mcp-session-id')
            print(f"✅ Session ID: {session_id}")
            
            if not session_id:
                print("❌ 无法获取 Session ID")
                return
            
            if response.status == 200:
                async for line in response.content:
                    if line.decode('utf-8').strip().startswith('data:'):
                        break
        
        headers = {**base_headers, 'mcp-session-id': session_id}
        
        await session.post(url, headers=headers, json={
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        })
        
        # 设置SizeDelta的X值
        print("\n🔄 设置m_SizeDelta.x = 200...")
        set_sizedelta_x = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "manage_components",
                "arguments": {
                    "action": "set_property",
                    "target": "LeaderboardButton",
                    "search_method": "by_name",
                    "component_type": "RectTransform",
                    "property": "sizeDelta",
                    "value": {"x": 200, "y": 75}
                }
            }
        }
        
        async with session.post(url, headers=headers, json=set_sizedelta_x) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        result = data.get('result', {}).get('structuredContent', {})
                        if result.get('success'):
                            print(f"✅ sizeDelta设置成功!")
                        else:
                            print(f"❌ 失败: {result.get('error', 'Unknown')}")
                            print(f"完整响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
                        break
        
        await asyncio.sleep(0.3)
        
        # 保存场景
        print("\n🔄 保存场景...")
        save_scene = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "manage_scene",
                "arguments": {
                    "action": "save"
                }
            }
        }
        
        async with session.post(url, headers=headers, json=save_scene) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        print(f"✅ 场景已保存")
                        break
        
        print("\n✅ 完成!")
        print("LeaderboardButton大小已设置为Button的一半: 200 x 75")

asyncio.run(correct_leaderboard_size())
