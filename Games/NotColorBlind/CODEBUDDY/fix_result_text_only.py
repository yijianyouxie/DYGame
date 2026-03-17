import asyncio
import aiohttp
import json

async def init_session(session, url):
    """初始化MCP session"""
    request = {
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'initialize',
        'params': {}
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream'
    }
    
    async with session.post(url, headers=headers, json=request) as response:
        text = await response.text()
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('data:'):
                data = json.loads(line[5:])
                if data.get('result', {}).get('session_id'):
                    return data['result']['session_id']
        return None

async def call_tool(session, url, headers, tool_name, params, tool_id=1):
    """调用MCP工具"""
    request = {
        'jsonrpc': '2.0',
        'id': tool_id,
        'method': 'tools/call',
        'params': {
            'name': tool_name,
            'arguments': params
        }
    }
    
    async with session.post(url, headers=headers, json=request) as response:
        text = await response.text()
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('data:'):
                data = json.loads(line[5:])
                return data
        return None

async def get_text_object_id(session, url, headers):
    """查找ResultScene中的ResultLeaderboardButton下的Text对象"""
    print("查找ResultLeaderboardButton/Text对象...")
    result = await call_tool(session, url, headers, 'find_gameobjects', {
        'scene_name': 'ResultScene',
        'path_pattern': '*ResultLeaderboardButton/Text'
    }, tool_id=100)
    
    if result and result.get('result', {}).get('contents'):
        content = result['result']['contents'][0]
        inner_text = content.get('text', '')
        if inner_text:
            inner_data = json.loads(inner_text)
            objects = inner_data.get('gameobjects', [])
            if objects:
                text_id = objects[0].get('id')
                print(f"  [+] 找到Text对象，ID: {text_id}")
                return text_id
    
    print("  [!] 未找到Text对象")
    return None

async def get_components(session, url, headers, object_id):
    """获取对象的所有组件"""
    result = await call_tool(session, url, headers, 'find_gameobjects', {
        'scene_name': 'ResultScene',
        'object_ids': [object_id]
    }, tool_id=200)
    
    if result and result.get('result', {}).get('contents'):
        content = result['result']['contents'][0]
        inner_text = content.get('text', '')
        if inner_text:
            inner_data = json.loads(inner_text)
            objects = inner_data.get('gameobjects', [])
            if objects:
                return objects[0].get('components', [])
    return []

async def main():
    url = "http://127.0.0.1:8080/mcp"
    
    async with aiohttp.ClientSession() as session:
        # 初始化session
        print("初始化MCP session...")
        session_id = await init_session(session, url)
        if not session_id:
            print("[!] 初始化失败")
            return
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream',
            'mcp-session-id': session_id
        }
        
        print(f"[-] MCP连接成功\n")
        await asyncio.sleep(1)
        
        # 加载ResultScene
        print("加载ResultScene...")
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'load',
            'build_index': 2
        }, tool_id=1)
        
        if not result or not result.get('result', {}).get('success'):
            print("[!] ResultScene加载失败")
            return
        
        print("  [+] ResultScene加载成功\n")
        
        # 查找Text对象ID
        text_id = await get_text_object_id(session, url, headers)
        if not text_id:
            print("[!] 无法找到Text对象")
            return
        
        print("\n检查Text对象的现有组件...")
        components = await get_components(session, url, headers, text_id)
        print(f"  现有组件数量: {len(components)}")
        for comp in components:
            print(f"    - {comp.get('type_name', 'Unknown')}")
        
        has_text = any('Text' in comp.get('type_name', '') for comp in components)
        
        if has_text:
            print("\n  [+] Text组件已存在")
        else:
            print("\n  [!] Text组件不存在，需要添加")
            
            # 添加Text组件
            print("\n添加Text组件...")
            result = await call_tool(session, url, headers, 'manage_components', {
                'action': 'add',
                'target': {
                    'id': text_id,
                    'scene_name': 'ResultScene'
                },
                'component_type': 'UnityEngine.UI.Text'
            }, tool_id=300)
            
            if result and result.get('result', {}).get('success'):
                print("  [+] Text组件添加成功")
            else:
                print("  [!] Text组件添加失败")
                print(f"  响应: {result}")
            
            # 设置Text组件属性
            print("\n设置Text组件属性...")
            result = await call_tool(session, url, headers, 'manage_components', {
                'action': 'modify',
                'target': {
                    'id': text_id,
                    'scene_name': 'ResultScene',
                    'component_type': 'UnityEngine.UI.Text'
                },
                'properties': {
                    'text': 'Leaderboard',
                    'fontSize': 32,
                    'alignment': 4,  # Center
                    'font': 'Assets/Font/FZLTH-GBK.TTF'
                }
            }, tool_id=301)
            
            if result and result.get('result', {}).get('success'):
                print("  [+] Text属性设置成功")
            else:
                print("  [!] Text属性设置失败")
            
            # 再次验证
            print("\n再次验证Text组件...")
            components = await get_components(session, url, headers, text_id)
            has_text = any('Text' in comp.get('type_name', '') for comp in components)
            
            if has_text:
                print("  [+] Text组件验证成功")
                for comp in components:
                    if 'Text' in comp.get('type_name', ''):
                        print(f"    类型: {comp.get('type_name')}")
                        props = comp.get('properties', {})
                        print(f"    文字: {props.get('text', '')}")
                        print(f"    字号: {props.get('fontSize', '')}")
            else:
                print("  [!] Text组件仍然不存在")
        
        # 保存场景
        print("\n保存ResultScene...")
        result = await call_tool(session, url, headers, 'manage_scene', {
            'action': 'save'
        }, tool_id=400)
        
        if result and result.get('result', {}).get('success'):
            print("  [+] ResultScene保存成功")
        else:
            print("  [!] ResultScene保存失败")

if __name__ == '__main__':
    asyncio.run(main())
