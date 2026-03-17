#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用build_index参数在ResultScene和LevelScene中创建按钮
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

async def get_resource(session, url, headers, resource_path, resource_id=1):
    """通过resource获取数据"""
    request = {
        'jsonrpc': '2.0',
        'id': resource_id,
        'method': 'resources/read',
        'params': {
            'uri': resource_path
        }
    }
    
    async with session.post(url, headers=headers, json=request) as response:
        text = await response.text()
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('data:'):
                data = json.loads(line[5:])
                return data
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

async def get_start_button_styles(session, url, headers):
    """从Start场景获取按钮样式"""
    print("\n从Start场景获取按钮样式...")
    
    # 加载Start场景 (使用build_index)
    print("加载Start场景 (build_index: 0)...")
    result = await call_tool(session, url, headers, 'manage_scene', {
        'action': 'load',
        'build_index': 0
    }, tool_id=1)
    
    if result and result.get('success'):
        print("✅ Start场景加载成功")
    else:
        print(f"❌ Start场景加载失败: {result}")
        return None, None
    
    await asyncio.sleep(2)
    
    # 查找LeaderboardButton
    print("查找LeaderboardButton...")
    find_result = await call_tool(session, url, headers, 'find_gameobjects', {
        'search_term': 'LeaderboardButton',
        'search_method': 'by_name'
    }, tool_id=2)
    
    if not find_result or not find_result.get('data', {}).get('instanceIDs'):
        print("❌ 未找到LeaderboardButton")
        return None, None
    
    leaderboard_id = str(find_result['data']['instanceIDs'][0])
    print(f"✅ 找到 LeaderboardButton: ID={leaderboard_id}")
    
    # 获取Image组件
    print("获取Image组件...")
    resource_path = f'mcpforunity://scene/gameobject/{leaderboard_id}/components'
    result = await get_resource(session, url, headers, resource_path, resource_id=3)
    
    sprite_path = None
    if result and result.get('result', {}).get('contents'):
        for content in result['result']['contents']:
            if content.get('mimeType') == 'application/json':
                data = json.loads(content['text'])
                for comp in data:
                    if comp.get('type') == 'UnityEngine.UI.Image':
                        sprite_path = comp.get('data', {}).get('sprite') or comp.get('data', {}).get('m_Sprite')
                        if sprite_path:
                            print(f"✅ 获取到Sprite: {sprite_path}")
                            break
    
    # 获取Text子对象的字体
    print("获取Text字体...")
    children_path = f'mcpforunity://scene/gameobject/{leaderboard_id}/children'
    result = await get_resource(session, url, headers, children_path, resource_id=4)
    
    font_path = None
    if result and result.get('result', {}).get('contents'):
        for content in result['result']['contents']:
            if content.get('mimeType') == 'application/json':
                data = json.loads(content['text'])
                if data and len(data) > 0:
                    text_id = str(data[0].get('instanceID', ''))
                    # 获取Text组件
                    text_resource = f'mcpforunity://scene/gameobject/{text_id}/components'
                    text_result = await get_resource(session, url, headers, text_resource, resource_id=5)
                    if text_result and text_result.get('result', {}).get('contents'):
                        for txt_content in text_result['result']['contents']:
                            if txt_content.get('mimeType') == 'application/json':
                                txt_data = json.loads(txt_content['text'])
                                for comp in txt_data:
                                    if comp.get('type') == 'UnityEngine.UI.Text':
                                        font_path = comp.get('data', {}).get('font') or comp.get('data', {}).get('m_Font')
                                        if font_path:
                                            print(f"✅ 获取到Font: {font_path}")
                                            break
    
    return sprite_path, font_path

