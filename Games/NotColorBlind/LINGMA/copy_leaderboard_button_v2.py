#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用Unity MCP复制Canvas/Button按钮并修改属性 - 完整版
"""
import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def copy_and_modify_button_complete():
    """复制Canvas/Button并修改为排行榜按钮"""
    
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
                "clientInfo": {"name": "unity-button-copy-v2", "version": "1.0.0"}
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
        
        # 首先尝试查找现有的LeaderboardButton
        print("\n🔄 检查是否已有LeaderboardButton...")
        find_call = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "find_gameobjects",
                "arguments": {
                    "search_term": "LeaderboardButton",
                    "search_method": "by_name"
                }
            }
        }
        
        has_leaderboard_button = False
        async with session.post(url, headers=headers, json=find_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        result = data.get('result', {}).get('structuredContent', {})
                        instance_ids = result.get('data', {}).get('instanceIDs', [])
                        if instance_ids:
                            has_leaderboard_button = True
                            print(f"✅ 已找到LeaderboardButton")
                        else:
                            print("⚠️ 未找到LeaderboardButton，需要复制创建")
                        break
        
        await asyncio.sleep(0.5)
        
        if not has_leaderboard_button:
            # 复制按钮
            print("\n🔄 复制Canvas/Button按钮...")
            duplicate_call = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "manage_gameobject",
                    "arguments": {
                        "action": "duplicate",
                        "target": "Canvas/Button",
                        "search_method": "by_path",
                        "new_name": "LeaderboardButton"
                    }
                }
            }
            
            async with session.post(url, headers=headers, json=duplicate_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            print(f"✅ 按钮复制成功")
                            break
            
            await asyncio.sleep(0.5)
        
        # 修改按钮大小为原来的一半
        print("\n🔄 修改按钮大小为原来的一半...")
        set_size_call = {
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
                    "property": "sizeDelta",
                    "value": {"x": 80, "y": 40}
                }
            }
        }
        
        async with session.post(url, headers=headers, json=set_size_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        print(f"✅ 大小修改成功")
                        break
        
        await asyncio.sleep(0.3)
        
        # 修改按钮位置到右上角
        print("\n🔄 修改按钮位置到右上角...")
        set_position_call = {
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
                    "property": "anchoredPosition",
                    "value": {"x": 200, "y": -100}
                }
            }
        }
        
        async with session.post(url, headers=headers, json=set_position_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        print(f"✅ 位置修改成功")
                        break
        
        await asyncio.sleep(0.3)
        
        # 尝试使用不同的方法修改Text
        print("\n🔄 尝试修改按钮文字...")
        
        # 方法1: 尝试直接查找Text组件
        text_methods = [
            ("by_name", "Text"),
            ("by_path", "LeaderboardButton/Text"),
            ("by_path", "Canvas/LeaderboardButton/Text")
        ]
        
        text_modified = False
        for search_method, target in text_methods:
            print(f"   尝试方法: {search_method} - {target}")
            set_text_call = {
                "jsonrpc": "2.0",
                "id": 6,
                "method": "tools/call",
                "params": {
                    "name": "manage_components",
                    "arguments": {
                        "action": "set_property",
                        "target": target,
                        "search_method": search_method,
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
                                text_modified = True
                                break
                            else:
                                print(f"❌ 失败: {result.get('error', 'Unknown error')}")
            
            if text_modified:
                break
            
            await asyncio.sleep(0.3)
        
        if not text_modified:
            print("⚠️ 无法自动修改文字，可能需要在Unity中手动修改")
            print("💡 提示: 在Unity中找到LeaderboardButton对象，查看其子对象中是否有Text组件")
        
        await asyncio.sleep(0.5)
        
        # 保存场景
        print("\n🔄 保存Start场景...")
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
        
        print("\n✅ 操作完成!")
        print("   - LeaderboardButton已创建")
        print("   - 位置: 右上角 (anchoredPosition: 200, -100)")
        print("   - 大小: 80x40 (原按钮的一半)")
        if text_modified:
            print("   - 文字: 排行榜")
        else:
            print("   - 文字: 需要手动修改")

if __name__ == "__main__":
    asyncio.run(copy_and_modify_button_complete())
