#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用正确的方式在LevelScene和ResultScene中创建与Start场景LeaderboardButton完全相同的按钮
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
                # 获取contents中的text字段
                if data.get('result', {}).get('contents'):
                    content = data['result']['contents'][0]
                    inner_text = content.get('text', '')
                    if inner_text:
                        # text字段是另一个JSON字符串
                        try:
                            inner_data = json.loads(inner_text)
                            return inner_data
                        except:
                            return None
                return data
        return {}

async def get_button_config(session, url, headers):
    """获取Start场景中LeaderboardButton的完整配置"""
    print("=" * 80)
    print("步骤1: 获取Start场景LeaderboardButton配置")
    print("=" * 80)
    
    # 加载Start场景
    print("\n加载Start场景...")
    result = await call_tool(session, url, headers, 'manage_scene', {
        'action': 'load',
        'build_index': 0
    }, tool_id=1)
    
    if not result or not result.get('success'):
        print("  ❌ 场景加载失败")
        return None
    print("  ✅ 场景加载成功")
    
    # 查找LeaderboardButton
    print("\n查找LeaderboardButton...")
    result = await call_tool(session, url, headers, 'find_gameobjects', {
        'search_term': 'LeaderboardButton',
        'search_method': 'by_name'
    }, tool_id=2)
    
    if not result or not result.get('data', {}).get('instanceIDs'):
        print("  ❌ 未找到LeaderboardButton")
        return None
    
    button_ids = result['data']['instanceIDs']
    button_id = str(button_ids[0])
    print(f"  ✅ 找到按钮 ID: {button_id}")
    
    # 获取组件信息
    print("\n获取按钮组件信息...")
    uri = f'mcpforunity://scene/gameobject/{button_id}/components'
    data = await get_resource(session, url, headers, uri, resource_id=3)
    
    if not data or not data.get('data', {}).get('components'):
        print("  ❌ 获取组件失败")
        return None
    
    components = data['data']['components']
    
    config = {
        'name': 'LeaderboardButton',
        'components': {}
    }
    
    for comp in components:
        comp_type = comp.get('typeName', '')
        props = comp.get('properties', {})
        
        if comp_type == 'UnityEngine.RectTransform':
            # 提取RectTransform的关键属性
            rt_config = {}
            for key in ['anchoredPosition', 'sizeDelta', 'anchorMin', 'anchorMax', 'pivot']:
                if key in props:
                    rt_config[key] = props[key]
            config['components']['RectTransform'] = rt_config
            print(f"  ✅ RectTransform: {rt_config}")
        
        elif comp_type == 'UnityEngine.UI.Image':
            img_config = {}
            sprite = props.get('sprite') or props.get('m_Sprite')
            if isinstance(sprite, str):
                img_config['sprite'] = sprite
                print(f"  ✅ Image sprite: {sprite}")
            config['components']['Image'] = img_config
        
        elif comp_type == 'UnityEngine.UI.Button':
            btn_config = {}
            transition = props.get('transition') or props.get('m_Transition')
            if transition:
                btn_config['transition'] = transition
            colors = props.get('colors') or props.get('m_Colors')
            if colors:
                btn_config['colors'] = colors
            config['components']['Button'] = btn_config
            print(f"  ✅ Button: transition={transition}")
    
    # 获取Canvas ID
    print("\n查找Canvas...")
    result = await call_tool(session, url, headers, 'find_gameobjects', {
        'search_term': 'Canvas',
        'search_method': 'by_name'
    }, tool_id=4)
    
    if result and result.get('data', {}).get('instanceIDs'):
        canvas_id = str(result['data']['instanceIDs'][0])
        config['canvas_id'] = canvas_id
        print(f"  ✅ Canvas ID: {canvas_id}")
    
    return config

