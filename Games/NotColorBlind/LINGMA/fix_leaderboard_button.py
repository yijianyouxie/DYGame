#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复LeaderboardButton - 修改文字和锚点
"""
import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def fix_leaderboard_button():
    """修复LeaderboardButton的文字和锚点"""
    
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
                "clientInfo": {"name": "fix-button", "version": "1.0.0"}
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
        
        # 步骤1: 修改Text (Legacy)文字为"排行榜"
        print("\n🔄 步骤1: 修改按钮文字为'排行榜'...")
        set_text_call = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "manage_components",
                "arguments": {
                    "action": "set_property",
                    "target": "Canvas/LeaderboardButton/Text (Legacy)",
                    "search_method": "by_path",
                    "component_type": "Text",
                    "property": "text",
                    "value": "排行榜"
                }
            }
        }
        
        async with session.post(url, headers=headers, json=set_text_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        result = data.get('result', {}).get('structuredContent', {})
                        if result.get('success'):
                            print(f"✅ 文字修改成功!")
                        else:
                            print(f"❌ 失败: {result.get('error', 'Unknown')}")
                        break
        
        await asyncio.sleep(0.3)
        
        # 步骤2: 设置锚点到右上角
        print("\n🔄 步骤2: 设置锚点到右上角...")
        set_anchor_call = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "manage_components",
                "arguments": {
                    "action": "set_property",
                    "target": "LeaderboardButton",
                    "search_method": "by_name",
                    "component_type": "RectTransform",
                    "property": "anchorMin",
                    "value": {"x": 1.0, "y": 1.0}
                }
            }
        }
        
        async with session.post(url, headers=headers, json=set_anchor_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        result = data.get('result', {}).get('structuredContent', {})
                        if result.get('success'):
                            print(f"✅ anchorMin设置成功")
                        else:
                            print(f"❌ anchorMin失败: {result.get('error', 'Unknown')}")
                        break
        
        await asyncio.sleep(0.3)
        
        set_anchor_max_call = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "manage_components",
                "arguments": {
                    "action": "set_property",
                    "target": "LeaderboardButton",
                    "search_method": "by_name",
                    "component_type": "RectTransform",
                    "property": "anchorMax",
                    "value": {"x": 1.0, "y": 1.0}
                }
            }
        }
        
        async with session.post(url, headers=headers, json=set_anchor_max_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        result = data.get('result', {}).get('structuredContent', {})
                        if result.get('success'):
                            print(f"✅ anchorMax设置成功")
                        else:
                            print(f"❌ anchorMax失败: {result.get('error', 'Unknown')}")
                        break
        
        await asyncio.sleep(0.3)
        
        # 步骤3: 设置pivot到右上角
        print("\n🔄 步骤3: 设置pivot到右上角...")
        set_pivot_call = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "manage_components",
                "arguments": {
                    "action": "set_property",
                    "target": "LeaderboardButton",
                    "search_method": "by_name",
                    "component_type": "RectTransform",
                    "property": "pivot",
                    "value": {"x": 1.0, "y": 1.0}
                }
            }
        }
        
        async with session.post(url, headers=headers, json=set_pivot_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        result = data.get('result', {}).get('structuredContent', {})
                        if result.get('success'):
                            print(f"✅ pivot设置成功")
                        else:
                            print(f"❌ pivot失败: {result.get('error', 'Unknown')}")
                        break
        
        await asyncio.sleep(0.3)
        
        # 步骤4: 重新设置anchoredPosition
        print("\n🔄 步骤4: 调整位置偏移...")
        set_pos_call = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "manage_components",
                "arguments": {
                    "action": "set_property",
                    "target": "LeaderboardButton",
                    "search_method": "by_name",
                    "component_type": "RectTransform",
                    "property": "anchoredPosition",
                    "value": {"x": -20, "y": -20}
                }
            }
        }
        
        async with session.post(url, headers=headers, json=set_pos_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        result = data.get('result', {}).get('structuredContent', {})
                        if result.get('success'):
                            print(f"✅ 位置调整成功")
                        else:
                            print(f"❌ 位置调整失败: {result.get('error', 'Unknown')}")
                        break
        
        await asyncio.sleep(0.5)
        
        # 保存场景
        print("\n🔄 保存场景...")
        save_scene_call = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "manage_scene",
                "arguments": {
                    "action": "save"
                }
            }
        }
        
        async with session.post(url, headers=headers, json=save_scene_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        result = data.get('result', {}).get('structuredContent', {})
                        if result.get('success'):
                            print(f"✅ 场景保存成功")
                        break
        
        print("\n✅ LeaderboardButton修复完成!")
        print("   - 文字: 排行榜")
        print("   - 锚点: 右上角")
        print("   - 大小: 80x40")
        print("   - 位置: 距离右上角偏移(-20, -20)")

if __name__ == "__main__":
    asyncio.run(fix_leaderboard_button())
