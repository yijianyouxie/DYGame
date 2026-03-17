#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加布局组件到排行榜的 ScrollContainer
解决排行榜项都堆在 (0,0) 位置的问题
"""
import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

MCP_URL = 'http://127.0.0.1:8080/mcp'

async def init_mcp_session(session):
    headers = {
        'Accept': 'application/json,text/event-stream',
        'Content-Type': 'application/json'
    }
    init_msg = {
        'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
        'params': {'protocolVersion': '2024-11-05', 'capabilities': {}, 'clientInfo': {'name': 'add-layout', 'version': '1.0'}}
    }
    session_id = None
    async with session.post(MCP_URL, headers=headers, json=init_msg) as r:
        session_id = r.headers.get('mcp-session-id')
        async for line in r.content:
            if line.decode().strip().startswith('data:'): break
    if session_id:
        headers['mcp-session-id'] = session_id
        await session.post(MCP_URL, headers=headers, json={'jsonrpc': '2.0', 'method': 'notifications/initialized', 'params': {}})
    return session_id, headers

async def call_tool(session, headers, tool_name, arguments, request_id=1):
    call_msg = {'jsonrpc': '2.0', 'id': request_id, 'method': 'tools/call', 'params': {'name': tool_name, 'arguments': arguments}}
    result = None
    async with session.post(MCP_URL, headers=headers, json=call_msg) as r:
        if r.status == 200:
            async for line in r.content:
                line_text = line.decode().strip()
                if line_text.startswith('data:'):
                    data = json.loads(line_text[5:])
                    result = data.get('result', {}).get('structuredContent', {})
                    break
    return result

async def main():
    async with aiohttp.ClientSession() as session:
        session_id, headers = await init_mcp_session(session)
        print(f"Session ID: {session_id}")

        if not session_id:
            print("[FAIL] Cannot connect to MCP")
            return

        print("\n1. 加载 LeaderboardPanel Prefab...")
        result = await call_tool(session, headers, 'unity.open_asset', {
            'path': 'Assets/Prefabs/LeaderboardPanel.prefab'
        })

        if result.get('error'):
            print(f"[FAIL] 加载 Prefab 失败: {result['error']}")
            return

        print("[OK] Prefab 加载成功")

        # 2. 给 ScrollContainer 添加 VerticalLayoutGroup 组件
        print("\n2. 给 ScrollContainer 添加 VerticalLayoutGroup 组件...")
        result = await call_tool(session, headers, 'unity.add_component', {
            'target': 6153998875634657607,  # ScrollContainer 的 ID
            'component': 'UnityEngine.UI.VerticalLayoutGroup'
        })

        if result.get('error'):
            print(f"[FAIL] 添加 VerticalLayoutGroup 失败: {result['error']}")
            return

        vlg_id = result.get('id')
        print(f"[OK] VerticalLayoutGroup 组件已添加，ID: {vlg_id}")

        # 3. 给 ScrollContainer 添加 ContentSizeFitter 组件
        print("\n3. 给 ScrollContainer 添加 ContentSizeFitter 组件...")
        result = await call_tool(session, headers, 'unity.add_component', {
            'target': 6153998875634657607,  # ScrollContainer 的 ID
            'component': 'UnityEngine.UI.ContentSizeFitter'
        })

        if result.get('error'):
            print(f"[FAIL] 添加 ContentSizeFitter 失败: {result['error']}")
            return

        csf_id = result.get('id')
        print(f"[OK] ContentSizeFitter 组件已添加，ID: {csf_id}")

        # 4. 配置 VerticalLayoutGroup 的属性
        print("\n4. 配置 VerticalLayoutGroup 属性...")
        vlg_properties = {
            'childAlignment': 0,  # UpperLeft (0)
            'childControlHeight': True,
            'childControlWidth': True,
            'childForceExpandHeight': False,
            'childForceExpandWidth': True,
            'spacing': 10.0  # 子项之间的间距
        }

        for prop_name, prop_value in vlg_properties.items():
            result = await call_tool(session, headers, 'unity.set_property', {
                'target': vlg_id,
                'property': prop_name,
                'value': prop_value
            })

            if result.get('error'):
                print(f"  [WARN] 设置 {prop_name} 失败: {result['error']}")
            else:
                print(f"  [OK] {prop_name} = {prop_value}")

        # 5. 配置 ContentSizeFitter 的属性
        print("\n5. 配置 ContentSizeFitter 属性...")
        csf_properties = {
            'verticalFit': 2,  # Preferred Size (2)
            'horizontalFit': 0  # Unconstrained (0)
        }

        for prop_name, prop_value in csf_properties.items():
            result = await call_tool(session, headers, 'unity.set_property', {
                'target': csf_id,
                'property': prop_name,
                'value': prop_value
            })

            if result.get('error'):
                print(f"  [WARN] 设置 {prop_name} 失败: {result['error']}")
            else:
                print(f"  [OK] {prop_name} = {prop_value}")

        # 6. 保存 Prefab
        print("\n6. 保存 LeaderboardPanel Prefab...")
        result = await call_tool(session, headers, 'unity.save', {
            'path': 'Assets/Prefabs/LeaderboardPanel.prefab'
        })

        if result.get('error'):
            print(f"[FAIL] 保存 Prefab 失败: {result['error']}")
            return

        print("[OK] Prefab 已保存")

        print("\n" + "="*50)
        print("[OK] 完成！已为排行榜 ScrollContainer 添加布局组件")
        print("="*50)
        print("\n已添加的组件:")
        print("  - VerticalLayoutGroup: 垂直排列子项，间距 10")
        print("  - ContentSizeFitter: 根据内容自动调整大小")
        print("\n现在排行榜项应该会自动垂直排列了。")

if __name__ == "__main__":
    asyncio.run(main())
