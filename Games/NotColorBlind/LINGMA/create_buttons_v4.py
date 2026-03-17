#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用正确的方式创建按钮：修正后的版本
"""
import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def init_session(session, url):
    base_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream'
    }
    
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
        return session_id

async def call_tool(session, url, headers, tool_name, arguments, tool_id=1):
    """调用MCP工具并返回结果"""
    request = {
        'jsonrpc': '2.0',
        'id': tool_id,
        'method': 'tools/call',
        'params': {
            'name': tool_name,
            'arguments': arguments
        }
    }
    
    async with session.post(url, headers=headers, json=request) as response:
        text = await response.text()
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('data:'):
                data = json.loads(line[5:])
                structured = data.get('result', {}).get('structuredContent', {})
                return structured
        return {}

async def delete_all_buttons(session, url, headers):
    """删除所有错误添加的按钮"""
    print("\n清理错误按钮...")
    
    for btn_name in ['ResultLeaderboardButton', 'ReturnButton']:
        find_result = await call_tool(session, url, headers, 'find_gameobjects', {
            'search_term': btn_name,
            'search_method': 'by_name'
        }, tool_id=10)
        
        if find_result:
            ids = find_result.get('data', {}).get('instanceIDs', [])
            if ids:
                print(f"找到 {len(ids)} 个{btn_name}")
                for btn_id in ids:
                    result = await call_tool(session, url, headers, 'manage_gameobject', {
                        'action': 'delete',
                        'target': str(btn_id)
                    }, tool_id=11)
                    if result and result.get('success'):
                        print(f"  ✅ 删除 ID={btn_id}")

async def create_button(session, url, headers, button_name, button_text, sprite_path, font_path):
    """在当前场景创建按钮"""
    print(f"\n创建按钮: {button_name}")
    
    # 1. 找到Canvas
    print("  [1/9] 查找Canvas...")
    canvas_result = await call_tool(session, url, headers, 'find_gameobjects', {
        'search_term': 'Canvas',
        'search_method': 'by_name'
    }, tool_id=99)
    
    canvas_id = None
    if canvas_result and canvas_result.get('data', {}).get('instanceIDs'):
        canvas_id = str(canvas_result['data']['instanceIDs'][0])
        print(f"    ✅ Canvas ID: {canvas_id}")
    else:
        print(f"    ❌ 未找到Canvas")
        return None
    
    # 2. 创建空GameObject
    print("  [2/9] 创建GameObject...")
    result = await call_tool(session, url, headers, 'manage_gameobject', {
        'action': 'create',
        'name': button_name,
        'parent': canvas_id
    }, tool_id=100)
    
    if not result or not result.get('success'):
        print(f"    ❌ 失败: {result}")
        return None
    
    print(f"    ✅ 创建成功")
    
    # 3. 通过名称查找新创建的GameObject
    print("  [3/9] 查找新创建的按钮...")
    find_result = await call_tool(session, url, headers, 'find_gameobjects', {
        'search_term': button_name,
        'search_method': 'by_name'
    }, tool_id=101)
    
    if not find_result or not find_result.get('data', {}).get('instanceIDs'):
        print(f"    ❌ 未找到刚创建的按钮: {button_name}")
        return None
    
    button_id = str(find_result['data']['instanceIDs'][0])
    print(f"    ✅ 按钮ID: {button_id}")
    
    # 4. 添加Button组件
    print("  [4/9] 添加Button组件...")
    result = await call_tool(session, url, headers, 'manage_gameobject', {
        'action': 'modify',
        'target': button_id,
        'components_to_add': ['UnityEngine.UI.Button']
    }, tool_id=102)
    
    if result and result.get('success'):
        print(f"    ✅ Button组件添加成功")
    else:
        print(f"    ⚠️ Button组件添加: {result}")
    
    # 5. 设置RectTransform
    print("  [5/9] 设置RectTransform...")
    await call_tool(session, url, headers, 'manage_components', {
        'action': 'set_property',
        'target': button_id,
        'component': 'RectTransform',
        'property_name': 'anchoredPosition',
        'value': [-100, -50]
    }, tool_id=103)
    
    await call_tool(session, url, headers, 'manage_components', {
        'action': 'set_property',
        'target': button_id,
        'component': 'RectTransform',
        'property_name': 'sizeDelta',
        'value': [200, 75]
    }, tool_id=104)
    
    await call_tool(session, url, headers, 'manage_components', {
        'action': 'set_property',
        'target': button_id,
        'component': 'RectTransform',
        'property_name': 'anchorMin',
        'value': [1, 1]
    }, tool_id=105)
    
    await call_tool(session, url, headers, 'manage_components', {
        'action': 'set_property',
        'target': button_id,
        'component': 'RectTransform',
        'property_name': 'anchorMax',
        'value': [1, 1]
    }, tool_id=106)
    
    await call_tool(session, url, headers, 'manage_components', {
        'action': 'set_property',
        'target': button_id,
        'component': 'RectTransform',
        'property_name': 'pivot',
        'value': [1, 1]
    }, tool_id=107)
    print(f"    ✅ RectTransform设置完成")
    
    # 6. 设置Sprite
    if sprite_path:
        print(f"  [6/9] 设置Sprite: {sprite_path}")
        await call_tool(session, url, headers, 'manage_components', {
            'action': 'set_property',
            'target': button_id,
            'component': 'UnityEngine.UI.Image',
            'property_name': 'sprite',
            'value': sprite_path
        }, tool_id=108)
        print(f"    ✅ Sprite设置完成")
    
    # 7. 创建Text子对象
    print("  [7/9] 创建Text子对象...")
    text_result = await call_tool(session, url, headers, 'manage_gameobject', {
        'action': 'create',
        'name': 'Text',
        'parent': button_id
    }, tool_id=109)
    
    if not text_result or not text_result.get('success'):
        print(f"    ❌ Text创建失败: {text_result}")
        return button_id
    
    print(f"    ✅ Text创建成功")
    
    # 8. 查找Text对象
    print("  [8/9] 查找Text对象...")
    find_text_result = await call_tool(session, url, headers, 'find_gameobjects', {
        'search_term': 'Text',
        'search_method': 'by_name'
    }, tool_id=110)
    
    text_id = None
    if find_text_result and find_text_result.get('data', {}).get('instanceIDs'):
        text_ids = find_text_result['data']['instanceIDs']
        text_id = str(text_ids[-1]) if text_ids else None
        print(f"    ✅ Text ID: {text_id}")
    else:
        print(f"    ⚠️ 未找到Text对象")
    
    if text_id:
        # 给Text添加UI组件
        await call_tool(session, url, headers, 'manage_gameobject', {
            'action': 'modify',
            'target': text_id,
            'components_to_add': ['UnityEngine.UI.Text']
        }, tool_id=111)
        
        # 设置Text属性
        await call_tool(session, url, headers, 'manage_components', {
            'action': 'set_property',
            'target': text_id,
            'component': 'UnityEngine.UI.Text',
            'property_name': 'text',
            'value': button_text
        }, tool_id=112)
        
        await call_tool(session, url, headers, 'manage_components', {
            'action': 'set_property',
            'target': text_id,
            'component': 'UnityEngine.UI.Text',
            'property_name': 'fontSize',
            'value': 32
        }, tool_id=113)
        
        if font_path:
            await call_tool(session, url, headers, 'manage_components', {
                'action': 'set_property',
                'target': text_id,
                'component': 'UnityEngine.UI.Text',
                'property_name': 'font',
                'value': font_path
            }, tool_id=114)
        
        # 设置Text的RectTransform
        await call_tool(session, url, headers, 'manage_components', {
            'action': 'set_property',
            'target': text_id,
            'component': 'RectTransform',
            'property_name': 'anchoredPosition',
            'value': [0, 0]
        }, tool_id=115)
        
        await call_tool(session, url, headers, 'manage_components', {
            'action': 'set_property',
            'target': text_id,
            'component': 'RectTransform',
            'property_name': 'sizeDelta',
            'value': [200, 75]
        }, tool_id=116)
        
        await call_tool(session, url, headers, 'manage_components', {
            'action': 'set_property',
            'target': text_id,
            'component': 'RectTransform',
            'property_name': 'anchorMin',
            'value': [0, 0]
        }, tool_id=117)
        
        await call_tool(session, url, headers, 'manage_components', {
            'action': 'set_property',
            'target': text_id,
            'component': 'RectTransform',
            'property_name': 'anchorMax',
            'value': [1, 1]
        }, tool_id=118)
        
        print(f"    ✅ Text设置完成")
    
    print("  [9/9] ✅ 按钮创建完成")
    return button_id

async def main():
    url = "http://127.0.0.1:8080/mcp"
    
    # 从Start场景获取的样式
    sprite_path = "Assets/Textures/bg_btn.png"
    font_path = "Assets/Font/FZLTH-GBK.TTF"
    
    async with aiohttp.ClientSession() as session:
        # 初始化
        session_id = await init_session(session, url)
        if not session_id:
            print("❌ 初始化失败")
            return
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream',
            'mcp-session-id': session_id
        }
        
        print("✅ MCP连接成功")
        await asyncio.sleep(1)
        
        # 清理错误按钮
        await delete_all_buttons(session, url, headers)
        
        print(f"\n使用样式:")
        print(f"  Sprite: {sprite_path}")
        print(f"  Font: {font_path}")
        
        # 在ResultScene创建按钮
        print("\n" + "=" * 60)
        print("在ResultScene创建按钮")
        print("=" * 60)
        
        # 先保存当前场景
        print("保存当前场景...")
        await call_tool(session, url, headers, 'manage_scene', {
            'action': 'save'
        }, tool_id=200)
        
        print("加载ResultScene (build_index: 2)...")
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'load',
            'build_index': 2
        }, tool_id=201)
        
        if result and result.get('success'):
            print("✅ ResultScene加载成功")
        else:
            print(f"❌ ResultScene加载失败: {result}")
            return
        
        await asyncio.sleep(2)
        
        btn_id = await create_button(session, url, headers, 'ResultLeaderboardButton', '排行榜', sprite_path, font_path)
        if btn_id:
            print(f"\n✅ ResultScene按钮创建成功: ID={btn_id}")
            
            # 保存场景
            result = await call_tool(session, url, headers, 'manage_scene', {
                'action': 'save'
            }, tool_id=202)
            if result and result.get('success'):
                print("✅ ResultScene保存成功")
        
        # 在LevelScene创建按钮
        print("\n" + "=" * 60)
        print("在LevelScene创建按钮")
        print("=" * 60)
        
        # 先保存当前场景
        print("保存当前场景...")
        await call_tool(session, url, headers, 'manage_scene', {
            'action': 'save'
        }, tool_id=300)
        
        print("加载LevelScene (build_index: 1)...")
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'load',
            'build_index': 1
        }, tool_id=301)
        
        if result and result.get('success'):
            print("✅ LevelScene加载成功")
        else:
            print(f"❌ LevelScene加载失败: {result}")
            return
        
        await asyncio.sleep(2)
        
        btn_id = await create_button(session, url, headers, 'ReturnButton', '返回', sprite_path, font_path)
        if btn_id:
            print(f"\n✅ LevelScene按钮创建成功: ID={btn_id}")
            
            # 保存场景
            result = await call_tool(session, url, headers, 'manage_scene', {
                'action': 'save'
            }, tool_id=302)
            if result and result.get('success'):
                print("✅ LevelScene保存成功")
        
        print("\n" + "=" * 60)
        print("✅ 所有操作完成！")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
