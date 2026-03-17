#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
正确地在ResultScene和LevelScene中创建按钮，并应用Start场景按钮的样式
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

async def delete_all_buttons_by_name(session, url, headers, button_name):
    """删除所有同名按钮"""
    find_result = await call_tool(session, url, headers, 'find_gameobjects', {
        'search_term': button_name,
        'search_method': 'by_name'
    }, tool_id=10)
    
    if find_result:
        existing_ids = find_result.get('data', {}).get('instanceIDs', [])
        if existing_ids:
            print(f"找到 {len(existing_ids)} 个{button_name}，删除...")
            for btn_id in existing_ids:
                result = await call_tool(session, url, headers, 'manage_gameobject', {
                    'action': 'delete',
                    'target': str(btn_id)
                }, tool_id=11)
                if result and result.get('success'):
                    print(f"✅ 删除成功: ID={btn_id}")
            await asyncio.sleep(0.5)
    
    return True

async def load_scene(session, url, headers, scene_path):
    """加载场景"""
    print(f"\n🔄 加载场景: {scene_path}")
    result = await call_tool(session, url, headers, 'manage_scene', {
        'action': 'load',
        'path': scene_path
    })
    
    if result and result.get('success'):
        print(f"✅ 场景加载成功")
        await asyncio.sleep(3)  # 等待场景完全加载
        return True
    else:
        print(f"❌ 场景加载失败: {result}")
        return False

async def save_scene(session, url, headers, scene_path):
    """保存场景"""
    print(f"\n💾 保存场景: {scene_path}")
    result = await call_tool(session, url, headers, 'manage_scene', {
        'action': 'save',
        'path': scene_path
    })
    
    if result and result.get('success'):
        print(f"✅ 场景保存成功")
        return True
    else:
        print(f"❌ 场景保存失败: {result}")
        return False

async def get_leaderboard_button_id(session, url, headers):
    """获取Start场景中LeaderboardButton的ID"""
    print("\n🔍 查找 StartScene 中的 LeaderboardButton")
    result = await call_tool(session, url, headers, 'find_gameobjects', {
        'search_term': 'LeaderboardButton',
        'search_method': 'by_name'
    }, tool_id=20)
    
    if result and result.get('data', {}).get('instanceIDs'):
        ids = result['data']['instanceIDs']
        print(f"✅ 找到 LeaderboardButton: {ids}")
        return str(ids[0])
    else:
        print("❌ 未找到 LeaderboardButton")
        return None

async def get_image_component(session, url, headers, go_id):
    """获取GameObject的Image组件"""
    print(f"\n🔍 获取 Image 组件 (ID: {go_id})")
    
    # 尝试通过resource获取组件数据
    resource_path = f'mcpforunity://scene/gameobject/{go_id}/components'
    result = await get_resource(session, url, headers, resource_path, resource_id=30)
    
    if result and result.get('result', {}).get('contents'):
        for content in result['result']['contents']:
            if content.get('mimeType') == 'application/json':
                data = json.loads(content['text'])
                # 查找Image组件
                for comp in data:
                    if comp.get('type') == 'UnityEngine.UI.Image':
                        sprite = comp.get('data', {}).get('sprite') or comp.get('data', {}).get('m_Sprite')
                        print(f"✅ Image组件找到，sprite: {sprite}")
                        return sprite
    return None

async def get_text_component(session, url, headers, go_id):
    """获取GameObject的Text组件（用于获取字体）"""
    print(f"\n🔍 获取 Text 组件 (ID: {go_id})")
    
    # 先找到Text子对象
    resource_path = f'mcpforunity://scene/gameobject/{go_id}/children'
    result = await get_resource(session, url, headers, resource_path, resource_id=31)
    
    if result and result.get('result', {}).get('contents'):
        for content in result['result']['contents']:
            if content.get('mimeType') == 'application/json':
                data = json.loads(content['text'])
                if data and len(data) > 0:
                    text_id = str(data[0].get('instanceID', ''))
                    print(f"✅ 找到Text子对象: ID={text_id}")
                    
                    # 获取Text组件
                    text_resource = f'mcpforunity://scene/gameobject/{text_id}/components'
                    text_result = await get_resource(session, url, headers, text_resource, resource_id=32)
                    
                    if text_result and text_result.get('result', {}).get('contents'):
                        for txt_content in text_result['result']['contents']:
                            if txt_content.get('mimeType') == 'application/json':
                                txt_data = json.loads(txt_content['text'])
                                for comp in txt_data:
                                    if comp.get('type') == 'UnityEngine.UI.Text':
                                        font = comp.get('data', {}).get('font') or comp.get('data', {}).get('m_Font')
                                        print(f"✅ Text组件找到，font: {font}")
                                        return font, text_id
    
    return None, None

