#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复ReturnButton的RectTransform属性
"""
import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def fix_button_properties():
    """修复按钮属性"""
    url = 'http://127.0.0.1:8080/mcp'
    headers = {
        'Accept': 'application/json,text/event-stream',
        'Content-Type': 'application/json'
    }
    
    async with aiohttp.ClientSession() as session:
        print("\n=== 修复ReturnButton的RectTransform属性 ===\n")
        
        # 初始化
        init_msg = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'initialize',
            'params': {
                'protocolVersion': '2024-11-05',
                'capabilities': {},
                'clientInfo': {'name': 'fix-button', 'version': '1.0.0'}
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
        
        # 设置ReturnButton的RectTransform属性
        print("设置ReturnButton的RectTransform属性...")
        
        async def set_property(prop_name, value):
            set_prop = {
                'jsonrpc': '2.0',
                'id': 100,
                'method': 'tools/call',
                'params': {
                    'name': 'manage_components',
                    'arguments': {
                        'action': 'set_property',
                        'search_method': 'by_name',
                        'target': 'ReturnButton',
                        'component_type': 'RectTransform',
                        'property': prop_name,
                        'value': value
                    }
                }
            }
            async with session.post(url, headers=headers, json=set_prop) as response:
                if response.status == 200:
                    response_text = await response.text()
                    for line in response_text.split('\n'):
                        line = line.strip()
                        if line.startswith('data:'):
                            data = json.loads(line[5:])
                            structured = data.get('result', {}).get('structuredContent', {})
                            if structured and structured.get('success'):
                                print(f"  ✅ {prop_name}设置成功")
                            elif structured:
                                print(f"  ❌ {prop_name}设置失败: {structured}")
        
        await set_property('anchorMin', {'x': 1, 'y': 1})
        await asyncio.sleep(0.3)
        await set_property('anchorMax', {'x': 1, 'y': 1})
        await asyncio.sleep(0.3)
        await set_property('anchoredPosition', {'x': -100, 'y': -50})
        await asyncio.sleep(0.3)
        await set_property('sizeDelta', {'x': 200, 'y': 75})
        
        # 设置Text属性
        print("\n设置Text属性...")
        
        async def set_text_property(prop_name, value, comp_type='UnityEngine.UI.Text'):
            set_prop = {
                'jsonrpc': '2.0',
                'id': 100,
                'method': 'tools/call',
                'params': {
                    'name': 'manage_components',
                    'arguments': {
                        'action': 'set_property',
                        'search_method': 'by_name',
                        'target': 'Text',
                        'component_type': comp_type,
                        'property': prop_name,
                        'value': value
                    }
                }
            }
            async with session.post(url, headers=headers, json=set_prop) as response:
                if response.status == 200:
                    response_text = await response.text()
                    for line in response_text.split('\n'):
                        line = line.strip()
                        if line.startswith('data:'):
                            data = json.loads(line[5:])
                            structured = data.get('result', {}).get('structuredContent', {})
                            if structured and structured.get('success'):
                                print(f"  ✅ Text.{prop_name}设置成功")
                            elif structured:
                                print(f"  ❌ Text.{prop_name}设置失败: {structured}")
        
        await set_text_property('fontSize', 32)
        await asyncio.sleep(0.3)
        await set_text_property('text', '返回')
        
        # 设置Text的RectTransform属性
        print("\n设置Text的RectTransform属性...")
        await set_text_property('anchorMin', {'x': 0, 'y': 0}, 'RectTransform')
        await asyncio.sleep(0.3)
        await set_text_property('anchorMax', {'x': 1, 'y': 1}, 'RectTransform')
        await asyncio.sleep(0.3)
        await set_text_property('anchoredPosition', {'x': 0, 'y': 0}, 'RectTransform')
        await asyncio.sleep(0.3)
        await set_text_property('sizeDelta', {'x': 0, 'y': 0}, 'RectTransform')
        
        # 保存场景
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
        
        print("\n🎉 ReturnButton属性修复完成！")

if __name__ == '__main__':
    asyncio.run(fix_button_properties())
