#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用Unity MCP复制Canvas/Button按钮并修改属性
"""
import asyncio
import aiohttp
import json
import sys
import io

# 设置输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def copy_and_modify_button():
    """复制Canvas/Button并修改为排行榜按钮"""
    
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        "Accept": "application/json,text/event-stream",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        # 步骤 1: 初始化连接
        print("🔄 步骤1: 初始化连接...")
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "unity-button-copy",
                    "version": "1.0.0"
                }
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
        
        # 发送 initialized 通知
        print("🔄 发送 initialized 通知...")
        await session.post(url, headers=headers, json={
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        })
        
        # 步骤 2: 加载Start场景
        print("\n🔄 步骤2: 加载Start场景...")
        load_scene_call = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "manage_scene",
                "arguments": {
                    "action": "load",
                    "path": "Assets/Scenes/Start.scene"
                }
            }
        }
        
        async with session.post(url, headers=headers, json=load_scene_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        print(f"✅ 场景加载: {json.dumps(data.get('result', {}).get('structuredContent', {}), ensure_ascii=False, indent=2)}")
                        break
        
        await asyncio.sleep(1)
        
        # 步骤 3: 复制Canvas/Button按钮
        print("\n🔄 步骤3: 复制Canvas/Button按钮...")
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
                        print(f"✅ 按钮复制: {json.dumps(data.get('result', {}).get('structuredContent', {}), ensure_ascii=False, indent=2)}")
                        break
        
        await asyncio.sleep(0.5)
        
        # 步骤 4: 修改按钮大小为原来的一半
        print("\n🔄 步骤4: 修改按钮大小为原来的一半...")
        # 先获取原始大小
        get_size_call = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "manage_components",
                "arguments": {
                    "action": "get_property",
                    "target": "LeaderboardButton",
                    "search_method": "by_name",
                    "component_type": "RectTransform",
                    "property": "sizeDelta"
                }
            }
        }
        
        original_size = None
        async with session.post(url, headers=headers, json=get_size_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        result = data.get('result', {}).get('structuredContent', {})
                        if 'value' in result:
                            original_size = result['value']
                            print(f"📏 原始大小: {original_size}")
                        break
        
        await asyncio.sleep(0.3)
        
        if original_size:
            # 计算一半大小
            new_size = {
                "x": original_size['x'] / 2,
                "y": original_size['y'] / 2
            }
            print(f"📏 新大小(一半): {new_size}")
            
            # 设置新大小
            set_size_call = {
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
                        "property": "sizeDelta",
                        "value": new_size
                    }
                }
            }
            
            async with session.post(url, headers=headers, json=set_size_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            print(f"✅ 大小修改: {json.dumps(data.get('result', {}).get('structuredContent', {}), ensure_ascii=False, indent=2)}")
                            break
        else:
            print("⚠️ 无法获取原始大小，使用默认大小")
            # 设置一个合理的大小
            set_size_call = {
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
                            data = json.loads(line_text[5:])
                            print(f"✅ 大小修改: {json.dumps(data.get('result', {}).get('structuredContent', {}), ensure_ascii=False, indent=2)}")
                            break
        
        await asyncio.sleep(0.5)
        
        # 步骤 5: 修改按钮位置到右上角
        print("\n🔄 步骤5: 修改按钮位置到右上角...")
        set_position_call = {
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
                    "value": {"x": 200, "y": -100}
                }
            }
        }
        
        async with session.post(url, headers=headers, json=set_position_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        data = json.loads(line_text[5:])
                        print(f"✅ 位置修改: {json.dumps(data.get('result', {}).get('structuredContent', {}), ensure_ascii=False, indent=2)}")
                        break
        
        await asyncio.sleep(0.5)
        
        # 步骤 6: 修改按钮文字为"排行榜"
        print("\n🔄 步骤6: 修改按钮文字为'排行榜'...")
        set_text_call = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "manage_components",
                "arguments": {
                    "action": "set_property",
                    "target": "LeaderboardButton/Text",
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
                        print(f"✅ 文字修改: {json.dumps(data.get('result', {}).get('structuredContent', {}), ensure_ascii=False, indent=2)}")
                        break
        
        await asyncio.sleep(0.5)
        
        # 步骤 7: 保存场景
        print("\n🔄 步骤7: 保存Start场景...")
        save_scene_call = {
            "jsonrpc": "2.0",
            "id": 8,
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
                        print(f"✅ 场景保存: {json.dumps(data.get('result', {}).get('structuredContent', {}), ensure_ascii=False, indent=2)}")
                        break
        
        print("\n✅ 完成！LeaderboardButton已创建并配置完成")
        print("   - 位置: 右上角")
        print("   - 大小: 原按钮的一半")
        print("   - 文字: 排行榜")

if __name__ == "__main__":
    asyncio.run(copy_and_modify_button())
