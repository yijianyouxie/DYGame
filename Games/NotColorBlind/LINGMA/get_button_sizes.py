#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""获取Start场景中LeaderboardButton的完整样式信息"""

import asyncio
import json

async def get_button_info():
    """获取LeaderboardButton的详细信息"""
    
    # 使用stdio方式调用MCP工具
    from mcp_client import MCPClient
    
    async with MCPClient() as client:
        # 先加载Start场景
        print("=== 加载Start场景 ===")
        result = await client.call_tool('manage_scene', {
            'action': 'load',
            'sceneName': 'StartScene'
        })
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 获取场景层级
        print("\n=== 获取场景层级 ===")
        result = await client.call_tool('manage_scene', {
            'action': 'get_hierarchy'
        })
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 查找LeaderboardButton
        print("\n=== 查找LeaderboardButton ===")
        result = await client.call_tool('manage_gameobject', {
            'action': 'find',
            'search_method': 'by_name',
            'name': 'LeaderboardButton'
        })
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if result.get('success') and result.get('game_objects'):
            button = result['game_objects'][0]
            button_id = button.get('instanceID')
            button_path = button.get('path', 'Canvas/LeaderboardButton')
            
            print(f"\n找到按钮: ID={button_id}, Path={button_path}")
            
            # 获取RectTransform组件
            print("\n=== 获取RectTransform ===")
            result = await client.call_tool('manage_components', {
                'action': 'get',
                'search_method': 'by_id',
                'id': button_id,
                'component_type': 'RectTransform'
            })
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # 获取Image组件
            print("\n=== 获取Image ===")
            result = await client.call_tool('manage_components', {
                'action': 'get',
                'search_method': 'by_id',
                'id': button_id,
                'component_type': 'Image'
            })
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # 获取Button组件
            print("\n=== 获取Button ===")
            result = await client.call_tool('manage_components', {
                'action': 'get',
                'search_method': 'by_id',
                'id': button_id,
                'component_type': 'Button'
            })
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # 查找Text子对象
            print("\n=== 查找Text子对象 ===")
            result = await client.call_tool('manage_gameobject', {
                'action': 'find',
                'search_method': 'by_path',
                'path': f'{button_path}/Text'
            })
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if result.get('success') and result.get('game_objects'):
                text_obj = result['game_objects'][0]
                text_id = text_obj.get('instanceID')
                
                # 获取Text组件
                print("\n=== 获取Text组件 ===")
                result = await client.call_tool('manage_components', {
                    'action': 'get',
                    'search_method': 'by_id',
                    'id': text_id,
                    'component_type': 'Text'
                })
                print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    asyncio.run(get_button_info())
