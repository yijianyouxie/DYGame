#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理多余按钮并在正确场景中重新创建
"""
import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def cleanup_and_create():
    """清理并重新创建按钮"""
    url = 'http://127.0.0.1:8080/mcp'
    headers = {
        'Accept': 'application/json,text/event-stream',
        'Content-Type': 'application/json'
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 清理多余按钮并重新创建 ===\n")
        
        # 初始化
        init_msg = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'initialize',
            'params': {
                'protocolVersion': '2024-11-05',
                'capabilities': {},
                'clientInfo': {'name': 'cleanup-buttons', 'version': '1.0.0'}
            }
        }
        
        async with session.post(url, headers=headers, json=init_msg) as response:
            session_id = response.headers.get('mcp-session-id')
            if response.status == 200:
                async for line in response.content:
                    if line.decode('utf-8').strip().startswith('data:'):
                        break
        
        if not session_id:
            print("无法获取session ID")
            return
        
        headers['mcp-session-id'] = session_id
        
        # 发送initialized
        await session.post(url, headers=headers, json={
            'jsonrpc': '2.0',
            'method': 'notifications/initialized'
        })
        
        # 查找所有ReturnButton
        print("查找所有ReturnButton...")
        find_return = {
            'jsonrpc': '2.0',
            'id': 2,
            'method': 'tools/call',
            'params': {
                'name': 'find_gameobjects',
                'arguments': {
                    'search_term': 'ReturnButton',
                    'search_method': 'by_name'
                }
            }
        }
        
        return_buttons = []
        async with session.post(url, headers=headers, json=find_return) as response:
            if response.status == 200:
                response_text = await response.text()
                for line in response_text.split('\n'):
                    line = line.strip()
                    if line.startswith('data:'):
                        data = json.loads(line[5:])
                        structured = data.get('result', {}).get('structuredContent', {})
                        if structured:
                            return_buttons = structured.get('data', {}).get('instanceIDs', [])
                            print(f"找到 {len(return_buttons)} 个ReturnButton: {return_buttons}")
        
        # 查找所有ResultLeaderboardButton
        print("\n查找所有ResultLeaderboardButton...")
        find_result = {
            'jsonrpc': '2.0',
            'id': 3,
            'method': 'tools/call',
            'params': {
                'name': 'find_gameobjects',
                'arguments': {
                    'search_term': 'ResultLeaderboardButton',
                    'search_method': 'by_name'
                }
            }
        }
        
        result_buttons = []
        async with session.post(url, headers=headers, json=find_result) as response:
            if response.status == 200:
                response_text = await response.text()
                for line in response_text.split('\n'):
                    line = line.strip()
                    if line.startswith('data:'):
                        data = json.loads(line[5:])
                        structured = data.get('result', {}).get('structuredContent', {})
                        if structured:
                            result_buttons = structured.get('data', {}).get('instanceIDs', [])
                            print(f"找到 {len(result_buttons)} 个ResultLeaderboardButton: {result_buttons}")
        
        # 删除所有找到的按钮（保留第一个ReturnButton）
        print("\n删除多余的按钮...")
        
        async def delete_object(obj_id):
            delete_call = {
                'jsonrpc': '2.0',
                'id': 100,
                'method': 'tools/call',
                'params': {
                    'name': 'manage_gameobject',
                    'arguments': {
                        'action': 'delete',
                        'target': str(obj_id)
                    }
                }
            }
            async with session.post(url, headers=headers, json=delete_call) as response:
                if response.status == 200:
                    response_text = await response.text()
                    for line in response_text.split('\n'):
                        line = line.strip()
                        if line.startswith('data:'):
                            data = json.loads(line[5:])
                            structured = data.get('result', {}).get('structuredContent', {})
                            if structured and structured.get('success'):
                                print(f"  ✅ 删除对象 {obj_id} 成功")
        
        # 删除多余的ReturnButton（保留第一个）
        if len(return_buttons) > 1:
            print(f"删除多余的ReturnButton（保留第一个）...")
            for btn_id in return_buttons[1:]:
                await delete_object(btn_id)
        
        # 删除所有ResultLeaderboardButton
        if result_buttons:
            print(f"删除所有ResultLeaderboardButton...")
            for btn_id in result_buttons:
                await delete_object(btn_id)
        
        await asyncio.sleep(0.5)
        
        # 保存当前场景
        print("\n保存LevelScene...")
        save_scene = {
            'jsonrpc': '2.0',
            'id': 10,
            'method': 'tools/call',
            'params': {
                'name': 'manage_scene',
                'arguments': {
                    'action': 'save'
                }
            }
        }
        
        async with session.post(url, headers=headers, json=save_scene) as response:
            if response.status == 200:
                response_text = await response.text()
                for line in response_text.split('\n'):
                    line = line.strip()
                    if line.startswith('data:'):
                        data = json.loads(line[5:])
                        structured = data.get('result', {}).get('structuredContent', {})
                        if structured and structured.get('success'):
                            print(f"✅ LevelScene保存成功")
        
        print("\n🎉 清理完成！")
        print("\n现在请在Unity编辑器中：")
        print("1. 打开ResultScene")
        print("2. 手动添加ResultLeaderboardButton（参考BUTTON_SETUP_GUIDE.md）")

if __name__ == '__main__':
    asyncio.run(cleanup_and_create())