async def create_button(session, url, headers, button_name, button_text, sprite_path, font_path):
    """在当前场景创建按钮"""
    print(f"\n创建按钮: {button_name}")
    
    # 创建GameObject
    print("  [1/7] 创建GameObject...")
    result = await call_tool(session, url, headers, 'manage_gameobject', {
        'action': 'create',
        'type': 'UnityEditor.UI.Button'
    }, tool_id=10)
    
    if not result or not result.get('success'):
        print(f"    ❌ 失败: {result}")
        return None
    
    button_id = result.get('target')
    print(f"    ✅ 创建成功: ID={button_id}")
    
    # 重命名
    print(f"  [2/7] 重命名为 {button_name}...")
    await call_tool(session, url, headers, 'manage_gameobject', {
        'action': 'set_name',
        'target': button_id,
        'new_name': button_name
    }, tool_id=11)
    
    # 设置父对象为Canvas（ID=0）
    print(f"  [3/7] 设置父对象...")
    await call_tool(session, url, headers, 'manage_gameobject', {
        'action': 'set_parent',
        'target': button_id,
        'new_parent': 0
    }, tool_id=12)
    
    # 设置RectTransform
    print(f"  [4/7] 设置RectTransform...")
    await call_tool(session, url, headers, 'manage_components', {
        'action': 'set_property',
        'target': button_id,
        'component': 'RectTransform',
        'property_name': 'anchoredPosition',
        'value': [-100, -50]
    }, tool_id=13)
    
    await call_tool(session, url, headers, 'manage_components', {
        'action': 'set_property',
        'target': button_id,
        'component': 'RectTransform',
        'property_name': 'sizeDelta',
        'value': [200, 75]
    }, tool_id=14)
    
    await call_tool(session, url, headers, 'manage_components', {
        'action': 'set_property',
        'target': button_id,
        'component': 'RectTransform',
        'property_name': 'anchorMin',
        'value': [1, 1]
    }, tool_id=15)
    
    await call_tool(session, url, headers, 'manage_components', {
        'action': 'set_property',
        'target': button_id,
        'component': 'RectTransform',
        'property_name': 'anchorMax',
        'value': [1, 1]
    }, tool_id=16)
    
    await call_tool(session, url, headers, 'manage_components', {
        'action': 'set_property',
        'target': button_id,
        'component': 'RectTransform',
        'property_name': 'pivot',
        'value': [1, 1]
    }, tool_id=17)
    print(f"    ✅ RectTransform设置完成")
    
    # 设置Sprite
    if sprite_path:
        print(f"  [5/7] 设置Sprite: {sprite_path}")
        await call_tool(session, url, headers, 'manage_components', {
            'action': 'set_property',
            'target': button_id,
            'component': 'UnityEngine.UI.Image',
            'property_name': 'sprite',
            'value': sprite_path
        }, tool_id=18)
        print(f"    ✅ Sprite设置完成")
    
    # 获取Text子对象并设置
    print(f"  [6/7] 设置Text...")
    children_resource = f'mcpforunity://scene/gameobject/{button_id}/children'
    result = await get_resource(session, url, headers, children_resource, resource_id=19)
    
    text_id = None
    if result and result.get('result', {}).get('contents'):
        for content in result['result']['contents']:
            if content.get('mimeType') == 'application/json':
                data = json.loads(content['text'])
                if data and len(data) > 0:
                    text_id = str(data[0].get('instanceID', ''))
                    break
    
    if text_id:
        # 设置文字
        await call_tool(session, url, headers, 'manage_components', {
            'action': 'set_property',
            'target': text_id,
            'component': 'UnityEngine.UI.Text',
            'property_name': 'text',
            'value': button_text
        }, tool_id=20)
        
        # 设置字体大小
        await call_tool(session, url, headers, 'manage_components', {
            'action': 'set_property',
            'target': text_id,
            'component': 'UnityEngine.UI.Text',
            'property_name': 'fontSize',
            'value': 32
        }, tool_id=21)
        
        # 设置字体
        if font_path:
            await call_tool(session, url, headers, 'manage_components', {
                'action': 'set_property',
                'target': text_id,
                'component': 'UnityEngine.UI.Text',
                'property_name': 'font',
                'value': font_path
            }, tool_id=22)
        
        print(f"    ✅ Text设置完成")
    
    print(f"  [7/7] 按钮创建完成")
    return button_id

async def main():
    url = "http://127.0.0.1:8080/mcp"
    
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
        
        # 获取Start场景按钮样式
        sprite_path, font_path = await get_start_button_styles(session, url, headers)
        
        if not sprite_path:
            print("❌ 无法获取按钮样式")
            return
        
        print(f"\n获取到的样式:")
        print(f"  Sprite: {sprite_path}")
        print(f"  Font: {font_path}")
        
        # 在ResultScene创建按钮
        print("\n" + "=" * 60)
        print("在ResultScene创建按钮")
        print("=" * 60)
        
        print("加载ResultScene (build_index: 2)...")
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'load',
            'build_index': 2
        }, tool_id=30)
        
        if result and result.get('success'):
            print("✅ ResultScene加载成功")
        else:
            print(f"❌ ResultScene加载失败: {result}")
            return
        
        await asyncio.sleep(2)
        
        btn_id = await create_button(session, url, headers, 'ResultLeaderboardButton', '排行榜', sprite_path, font_path)
        if btn_id:
            print(f"\n✅ ResultScene按钮创建成功")
            
            # 保存场景
            result = await call_tool(session, url, headers, 'manage_scene', {
                'action': 'save'
            }, tool_id=31)
            if result and result.get('success'):
                print("✅ ResultScene保存成功")
        
        # 在LevelScene创建按钮
        print("\n" + "=" * 60)
        print("在LevelScene创建按钮")
        print("=" * 60)
        
        print("加载LevelScene (build_index: 1)...")
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'load',
            'build_index': 1
        }, tool_id=40)
        
        if result and result.get('success'):
            print("✅ LevelScene加载成功")
        else:
            print(f"❌ LevelScene加载失败: {result}")
            return
        
        await asyncio.sleep(2)
        
        btn_id = await create_button(session, url, headers, 'ReturnButton', '返回', sprite_path, font_path)
        if btn_id:
            print(f"\n✅ LevelScene按钮创建成功")
            
            # 保存场景
            result = await call_tool(session, url, headers, 'manage_scene', {
                'action': 'save'
            }, tool_id=41)
            if result and result.get('success'):
                print("✅ LevelScene保存成功")
        
        print("\n" + "=" * 60)
        print("✅ 所有操作完成！")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
