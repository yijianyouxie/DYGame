import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def direct_text_modify():
    url = 'http://127.0.0.1:8080/mcp'
    headers = {
        'Accept': 'application/json,text/event-stream',
        'Content-Type': 'application/json'
    }
    
    async with aiohttp.ClientSession() as session:
        # 初始化
        init_msg = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'initialize',
            'params': {
                'protocolVersion': '2024-11-05',
                'capabilities': {},
                'clientInfo': {'name': 'direct-text-modify', 'version': '1.0.0'}
            }
        }
        
        async with session.post(url, headers=headers, json=init_msg) as response:
            session_id = response.headers.get('mcp-session-id')
            if response.status == 200:
                async for line in response.content:
                    if line.decode('utf-8').strip().startswith('data:'):
                        break
        
        if not session_id:
            return
        
        headers['mcp-session-id'] = session_id
        
        await session.post(url, headers=headers, json={
            'jsonrpc': '2.0',
            'method': 'notifications/initialized',
            'params': {}
        })
        
        print("🔄 尝试直接修改Text (Legacy)组件...")
        
        # 尝试各种可能的路径
        paths = [
            'Canvas/LeaderboardButton/Text (Legacy)',
            'LeaderboardButton/Text (Legacy)',
            'Canvas/LeaderboardButton/Text',
            'LeaderboardButton/Text',
        ]
        
        success = False
        for path in paths:
            print(f"\n尝试路径: '{path}'")
            
            # 首先尝试获取对象信息
            get_info_call = {
                'jsonrpc': '2.0',
                'id': 2,
                'method': 'tools/call',
                'params': {
                    'name': 'manage_gameobject',
                    'arguments': {
                        'action': 'get_info',
                        'target': path,
                        'search_method': 'by_path'
                    }
                }
            }
            
            async with session.post(url, headers=headers, json=get_info_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            result = data.get('result', {}).get('structuredContent', {})
                            if result.get('success'):
                                obj_data = result.get('data', {})
                                print(f"✅ 找到对象: {obj_data.get('name')}")
                                print(f"   组件: {obj_data.get('componentNames', [])}")
                                
                                # 尝试修改文字
                                set_text_call = {
                                    'jsonrpc': '2.0',
                                    'id': 3,
                                    'method': 'tools/call',
                                    'params': {
                                        'name': 'manage_components',
                                        'arguments': {
                                            'action': 'set_property',
                                            'target': path,
                                            'search_method': 'by_path',
                                            'component_type': 'Text',
                                            'property': 'text',
                                            'value': '排行榜'
                                        }
                                    }
                                }
                                
                                async with session.post(url, headers=headers, json=set_text_call) as response:
                                    if response.status == 200:
                                        async for line in response.content:
                                            line_text = line.decode('utf-8').strip()
                                            if line_text.startswith('data:'):
                                                data = json.loads(line_text[5:])
                                                result = data.get('result', {}).get('structuredContent', {})
                                                if result.get('success'):
                                                    print(f"✅ 成功修改文字为'排行榜'!")
                                                    success = True
                                                else:
                                                    print(f"❌ 修改失败: {result.get('error', 'Unknown')}")
                                                break
                            else:
                                print(f"❌ 未找到对象: {result.get('error', 'Unknown')}")
            
            if success:
                break
            
            await asyncio.sleep(0.3)
        
        if not success:
            print("\n⚠️ 无法通过路径找到Text对象")
            print("💡 原因可能是:")
            print("   1. 路径不正确")
            print("   2. Text (Legacy) 对象在复制时没有被包含")
            print("   3. MCP的by_path搜索功能有限制")
            print("\n建议:")
            print("   在Unity编辑器中手动修改Text (Legacy)的text属性为'排行榜'")
        
        # 保存场景
        print("\n🔄 保存场景...")
        save_scene_call = {
            'jsonrpc': '2.0',
            'id': 99,
            'method': 'tools/call',
            'params': {
                'name': 'manage_scene',
                'arguments': {
                    'action': 'save'
                }
            }
        }
        
        async with session.post(url, headers=headers, json=save_scene_call) as response:
            if response.status == 200:
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    if line_text.startswith('data:'):
                        print(f"✅ 场景保存成功")
                        break

if __name__ == "__main__":
    asyncio.run(direct_text_modify())
