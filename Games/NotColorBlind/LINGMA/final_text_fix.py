import asyncio
import aiohttp
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def final_text_fix():
    url = 'http://127.0.0.1:8080/mcp'
    headers = {
        'Accept': 'application/json,text/event-stream',
        'Content-Type': 'application/json'
    }
    
    async with aiohttp.ClientSession() as session:
        init_msg = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'initialize',
            'params': {
                'protocolVersion': '2024-11-05',
                'capabilities': {},
                'clientInfo': {'name': 'final-text-fix', 'version': '1.0.0'}
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
        
        print("🔄 尝试多种方法修改Text...")
        
        # 方法1: 使用绝对路径
        methods = [
            ("Canvas/LeaderboardButton/Text (Legacy)", "by_path"),
            ("LeaderboardButton/Text (Legacy)", "by_path"),
            ("Text (Legacy)", "by_name"),
        ]
        
        success = False
        for target, search_method in methods:
            print(f"\n🔍 尝试: {search_method} - '{target}'")
            set_text_call = {
                'jsonrpc': '2.0',
                'id': 2,
                'method': 'tools/call',
                'params': {
                    'name': 'manage_components',
                    'arguments': {
                        'action': 'set_property',
                        'target': target,
                        'search_method': search_method,
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
                                print(f"✅ 成功修改文字!")
                                success = True
                                break
                            else:
                                print(f"❌ 失败: {result.get('error', 'Unknown')}")
            
            if success:
                break
            
            await asyncio.sleep(0.3)
        
        # 方法2: 使用自定义脚本
        if not success:
            print("\n🔄 创建临时脚本修改文字...")
            create_script_call = {
                'jsonrpc': '2.0',
                'id': 3,
                'method': 'tools/call',
                'params': {
                    'name': 'create_script',
                    'arguments': {
                        'script_path': 'Assets/Scripts/FixText.cs',
                        'content': '''using UnityEngine;
using UnityEngine.UI;

public class FixText : MonoBehaviour
{
    public void FixLeaderboardText()
    {
        GameObject[] buttons = GameObject.FindGameObjectsWithTag("Untagged");
        foreach (var button in buttons)
        {
            if (button.name == "LeaderboardButton")
            {
                Text textComponent = button.GetComponentInChildren<Text>();
                if (textComponent != null)
                {
                    textComponent.text = "排行榜";
                    Debug.Log("✅ 修改LeaderboardButton文字成功");
                }
            }
        }
    }
}'''
                    }
                }
            }
            
            async with session.post(url, headers=headers, json=create_script_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            result = data.get('result', {}).get('structuredContent', {})
                            if result.get('success'):
                                print(f"✅ 脚本创建成功")
                            else:
                                print(f"❌ 脚本创建失败: {result.get('error', 'Unknown')}")
                            break
            
            await asyncio.sleep(0.5)
            
            # 将脚本添加到Canvas
            add_component_call = {
                'jsonrpc': '2.0',
                'id': 4,
                'method': 'tools/call',
                'params': {
                    'name': 'manage_components',
                    'arguments': {
                        'action': 'add',
                        'target': 'Canvas',
                        'search_method': 'by_name',
                        'component_type': 'FixText'
                    }
                }
            }
            
            async with session.post(url, headers=headers, json=add_component_call) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data:'):
                            data = json.loads(line_text[5:])
                            result = data.get('result', {}).get('structuredContent', {})
                            if result.get('success'):
                                print(f"✅ 脚本添加成功")
                            else:
                                print(f"❌ 脚本添加失败: {result.get('error', 'Unknown')}")
                            break
        
        # 保存场景
        print("\n🔄 保存场景...")
        save_scene_call = {
            'jsonrpc': '2.0',
            'id': 5,
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
                        data = json.loads(line_text[5:])
                        result = data.get('result', {}).get('structuredContent', {})
                        if result.get('success'):
                            print(f"✅ 场景保存成功")
                        break
        
        if success:
            print("\n✅ 文字修改完成!")
        else:
            print("\n⚠️ 自动修改文字失败")
            print("💡 请在Unity中手动修改:")
            print("   1. 打开Unity编辑器")
            print("   2. 在Hierarchy中找到 Canvas/LeaderboardButton")
            print("   3. 展开LeaderboardButton")
            print("   4. 选中 Text (Legacy) 对象")
            print("   5. 在Inspector中将Text属性改为'排行榜'")

if __name__ == "__main__":
    asyncio.run(final_text_fix())