async def create_button(session, url, headers, scene_name, button_name, config):
    """在指定场景中创建按钮"""
    print("\n" + "=" * 80)
    print(f"在{scene_name}创建按钮: {button_name}")
    print("=" * 80)
    
    # 1. 查找Canvas
    print("  [1/9] 查找Canvas...")
    result = await call_tool(session, url, headers, 'find_gameobjects', {
        'search_term': 'Canvas',
        'search_method': 'by_name'
    }, tool_id=100)
    
    if not result or not result.get('data', {}).get('instanceIDs'):
        print("    ❌ 未找到Canvas")
        return False
    
    canvas_id = str(result['data']['instanceIDs'][0])
    print(f"    Canvas ID: {canvas_id}")
    
    # 2. 创建GameObject
    print(f"  [2/9] 创建GameObject: {button_name}...")
    result = await call_tool(session, url, headers, 'manage_gameobject', {
        'action': 'create',
        'name': button_name,
        'parent': canvas_id
    }, tool_id=101)
    
    if not result or not result.get('success'):
        print("    ❌ 创建失败")
        return False
    print("    ✅ 创建成功")
    
    # 3. 查找新创建的按钮ID
    print("  [3/9] 查找按钮ID...")
    result = await call_tool(session, url, headers, 'find_gameobjects', {
        'search_term': button_name,
        'search_method': 'by_name'
    }, tool_id=102)
    
    if not result or not result.get('data', {}).get('instanceIDs'):
        print("    ❌ 未找到按钮")
        return False
    
    button_id = str(result['data']['instanceIDs'][0])
    print(f"    按钮ID: {button_id}")
    
    # 4. 添加RectTransform
    print("  [4/9] 添加RectTransform...")
    result = await call_tool(session, url, headers, 'manage_gameobject', {
        'action': 'modify',
        'target': button_id,
        'components_to_add': ['UnityEngine.RectTransform']
    }, tool_id=103)
    print("    ✅ RectTransform已添加")
    
    # 5. 设置RectTransform属性
    print("  [5/9] 设置RectTransform属性...")
    rt_config = config['components'].get('RectTransform', {})
    for prop_name, prop_value in rt_config.items():
        await call_tool(session, url, headers, 'manage_components', {
            'action': 'set_property',
            'target': button_id,
            'component': 'UnityEngine.RectTransform',
            'property_name': prop_name,
            'value': prop_value
        }, tool_id=104)
    print(f"    ✅ RectTransform已设置: {rt_config}")
    
    # 6. 添加Image组件
    print("  [6/9] 添加Image组件...")
    result = await call_tool(session, url, headers, 'manage_gameobject', {
        'action': 'modify',
        'target': button_id,
        'components_to_add': ['UnityEngine.UI.Image']
    }, tool_id=105)
    print("    ✅ Image已添加")
    
    # 7. 设置Image sprite
    print("  [7/9] 设置Image sprite...")
    img_config = config['components'].get('Image', {})
    sprite_path = img_config.get('sprite')
    if sprite_path:
        result = await call_tool(session, url, headers, 'manage_components', {
            'action': 'set_property',
            'target': button_id,
            'component': 'UnityEngine.UI.Image',
            'property_name': 'sprite',
            'value': sprite_path
        }, tool_id=106)
        print(f"    ✅ Sprite已设置: {sprite_path}")
    
    # 8. 添加Button组件
    print("  [8/9] 添加Button组件...")
    result = await call_tool(session, url, headers, 'manage_gameobject', {
        'action': 'modify',
        'target': button_id,
        'components_to_add': ['UnityEngine.UI.Button']
    }, tool_id=107)
    print("    ✅ Button已添加")
    
    # 9. 创建Text子对象
    print("  [9/9] 创建Text子对象...")
    result = await call_tool(session, url, headers, 'manage_gameobject', {
        'action': 'create',
        'name': 'Text',
        'parent': button_id
    }, tool_id=108)
    
    if result and result.get('success'):
        print("    ✅ Text对象已创建")
        
        # 查找Text对象ID
        result = await call_tool(session, url, headers, 'find_gameobjects', {
            'search_term': 'Text',
            'search_method': 'by_name'
        }, tool_id=109)
        
        if result and result.get('data', {}).get('instanceIDs'):
            text_ids = result['data']['instanceIDs']
            text_id = str(text_ids[-1])  # 取最后一个（最新的）
            
            # 添加RectTransform
            await call_tool(session, url, headers, 'manage_gameobject', {
                'action': 'modify',
                'target': text_id,
                'components_to_add': ['UnityEngine.RectTransform']
            }, tool_id=110)
            
            # 设置RectTransform为全拉伸
            await call_tool(session, url, headers, 'manage_components', {
                'action': 'set_property',
                'target': text_id,
                'component': 'UnityEngine.RectTransform',
                'property_name': 'anchorMin',
                'value': {'x': 0, 'y': 0}
            }, tool_id=111)
            
            await call_tool(session, url, headers, 'manage_components', {
                'action': 'set_property',
                'target': text_id,
                'component': 'UnityEngine.RectTransform',
                'property_name': 'anchorMax',
                'value': {'x': 1, 'y': 1}
            }, tool_id=112)
            
            await call_tool(session, url, headers, 'manage_components', {
                'action': 'set_property',
                'target': text_id,
                'component': 'UnityEngine.RectTransform',
                'property_name': 'pivot',
                'value': {'x': 0.5, 'y': 0.5}
            }, tool_id=113)
            
            await call_tool(session, url, headers, 'manage_components', {
                'action': 'set_property',
                'target': text_id,
                'component': 'UnityEngine.RectTransform',
                'property_name': 'anchoredPosition',
                'value': {'x': 0, 'y': 0}
            }, tool_id=114)
            
            await call_tool(session, url, headers, 'manage_components', {
                'action': 'set_property',
                'target': text_id,
                'component': 'UnityEngine.RectTransform',
                'property_name': 'sizeDelta',
                'value': {'x': 0, 'y': 0}
            }, tool_id=115)
            
            # 添加Text组件
            await call_tool(session, url, headers, 'manage_gameobject', {
                'action': 'modify',
                'target': text_id,
                'components_to_add': ['UnityEngine.UI.Text']
            }, tool_id=116)
            
            # 设置Text属性
            text_content = button_name.replace('Result', '').replace('Button', '')
            await call_tool(session, url, headers, 'manage_components', {
                'action': 'set_property',
                'target': text_id,
                'component': 'UnityEngine.UI.Text',
                'property_name': 'text',
                'value': text_content
            }, tool_id=117)
            
            # 设置字体
            await call_tool(session, url, headers, 'manage_components', {
                'action': 'set_property',
                'target': text_id,
                'component': 'UnityEngine.UI.Text',
                'property_name': 'font',
                'value': 'Assets/Font/FZLTH-GBK.TTF'
            }, tool_id=118)
            
            # 设置字体大小
            await call_tool(session, url, headers, 'manage_components', {
                'action': 'set_property',
                'target': text_id,
                'component': 'UnityEngine.UI.Text',
                'property_name': 'fontSize',
                'value': 32
            }, tool_id=119)
            
            # 设置对齐方式
            await call_tool(session, url, headers, 'manage_components', {
                'action': 'set_property',
                'target': text_id,
                'component': 'UnityEngine.UI.Text',
                'property_name': 'alignment',
                'value': 4  # Center
            }, tool_id=120)
            
            print(f"    ✅ Text已配置: {text_content}")
    
    return True