async def create_button_in_scene(session, url, headers, button_name, button_text, sprite_path, font_path=None):
    """在当前场景中创建按钮"""
    print(f"\n🔨 创建按钮: {button_name}")
    
    # 1. 创建GameObject
    result = await call_tool(session, url, headers, 'manage_gameobject', {
        'action': 'create',
        'type': 'UnityEditor.UI.Button'
    }, tool_id=40)
    
    if not result or not result.get('success'):
        print(f"❌ GameObject创建失败: {result}")
        return None
    
    button_id = result.get('target')
    print(f"✅ GameObject创建成功: ID={button_id}")
    
    # 2. 重命名
    await call_tool(session, url, headers, 'manage_gameobject', {
        'action': 'set_name',
        'target': button_id,
        'new_name': button_name
    }, tool_id=41)
    
    # 3. 设置RectTransform属性（右上角）
    await call_tool(session, url, headers, 'manage_gameobject', {
        'action': 'set_parent',
        'target': button_id,
        'new_parent': 0  # Canvas的ID通常是0
    }, tool_id=42)
    
    # 设置RectTransform
    await call_tool(session, url, headers, 'manage_components', {
        'action': 'set_property',
        'target': button_id,
        'component': 'RectTransform',
        'property_name': 'anchoredPosition',
        'value': [-100, -50]
    }, tool_id=43)
    
    await call_tool(session, url, headers, 'manage_components', {
        'action': 'set_property',
        'target': button_id,
        'component': 'RectTransform',
        'property_name': 'sizeDelta',
        'value': [200, 75]
    }, tool_id=44)
    
    await call_tool(session, url, headers, 'manage_components', {
        'action': 'set_property',
        'target': button_id,
        'component': 'RectTransform',
        'property_name': 'anchorMin',
        'value': [1, 1]
    }, tool_id=45)
    
    await call_tool(session, url, headers, 'manage_components', {
        'action': 'set_property',
        'target': button_id,
        'component': 'RectTransform',
        'property_name': 'anchorMax',
        'value': [1, 1]
    }, tool_id=46)
    
    await call_tool(session, url, headers, 'manage_components', {
        'action': 'set_property',
        'target': button_id,
        'component': 'RectTransform',
        'property_name': 'pivot',
        'value': [1, 1]
    }, tool_id=47)
    
    print(f"✅ RectTransform设置完成")
    
    # 4. 设置Image的sprite
    if sprite_path:
        await call_tool(session, url, headers, 'manage_components', {
            'action': 'set_property',
            'target': button_id,
            'component': 'UnityEngine.UI.Image',
            'property_name': 'sprite',
            'value': sprite_path
        }, tool_id=48)
        print(f"✅ Sprite设置完成: {sprite_path}")
    
    # 5. 获取Text子对象
    resource_path = f'mcpforunity://scene/gameobject/{button_id}/children'
    result = await get_resource(session, url, headers, resource_path, resource_id=49)
    
    text_id = None
    if result and result.get('result', {}).get('contents'):
        for content in result['result']['contents']:
            if content.get('mimeType') == 'application/json':
                data = json.loads(content['text'])
                if data and len(data) > 0:
                    text_id = str(data[0].get('instanceID', ''))
                    print(f"✅ 找到Text子对象: ID={text_id}")
    
    if text_id:
        # 设置Text
        await call_tool(session, url, headers, 'manage_components', {
            'action': 'set_property',
            'target': text_id,
            'component': 'UnityEngine.UI.Text',
            'property_name': 'text',
            'value': button_text
        }, tool_id=50)
        
        await call_tool(session, url, headers, 'manage_components', {
            'action': 'set_property',
            'target': text_id,
            'component': 'UnityEngine.UI.Text',
            'property_name': 'fontSize',
            'value': 32
        }, tool_id=51)
        
        # 设置字体
        if font_path:
            await call_tool(session, url, headers, 'manage_components', {
                'action': 'set_property',
                'target': text_id,
                'component': 'UnityEngine.UI.Text',
                'property_name': 'font',
                'value': font_path
            }, tool_id=52)
            print(f"✅ Font设置完成: {font_path}")
        
        await call_tool(session, url, headers, 'manage_components', {
            'action': 'set_property',
            'target': text_id,
            'component': 'RectTransform',
            'property_name': 'anchoredPosition',
            'value': [0, 0]
        }, tool_id=53)
        
        await call_tool(session, url, headers, 'manage_components', {
            'action': 'set_property',
            'target': text_id,
            'component': 'RectTransform',
            'property_name': 'sizeDelta',
            'value': [200, 75]
        }, tool_id=54)
        
        await call_tool(session, url, headers, 'manage_components', {
            'action': 'set_property',
            'target': text_id,
            'component': 'RectTransform',
            'property_name': 'anchorMin',
            'value': [0, 0]
        }, tool_id=55)
        
        await call_tool(session, url, headers, 'manage_components', {
            'action': 'set_property',
            'target': text_id,
            'component': 'RectTransform',
            'property_name': 'anchorMax',
            'value': [1, 1]
        }, tool_id=56)
        
        print(f"✅ Text设置完成")
    
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
        
        print("✅ MCP连接成功\n")
        await asyncio.sleep(1)
        
        # ===== 步骤1: 清理所有错误添加的按钮 =====
        print("=" * 60)
        print("步骤1: 清理错误添加的按钮")
        print("=" * 60)
        
        await delete_all_buttons_by_name(session, url, headers, 'ResultLeaderboardButton')
        await delete_all_buttons_by_name(session, url, headers, 'ReturnButton')
        
        # ===== 步骤2: 加载StartScene并获取按钮样式 =====
        print("\n" + "=" * 60)
        print("步骤2: 获取StartScene LeaderboardButton样式")
        print("=" * 60)
        
        if not await load_scene(session, url, headers, 'Assets/Scenes/Start.scene'):
            return
        
        leaderboard_id = await get_leaderboard_button_id(session, url, headers)
        if not leaderboard_id:
            print("❌ 无法找到LeaderboardButton")
            return
        
        sprite_path = await get_image_component(session, url, headers, leaderboard_id)
        font_path, _ = await get_text_component(session, url, headers, leaderboard_id)
        
        print(f"\n📋 获取到的样式:")
        print(f"  - Sprite: {sprite_path}")
        print(f"  - Font: {font_path}")
        
        # ===== 步骤3: 在ResultScene创建按钮 =====
        print("\n" + "=" * 60)
        print("步骤3: 在ResultScene创建排行榜按钮")
        print("=" * 60)
        
        if not await load_scene(session, url, headers, 'Assets/Scenes/ResultScene.unity'):
            return
        
        result_btn_id = await create_button_in_scene(
            session, url, headers, 
            'ResultLeaderboardButton', '排行榜', 
            sprite_path, font_path
        )
        
        if result_btn_id:
            print(f"\n✅ ResultScene按钮创建成功: ID={result_btn_id}")
            await save_scene(session, url, headers, 'Assets/Scenes/ResultScene.unity')
        else:
            print(f"❌ ResultScene按钮创建失败")
        
        # ===== 步骤4: 在LevelScene创建按钮 =====
        print("\n" + "=" * 60)
        print("步骤4: 在LevelScene创建返回按钮")
        print("=" * 60)
        
        if not await load_scene(session, url, headers, 'Assets/Scenes/LevelScene.unity'):
            return
        
        return_btn_id = await create_button_in_scene(
            session, url, headers, 
            'ReturnButton', '返回', 
            sprite_path, font_path
        )
        
        if return_btn_id:
            print(f"\n✅ LevelScene按钮创建成功: ID={return_btn_id}")
            await save_scene(session, url, headers, 'Assets/Scenes/LevelScene.unity')
        else:
            print(f"❌ LevelScene按钮创建失败")
        
        print("\n" + "=" * 60)
        print("✅ 所有操作完成！")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
