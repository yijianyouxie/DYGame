#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查询MCP场景操作相关的API描述"""
import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def main():
    url = "http://127.0.0.1:8080/mcp"
    base_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream'
    }
    
    async with aiohttp.ClientSession() as session:
        # 初始化
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
            print(f"✅ Session ID: {session_id}")
            
            # 读取所有数据
            full_response = await response.text()
        
        headers = {**base_headers, 'mcp-session-id': session_id}
        
        # 等待初始化完成
        await asyncio.sleep(0.5)
        
        # 发送 initialized 通知
        await session.post(url, headers=headers, json={
            'jsonrpc': '2.0',
            'method': 'notifications/initialized'
        })
        
        await asyncio.sleep(0.5)
        
        # 查询工具列表
        request = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'tools/list'
        }
        
        async with session.post(url, headers=headers, json=request) as response:
            full_response = await response.text()
            tools = None
            for line in full_response.split('\n'):
                line = line.strip()
                if line.startswith('data:'):
                    data = json.loads(line[5:])
                    tools = data.get('result', {})
                    break
            
            if tools:
                # 打印所有与场景相关的工具
                scene_related_tools = []
                for tool in tools.get('tools', []):
                    tool_name = tool['name']
                    if 'scene' in tool_name.lower():
                        scene_related_tools.append(tool)
                
                print("\n" + "=" * 80)
                print(f"场景相关工具 (共 {len(scene_related_tools)} 个):")
                print("=" * 80)
                for i, tool in enumerate(scene_related_tools, 1):
                    print(f"\n{i}. {tool['name']}")
                    print(f"   标题: {tool.get('title', 'N/A')}")
                    print(f"   描述: {tool.get('description', 'N/A')}")
                    print(f"   输入参数:")
                    if 'inputSchema' in tool:
                        props = tool['inputSchema'].get('properties', {})
                        required = tool['inputSchema'].get('required', [])
                        for prop_name, prop_info in props.items():
                            is_required = ' (必需)' if prop_name in required else ' (可选)'
                            print(f"      - {prop_name}{is_required}: {prop_info.get('description', prop_info.get('type', 'N/A'))}")
                            if 'enum' in prop_info:
                                print(f"        可选值: {prop_info['enum']}")
                    print(f"   输出:")
                    if 'outputSchema' in tool:
                        print(f"      {tool['outputSchema']}")
                
                # 详细输出 manage_scene 工具
                print("\n" + "=" * 80)
                print("manage_scene 工具详细信息:")
                print("=" * 80)
                for tool in tools.get('tools', []):
                    if tool['name'] == 'manage_scene':
                        print(json.dumps(tool, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