async def main():
    url = "http://127.0.0.1:8080/mcp"
    
    async with aiohttp.ClientSession() as session:
        # 初始化session
        print("初始化MCP session...")
        session_id = await init_session(session, url)
        if not session_id:
            print("❌ 初始化失败")
            return
        
        base_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream',
            'mcp-session-id': session_id
        }
        
        print(f"✅ MCP连接成功 (session_id: {session_id})")
        await asyncio.sleep(1)
        
        # 获取Start场景按钮配置
        config = await get_button_config(session, url, base_headers)
        
        if not config:
            print("❌ 获取配置失败")
            return
        
        # 保存配置
        with open('button_config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print("\n✅ 配置已保存到 button_config.json")
        
        # 在ResultScene创建按钮
        print("\n加载ResultScene...")
        result = await call_tool(session, url, base_headers, 'manage_scene', {
            'action': 'load',
            'build_index': 2
        }, tool_id=200)
        
        if result and result.get('success'):
            print("  ✅ ResultScene加载成功")
            success = await create_button(session, url, base_headers, 'ResultScene', 'ResultLeaderboardButton', config)
            
            if success:
                print("\n保存ResultScene...")
                result = await call_tool(session, url, base_headers, 'manage_scene', {
                    'action': 'save'
                }, tool_id=201)
                if result and result.get('success'):
                    print("  ✅ ResultScene保存成功")
        
        # 在LevelScene创建按钮
        print("\n加载LevelScene...")
        result = await call_tool(session, url, base_headers, 'manage_scene', {
            'action': 'load',
            'build_index': 1
        }, tool_id=300)
        
        if result and result.get('success'):
            print("  ✅ LevelScene加载成功")
            success = await create_button(session, url, base_headers, 'LevelScene', 'ReturnButton', config)
            
            if success:
                print("\n保存LevelScene...")
                result = await call_tool(session, url, base_headers, 'manage_scene', {
                    'action': 'save'
                }, tool_id=301)
                if result and result.get('success'):
                    print("  ✅ LevelScene保存成功")
        
        print("\n" + "=" * 80)
        print("✅ 任务完成！")
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
